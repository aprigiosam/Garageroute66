from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg, Prefetch
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Cliente, OrdemServico, Veiculo, StatusHistorico, Agendamento
from .forms import (
    ClienteForm, OrdemServicoForm, VeiculoForm,
    FiltroOrdemServicoForm, AgendamentoForm, RelatorioForm,
    ItemOrdemServicoFormSet
)
from .cache_utils import DashboardCache, QueryCache, cache_page_if_not_staff
from .backup_utils import create_db_backup
from django.core.management.base import CommandError


@login_required
@cache_page_if_not_staff(timeout=300)
def dashboard(request):
    """Dashboard principal com estatísticas otimizadas"""
    hoje = timezone.now().date()

    # Usar cache para estatísticas básicas
    stats = DashboardCache.get_stats()

    # Ordens por status
    ordens_por_status = OrdemServico.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Ordens urgentes com prefetch otimizado
    ordens_urgentes = OrdemServico.objects.select_related(
        'veiculo__cliente'
    ).filter(
        prioridade=OrdemServico.Prioridade.URGENTE,
        status__in=[OrdemServico.Status.ABERTA, OrdemServico.Status.EM_ANDAMENTO]
    )[:5]

    # Ordens vencidas
    ordens_vencidas = OrdemServico.objects.select_related(
        'veiculo__cliente'
    ).filter(
        prazo_entrega__lt=timezone.now(),
        status__in=[OrdemServico.Status.ABERTA, OrdemServico.Status.EM_ANDAMENTO]
    )[:5]

    # Agendamentos de hoje
    agendamentos_hoje = Agendamento.objects.select_related(
        'cliente', 'veiculo'
    ).filter(
        data_agendamento__date=hoje,
        confirmado=True
    ).order_by('data_agendamento')[:5]

    # Faturamento mensal com cache
    faturamento_mensal = DashboardCache.get_faturamento_mensal()

    context = {
        'stats': stats,
        'faturamento_mes': stats['faturamento_mes'],
        'ordens_por_status': ordens_por_status,
        'ordens_urgentes': ordens_urgentes,
        'ordens_vencidas': ordens_vencidas,
        'agendamentos_hoje': agendamentos_hoje,
        'faturamento_mensal': json.dumps(faturamento_mensal),
    }

    return render(request, 'core/dashboard.html', context)


@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, user=request.user)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente {cliente.nome} cadastrado com sucesso.")
            return redirect(reverse('core:cadastrar_cliente'))
    else:
        form = ClienteForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'core/cadastrar_cliente.html', context)


@login_required
def listar_clientes(request):
    clientes = Cliente.objects.filter(ativo=True).order_by('nome')
    
    # Busca
    busca = request.GET.get('busca')
    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(telefone__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(clientes, 20)
    page = request.GET.get('page')
    clientes = paginator.get_page(page)
    
    context = {
        'clientes': clientes,
        'busca': busca,
    }
    return render(request, 'core/listar_clientes.html', context)


@csrf_protect
def login_usuario(request):
    if request.user.is_authenticated:
        return redirect(reverse('core:dashboard'))

    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        css = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f"{css} form-control".strip()

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Bem-vindo, {user.get_full_name() or user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next') or reverse('core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    context = {'form': form, 'next': request.GET.get('next', '')}
    return render(request, 'core/login.html', context)


@login_required
def logout_usuario(request):
    auth_logout(request)
    messages.info(request, "Sessão encerrada com sucesso.")
    return redirect(reverse('core:login'))


@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cliente {cliente.nome} atualizado com sucesso.")
            return redirect(reverse('core:listar_clientes'))
    else:
        form = ClienteForm(instance=cliente, user=request.user)
    
    context = {'form': form, 'cliente': cliente}
    return render(request, 'core/editar_cliente.html', context)


@login_required
def cadastrar_veiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST, user=request.user)
        if form.is_valid():
            veiculo = form.save()
            cliente_nome = veiculo.cliente.nome if veiculo.cliente else 'sem cliente vinculado'
            messages.success(
                request,
                f"Veículo {veiculo.placa} cadastrado para {cliente_nome}.",
            )
            return redirect(reverse('core:cadastrar_veiculo'))
    else:
        form = VeiculoForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'core/cadastrar_veiculo.html', context)


@login_required
def editar_veiculo(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Veículo {veiculo.placa} atualizado com sucesso.",
            )
            return redirect(reverse('core:listar_veiculos'))
    else:
        form = VeiculoForm(instance=veiculo, user=request.user)

    context = {'form': form, 'veiculo': veiculo}
    return render(request, 'core/editar_veiculo.html', context)


