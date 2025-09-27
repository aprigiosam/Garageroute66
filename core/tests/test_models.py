"""
Testes para os models do GarageRoute66
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from core.models import Cliente, Veiculo, OrdemServico, ItemOrdemServico, Agendamento


class ClienteModelTest(TestCase):
    """Testes para o modelo Cliente"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_criar_cliente_valido(self):
        """Testa criação de cliente com dados válidos"""
        cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )

        self.assertEqual(cliente.nome, 'João Silva')
        self.assertTrue(cliente.ativo)
        self.assertEqual(str(cliente), 'João Silva')

    def test_cpf_unico(self):
        """Testa que CPF deve ser único"""
        Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )

        # Tentar criar outro cliente com mesmo CPF
        with self.assertRaises(Exception):
            Cliente.objects.create(
                nome='Maria Silva',
                telefone='(11) 88888-8888',
                email='maria@email.com',
                endereco='Rua Outro, 456',
                cpf='123.456.789-10',  # Mesmo CPF
                criado_por=self.user
            )

    def test_total_ordens_servico_property(self):
        """Testa propriedade total_ordens_servico"""
        cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )

        veiculo = Veiculo.objects.create(
            cliente=cliente,
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            cor='Prata',
            chassi='12345678901234567',
            km_atual=50000,
            criado_por=self.user
        )

        # Criar algumas ordens de serviço
        for i in range(3):
            OrdemServico.objects.create(
                veiculo=veiculo,
                descricao_problema=f'Problema {i}',
                criado_por=self.user
            )

        self.assertEqual(cliente.total_ordens_servico, 3)


class VeiculoModelTest(TestCase):
    """Testes para o modelo Veiculo"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )

    def test_criar_veiculo_valido(self):
        """Testa criação de veículo com dados válidos"""
        veiculo = Veiculo.objects.create(
            cliente=self.cliente,
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            cor='Prata',
            chassi='12345678901234567',
            km_atual=50000,
            criado_por=self.user
        )

        self.assertEqual(veiculo.placa, 'ABC-1234')
        self.assertEqual(veiculo.cliente, self.cliente)
        self.assertTrue(veiculo.ativo)
        self.assertEqual(str(veiculo), 'ABC-1234 - Toyota Corolla')

    def test_placa_unica(self):
        """Testa que placa deve ser única"""
        Veiculo.objects.create(
            cliente=self.cliente,
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            cor='Prata',
            chassi='12345678901234567',
            km_atual=50000,
            criado_por=self.user
        )

        # Tentar criar outro veículo com mesma placa
        with self.assertRaises(Exception):
            Veiculo.objects.create(
                cliente=self.cliente,
                placa='ABC-1234',  # Mesma placa
                marca='Honda',
                modelo='Civic',
                ano=2019,
                cor='Azul',
                chassi='98765432109876543',
                km_atual=30000,
                criado_por=self.user
            )


class OrdemServicoModelTest(TestCase):
    """Testes para o modelo OrdemServico"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )
        self.veiculo = Veiculo.objects.create(
            cliente=self.cliente,
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            cor='Prata',
            chassi='12345678901234567',
            km_atual=50000,
            criado_por=self.user
        )

    def test_criar_ordem_servico(self):
        """Testa criação de ordem de serviço"""
        ordem = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Motor fazendo barulho',
            valor_mao_obra=Decimal('100.00'),
            valor_pecas=Decimal('50.00'),
            criado_por=self.user
        )

        self.assertEqual(ordem.veiculo, self.veiculo)
        self.assertEqual(ordem.status, OrdemServico.Status.ABERTA)
        self.assertIsNotNone(ordem.numero_os)

    def test_calcular_total(self):
        """Testa cálculo do total da ordem"""
        ordem = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Motor fazendo barulho',
            valor_mao_obra=Decimal('100.00'),
            valor_pecas=Decimal('50.00'),
            valor_terceiros=Decimal('25.00'),
            desconto=Decimal('10.00'),
            criado_por=self.user
        )

        total_esperado = Decimal('165.00')  # 100 + 50 + 25 - 10
        self.assertEqual(ordem.total, total_esperado)

    def test_numero_os_automatico(self):
        """Testa geração automática do número da OS"""
        ordem = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Teste',
            criado_por=self.user
        )

        self.assertIsNotNone(ordem.numero_os)
        self.assertIn(str(timezone.now().year), ordem.numero_os)

    def test_prazo_vencido_property(self):
        """Testa propriedade prazo_vencido"""
        # Ordem com prazo vencido
        ordem_vencida = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Teste',
            prazo_entrega=timezone.now() - timedelta(days=1),
            criado_por=self.user
        )

        # Ordem com prazo no futuro
        ordem_no_prazo = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Teste 2',
            prazo_entrega=timezone.now() + timedelta(days=1),
            criado_por=self.user
        )

        self.assertTrue(ordem_vencida.prazo_vencido)
        self.assertFalse(ordem_no_prazo.prazo_vencido)


class ItemOrdemServicoModelTest(TestCase):
    """Testes para o modelo ItemOrdemServico"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )
        self.veiculo = Veiculo.objects.create(
            cliente=self.cliente,
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            cor='Prata',
            chassi='12345678901234567',
            km_atual=50000,
            criado_por=self.user
        )
        self.ordem = OrdemServico.objects.create(
            veiculo=self.veiculo,
            descricao_problema='Teste',
            criado_por=self.user
        )

    def test_calculo_valor_total_item(self):
        """Testa cálculo do valor total do item"""
        item = ItemOrdemServico.objects.create(
            ordem_servico=self.ordem,
            descricao='Troca de óleo',
            quantidade=Decimal('2.000'),
            valor_unitario=Decimal('25.00'),
            tipo='SERVICO'
        )

        self.assertEqual(item.valor_total, Decimal('50.00'))


class AgendamentoModelTest(TestCase):
    """Testes para o modelo Agendamento"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )

    def test_criar_agendamento(self):
        """Testa criação de agendamento"""
        data_agendamento = timezone.now() + timedelta(days=1)

        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            data_agendamento=data_agendamento,
            servico_solicitado='Revisão geral',
            criado_por=self.user
        )

        self.assertEqual(agendamento.cliente, self.cliente)
        self.assertFalse(agendamento.confirmado)
        self.assertFalse(agendamento.compareceu)
        self.assertIsNone(agendamento.ordem_servico)