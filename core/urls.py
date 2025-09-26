from django.urls import path

from . import views

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

    path('api/veiculos-cliente/', views.api_veiculos_cliente, name='api_veiculos_cliente'),
]
