import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cpf(value):
    """
    Valida se o CPF está no formato correto e é válido.
    """
    if not value:
        return
    
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise ValidationError(_('CPF deve ter 11 dígitos.'))
    
    # Verifica se não são todos os números iguais
    if cpf == cpf[0] * 11:
        raise ValidationError(_('CPF inválido.'))
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        raise ValidationError(_('CPF inválido.'))
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[10]) != digito2:
        raise ValidationError(_('CPF inválido.'))


def validate_cnpj(value):
    """
    Valida se o CNPJ está no formato correto e é válido.
    """
    if not value:
        return
    
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        raise ValidationError(_('CNPJ deve ter 14 dígitos.'))
    
    # Verifica se não são todos os números iguais
    if cnpj == cnpj[0] * 14:
        raise ValidationError(_('CNPJ inválido.'))
    
    # Validação do primeiro dígito verificador
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        raise ValidationError(_('CNPJ inválido.'))
    
    # Validação do segundo dígito verificador
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[13]) != digito2:
        raise ValidationError(_('CNPJ inválido.'))


def validate_placa(value):
    """
    Valida se a placa está no formato brasileiro correto.
    Aceita formato antigo (ABC-1234) e Mercosul (ABC1D23).
    """
    if not value:
        return
    
    placa = str(value).upper().strip()
    
    # Formato antigo: ABC-1234 ou ABC1234
    padrao_antigo = r'^[A-Z]{3}-?\d{4}$'
    
    # Formato Mercosul: ABC1D23
    padrao_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    
    if not (re.match(padrao_antigo, placa) or re.match(padrao_mercosul, placa)):
        raise ValidationError(_('Formato de placa inválido. Use ABC-1234 ou ABC1D23.'))


def validate_telefone(value):
    """
    Valida se o telefone está no formato brasileiro correto.
    """
    if not value:
        return
    
    # Remove caracteres não numéricos
    telefone = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se tem 10 ou 11 dígitos (com DDD)
    if len(telefone) not in [10, 11]:
        raise ValidationError(_('Telefone deve ter 10 ou 11 dígitos com DDD.'))
    
    # Verifica se o DDD é válido (11 a 99)
    ddd = int(telefone[:2])
    if ddd < 11 or ddd > 99:
        raise ValidationError(_('DDD inválido.'))
    
    # Para celular (11 dígitos), o terceiro dígito deve ser 9
    if len(telefone) == 11 and telefone[2] != '9':
        raise ValidationError(_('Para celular, o terceiro dígito deve ser 9.'))


def validate_email_domain(value):
    """
    Valida domínios de e-mail específicos se necessário.
    """
    if not value:
        return
    
    # Lista de domínios bloqueados (exemplo)
    dominios_bloqueados = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
    
    dominio = value.split('@')[-1].lower()
    
    if dominio in dominios_bloqueados:
        raise ValidationError(_('Este domínio de e-mail não é permitido.'))


def validate_chassi(value):
    """
    Valida o número do chassi do veículo.
    """
    if not value:
        return
    
    chassi = str(value).upper().strip()
    
    # Chassi deve ter 17 caracteres
    if len(chassi) != 17:
        raise ValidationError(_('Chassi deve ter exatamente 17 caracteres.'))
    
    # Não pode conter certas letras que podem ser confundidas
    letras_proibidas = ['I', 'O', 'Q']
    for letra in letras_proibidas:
        if letra in chassi:
            raise ValidationError(_('Chassi não pode conter as letras I, O ou Q.'))
    
    # Deve conter apenas letras e números
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', chassi):
        raise ValidationError(_('Chassi contém caracteres inválidos.'))


def validate_ano_veiculo(value):
    """
    Valida se o ano do veículo está em uma faixa aceitável.
    """
    from datetime import datetime
    
    if not value:
        return
    
    ano_atual = datetime.now().year
    ano_minimo = 1900
    ano_maximo = ano_atual + 1  # Permite veículos do próximo ano
    
    if value < ano_minimo or value > ano_maximo:
        raise ValidationError(
            _('Ano deve estar entre %(min)s e %(max)s.') % {
                'min': ano_minimo, 
                'max': ano_maximo
            }
        )


