from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    Cliente, OrdemServico, Veiculo, ItemOrdemServico,
    FotoOrdemServico, StatusHistorico, Agendamento, CategoriaPeca, Fornecedor,
    Peca, MovimentacaoEstoque
)


class ItemOrdemServicoInline(admin.TabularInline):
    model = ItemOrdemServico
    extra = 1
    fields = ('descricao', 'tipo', 'quantidade', 'valor_unitario', 'valor_total')
    readonly_fields = ('valor_total',)


class StatusHistoricoInline(admin.TabularInline):
    model = StatusHistorico
    extra = 0
    fields = ('status_anterior', 'status_novo', 'data_mudanca', 'usuario', 'observacao')
    readonly_fields = ('data_mudanca', 'usuario')
    
    def has_add_permission(self, request, obj=None):
        return False


class FotoOrdemServicoInline(admin.TabularInline):
    model = FotoOrdemServico
    extra = 1
    fields = ('imagem_preview', 'imagem', 'legenda')
    readonly_fields = ('imagem_preview',)

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height: 120px; border-radius: 6px;" />', obj.imagem.url)
        return "-"
    imagem_preview.short_description = 'Pré-visualização'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'cpf', 'total_veiculos', 'valor_gasto_total', 'ativo', 'criado_em')
    list_filter = ('ativo', 'criado_em', 'atualizado_em')
    search_fields = ('nome', 'telefone', 'email', 'cpf')
    ordering = ('nome',)
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco',)
        }),
        ('Status', {
            'fields': ('ativo', 'observacoes')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def total_veiculos(self, obj):
        count = obj.veiculos.count()
        if count > 0:
            url = reverse('admin:core_veiculo_changelist') + f'?cliente__id__exact={obj.id}'
            return format_html('<a href="{}">{} veículos</a>', url, count)
        return '0 veículos'
    total_veiculos.short_description = 'Veículos'
    
    def valor_gasto_total(self, obj):
        valor = obj.valor_total_gasto
        if valor > 0:
            return f'R$ {valor:,.2f}'
        return 'R$ 0,00'
    valor_gasto_total.short_description = 'Total gasto'
    valor_gasto_total.admin_order_field = 'valor_total_gasto'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = (
        'placa', 'marca', 'modelo', 'ano', 'cor', 'cliente_link', 
        'tipo_veiculo', 'batido', 'total_ordens', 'valor_manutencoes', 'ativo'
    )
    list_filter = ('marca', 'tipo_veiculo', 'ano', 'batido', 'ativo', 'cliente')
    search_fields = ('placa', 'marca', 'modelo', 'chassi', 'cliente__nome', 'cliente__cpf')
    autocomplete_fields = ['cliente']
    ordering = ('placa',)
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')
    
    fieldsets = (
        ('Informações do Veículo', {
            'fields': ('cliente', 'placa', 'marca', 'modelo', 'ano', 'cor', 'tipo_veiculo')
        }),
        ('Detalhes Técnicos', {
            'fields': ('chassi', 'km_atual', 'batido')
        }),
        ('Status', {
            'fields': ('ativo', 'observacoes')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def cliente_link(self, obj):
        if obj.cliente:
            url = reverse('admin:core_cliente_change', args=[obj.cliente.pk])
            return format_html('<a href="{}">{}</a>', url, obj.cliente.nome)
        return '-'
    cliente_link.short_description = 'Cliente'
    cliente_link.admin_order_field = 'cliente__nome'
    
    def total_ordens(self, obj):
        count = obj.ordens_servico.count()
        if count > 0:
            url = reverse('admin:core_ordemservico_changelist') + f'?veiculo__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return '0'
    total_ordens.short_description = 'OS'
    
    def valor_manutencoes(self, obj):
        valor = obj.valor_total_manutencoes
        if valor > 0:
            return f'R$ {valor:,.2f}'
        return 'R$ 0,00'
    valor_manutencoes.short_description = 'Total manutenções'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_os_link', 'veiculo_info', 'cliente_info', 'status_badge', 
        'prioridade_badge', 'data_abertura', 'data_conclusao', 'total_formatado',
        'responsavel_tecnico', 'prazo_status'
    )
    list_filter = (
        'status', 'prioridade', 'data_abertura', 'data_conclusao', 
        'veiculo__marca', 'responsavel_tecnico'
    )
    search_fields = (
        'numero_os', 'veiculo__placa', 'veiculo__cliente__nome', 
        'descricao_problema', 'diagnostico'
    )
    autocomplete_fields = ['veiculo', 'responsavel_tecnico']
    readonly_fields = (
        'numero_os', 'total', 'criado_em', 'atualizado_em', 
        'criado_por', 'atualizado_por'
    )
    date_hierarchy = 'data_abertura'
    list_select_related = ('veiculo', 'veiculo__cliente', 'responsavel_tecnico')
    inlines = [ItemOrdemServicoInline, FotoOrdemServicoInline, StatusHistoricoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_os', 'veiculo', 'responsavel_tecnico', 'status', 'prioridade')
        }),
        ('Descrição do Problema', {
            'fields': ('descricao_problema', 'diagnostico', 'solucao', 'km_entrada')
        }),
        ('Datas', {
            'fields': (
                'data_abertura', 'data_orcamento', 'data_aprovacao', 
                'data_inicio', 'data_conclusao', 'data_entrega', 'prazo_entrega'
            ),
            'classes': ('collapse',)
        }),
        ('Valores', {
            'fields': (
                'valor_mao_obra', 'valor_pecas', 'valor_terceiros', 
                'desconto', 'total'
            )
        }),
        ('Observações', {
            'fields': ('observacoes', 'observacoes_internas'),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly.append('data_abertura')
        return readonly
    
    def numero_os_link(self, obj):
        return format_html('<strong>{}</strong>', obj.numero_os or f'#{obj.pk}')
    numero_os_link.short_description = 'OS #'
    numero_os_link.admin_order_field = 'numero_os'
    
    def veiculo_info(self, obj):
        if obj.veiculo:
            return format_html(
                '<strong>{}</strong><br><small>{} {}</small>',
                obj.veiculo.placa,
                obj.veiculo.marca,
                obj.veiculo.modelo
            )
        return '-'
    veiculo_info.short_description = 'Veículo'
    veiculo_info.admin_order_field = 'veiculo__placa'
    
    def cliente_info(self, obj):
        if obj.veiculo and obj.veiculo.cliente:
            cliente = obj.veiculo.cliente
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                cliente.nome,
                cliente.telefone
            )
        return '-'
    cliente_info.short_description = 'Cliente'
    cliente_info.admin_order_field = 'veiculo__cliente__nome'
    
    def status_badge(self, obj):
        color_map = {
            'ABERTA': 'primary',
            'ORCAMENTO': 'info',
            'APROVADA': 'success',
            'EM_ANDAMENTO': 'warning',
            'AGUARDANDO_PECA': 'secondary',
            'CONCLUIDA': 'success',
            'ENTREGUE': 'info',
            'CANCELADA': 'danger',
        }
        color = color_map.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def prioridade_badge(self, obj):
        color_map = {
            'URGENTE': 'danger',
            'ALTA': 'warning',
            'NORMAL': 'primary',
            'BAIXA': 'secondary',
        }
        color = color_map.get(obj.prioridade, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_prioridade_display()
        )
    prioridade_badge.short_description = 'Prioridade'
    prioridade_badge.admin_order_field = 'prioridade'
    
    def total_formatado(self, obj):
        return f'R$ {obj.total:,.2f}'
    total_formatado.short_description = 'Total'
    total_formatado.admin_order_field = 'total'
    
    def prazo_status(self, obj):
        if obj.prazo_entrega:
            if obj.status in [OrdemServico.Status.ENTREGUE]:
                return format_html('<span class="text-success">✓ Entregue</span>')
            elif obj.prazo_vencido:
                return format_html('<span class="text-danger">⚠ Vencido</span>')
            else:
                return format_html('<span class="text-warning">⏰ No prazo</span>')
        return '-'
    prazo_status.short_description = 'Prazo'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(ItemOrdemServico)
class ItemOrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('ordem_servico', 'descricao', 'tipo', 'quantidade', 'valor_unitario', 'valor_total')
    list_filter = ('tipo', 'ordem_servico__status')
    search_fields = ('descricao', 'ordem_servico__numero_os')
    autocomplete_fields = ['ordem_servico']


@admin.register(StatusHistorico)
class StatusHistoricoAdmin(admin.ModelAdmin):
    list_display = ('ordem_servico', 'status_anterior', 'status_novo', 'data_mudanca', 'usuario')
    list_filter = ('status_anterior', 'status_novo', 'data_mudanca', 'usuario')
    search_fields = ('ordem_servico__numero_os', 'observacao')
    readonly_fields = ('data_mudanca',)
    
    def has_add_permission(self, request):
        return False


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = (
        'data_agendamento', 'cliente', 'veiculo', 'servico_resumo', 
        'confirmado', 'compareceu', 'tem_ordem_servico'
    )
    list_filter = ('confirmado', 'compareceu', 'data_agendamento', 'cliente')
    search_fields = ('cliente__nome', 'veiculo__placa', 'servico_solicitado')
    autocomplete_fields = ['cliente', 'veiculo', 'ordem_servico']
    date_hierarchy = 'data_agendamento'
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')
    
    def servico_resumo(self, obj):
        return obj.servico_solicitado[:50] + '...' if len(obj.servico_solicitado) > 50 else obj.servico_solicitado
    servico_resumo.short_description = 'Serviço solicitado'
    
    def tem_ordem_servico(self, obj):
        if obj.ordem_servico:
            url = reverse('admin:core_ordemservico_change', args=[obj.ordem_servico.pk])
            return format_html('<a href="{}">OS #{}</a>', url, obj.ordem_servico.numero_os)
        return '-'
    tem_ordem_servico.short_description = 'Ordem de Serviço'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(CategoriaPeca)
class CategoriaPecaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'total_pecas_count', 'ativo', 'criado_em')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')

    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )

    def total_pecas_count(self, obj):
        count = obj.total_pecas
        if count > 0:
            url = reverse('admin:core_peca_changelist') + f'?categoria__id__exact={obj.id}'
            return format_html('<a href="{}">{} peças</a>', url, count)
        return '0 peças'
    total_pecas_count.short_description = 'Total de Peças'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'telefone', 'email', 'cidade', 'estado', 'total_pecas_count', 'ativo')
    list_filter = ('ativo', 'estado', 'cidade', 'criado_em')
    search_fields = ('nome', 'razao_social', 'cnpj', 'email', 'telefone', 'contato')
    ordering = ('nome',)
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')

    fieldsets = (
        ('Informações da Empresa', {
            'fields': ('nome', 'razao_social', 'cnpj')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'contato')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Status', {
            'fields': ('ativo', 'observacoes')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )

    def total_pecas_count(self, obj):
        count = obj.total_pecas_fornecidas
        if count > 0:
            url = reverse('admin:core_peca_changelist') + f'?fornecedor__id__exact={obj.id}'
            return format_html('<a href="{}">{} peças</a>', url, count)
        return '0 peças'
    total_pecas_count.short_description = 'Peças Fornecidas'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)


class MovimentacaoEstoqueInline(admin.TabularInline):
    model = MovimentacaoEstoque
    extra = 0
    fields = ('tipo', 'quantidade', 'valor_unitario', 'data_movimentacao', 'usuario', 'motivo')
    readonly_fields = ('data_movimentacao', 'usuario')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'nome', 'categoria', 'fornecedor',
        'quantidade_estoque_display', 'estoque_status',
        'preco_custo_display', 'preco_venda_display',
        'margem_lucro_display', 'valor_estoque_display', 'ativo'
    )
    list_filter = ('categoria', 'fornecedor', 'ativo', 'unidade_medida', 'criado_em')
    search_fields = ('codigo', 'nome', 'descricao', 'codigo_fabricante', 'codigo_barras')
    autocomplete_fields = ['categoria', 'fornecedor']
    ordering = ('nome',)
    readonly_fields = ('margem_lucro', 'criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')
    inlines = [MovimentacaoEstoqueInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'nome', 'descricao', 'categoria', 'fornecedor')
        }),
        ('Estoque', {
            'fields': (
                'quantidade_estoque', 'estoque_minimo', 'estoque_maximo',
                'unidade_medida', 'localizacao'
            )
        }),
        ('Preços', {
            'fields': ('preco_custo', 'preco_venda', 'margem_lucro')
        }),
        ('Informações Adicionais', {
            'fields': ('codigo_fabricante', 'codigo_barras', 'peso', 'observacoes'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )

    def quantidade_estoque_display(self, obj):
        return f'{obj.quantidade_estoque} {obj.get_unidade_medida_display()}'
    quantidade_estoque_display.short_description = 'Estoque'
    quantidade_estoque_display.admin_order_field = 'quantidade_estoque'

    def estoque_status(self, obj):
        if obj.estoque_critico:
            return format_html('<span class="badge badge-danger">⚠ Crítico</span>')
        elif obj.estoque_baixo:
            return format_html('<span class="badge badge-warning">⚠ Baixo</span>')
        else:
            return format_html('<span class="badge badge-success">✓ OK</span>')
    estoque_status.short_description = 'Status'

    def preco_custo_display(self, obj):
        return f'R$ {obj.preco_custo:,.2f}'
    preco_custo_display.short_description = 'Custo'
    preco_custo_display.admin_order_field = 'preco_custo'

    def preco_venda_display(self, obj):
        return f'R$ {obj.preco_venda:,.2f}'
    preco_venda_display.short_description = 'Venda'
    preco_venda_display.admin_order_field = 'preco_venda'

    def margem_lucro_display(self, obj):
        return f'{obj.margem_lucro:.1f}%'
    margem_lucro_display.short_description = 'Margem'
    margem_lucro_display.admin_order_field = 'margem_lucro'

    def valor_estoque_display(self, obj):
        return f'R$ {obj.valor_total_estoque:,.2f}'
    valor_estoque_display.short_description = 'Valor Estoque'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'data_movimentacao', 'peca', 'tipo_badge', 'quantidade_display',
        'quantidade_anterior', 'quantidade_nova', 'valor_total_display',
        'ordem_servico_link', 'usuario'
    )
    list_filter = ('tipo', 'data_movimentacao', 'usuario', 'peca__categoria')
    search_fields = ('peca__codigo', 'peca__nome', 'motivo', 'numero_documento', 'ordem_servico__numero_os')
    autocomplete_fields = ['peca', 'ordem_servico', 'usuario']
    readonly_fields = ('valor_total', 'data_movimentacao')
    date_hierarchy = 'data_movimentacao'

    fieldsets = (
        ('Movimentação', {
            'fields': ('peca', 'tipo', 'quantidade', 'valor_unitario', 'valor_total')
        }),
        ('Quantidades', {
            'fields': ('quantidade_anterior', 'quantidade_nova')
        }),
        ('Relacionamentos', {
            'fields': ('ordem_servico', 'usuario')
        }),
        ('Informações Adicionais', {
            'fields': ('motivo', 'numero_documento', 'data_movimentacao')
        }),
    )

    def tipo_badge(self, obj):
        color_map = {
            'ENTRADA': 'success',
            'SAIDA': 'danger',
            'AJUSTE': 'warning',
            'DEVOLUCAO': 'info',
            'PERDA': 'dark',
            'TRANSFERENCIA': 'primary',
        }
        color = color_map.get(obj.tipo, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    tipo_badge.admin_order_field = 'tipo'

    def quantidade_display(self, obj):
        return f'{obj.quantidade} {obj.peca.get_unidade_medida_display()}'
    quantidade_display.short_description = 'Quantidade'

    def valor_total_display(self, obj):
        return f'R$ {obj.valor_total:,.2f}'
    valor_total_display.short_description = 'Valor Total'
    valor_total_display.admin_order_field = 'valor_total'

    def ordem_servico_link(self, obj):
        if obj.ordem_servico:
            url = reverse('admin:core_ordemservico_change', args=[obj.ordem_servico.pk])
            return format_html('<a href="{}">OS #{}</a>', url, obj.ordem_servico.numero_os)
        return '-'
    ordem_servico_link.short_description = 'OS'

    def has_add_permission(self, request):
        # Permitir adicionar movimentações manualmente
        return True

    def has_change_permission(self, request, obj=None):
        # Não permitir edição de movimentações existentes
        return False

    def has_delete_permission(self, request, obj=None):
        # Não permitir exclusão de movimentações
        return False


# Personalização do Admin Site
admin.site.site_header = "GarageRoute66 - Administração"
admin.site.site_title = "GarageRoute66 Admin"
admin.site.index_title = "Painel de Controle"
