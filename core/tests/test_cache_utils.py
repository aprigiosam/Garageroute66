from decimal import Decimal
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache

from core.cache_utils import DashboardCache
from core.models import Cliente, Veiculo, OrdemServico


class DashboardCacheTest(TestCase):
    """Testes para utilitários de cache do dashboard."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='cache_user',
            email='cache@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nome='Cliente Cache',
            telefone='(11) 99999-9999',
            email='cache@example.com',
            endereco='Rua Cache, 123',
            cpf='123.456.789-00',
            criado_por=self.user
        )
        self.veiculo = Veiculo.objects.create(
            cliente=self.cliente,
            placa='AAA-0001',
            marca='Ford',
            modelo='Fiesta',
            ano=2022,
            cor='Preto',
            chassi='1HGCM82633A004352',
            km_atual=15000,
            criado_por=self.user
        )

    def _criar_os(self, data_abertura, total):
        """Cria ordem de serviço concluída com data e total específicos."""
        ordem = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Teste cache',
            valor_mao_obra=Decimal(total),
            criado_por=self.user
        )
        ordem.data_abertura = data_abertura
        ordem.status = OrdemServico.Status.ENTREGUE
        ordem.total = Decimal(total)
        ordem.save(update_fields=['data_abertura', 'status', 'total'])
        return ordem

    @patch('core.cache_utils.timezone.localtime')
    def test_get_stats_considera_inicio_mes(self, localtime_mock):
        """Garante que get_stats utiliza início do mês com timezone."""
        referencia = timezone.make_aware(datetime(2025, 10, 28, 12, 0))
        localtime_mock.return_value = referencia

        inicio_mes = referencia.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self._criar_os(inicio_mes, '150.00')

        stats = DashboardCache.get_stats()
        self.assertEqual(stats['ordens_mes'], 1)
        self.assertEqual(float(stats['faturamento_mes']), 150.0)

    @patch('core.cache_utils.timezone.localtime')
    def test_get_faturamento_mensal_ordem_cronologica(self, localtime_mock):
        """Verifica que a resposta traz meses em ordem cronológica crescente."""
        referencia = timezone.make_aware(datetime(2025, 10, 28, 12, 0))
        localtime_mock.return_value = referencia

        # Criar ordens em meses diferentes (Junho a Outubro)
        for idx, valor in enumerate([100, 200, 300, 400, 500], start=1):
            data = timezone.make_aware(datetime(2025, idx + 5, 5, 10, 0))
            self._criar_os(data, str(valor))

        faturamento = DashboardCache.get_faturamento_mensal(meses=6)
        meses = [item['mes'] for item in faturamento]

        # Deve retornar 6 entradas e estar em ordem crescente de tempo
        self.assertEqual(len(faturamento), 6)
        self.assertEqual(meses, sorted(meses, key=lambda m: datetime.strptime(m, '%b/%Y')))
        self.assertAlmostEqual(faturamento[-1]['valor'], 500.0)