def validate_km_veiculo(value):
    """
    Valida se a quilometragem do veículo é razoável.
    """
    if not value:
        return
    
    if value < 0:
        raise ValidationError(_('Quilometragem não pode ser negativa.'))
    
    # Limite máximo razoável (ex: 1 milhão de km)
    if value > 1000000:
        raise ValidationError(_('Quilometragem parece muito alta.'))


def validate_valor_monetario(value):
    """
    Valida se o valor monetário está em uma faixa aceitável.
    """
    from decimal import Decimal
    
    if not value:
        return
    
    if value < Decimal('0'):
        raise ValidationError(_('Valor não pode ser negativo.'))
    
    # Limite máximo razoável (ex: R$ 100.000,00)
    if value > Decimal('100000.00'):
        raise ValidationError(_('Valor parece muito alto.'))


def validate_prazo_futuro(value):
    """
    Valida se uma data/prazo está no futuro.
    """
    from django.utils import timezone
    
    if not value:
        return
    
    if value <= timezone.now():
        raise ValidationError(_('Data/prazo deve ser no futuro.'))


def validate_cep(value):
    """
    Valida se o CEP está no formato correto.
    """
    if not value:
        return
    
    # Remove caracteres não numéricos
    cep = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se tem 8 dígitos
    if len(cep) != 8:
        raise ValidationError(_('CEP deve ter 8 dígitos.'))
    
    # Verifica se não são todos zeros
    if cep == '00000000':
        raise ValidationError(_('CEP inválido.'))


class ValidadorPersonalizado:
    """
    Classe para validações mais complexas que necessitam de contexto.
    """
    
    @staticmethod
    def validar_cliente_unico_por_cpf(cpf, cliente_id=None):
        """
        Verifica se já existe um cliente com o mesmo CPF.
        """
        from .models import Cliente
        
        queryset = Cliente.objects.filter(cpf=cpf, ativo=True)
        if cliente_id:
            queryset = queryset.exclude(id=cliente_id)
        
        if queryset.exists():
            raise ValidationError(_('Já existe um cliente ativo com este CPF.'))
    
    @staticmethod
    def validar_placa_unica(placa, veiculo_id=None):
        """
        Verifica se já existe um veículo com a mesma placa.
        """
        from .models import Veiculo
        
        queryset = Veiculo.objects.filter(placa=placa, ativo=True)
        if veiculo_id:
            queryset = queryset.exclude(id=veiculo_id)
        
        if queryset.exists():
            raise ValidationError(_('Já existe um veículo ativo com este chassi.'))
    
    @staticmethod
    def validar_agendamento_disponibilidade(data_agendamento, agendamento_id=None):
        """
        Verifica se já existe um agendamento no mesmo horário.
        """
        from .models import Agendamento
        from datetime import timedelta
        
        # Criar janela de 1 hora antes e depois
        inicio = data_agendamento - timedelta(hours=1)
        fim = data_agendamento + timedelta(hours=1)
        
        queryset = Agendamento.objects.filter(
            data_agendamento__range=[inicio, fim],
            confirmado=True
        )
        
        if agendamento_id:
            queryset = queryset.exclude(id=agendamento_id)
        
        if queryset.exists():
            raise ValidationError(
                _('Já existe um agendamento próximo a este horário.')
            )
    
    @staticmethod
    def validar_desconto_maximo(valor_total, desconto):
        """
        Verifica se o desconto não ultrapassa o valor total.
        """
        if desconto and valor_total:
            if desconto > valor_total:
                raise ValidationError(
                    _('Desconto não pode ser maior que o valor total.')
                )
            
            # Limitar desconto a 50% do valor total
            desconto_maximo = valor_total * 0.5
            if desconto > desconto_maximo:
                raise ValidationError(
                    _('Desconto não pode ser maior que 50%% do valor total.')
                )


