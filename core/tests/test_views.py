"""
Testes para as views do GarageRoute66
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from core.models import Cliente, Veiculo, OrdemServico


class DashboardViewTest(TestCase):
    """Testes para a view dashboard"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_dashboard_acesso_publico(self):
        """Testa acesso público ao dashboard"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_conteudo(self):
        """Testa conteúdo básico do dashboard"""
        # Criar alguns dados de teste
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

        OrdemServico.objects.create(
            veiculo=veiculo,
            descricao_problema='Teste',
            criado_por=self.user
        )

        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'stats')
        self.assertContains(response, 'ordens_urgentes')


class ClienteViewsTest(TestCase):
    """Testes para views de Cliente"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.cliente = Cliente.objects.create(
            nome='João Silva',
            telefone='(11) 99999-9999',
            email='joao@email.com',
            endereco='Rua Teste, 123',
            cpf='123.456.789-10',
            criado_por=self.user
        )

    def test_listar_clientes(self):
        """Testa listagem de clientes"""
        response = self.client.get(reverse('core:listar_clientes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')

    def test_cadastrar_cliente_get(self):
        """Testa exibição do formulário de cadastro"""
        response = self.client.get(reverse('core:cadastrar_cliente'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_cadastrar_cliente_post(self):
        """Testa cadastro de cliente via POST"""
        data = {
            'nome': 'Maria Santos',
            'telefone': '(11) 88888-8888',
            'email': 'maria@email.com',
            'endereco': 'Rua Nova, 456',
            'cpf': '987.654.321-00',
        }

        response = self.client.post(reverse('core:cadastrar_cliente'), data)
        self.assertEqual(response.status_code, 302)  # Redirect após sucesso

        # Verificar se cliente foi criado
        self.assertTrue(Cliente.objects.filter(nome='Maria Santos').exists())

    def test_editar_cliente(self):
        """Testa edição de cliente"""
        response = self.client.get(
            reverse('core:editar_cliente', args=[self.cliente.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')

    def test_busca_clientes(self):
        """Testa busca de clientes"""
        response = self.client.get(
            reverse('core:listar_clientes'),
            {'busca': 'João'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')


class VeiculoViewsTest(TestCase):
    """Testes para views de Veículo"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

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

    def test_listar_veiculos(self):
        """Testa listagem de veículos"""
        response = self.client.get(reverse('core:listar_veiculos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ABC-1234')

    def test_cadastrar_veiculo_get(self):
        """Testa exibição do formulário de cadastro de veículo"""
        response = self.client.get(reverse('core:cadastrar_veiculo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_cadastrar_veiculo_post(self):
        """Testa cadastro de veículo via POST"""
        data = {
            'cliente': self.cliente.id,
            'placa': 'DEF-5678',
            'marca': 'Honda',
            'modelo': 'Civic',
            'ano': 2019,
            'cor': 'Azul',
            'chassi': '98765432109876543',
            'km_atual': 30000,
            'tipo_veiculo': 'CARRO',
        }

        response = self.client.post(reverse('core:cadastrar_veiculo'), data)
        self.assertEqual(response.status_code, 302)  # Redirect após sucesso

        # Verificar se veículo foi criado
        self.assertTrue(Veiculo.objects.filter(placa='DEF-5678').exists())


class OrdemServicoViewsTest(TestCase):
    """Testes para views de Ordem de Serviço"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

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
            descricao_problema='Motor fazendo barulho',
            criado_por=self.user
        )

    def test_listar_ordens_servico(self):
        """Testa listagem de ordens de serviço"""
        response = self.client.get(reverse('core:listar_ordens_servico'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Motor fazendo barulho')

    def test_abrir_ordem_servico_get(self):
        """Testa exibição do formulário de abertura de OS"""
        response = self.client.get(reverse('core:abrir_ordem_servico'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_detalhes_ordem_servico(self):
        """Testa visualização de detalhes da OS"""
        response = self.client.get(
            reverse('core:detalhes_ordem_servico', args=[self.ordem.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Motor fazendo barulho')

    def test_editar_ordem_servico(self):
        """Testa edição de ordem de serviço"""
        response = self.client.get(
            reverse('core:editar_ordem_servico', args=[self.ordem.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Motor fazendo barulho')

    def test_filtros_ordens_servico(self):
        """Testa filtros na listagem de OS"""
        response = self.client.get(
            reverse('core:listar_ordens_servico'),
            {'status': 'ABERTA'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Motor fazendo barulho')


class ApiViewsTest(TestCase):
    """Testes para views de API"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

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

    def test_api_veiculos_cliente(self):
        """Testa API de veículos por cliente"""
        response = self.client.get(
            reverse('core:api_veiculos_cliente'),
            {'cliente_id': self.cliente.id}
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['placa'], 'ABC-1234')


class LoginRequiredTest(TestCase):
    """Testa proteção de rotas que requerem login"""

    def setUp(self):
        self.client = Client()

    def test_views_requerem_login(self):
        """Testa que views protegidas redirecionam para login"""
        protected_urls = [
            'core:cadastrar_cliente',
            'core:listar_clientes',
            'core:cadastrar_veiculo',
            'core:listar_veiculos',
            'core:abrir_ordem_servico',
            'core:listar_ordens_servico',
            'core:agendamentos',
            'core:relatorios',
        ]

        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [302, 403])  # Redirect ou Forbidden