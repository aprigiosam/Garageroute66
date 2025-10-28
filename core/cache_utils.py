"""
Utilitários para cache otimizado do GarageRoute66
"""
from django.core.cache import cache
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime
from functools import wraps
import hashlib
import json
import calendar


def _start_of_month(aware_dt):
    """Retorna o início do mês para um datetime consciente."""
    return aware_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _add_months(aware_dt, months):
    """Adiciona meses a um datetime consciente preservando o fuso."""
    year = aware_dt.year + (aware_dt.month - 1 + months) // 12
    month = (aware_dt.month - 1 + months) % 12 + 1
    day = min(aware_dt.day, calendar.monthrange(year, month)[1])
    return aware_dt.replace(year=year, month=month, day=day)


def cache_key_generator(*args, **kwargs):
    """Gera chave de cache única baseada nos argumentos"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached_query(timeout=300, key_prefix=''):
    """Decorator para cache de queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = f"{key_prefix}_{func.__name__}_{cache_key_generator(*args, **kwargs)}"

            # Tentar buscar do cache
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)

            return result
        return wrapper
    return decorator


class DashboardCache:
    """Gerenciador de cache para dashboard"""

    CACHE_TIMEOUT = 300  # 5 minutos

    @classmethod
    def get_stats(cls):
        """Obtém estatísticas do dashboard com cache"""
        cache_key = 'dashboard_stats'
        stats = cache.get(cache_key)

        if stats is None:
            from .models import Cliente, Veiculo, OrdemServico

            agora = timezone.localtime()
            mes_inicio = _start_of_month(agora)

            stats = {
                'total_clientes': Cliente.objects.filter(ativo=True).count(),
                'total_veiculos': Veiculo.objects.filter(ativo=True).count(),
                'ordens_abertas': OrdemServico.objects.filter(
                    status__in=[OrdemServico.Status.ABERTA, OrdemServico.Status.EM_ANDAMENTO]
                ).count(),
                'ordens_mes': OrdemServico.objects.filter(data_abertura__gte=mes_inicio).count(),
                'faturamento_mes': OrdemServico.objects.filter(
                    data_abertura__gte=mes_inicio,
                    status=OrdemServico.Status.ENTREGUE
                ).aggregate(total=Sum('total'))['total'] or 0,
            }

            cache.set(cache_key, stats, cls.CACHE_TIMEOUT)

        return stats

    @classmethod
    def clear_stats(cls):
        """Limpa cache das estatísticas"""
        cache.delete('dashboard_stats')

    @classmethod
    def get_faturamento_mensal(cls, meses=6):
        """Obtém dados de faturamento mensal com cache"""
        cache_key = f'faturamento_mensal_{meses}'
        dados = cache.get(cache_key)

        if dados is None:
            from .models import OrdemServico

            agora = timezone.localtime()
            inicio_mes_atual = _start_of_month(agora)
            dados = []

            for offset in range(meses):
                periodo_inicio = _start_of_month(_add_months(inicio_mes_atual, -offset))
                periodo_fim = _start_of_month(_add_months(inicio_mes_atual, -offset + 1))

                valor = OrdemServico.objects.filter(
                    data_abertura__gte=periodo_inicio,
                    data_abertura__lt=periodo_fim,
                    status=OrdemServico.Status.ENTREGUE
                ).aggregate(total=Sum('total'))['total'] or 0

                dados.append({
                    'mes': periodo_inicio.strftime('%b/%Y'),
                    'valor': float(valor)
                })

            dados.reverse()
            cache.set(cache_key, dados, cls.CACHE_TIMEOUT)

        return dados


class QueryCache:
    """Utilitários para cache de queries complexas"""

    @staticmethod
    @cached_query(timeout=600, key_prefix='clientes')
    def get_clientes_ativos():
        """Lista clientes ativos com cache"""
        from .models import Cliente
        return Cliente.objects.filter(ativo=True).order_by('nome')

    @staticmethod
    @cached_query(timeout=600, key_prefix='veiculos')
    def get_veiculos_com_cliente():
        """Lista veículos com dados do cliente"""
        from .models import Veiculo
        return Veiculo.objects.select_related('cliente').filter(ativo=True).order_by('placa')

    @staticmethod
    @cached_query(timeout=300, key_prefix='ordens')
    def get_ordens_abertas():
        """Lista ordens de serviço abertas otimizada"""
        from .models import OrdemServico
        return OrdemServico.objects.select_related(
            'veiculo__cliente', 'responsavel_tecnico'
        ).filter(
            status__in=[OrdemServico.Status.ABERTA, OrdemServico.Status.EM_ANDAMENTO]
        ).order_by('-data_abertura')

    @staticmethod
    def clear_all():
        """Limpa todos os caches de queries"""
        cache_keys = [
            'clientes_*', 'veiculos_*', 'ordens_*', 'dashboard_*'
        ]
        for pattern in cache_keys:
            cache.delete_pattern(pattern)


def invalidate_model_cache(model_name):
    """Invalida cache relacionado a um modelo específico"""
    patterns = [
        f'{model_name.lower()}_*',
        'dashboard_*',
        'ordens_*' if model_name == 'OrdemServico' else '',
    ]

    for pattern in patterns:
        if pattern:
            try:
                cache.delete_pattern(pattern)
            except AttributeError:
                # Fallback para backends que não suportam delete_pattern
                pass


# Decorators específicos para views
def cache_page_if_not_staff(timeout=300):
    """Cache página apenas para usuários não-staff"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_staff:
                from django.views.decorators.cache import cache_page
                cached_view = cache_page(timeout)(view_func)
                return cached_view(request, *args, **kwargs)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