@login_required
def listar_veiculos(request):
    veiculos = Veiculo.objects.select_related('cliente').filter(ativo=True).order_by('placa')
    
    # Busca
    busca = request.GET.get('busca')
    if busca:
        veiculos = veiculos.filter(
            Q(placa__icontains=busca) |
            Q(marca__icontains=busca) |
            Q(modelo__icontains=busca) |
            Q(chassi__icontains=busca) |
            Q(cliente__nome__icontains=busca) |
            Q(cliente__cpf__icontains=busca)
        )
    
    # Filtros
    cliente_id = request.GET.get('cliente')
    if cliente_id:
        veiculos = veiculos.filter(cliente_id=cliente_id)
    
    # Paginação
    paginator = Paginator(veiculos, 20)
    page = request.GET.get('page')
    veiculos = paginator.get_page(page)
    
    context = {
        'veiculos': veiculos,
        'busca': busca,
        'clientes': Cliente.objects.filter(ativo=True).order_by('nome'),
        'cliente_selecionado': int(cliente_id) if cliente_id else None,
    }
    return render(request, 'core/listar_veiculos.html', context)


@login_required
def abrir_ordem_servico(request):
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST, user=request.user)
        formset = ItemOrdemServicoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            ordem_servico = form.save()
            formset.instance = ordem_servico
            formset.save()
            
            cliente_nome = (
                ordem_servico.veiculo.cliente.nome
                if ordem_servico.veiculo and ordem_servico.veiculo.cliente
                else 'sem cliente vinculado'
            )
            messages.success(
                request,
                f"Ordem de serviço #{ordem_servico.numero_os} criada para {ordem_servico.veiculo.placa} ({cliente_nome}).",
            )
            return redirect(reverse('core:listar_ordens_servico'))
    else:
        form = OrdemServicoForm(user=request.user)
        formset = ItemOrdemServicoFormSet()
    
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'core/abrir_ordem_servico.html', context)


@login_required
def listar_ordens_servico(request):
    ordens = OrdemServico.objects.select_related(
        'veiculo__cliente', 'responsavel_tecnico'
    ).prefetch_related('itens').order_by('-data_abertura')
    
    # Aplicar filtros
    form = FiltroOrdemServicoForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        
        if data['status']:
            ordens = ordens.filter(status=data['status'])
        if data['prioridade']:
            ordens = ordens.filter(prioridade=data['prioridade'])
        if data['cliente']:
            ordens = ordens.filter(veiculo__cliente=data['cliente'])
        if data['veiculo']:
            ordens = ordens.filter(veiculo=data['veiculo'])
        if data['data_inicio']:
            ordens = ordens.filter(data_abertura__date__gte=data['data_inicio'])
        if data['data_fim']:
            ordens = ordens.filter(data_abertura__date__lte=data['data_fim'])
        if data['busca']:
            ordens = ordens.filter(
                Q(numero_os__icontains=data['busca']) |
                Q(veiculo__placa__icontains=data['busca']) |
                Q(veiculo__cliente__nome__icontains=data['busca'])
            )
    
    # Paginação
    paginator = Paginator(ordens, 15)
    page = request.GET.get('page')
    ordens = paginator.get_page(page)
    
    context = {
        'ordens': ordens,
        'form': form,
    }
    return render(request, 'core/listar_ordens_servico.html', context)


@login_required
def editar_ordem_servico(request, ordem_id):
    ordem = get_object_or_404(OrdemServico, id=ordem_id)
    status_anterior = ordem.status
    
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST, instance=ordem, user=request.user)
        formset = ItemOrdemServicoFormSet(request.POST, instance=ordem)
        
        if form.is_valid() and formset.is_valid():
            ordem_servico = form.save()
            formset.save()
            
            # Registrar mudança de status se houve alteração
            status_novo = request.POST.get('status', ordem_servico.status)
            if status_novo != status_anterior:
                StatusHistorico.objects.create(
                    ordem_servico=ordem_servico,
                    status_anterior=status_anterior,
                    status_novo=status_novo,
                    usuario=request.user
                )
                ordem_servico.status = status_novo
                ordem_servico.save()
            
            messages.success(request, f"Ordem de serviço #{ordem_servico.numero_os} atualizada com sucesso.")
            return redirect(reverse('core:listar_ordens_servico'))
    else:
        form = OrdemServicoForm(instance=ordem, user=request.user)
        formset = ItemOrdemServicoFormSet(instance=ordem)
    
    # Histórico de status
    historico = ordem.historico_status.all()[:10]
    
    context = {
        'form': form,
        'formset': formset,
        'ordem': ordem,
        'historico': historico,
    }
    return render(request, 'core/editar_ordem_servico.html', context)