def clean_cpf(cpf_string):
    """
    Remove formatação do CPF e retorna apenas números.
    """
    return re.sub(r'[^0-9]', '', str(cpf_string))


def format_cpf(cpf_string):
    """
    Formata CPF no padrão 000.000.000-00.
    """
    cpf = clean_cpf(cpf_string)
    if len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf_string


def clean_cnpj(cnpj_string):
    """
    Remove formatação do CNPJ e retorna apenas números.
    """
    return re.sub(r'[^0-9]', '', str(cnpj_string))


def format_cnpj(cnpj_string):
    """
    Formata CNPJ no padrão 00.000.000/0000-00.
    """
    cnpj = clean_cnpj(cnpj_string)
    if len(cnpj) == 14:
        return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'
    return cnpj_string


def clean_telefone(telefone_string):
    """
    Remove formatação do telefone e retorna apenas números.
    """
    return re.sub(r'[^0-9]', '', str(telefone_string))


def format_telefone(telefone_string):
    """
    Formata telefone no padrão (00) 00000-0000 ou (00) 0000-0000.
    """
    telefone = clean_telefone(telefone_string)
    if len(telefone) == 11:  # Celular
        return f'({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}'
    elif len(telefone) == 10:  # Fixo
        return f'({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}'
    return telefone_string


def format_placa(placa_string):
    """
    Formata placa no padrão ABC-1234.
    """
    placa = str(placa_string).upper().replace('-', '')
    if len(placa) == 7:
        return f'{placa[:3]}-{placa[3:]}'
    return placa_string


def format_cep(cep_string):
    """
    Formata CEP no padrão 00000-000.
    """
    cep = re.sub(r'[^0-9]', '', str(cep_string))
    if len(cep) == 8:
        return f'{cep[:5]}-{cep[5:]}'
    return cep_string


def validate_file_size(value):
    """
    Valida o tamanho de arquivos enviados (máximo 5MB).
    """
    if value:
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError(_('Arquivo muito grande. Tamanho máximo: 5MB.'))


def validate_image_file(value):
    """
    Valida se o arquivo é uma imagem válida.
    """
    if value:
        # Verificar extensão
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = value.name.lower().split('.')[-1]
        if f'.{ext}' not in valid_extensions:
            raise ValidationError(
                _('Formato de imagem inválido. Use: JPG, PNG, GIF ou WebP.')
            )
        
        # Verificar tamanho
        validate_file_size(value)


# Dicionário com validadores para fácil importação
VALIDATORS = {
    'cpf': validate_cpf,
    'cnpj': validate_cnpj,
    'placa': validate_placa,
    'telefone': validate_telefone,
    'email_domain': validate_email_domain,
    'chassi': validate_chassi,
    'ano_veiculo': validate_ano_veiculo,
    'km_veiculo': validate_km_veiculo,
    'valor_monetario': validate_valor_monetario,
    'prazo_futuro': validate_prazo_futuro,
    'cep': validate_cep,
    'file_size': validate_file_size,
    'image_file': validate_image_file,
}

# Formatadores para fácil importação
FORMATTERS = {
    'cpf': format_cpf,
    'cnpj': format_cnpj,
    'telefone': format_telefone,
    'placa': format_placa,
    'cep': format_cep,
}

# Limpadores para fácil importação
CLEANERS = {
    'cpf': clean_cpf,
    'cnpj': clean_cnpj,
    'telefone': clean_telefone,
}
            queryset = queryset.exclude(id=veiculo_id)
        
        if queryset.exists():
            raise ValidationError(_('Já existe um veículo ativo com esta placa.'))
    
    @staticmethod
    def validar_chassi_unico(chassi, veiculo_id=None):
        """
        Verifica se já existe um veículo com o mesmo chassi.
        """
        from .models import Veiculo
        
        if not chassi:
            return
        
        queryset = Veiculo.objects.filter(chassi=chassi, ativo=True)
        if veiculo_id: