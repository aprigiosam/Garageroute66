from typing import Any
import re
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import (
    Cliente, OrdemServico, Veiculo, ItemOrdemServico, FotoOrdemServico,
    PagamentoOrdemServico, Agendamento, CategoriaPeca, Fornecedor, Peca, MovimentacaoEstoque
)


def validar_cpf(cpf: str) -> bool:
    """Validação básica de CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    def calcular_digito(cpf_parcial):
        soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    return (calcular_digito(cpf[:9]) == int(cpf[9]) and 
            calcular_digito(cpf[:10]) == int(cpf[10]))


class BaseBootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def _apply_bootstrap(self) -> None:
        for field_name, field in self.fields.items():
            widget = field.widget
            css_class = widget.attrs.get('class', '')
            
            if isinstance(widget, forms.CheckboxInput):
                base_class = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                base_class = 'form-select'
            elif isinstance(widget, forms.Textarea):
                base_class = 'form-control'
                if 'rows' not in widget.attrs:
                    widget.attrs['rows'] = 3
            elif isinstance(widget, forms.DateTimeInput):
                base_class = 'form-control'
                widget.attrs['type'] = 'datetime-local'
            elif isinstance(widget, forms.DateInput):
                base_class = 'form-control'
                widget.attrs['type'] = 'date'
            elif isinstance(widget, forms.TimeInput):
                base_class = 'form-control'
                widget.attrs['type'] = 'time'
            elif isinstance(widget, forms.NumberInput):
                base_class = 'form-control'
                if field_name in ['valor_mao_obra', 'valor_pecas', 'valor_terceiros', 'desconto', 'valor_unitario']:
                    widget.attrs['step'] = '0.01'
                    widget.attrs['min'] = '0'
            else:
                base_class = 'form-control'

            if base_class not in css_class.split():
                widget.attrs['class'] = f"{css_class} {base_class}".strip()

            # Adicionar placeholder baseado no label
            if hasattr(field, 'label') and field.label and 'placeholder' not in widget.attrs:
                if not isinstance(widget, (forms.Select, forms.SelectMultiple, forms.CheckboxInput)):
                    widget.attrs['placeholder'] = f"Digite {field.label.lower()}"

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(instance, 'criado_por') and not instance.pk and self.user:
            instance.criado_por = self.user
        if hasattr(instance, 'atualizado_por') and self.user:
            instance.atualizado_por = self.user
        if commit:
            instance.save()
        return instance


class ClienteForm(BaseBootstrapForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'email', 'endereco', 'cpf', 'observacoes']
        widgets = {
            'endereco': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs['autofocus'] = True
        self.fields['cpf'].help_text = 'Formato: 000.000.000-00'
        self.fields['telefone'].help_text = 'Formato: (11) 99999-9999'

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        
        if not validar_cpf(cpf):
            raise ValidationError('CPF inválido.')
        
        # Verificar se já existe outro cliente com este CPF
        if self.instance.pk:
            if Cliente.objects.exclude(pk=self.instance.pk).filter(cpf=cpf).exists():
                raise ValidationError('Já existe um cliente com este CPF.')
        else:
            if Cliente.objects.filter(cpf=cpf).exists():
                raise ValidationError('Já existe um cliente com este CPF.')
        
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        
        # Verificar se já existe outro cliente com este email
        if email:
            if self.instance.pk:
                if Cliente.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                    raise ValidationError('Já existe um cliente com este e-mail.')
            else:
                if Cliente.objects.filter(email=email).exists():
                    raise ValidationError('Já existe um cliente com este e-mail.')
        
        return email


class VeiculoForm(BaseBootstrapForm):
    class Meta:
        model = Veiculo
        fields = [
            'cliente', 'placa', 'marca', 'modelo', 'ano', 'cor', 
            'chassi', 'tipo_veiculo', 'batido', 'km_atual', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(ativo=True).order_by('nome')
        self.fields['placa'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['chassi'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['placa'].help_text = 'Formato: ABC-1234 ou ABC1D23'

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').upper()
        
        # Verificar se já existe outro veículo com esta placa
        if self.instance.pk:
            if Veiculo.objects.exclude(pk=self.instance.pk).filter(placa=placa).exists():
                raise ValidationError('Já existe um veículo com esta placa.')
        else:
            if Veiculo.objects.filter(placa=placa).exists():
                raise ValidationError('Já existe um veículo com esta placa.')
        
        return placa

    def clean_chassi(self):
        chassi = self.cleaned_data.get('chassi', '').upper()
        
        # Verificar se já existe outro veículo com este chassi
        if chassi:
            if self.instance.pk:
                if Veiculo.objects.exclude(pk=self.instance.pk).filter(chassi=chassi).exists():
                    raise ValidationError('Já existe um veículo com este chassi.')
            else:
                if Veiculo.objects.filter(chassi=chassi).exists():
                    raise ValidationError('Já existe um veículo com este chassi.')
        
        return chassi


class OrdemServicoForm(BaseBootstrapForm):
    veiculo = forms.ModelChoiceField(
        queryset=Veiculo.objects.select_related('cliente').filter(ativo=True).order_by('placa'),
        label='Veículo',
    )
    responsavel_tecnico = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'username'),
        label='Responsável técnico',
        required=False,
    )

    class Meta:
        model = OrdemServico
        fields = [
            'veiculo', 'descricao_problema', 'diagnostico', 'prioridade',
            'requires_diagnosis', 'estimate_type', 'orcamento_total_estimado',
            'valor_mao_obra', 'valor_pecas', 'valor_terceiros', 'desconto',
            'km_entrada', 'prazo_entrega', 'responsavel_tecnico', 'observacoes'
        ]
        widgets = {
            'descricao_problema': forms.Textarea(attrs={'rows': 4}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'prazo_entrega': forms.DateTimeInput(),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        
        # Melhorar a exibição do queryset do veículo
        self.fields['veiculo'].queryset = self.fields['veiculo'].queryset.select_related('cliente')
        
        # Se estiver editando, mostrar campos adicionais
        if self.instance.pk:
            self.fields.update({
                'status': forms.ChoiceField(
                    choices=OrdemServico.Status.choices,
                    widget=forms.Select(attrs={'class': 'form-select'})
                ),
                'solucao': forms.CharField(
                    label='Solução aplicada',
                    widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                    required=False
                ),
                'observacoes_internas': forms.CharField(
                    label='Observações internas',
                    widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
                    required=False
                ),
            })

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar se os valores são positivos
        campos_valor = ['valor_mao_obra', 'valor_pecas', 'valor_terceiros', 'desconto']
        for campo in campos_valor:
            valor = cleaned_data.get(campo)
            if valor and valor < 0:
                self.add_error(campo, 'O valor não pode ser negativo.')

        # Validar se o desconto não é maior que o total
        valor_total = sum(cleaned_data.get(campo, Decimal('0')) for campo in ['valor_mao_obra', 'valor_pecas', 'valor_terceiros'])
        desconto = cleaned_data.get('desconto', Decimal('0'))
        
        if desconto > valor_total:
            self.add_error('desconto', 'O desconto não pode ser maior que o valor total dos serviços.')

        estimate_type = cleaned_data.get('estimate_type')
        requires_diagnosis = cleaned_data.get('requires_diagnosis')
        orcamento_total_estimado = cleaned_data.get('orcamento_total_estimado')

        if estimate_type == OrdemServico.EstimateType.FIXED and not orcamento_total_estimado:
            self.add_error('orcamento_total_estimado', 'Informe o valor estimado para serviços padrão.')

        if estimate_type == OrdemServico.EstimateType.FIXED:
            cleaned_data['requires_diagnosis'] = False
        elif estimate_type == OrdemServico.EstimateType.PERSONALIZADO:
            cleaned_data['requires_diagnosis'] = True
        elif requires_diagnosis and not estimate_type:
            cleaned_data['estimate_type'] = OrdemServico.EstimateType.PERSONALIZADO
        
        return cleaned_data

    def save(self, commit: bool = True) -> OrdemServico:
        ordem_servico = super().save(commit=False)
        
        # Se for uma nova OS, definir status como ABERTA
        if not ordem_servico.pk:
            ordem_servico.status = OrdemServico.Status.ABERTA

        if commit:
            ordem_servico.save()
        return ordem_servico


class ItemOrdemServicoForm(forms.ModelForm):
    class Meta:
        model = ItemOrdemServico
        fields = ['descricao', 'tipo', 'quantidade', 'valor_unitario']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'valor_unitario': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


ItemOrdemServicoFormSet = forms.inlineformset_factory(
    OrdemServico,
    ItemOrdemServico,
    form=ItemOrdemServicoForm,
    extra=1,
    can_delete=True,
)


class FotoOrdemServicoForm(BaseBootstrapForm):
    class Meta:
        model = FotoOrdemServico
        fields = ['imagem', 'legenda']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'legenda': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 120}),
        }


FotoOrdemServicoFormSet = forms.inlineformset_factory(
    OrdemServico,
    FotoOrdemServico,
    form=FotoOrdemServicoForm,
    extra=1,
    can_delete=True,
)


class DiagnosticoOrdemServicoForm(BaseBootstrapForm):
    class Meta:
        model = OrdemServico
        fields = [
            'diagnostico', 'solucao', 'valor_mao_obra', 'valor_pecas',
            'valor_terceiros', 'desconto', 'observacoes_internas'
        ]
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 4}),
            'solucao': forms.Textarea(attrs={'rows': 3}),
            'observacoes_internas': forms.Textarea(attrs={'rows': 2}),
        }


class PagamentoOrdemServicoForm(BaseBootstrapForm):
    class Meta:
        model = PagamentoOrdemServico
        fields = ['valor', 'forma_pagamento', 'status', 'parcelas', 'valor_recebido', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = PagamentoOrdemServico.Status.PAGO
        self.fields['valor'].widget.attrs['min'] = '0.01'
        self.fields['valor'].widget.attrs['step'] = '0.01'
        self.fields['valor_recebido'].widget.attrs['step'] = '0.01'
        self.fields['valor_recebido'].required = False
        self.fields['parcelas'].required = False

    def clean(self):
        cleaned_data = super().clean()
        valor = cleaned_data.get('valor') or Decimal('0.00')
        forma_pagamento = cleaned_data.get('forma_pagamento')

        if forma_pagamento == PagamentoOrdemServico.FormaPagamento.DINHEIRO:
            valor_recebido = cleaned_data.get('valor_recebido') or valor
            if valor_recebido < valor:
                self.add_error('valor_recebido', 'O valor recebido precisa ser igual ou superior ao valor do pagamento.')
            cleaned_data['valor_recebido'] = valor_recebido
            cleaned_data['troco'] = valor_recebido - valor
        else:
            cleaned_data['valor_recebido'] = None
            cleaned_data['troco'] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        cleaned_data = getattr(self, 'cleaned_data', {})

        if cleaned_data:
            if instance.forma_pagamento == PagamentoOrdemServico.FormaPagamento.DINHEIRO:
                instance.valor_recebido = cleaned_data.get('valor_recebido')
                instance.troco = cleaned_data.get('troco')
            else:
                instance.valor_recebido = None
                instance.troco = None

        if not instance.pk and self.user and not instance.recebido_por:
            instance.recebido_por = self.user

        if commit:
            instance.save()
        return instance


class AgendamentoForm(BaseBootstrapForm):
    class Meta:
        model = Agendamento
        fields = [
            'cliente', 'veiculo', 'data_agendamento', 'servico_solicitado', 
            'observacoes'
        ]
        widgets = {
            'data_agendamento': forms.DateTimeInput(),
            'servico_solicitado': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(ativo=True).order_by('nome')
        self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True).order_by('placa')
        self.fields['veiculo'].required = False

    def clean_data_agendamento(self):
        from django.utils import timezone
        data = self.cleaned_data.get('data_agendamento')
        
        if data and data < timezone.now():
            raise ValidationError('A data do agendamento não pode ser no passado.')
        
        return data


class FiltroOrdemServicoForm(forms.Form):
    """Formulário para filtrar ordens de serviço"""
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + list(OrdemServico.Status.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    prioridade = forms.ChoiceField(
        choices=[('', 'Todas as prioridades')] + list(OrdemServico.Prioridade.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(ativo=True).order_by('nome'),
        required=False,
        empty_label='Todos os clientes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    veiculo = forms.ModelChoiceField(
        queryset=Veiculo.objects.filter(ativo=True).order_by('placa'),
        required=False,
        empty_label='Todos os veículos',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    busca = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número OS, placa ou cliente...'
        })
    )


class RelatorioForm(forms.Form):
    """Formulário para gerar relatórios"""
    TIPO_CHOICES = [
        ('faturamento', 'Faturamento'),
        ('servicos', 'Serviços realizados'),
        ('clientes', 'Clientes'),
        ('veiculos', 'Veículos'),
    ]
    
    PERIODO_CHOICES = [
        ('hoje', 'Hoje'),
        ('semana', 'Esta semana'),
        ('mes', 'Este mês'),
        ('trimestre', 'Este trimestre'),
        ('ano', 'Este ano'),
        ('personalizado', 'Período personalizado'),
    ]
    
    tipo_relatorio = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        periodo = cleaned_data.get('periodo')
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if periodo == 'personalizado':
            if not data_inicio or not data_fim:
                raise ValidationError('Para período personalizado, informe data início e fim.')
            if data_inicio > data_fim:
                raise ValidationError('Data início deve ser anterior à data fim.')
        
        return cleaned_data

# ===== FORMULÁRIOS DE PEÇAS E ESTOQUE =====

class CategoriaPecaForm(BaseBootstrapForm):
    class Meta:
        model = CategoriaPeca
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class FornecedorForm(BaseBootstrapForm):
    class Meta:
        model = Fornecedor
        fields = [
            'nome', 'razao_social', 'cnpj', 'telefone', 'email',
            'endereco', 'cidade', 'estado', 'cep', 'contato',
            'observacoes', 'ativo'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            qs = Fornecedor.objects.filter(cnpj=cnpj)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Já existe um fornecedor cadastrado com este CNPJ.')
        return cnpj


class PecaForm(BaseBootstrapForm):
    class Meta:
        model = Peca
        fields = [
            'codigo', 'nome', 'descricao', 'categoria', 'fornecedor',
            'quantidade_estoque', 'estoque_minimo', 'estoque_maximo',
            'unidade_medida', 'preco_custo', 'preco_venda',
            'localizacao', 'codigo_fabricante', 'codigo_barras',
            'peso', 'observacoes', 'ativo'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo'].widget.attrs['placeholder'] = 'Ex: FIL001'
        self.fields['nome'].widget.attrs['placeholder'] = 'Ex: Filtro de Óleo Mann W719/30'
        self.fields['localizacao'].widget.attrs['placeholder'] = 'Ex: Prateleira A1, Setor 3'

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            qs = Peca.objects.filter(codigo=codigo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Já existe uma peça cadastrada com este código.')
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        preco_custo = cleaned_data.get('preco_custo', Decimal('0'))
        preco_venda = cleaned_data.get('preco_venda', Decimal('0'))

        if preco_venda < preco_custo:
            self.add_error('preco_venda', 'Preço de venda não pode ser menor que o preço de custo.')

        estoque_minimo = cleaned_data.get('estoque_minimo', Decimal('0'))
        estoque_maximo = cleaned_data.get('estoque_maximo')

        if estoque_maximo and estoque_maximo < estoque_minimo:
            self.add_error('estoque_maximo', 'Estoque máximo não pode ser menor que o mínimo.')

        return cleaned_data


class MovimentacaoEstoqueForm(BaseBootstrapForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = [
            'peca', 'tipo', 'quantidade', 'valor_unitario',
            'ordem_servico', 'motivo', 'numero_documento'
        ]
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['peca'].queryset = Peca.objects.filter(ativo=True).select_related('categoria')
        self.fields['ordem_servico'].required = False

    def clean(self):
        cleaned_data = super().clean()
        peca = cleaned_data.get('peca')
        tipo = cleaned_data.get('tipo')
        quantidade = cleaned_data.get('quantidade', Decimal('0'))

        if peca and tipo:
            if tipo in [MovimentacaoEstoque.TipoMovimentacao.SAIDA,
                       MovimentacaoEstoque.TipoMovimentacao.PERDA]:
                if peca.quantidade_estoque < quantidade:
                    self.add_error('quantidade',
                        f'Estoque insuficiente. Disponível: {peca.quantidade_estoque} {peca.get_unidade_medida_display()}'
                    )

        return cleaned_data


class FiltroPecaForm(forms.Form):
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nome...'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaPeca.objects.filter(ativo=True),
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.filter(ativo=True),
        required=False,
        empty_label='Todos os fornecedores',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estoque = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('baixo', 'Estoque Baixo'),
            ('critico', 'Estoque Crítico'),
            ('ok', 'Estoque OK'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ativo = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('True', 'Apenas Ativos'),
            ('False', 'Apenas Inativos'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
