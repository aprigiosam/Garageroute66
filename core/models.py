from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count, Sum, Prefetch


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
        ORCAMENTO = 'ORCAMENTO', 'Orçamento'
        APROVADA = 'APROVADA', 'Aprovada'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em andamento'
        AGUARDANDO_PECA = 'AGUARDANDO_PECA', 'Aguardando peça'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class Prioridade(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa'
        NORMAL = 'NORMAL', 'Normal'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'

    veiculo = models.ForeignKey(Veiculo, verbose_name='Veículo', related_name='ordens_servico', on_delete=models.CASCADE)
    numero_os = models.CharField('Número OS', max_length=20, unique=True, blank=True)
    descricao_problema = models.TextField('Descrição do problema')
    diagnostico = models.TextField('Diagnóstico', blank=True)
    solucao = models.TextField('Solução aplicada', blank=True)
    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.ABERTA)
    prioridade = models.CharField('Prioridade', max_length=20, choices=Prioridade.choices, default=Prioridade.NORMAL)
    
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
        if self.status == self.Status.ORCAMENTO and not self.data_orcamento:
            self.data_orcamento = now
        elif self.status == self.Status.APROVADA and not self.data_aprovacao:
            self.data_aprovacao = now
        elif self.status == self.Status.EM_ANDAMENTO and not self.data_inicio:
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


class ItemOrdemServico(models.Model):
    """Itens/serviços específicos de uma ordem de serviço"""
    ordem_servico = models.ForeignKey(OrdemServico, verbose_name='Ordem de Serviço', related_name='itens', on_delete=models.CASCADE)
    descricao = models.CharField('Descrição', max_length=255)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=3, default=Decimal('1.000'))
    valor_unitario = models.DecimalField('Valor unitário', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField('Valor total', max_digits=10, decimal_places=2, editable=False)
    tipo = models.CharField('Tipo', max_length=20, choices=[
        ('SERVICO', 'Serviço'),
        ('PECA', 'Peça'),
        ('TERCEIRO', 'Terceiro'),
    ], default='SERVICO')

    class Meta:
        verbose_name = 'Item da Ordem de Serviço'
        verbose_name_plural = 'Itens da Ordem de Serviço'

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)


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