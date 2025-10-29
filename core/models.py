from decimal import Decimal
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count, Sum, Prefetch
from django.conf import settings


class TimestampedModel(models.Model):
    """Modelo base com campos de auditoria"""
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    criado_por = models.ForeignKey(User, verbose_name='Criado por', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    atualizado_por = models.ForeignKey(User, verbose_name='Atualizado por', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save para invalidar cache relacionado"""
        super().save(*args, **kwargs)
        self._clear_related_cache()

    def _clear_related_cache(self):
        """Limpa cache relacionado ao modelo"""
        model_name = self.__class__.__name__.lower()
        cache_keys = [
            f'{model_name}_list',
            f'{model_name}_count',
            f'dashboard_stats',
        ]
        cache.delete_many(cache_keys)


class OptimizedManager(models.Manager):
    """Manager otimizado com cache e prefetch"""

    def get_with_cache(self, cache_key, cache_timeout=300, **kwargs):
        """Busca objeto com cache"""
        cached_obj = cache.get(cache_key)
        if cached_obj is None:
            try:
                cached_obj = self.get(**kwargs)
                cache.set(cache_key, cached_obj, cache_timeout)
            except self.model.DoesNotExist:
                return None
        return cached_obj

    def list_with_cache(self, cache_key, cache_timeout=300, **filters):
        """Lista objetos com cache"""
        cached_list = cache.get(cache_key)
        if cached_list is None:
            cached_list = list(self.filter(**filters))
            cache.set(cache_key, cached_list, cache_timeout)
        return cached_list


class Cliente(TimestampedModel):
    nome = models.CharField('Nome', max_length=150)
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        validators=[RegexValidator(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', 'Formato: (11) 99999-9999')]
    )
    email = models.EmailField('E-mail')
    endereco = models.CharField('Endereço', max_length=255)
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'Formato: 000.000.000-00')]
    )
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)

    objects = OptimizedManager()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cpf']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self) -> str:
        return self.nome

    @property
    def total_ordens_servico(self):
        from django.db.models import Count
        return self.veiculos.aggregate(
            total=Count('ordens_servico')
        )['total'] or 0

    @property
    def valor_total_gasto(self):
        from django.db.models import Sum
        return self.veiculos.filter(
            ordens_servico__status=OrdemServico.Status.ENTREGUE
        ).aggregate(
            total=Sum('ordens_servico__total')
        )['total'] or Decimal('0.00')


class Veiculo(TimestampedModel):
    class TipoVeiculo(models.TextChoices):
        CARRO = 'CARRO', 'Carro'
        MOTO = 'MOTO', 'Moto'
        CAMINHAO = 'CAMINHAO', 'Caminhão'
        VAN = 'VAN', 'Van'
        OUTROS = 'OUTROS', 'Outros'

    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', related_name='veiculos', on_delete=models.CASCADE)
    placa = models.CharField(
        'Placa', 
        max_length=10, 
        unique=True,
        validators=[RegexValidator(r'^[A-Z]{3}-?\d{4}$|^[A-Z]{3}\d[A-Z]\d{2}$', 'Formato inválido de placa')]
    )
    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    ano = models.PositiveIntegerField(
        'Ano',
        validators=[MinValueValidator(1900)]
    )
    cor = models.CharField('Cor', max_length=30)
    chassi = models.CharField('Chassi', max_length=50, unique=True)
    tipo_veiculo = models.CharField('Tipo de Veículo', max_length=20, choices=TipoVeiculo.choices, default=TipoVeiculo.CARRO)
    batido = models.BooleanField('Veículo batido?', default=False)
    km_atual = models.PositiveIntegerField('Quilometragem Atual')
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['placa']
        indexes = [
            models.Index(fields=['placa']),
            models.Index(fields=['chassi']),
            models.Index(fields=['cliente', 'ativo']),
        ]

    def __str__(self) -> str:
        return f"{self.placa} - {self.marca} {self.modelo}"

    @property
    def ultima_manutencao(self):
        return self.ordens_servico.filter(status=OrdemServico.Status.ENTREGUE).first()

    @property
    def valor_total_manutencoes(self):
        return self.ordens_servico.filter(
            status=OrdemServico.Status.ENTREGUE
        ).aggregate(
            total=models.Sum('total')
        )['total'] or Decimal('0.00')


class OrdemServico(TimestampedModel):
    class Status(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        DIAGNOSTICO = 'DIAGNOSTICO', 'Em diagnóstico'
        ORCAMENTO = 'ORCAMENTO', 'Orçamento interno'
        ORCAMENTO_ENVIADO = 'ORCAMENTO_ENVIADO', 'Orçamento enviado'
        APROVADA = 'APROVADA', 'Aprovada'
        EM_EXECUCAO = 'EM_ANDAMENTO', 'Em execução'
        AGUARDANDO_PECA = 'AGUARDANDO_PECA', 'Aguardando peça'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class Prioridade(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa'
        NORMAL = 'NORMAL', 'Normal'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'

    class EstimateType(models.TextChoices):
        FIXED = 'FIXED', 'Serviço padrão (preço conhecido)'
        PERSONALIZADO = 'PERSONALIZADO', 'Sob diagnóstico'

    veiculo = models.ForeignKey(Veiculo, verbose_name='Veículo', related_name='ordens_servico', on_delete=models.CASCADE)
    numero_os = models.CharField('Número OS', max_length=20, unique=True, blank=True)
    descricao_problema = models.TextField('Descrição do problema')
    diagnostico = models.TextField('Diagnóstico', blank=True)
    solucao = models.TextField('Solução aplicada', blank=True)
    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.ABERTA)
    prioridade = models.CharField('Prioridade', max_length=20, choices=Prioridade.choices, default=Prioridade.NORMAL)
    requires_diagnosis = models.BooleanField('Requer diagnóstico', default=False)
    estimate_type = models.CharField('Tipo de orçamento', max_length=20, choices=EstimateType.choices, blank=True)
    orcamento_total_estimado = models.DecimalField('Total estimado', max_digits=10, decimal_places=2, null=True, blank=True)
    orcamento_total_aprovado = models.DecimalField('Total aprovado', max_digits=10, decimal_places=2, null=True, blank=True)
    orcamento_aprovado_em = models.DateTimeField('Data de aprovação', null=True, blank=True)
    orcamento_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    orcamento_requer_reaprovacao = models.BooleanField('Requer reaprovação?', default=False)
    
    # Datas
    data_abertura = models.DateTimeField('Data de abertura', default=timezone.now)
    data_orcamento = models.DateTimeField('Data do orçamento', blank=True, null=True)
    data_aprovacao = models.DateTimeField('Data de aprovação', blank=True, null=True)
    data_inicio = models.DateTimeField('Data de início', blank=True, null=True)
    data_conclusao = models.DateTimeField('Data de conclusão', blank=True, null=True)
    data_entrega = models.DateTimeField('Data de entrega', blank=True, null=True)
    prazo_entrega = models.DateTimeField('Prazo de entrega', blank=True, null=True)
    
    # Valores
    valor_mao_obra = models.DecimalField('Valor mão de obra', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_pecas = models.DecimalField('Valor peças', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_terceiros = models.DecimalField('Valor terceiros', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, editable=False, default=Decimal('0.00'))
    
    # Outros
    km_entrada = models.PositiveIntegerField('KM na entrada', blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True)
    observacoes_internas = models.TextField('Observações internas', blank=True)
    
    # Responsável técnico
    responsavel_tecnico = models.ForeignKey(
        User, 
        verbose_name='Responsável técnico', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordens_responsavel'
    )

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_abertura']
        indexes = [
            models.Index(fields=['numero_os']),
            models.Index(fields=['status']),
            models.Index(fields=['data_abertura']),
            models.Index(fields=['veiculo', 'status']),
            models.Index(fields=['orcamento_token']),
        ]

    def __str__(self) -> str:
        return f"OS #{self.numero_os or self.pk} - {self.veiculo.placa}"

    def save(self, *args, **kwargs) -> None:
        # Gerar número da OS se não existir
        if not self.numero_os:
            year = timezone.now().year
            last_os = OrdemServico.objects.filter(
                data_abertura__year=year
            ).order_by('-id').first()
            
            if last_os and last_os.numero_os:
                try:
                    last_num = int(last_os.numero_os.split('-')[1])
                    new_num = last_num + 1
                except (IndexError, ValueError):
                    new_num = 1
            else:
                new_num = 1
            
            self.numero_os = f"{year}-{new_num:06d}"
        
        # Calcular total
        self.total = self.calcular_total()
        
        # Atualizar datas baseadas no status
        now = timezone.now()
        if self.status in [self.Status.ORCAMENTO, self.Status.ORCAMENTO_ENVIADO] and not self.data_orcamento:
            self.data_orcamento = now
        elif self.status == self.Status.APROVADA and not self.data_aprovacao:
            self.data_aprovacao = now
        elif self.status == self.Status.EM_EXECUCAO and not self.data_inicio:
            self.data_inicio = now
        elif self.status == self.Status.CONCLUIDA and not self.data_conclusao:
            self.data_conclusao = now
        elif self.status == self.Status.ENTREGUE and not self.data_entrega:
            self.data_entrega = now
        
        super().save(*args, **kwargs)

    def calcular_total(self) -> Decimal:
        return (
            (self.valor_mao_obra or Decimal('0.00')) + 
            (self.valor_pecas or Decimal('0.00')) + 
            (self.valor_terceiros or Decimal('0.00')) - 
            (self.desconto or Decimal('0.00'))
        )

    @property
    def public_approval_path(self):
        from django.urls import reverse
        return reverse('core:orcamento_publico', args=[self.orcamento_token])

    def registrar_aprovacao(self, total_aprovado=None):
        if total_aprovado is None:
            total_aprovado = self.orcamento_total_estimado or self.total
        self.status = self.Status.APROVADA
        self.orcamento_total_aprovado = total_aprovado
        self.orcamento_aprovado_em = timezone.now()
        self.orcamento_requer_reaprovacao = False
        self.save(update_fields=[
            'status', 'orcamento_total_aprovado', 'orcamento_aprovado_em', 'orcamento_requer_reaprovacao'
        ])

    def exigir_reaprovacao(self):
        self.orcamento_requer_reaprovacao = True
        self.status = self.Status.ORCAMENTO_ENVIADO
        self.save(update_fields=['orcamento_requer_reaprovacao', 'status'])

    @property
    def tempo_execucao(self):
        if self.data_inicio and self.data_conclusao:
            return self.data_conclusao - self.data_inicio
        return None

    @property
    def prazo_vencido(self):
        if self.prazo_entrega and self.status not in [self.Status.ENTREGUE, self.Status.CANCELADA]:
            return timezone.now() > self.prazo_entrega
        return False

    @property
    def cliente(self):
        return self.veiculo.cliente if self.veiculo else None

    @property
    def total_pago(self):
        return self.pagamentos.filter(
            status=PagamentoOrdemServico.Status.PAGO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

    @property
    def saldo_pendente(self):
        total_base = self.orcamento_total_aprovado or self.orcamento_total_estimado or self.total
        return max(Decimal('0.00'), total_base - (self.total_pago or Decimal('0.00')))

    @property
    def quitada(self):
        return self.saldo_pendente == Decimal('0.00')

    @property
    def possui_pecas_pendentes(self):
        return self.requisicoes_pecas.filter(
            status__in=['SOLICITADO', 'EM_COMPRA', 'AGUARDANDO_ENTREGA']
        ).exists()

    @property
    def valor_minimo_sinal(self):
        ratio = Decimal(str(getattr(settings, 'GARAGE_CONFIG', {}).get('MIN_DEPOSIT_RATIO', 0.5)))
        total_referencia = self.orcamento_total_aprovado or self.orcamento_total_estimado or self.total
        total_referencia = total_referencia or Decimal('0.00')
        return (total_referencia * ratio).quantize(Decimal('0.01'))

    @property
    def sinal_atendido(self):
        return self.total_pago >= self.valor_minimo_sinal

    @property
    def percentual_pago(self):
        total_referencia = self.orcamento_total_aprovado or self.orcamento_total_estimado or self.total
        if not total_referencia:
            return Decimal('0.00')
        return (self.total_pago / total_referencia * Decimal('100')).quantize(Decimal('0.01'))

    def atualizar_totais_por_itens(self, commit=True):
        totais = self.itens.values('tipo').annotate(total=Sum('valor_total'))
        total_servico = Decimal('0.00')
        total_pecas = Decimal('0.00')
        total_terceiros = Decimal('0.00')

        for grupo in totais:
            tipo = grupo['tipo']
            valor = grupo['total'] or Decimal('0.00')
            if tipo == 'SERVICO':
                total_servico = valor
            elif tipo == 'PECA':
                total_pecas = valor
            elif tipo == 'TERCEIRO':
                total_terceiros = valor

        self.valor_mao_obra = total_servico
        self.valor_pecas = total_pecas
        self.valor_terceiros = total_terceiros
        self.total = self.calcular_total()
        if self.estimate_type == self.EstimateType.FIXED:
            self.orcamento_total_estimado = self.total

        if commit:
            self.save(update_fields=[
                'valor_mao_obra', 'valor_pecas', 'valor_terceiros',
                'total', 'orcamento_total_estimado', 'atualizado_em'
            ])


class ItemOrdemServico(models.Model):
    """Itens/serviços específicos de uma ordem de serviço"""
    ordem_servico = models.ForeignKey(OrdemServico, verbose_name='Ordem de Serviço', related_name='itens', on_delete=models.CASCADE)

    # Pode ser uma peça do estoque ou um serviço/item avulso
    peca = models.ForeignKey('Peca', verbose_name='Peça', on_delete=models.PROTECT, null=True, blank=True, related_name='itens_ordem')
    descricao = models.CharField('Descrição', max_length=255, help_text='Preencha se for serviço ou item avulso')

    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=3, default=Decimal('1.000'))
    valor_unitario = models.DecimalField('Valor unitário', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField('Valor total', max_digits=10, decimal_places=2, editable=False)

    tipo = models.CharField('Tipo', max_length=20, choices=[
        ('SERVICO', 'Serviço'),
        ('PECA', 'Peça'),
        ('TERCEIRO', 'Terceiro'),
    ], default='SERVICO')

    dar_baixa_estoque = models.BooleanField('Dar baixa no estoque', default=True, help_text='Desmarque para não movimentar estoque')

    class Meta:
        verbose_name = 'Item da Ordem de Serviço'
        verbose_name_plural = 'Itens da Ordem de Serviço'

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario

        # Se é uma peça do estoque e deve dar baixa
        is_new = not self.pk
        if is_new and self.peca and self.tipo == 'PECA' and self.dar_baixa_estoque:
            # Importar aqui para evitar circular import
            from core.models import MovimentacaoEstoque

            # Criar movimentação de saída
            MovimentacaoEstoque.objects.create(
                peca=self.peca,
                tipo=MovimentacaoEstoque.TipoMovimentacao.SAIDA,
                quantidade=self.quantidade,
                valor_unitario=self.valor_unitario,
                ordem_servico=self.ordem_servico,
                motivo=f'Saída para OS #{self.ordem_servico.numero_os}'
            )

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.peca:
            return f"{self.peca.codigo} - {self.peca.nome}"
        return self.descricao


class FotoOrdemServico(TimestampedModel):
    """Registro de fotos anexadas às ordens de serviço"""
    ordem_servico = models.ForeignKey(
        OrdemServico,
        verbose_name='Ordem de Serviço',
        related_name='fotos',
        on_delete=models.CASCADE
    )
    imagem = models.ImageField('Imagem', upload_to='ordens/%Y/%m/')
    legenda = models.CharField('Legenda', max_length=120, blank=True)

    class Meta:
        verbose_name = 'Foto da Ordem de Serviço'
        verbose_name_plural = 'Fotos das Ordens de Serviço'
        ordering = ['-criado_em']

    def __str__(self) -> str:
        return self.legenda or f"Foto OS #{self.ordem_servico.numero_os}"


class PagamentoOrdemServico(TimestampedModel):
    class FormaPagamento(models.TextChoices):
        PIX = 'PIX', 'PIX'
        CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de crédito'
        CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de débito'
        DINHEIRO = 'DINHEIRO', 'Dinheiro'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferência'
        BOLETO = 'BOLETO', 'Boleto'
        OUTROS = 'OUTROS', 'Outros'

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PAGO = 'PAGO', 'Pago'
        ESTORNADO = 'ESTORNADO', 'Estornado'

    ordem_servico = models.ForeignKey(
        OrdemServico,
        verbose_name='Ordem de Serviço',
        related_name='pagamentos',
        on_delete=models.CASCADE,
    )
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    valor_recebido = models.DecimalField('Valor recebido', max_digits=10, decimal_places=2, null=True, blank=True)
    troco = models.DecimalField('Troco', max_digits=10, decimal_places=2, null=True, blank=True)
    forma_pagamento = models.CharField('Forma de pagamento', max_length=20, choices=FormaPagamento.choices)
    parcelas = models.PositiveSmallIntegerField('Parcelas', null=True, blank=True)
    status = models.CharField('Status', max_length=15, choices=Status.choices, default=Status.PAGO)
    data_pagamento = models.DateTimeField('Data do pagamento', default=timezone.now)
    recebido_por = models.ForeignKey(
        User,
        verbose_name='Recebido por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagamentos_recebidos'
    )
    observacao = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_pagamento']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['forma_pagamento']),
            models.Index(fields=['data_pagamento']),
        ]

    def __str__(self) -> str:
        return f"Pagamento OS {self.ordem_servico.numero_os} - {self.valor}"

    def clean(self):
        super().clean()
        if self.forma_pagamento != self.FormaPagamento.DINHEIRO:
            self.valor_recebido = None
            self.troco = None
        elif self.valor_recebido and self.valor_recebido < self.valor:
            raise ValidationError({'valor_recebido': 'O valor recebido não pode ser menor que o valor do pagamento.'})


class PedidoPecaOrdem(TimestampedModel):
    class Status(models.TextChoices):
        SOLICITADO = 'SOLICITADO', 'Solicitado'
        EM_COMPRA = 'EM_COMPRA', 'Em compra'
        AGUARDANDO_ENTREGA = 'AGUARDANDO_ENTREGA', 'Aguardando entrega'
        RECEBIDO = 'RECEBIDO', 'Recebido'
        CANCELADO = 'CANCELADO', 'Cancelado'

    ordem_servico = models.ForeignKey(
        OrdemServico,
        verbose_name='Ordem de Serviço',
        related_name='requisicoes_pecas',
        on_delete=models.CASCADE
    )
    peca = models.ForeignKey(
        'Peca',
        verbose_name='Peça do estoque',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    descricao = models.CharField('Descrição da peça', max_length=255, blank=True)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, default=Decimal('1.00'))
    fornecedor = models.ForeignKey(
        'Fornecedor',
        verbose_name='Fornecedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.SOLICITADO)
    previsao_entrega = models.DateField('Previsão de entrega', null=True, blank=True)
    data_recebimento = models.DateTimeField('Data de recebimento', null=True, blank=True)
    solicitado_por = models.ForeignKey(
        User,
        verbose_name='Solicitado por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisicoes_pecas_solicitadas'
    )
    recebido_por = models.ForeignKey(
        User,
        verbose_name='Recebido por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisicoes_pecas_recebidas'
    )
    observacao = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Requisição de Peça'
        verbose_name_plural = 'Requisições de Peças'
        ordering = ['status', 'criado_em']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['previsao_entrega']),
        ]

    def __str__(self) -> str:
        base = self.peca.nome if self.peca else (self.descricao or 'Peça não informada')
        return f"{base} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if not self.peca and not self.descricao:
            raise ValidationError('Informe a peça do estoque ou uma descrição.')
        if self.quantidade <= 0:
            raise ValidationError({'quantidade': 'A quantidade precisa ser maior que zero.'})

    def marcar_como_recebido(self, usuario):
        self.status = self.Status.RECEBIDO
        self.data_recebimento = timezone.now()
        self.recebido_por = usuario
        self.save(update_fields=['status', 'data_recebimento', 'recebido_por', 'atualizado_em'])


class Caixa(TimestampedModel):
    class Status(models.TextChoices):
        ABERTO = 'ABERTO', 'Aberto'
        FECHADO = 'FECHADO', 'Fechado'

    data_abertura = models.DateTimeField('Data de abertura', default=timezone.now)
    data_fechamento = models.DateTimeField('Data de fechamento', null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=Status.choices, default=Status.ABERTO)
    saldo_inicial = models.DecimalField('Saldo inicial', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    saldo_final = models.DecimalField('Saldo final', max_digits=10, decimal_places=2, null=True, blank=True)
    aberto_por = models.ForeignKey(
        User,
        verbose_name='Aberto por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caixas_abertos'
    )
    fechado_por = models.ForeignKey(
        User,
        verbose_name='Fechado por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caixas_fechados'
    )
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Caixa'
        verbose_name_plural = 'Caixas'
        ordering = ['-data_abertura']

    def __str__(self) -> str:
        return f"Caixa {self.data_abertura.strftime('%d/%m/%Y')}"

    @property
    def total_entradas(self):
        from django.db.models import Sum

        return self.lancamentos.filter(tipo=LancamentoCaixa.TipoLancamento.ENTRADA).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0.00')

    @property
    def total_saidas(self):
        from django.db.models import Sum

        return self.lancamentos.filter(tipo=LancamentoCaixa.TipoLancamento.SAIDA).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0.00')


class LancamentoCaixa(TimestampedModel):
    class TipoLancamento(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SAIDA = 'SAIDA', 'Saída'

    caixa = models.ForeignKey(
        Caixa,
        verbose_name='Caixa',
        related_name='lancamentos',
        on_delete=models.CASCADE
    )
    pagamento = models.ForeignKey(
        PagamentoOrdemServico,
        verbose_name='Pagamento relacionado',
        related_name='lancamentos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tipo = models.CharField('Tipo', max_length=10, choices=TipoLancamento.choices)
    descricao = models.CharField('Descrição', max_length=255)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField('Forma de pagamento', max_length=20, choices=PagamentoOrdemServico.FormaPagamento.choices)
    registrado_por = models.ForeignKey(
        User,
        verbose_name='Registrado por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_registrados'
    )
    data_lancamento = models.DateTimeField('Data do lançamento', default=timezone.now)
    observacao = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Lançamento de Caixa'
        verbose_name_plural = 'Lançamentos de Caixa'
        ordering = ['-data_lancamento']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['forma_pagamento']),
            models.Index(fields=['data_lancamento']),
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} - {self.valor}"


class StatusHistorico(models.Model):
    """Histórico de mudanças de status"""
    ordem_servico = models.ForeignKey(OrdemServico, verbose_name='Ordem de Serviço', related_name='historico_status', on_delete=models.CASCADE)
    status_anterior = models.CharField('Status anterior', max_length=20, choices=OrdemServico.Status.choices, blank=True)
    status_novo = models.CharField('Status novo', max_length=20, choices=OrdemServico.Status.choices)
    data_mudanca = models.DateTimeField('Data da mudança', auto_now_add=True)
    usuario = models.ForeignKey(User, verbose_name='Usuário', on_delete=models.SET_NULL, null=True, blank=True)
    observacao = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Histórico de Status'
        verbose_name_plural = 'Históricos de Status'
        ordering = ['-data_mudanca']


class Agendamento(TimestampedModel):
    """Sistema de agendamento de serviços"""
    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, verbose_name='Veículo', on_delete=models.CASCADE, blank=True, null=True)
    data_agendamento = models.DateTimeField('Data do agendamento')
    servico_solicitado = models.TextField('Serviço solicitado')
    observacoes = models.TextField('Observações', blank=True)
    confirmado = models.BooleanField('Confirmado', default=False)
    compareceu = models.BooleanField('Compareceu', default=False)
    ordem_servico = models.OneToOneField(OrdemServico, verbose_name='Ordem de Serviço', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['data_agendamento']


class CategoriaPeca(TimestampedModel):
    """Categorias para organizar peças"""
    nome = models.CharField('Nome', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Categoria de Peça'
        verbose_name_plural = 'Categorias de Peças'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
        ]

    def __str__(self) -> str:
        return self.nome

    @property
    def total_pecas(self):
        return self.pecas.filter(ativo=True).count()


class Fornecedor(TimestampedModel):
    """Fornecedores de peças"""
    nome = models.CharField('Nome', max_length=150)
    razao_social = models.CharField('Razão Social', max_length=200, blank=True)
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        validators=[RegexValidator(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', 'Formato: 00.000.000/0000-00')]
    )
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        validators=[RegexValidator(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', 'Formato: (11) 99999-9999')]
    )
    email = models.EmailField('E-mail')
    endereco = models.CharField('Endereço', max_length=255, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    cep = models.CharField(
        'CEP',
        max_length=9,
        blank=True,
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'Formato: 00000-000')]
    )
    contato = models.CharField('Nome do Contato', max_length=100, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    objects = OptimizedManager()

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cnpj']),
        ]

    def __str__(self) -> str:
        return self.nome

    @property
    def total_pecas_fornecidas(self):
        return self.pecas.filter(ativo=True).count()


class Peca(TimestampedModel):
    """Estoque de peças"""
    codigo = models.CharField('Código', max_length=50, unique=True)
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    categoria = models.ForeignKey(
        CategoriaPeca,
        verbose_name='Categoria',
        related_name='pecas',
        on_delete=models.PROTECT
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        verbose_name='Fornecedor',
        related_name='pecas',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    # Estoque
    quantidade_estoque = models.DecimalField(
        'Quantidade em Estoque',
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    estoque_minimo = models.DecimalField(
        'Estoque Mínimo',
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    estoque_maximo = models.DecimalField(
        'Estoque Máximo',
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        blank=True,
        null=True
    )

    # Unidade de medida
    class UnidadeMedida(models.TextChoices):
        UNIDADE = 'UN', 'Unidade'
        PAR = 'PAR', 'Par'
        CONJUNTO = 'CJ', 'Conjunto'
        METRO = 'M', 'Metro'
        LITRO = 'L', 'Litro'
        QUILOGRAMA = 'KG', 'Quilograma'
        CAIXA = 'CX', 'Caixa'

    unidade_medida = models.CharField(
        'Unidade de Medida',
        max_length=10,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.UNIDADE
    )

    # Preços
    preco_custo = models.DecimalField(
        'Preço de Custo',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    preco_venda = models.DecimalField(
        'Preço de Venda',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    margem_lucro = models.DecimalField(
        'Margem de Lucro (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False
    )

    # Localização
    localizacao = models.CharField('Localização no Estoque', max_length=100, blank=True, help_text='Ex: Prateleira A1, Setor 3')

    # Status
    ativo = models.BooleanField('Ativo', default=True)

    # Outras informações
    codigo_fabricante = models.CharField('Código do Fabricante', max_length=100, blank=True)
    codigo_barras = models.CharField('Código de Barras', max_length=50, blank=True)
    peso = models.DecimalField('Peso (kg)', max_digits=10, decimal_places=3, null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)

    objects = OptimizedManager()

    class Meta:
        verbose_name = 'Peça'
        verbose_name_plural = 'Peças'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nome']),
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['codigo_barras']),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nome}"

    def save(self, *args, **kwargs):
        # Calcular margem de lucro
        if self.preco_custo > 0:
            self.margem_lucro = ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        else:
            self.margem_lucro = Decimal('0.00')

        super().save(*args, **kwargs)

    @property
    def estoque_baixo(self):
        """Verifica se o estoque está abaixo do mínimo"""
        return self.quantidade_estoque <= self.estoque_minimo

    @property
    def estoque_critico(self):
        """Verifica se o estoque está crítico (50% do mínimo)"""
        return self.quantidade_estoque <= (self.estoque_minimo * Decimal('0.5'))

    @property
    def valor_total_estoque(self):
        """Valor total do estoque (custo)"""
        return self.quantidade_estoque * self.preco_custo

    @property
    def disponivel(self):
        """Verifica se há peça disponível"""
        return self.quantidade_estoque > 0 and self.ativo


class MovimentacaoEstoque(models.Model):
    """Registro de movimentações de estoque"""
    class TipoMovimentacao(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SAIDA = 'SAIDA', 'Saída'
        AJUSTE = 'AJUSTE', 'Ajuste'
        DEVOLUCAO = 'DEVOLUCAO', 'Devolução'
        PERDA = 'PERDA', 'Perda'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferência'

    peca = models.ForeignKey(Peca, verbose_name='Peça', related_name='movimentacoes', on_delete=models.PROTECT)
    tipo = models.CharField('Tipo', max_length=20, choices=TipoMovimentacao.choices)
    quantidade = models.DecimalField(
        'Quantidade',
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    quantidade_anterior = models.DecimalField('Quantidade Anterior', max_digits=10, decimal_places=3)
    quantidade_nova = models.DecimalField('Quantidade Nova', max_digits=10, decimal_places=3)

    # Valores
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2, editable=False)

    # Relações
    ordem_servico = models.ForeignKey(
        OrdemServico,
        verbose_name='Ordem de Serviço',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_estoque'
    )
    usuario = models.ForeignKey(User, verbose_name='Usuário', on_delete=models.SET_NULL, null=True)

    # Informações adicionais
    data_movimentacao = models.DateTimeField('Data da Movimentação', auto_now_add=True)
    motivo = models.TextField('Motivo', blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=50, blank=True, help_text='NF, Pedido, etc.')

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data_movimentacao']
        indexes = [
            models.Index(fields=['peca', '-data_movimentacao']),
            models.Index(fields=['tipo', '-data_movimentacao']),
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} - {self.peca.codigo} - {self.quantidade}"

    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = self.quantidade * self.valor_unitario

        # Salvar quantidade anterior
        if not self.pk:  # Nova movimentação
            self.quantidade_anterior = self.peca.quantidade_estoque

            # Atualizar estoque da peça
            if self.tipo in [self.TipoMovimentacao.ENTRADA, self.TipoMovimentacao.DEVOLUCAO]:
                self.peca.quantidade_estoque += self.quantidade
            elif self.tipo in [self.TipoMovimentacao.SAIDA, self.TipoMovimentacao.PERDA]:
                self.peca.quantidade_estoque -= self.quantidade
            elif self.tipo == self.TipoMovimentacao.AJUSTE:
                # Para ajuste, a quantidade é o novo valor total
                self.peca.quantidade_estoque = self.quantidade

            self.quantidade_nova = self.peca.quantidade_estoque
            self.peca.save()

        super().save(*args, **kwargs)