@login_required
def detalhes_ordem_servico(request, ordem_id):
    ordem = get_object_or_404(
        OrdemServico.objects.select_related('veiculo__cliente', 'responsavel_tecnico'),
        id=ordem_id
    )
    
    # Histórico completo
    historico = ordem.historico_status.select_related('usuario').all()
    
    context = {
        'ordem': ordem,
        'historico': historico,
    }
    return render(request, 'core/detalhes_ordem_servico.html', context)


@login_required
@require_http_methods(["POST"])
def atualizar_status_ordem(request, ordem_id):
    """Atualização rápida de status via AJAX"""
    ordem = get_object_or_404(OrdemServico, id=ordem_id)
    status_anterior = ordem.status
    novo_status = request.POST.get('status')
    
    if novo_status in dict(OrdemServico.Status.choices):
        # Registrar no histórico
        StatusHistorico.objects.create(
            ordem_servico=ordem,
            status_anterior=status_anterior,
            status_novo=novo_status,
            usuario=request.user,
            observacao=request.POST.get('observacao', '')
        )
        
        ordem.status = novo_status
        ordem.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status atualizado para {ordem.get_status_display()}'
        })
    
    return JsonResponse({'success': False, 'message': 'Status inválido'})


@login_required
def agendamentos(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, user=request.user)
        if form.is_valid():
            agendamento = form.save()
            messages.success(request, f"Agendamento criado para {agendamento.cliente.nome}.")
            return redirect(reverse('core:agendamentos'))
    else:
        form = AgendamentoForm(user=request.user)
    
    # Lista de agendamentos
    hoje = timezone.now().date()
    agendamentos_lista = Agendamento.objects.select_related(
        'cliente', 'veiculo'
    ).filter(
        data_agendamento__date__gte=hoje
    ).order_by('data_agendamento')[:20]
    
    context = {
        'form': form,
        'agendamentos': agendamentos_lista,
    }
    return render(request, 'core/agendamentos.html', context)


@login_required
def relatorios(request):
    form = RelatorioForm()
    dados_relatorio = None
    
    if request.method == 'POST':
        form = RelatorioForm(request.POST)
        if form.is_valid():
            dados_relatorio = gerar_relatorio(form.cleaned_data)
    
    context = {
        'form': form,
        'dados': dados_relatorio,
    }
    return render(request, 'core/relatorios.html', context)


def gerar_relatorio(dados_form):
    """Gera dados para relatórios"""
    tipo = dados_form['tipo_relatorio']
    periodo = dados_form['periodo']
    
    # Calcular datas
    hoje = timezone.now().date()
    
    if periodo == 'hoje':
        data_inicio = data_fim = hoje
    elif periodo == 'semana':
        data_inicio = hoje - timedelta(days=hoje.weekday())
        data_fim = data_inicio + timedelta(days=6)
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1)
        data_fim = (data_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif periodo == 'personalizado':
        data_inicio = dados_form['data_inicio']
        data_fim = dados_form['data_fim']
    
    if tipo == 'faturamento':
        ordens = OrdemServico.objects.filter(
            data_abertura__date__range=[data_inicio, data_fim],
            status=OrdemServico.Status.ENTREGUE
        )
        
        total_faturamento = ordens.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        total_ordens = ordens.count()
        ticket_medio = total_faturamento / total_ordens if total_ordens > 0 else Decimal('0.00')
        
        return {
            'tipo': 'Faturamento',
            'periodo_texto': f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
            'total_faturamento': total_faturamento,
            'total_ordens': total_ordens,
            'ticket_medio': ticket_medio,
            'ordens': ordens.select_related('veiculo__cliente')[:50],
        }
    
    return None


# API para AJAX
@login_required
def api_veiculos_cliente(request):
    """Retorna veículos de um cliente via AJAX"""
    cliente_id = request.GET.get('cliente_id')
    veiculos = Veiculo.objects.filter(
        cliente_id=cliente_id, ativo=True
    ).values('id', 'placa', 'marca', 'modelo')
    
    return JsonResponse(list(veiculos), safe=False)

@login_required
@permission_required('is_superuser', raise_exception=True)
def backup_database(request):
    """
    View para criar um backup do banco de dados.
    """
    if request.method == 'POST':
        try:
            backup_path = create_db_backup()
            messages.success(request, f'Backup do banco de dados criado com sucesso em: {backup_path}')
        except CommandError as e:
            messages.error(request, f'Erro ao criar o backup: {e}')
    
    return redirect('core:dashboard')
