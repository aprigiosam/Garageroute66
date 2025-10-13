from django.urls import path

from . import views
from . import views_pecas

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/novo/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),

    path('veiculos/', views.listar_veiculos, name='listar_veiculos'),
    path('veiculos/novo/', views.cadastrar_veiculo, name='cadastrar_veiculo'),

    path('ordens/', views.listar_ordens_servico, name='listar_ordens_servico'),
    path('ordens/nova/', views.abrir_ordem_servico, name='abrir_ordem_servico'),
    path('ordens/<int:ordem_id>/', views.detalhes_ordem_servico, name='detalhes_ordem_servico'),
    path('ordens/<int:ordem_id>/editar/', views.editar_ordem_servico, name='editar_ordem_servico'),
    path('ordens/<int:ordem_id>/status/', views.atualizar_status_ordem, name='atualizar_status_ordem'),

    path('agendamentos/', views.agendamentos, name='agendamentos'),

    path('relatorios/', views.relatorios, name='relatorios'),
    path('backup-database/', views.backup_database, name='backup_database'),

    # URLs de Peças
    path('pecas/', views_pecas.listar_pecas, name='listar_pecas'),
    path('pecas/nova/', views_pecas.cadastrar_peca, name='cadastrar_peca'),
    path('pecas/<int:peca_id>/', views_pecas.detalhes_peca, name='detalhes_peca'),
    path('pecas/<int:peca_id>/editar/', views_pecas.editar_peca, name='editar_peca'),

    # URLs de Estoque
    path('estoque/movimentacoes/', views_pecas.movimentacoes_estoque, name='movimentacoes_estoque'),
    path('estoque/entrada/', views_pecas.entrada_estoque, name='entrada_estoque'),
    path('estoque/saida/', views_pecas.saida_estoque, name='saida_estoque'),
    path('estoque/ajuste/', views_pecas.ajuste_estoque, name='ajuste_estoque'),

    # URLs de Categorias
    path('categorias/', views_pecas.listar_categorias, name='listar_categorias'),
    path('categorias/nova/', views_pecas.cadastrar_categoria, name='cadastrar_categoria'),

    # URLs de Fornecedores
    path('fornecedores/', views_pecas.listar_fornecedores, name='listar_fornecedores'),
    path('fornecedores/novo/', views_pecas.cadastrar_fornecedor, name='cadastrar_fornecedor'),

    # API AJAX
    path('api/veiculos-cliente/', views.api_veiculos_cliente, name='api_veiculos_cliente'),
    path('api/buscar-peca/', views_pecas.api_buscar_peca, name='api_buscar_peca'),
]
