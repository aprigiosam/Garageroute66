from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
import logging

from .models import OrdemServico, StatusHistorico, Cliente, Veiculo, Agendamento

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=OrdemServico)
def ordem_servico_pre_save(sender, instance, **kwargs):
    """
    Executa ações antes de salvar uma ordem de serviço
    """
    # Se é uma atualização, verifica mudança de status
    if instance.pk:
        try:
            old_instance = OrdemServico.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Criar histórico de mudança de status
                StatusHistorico.objects.create(
                    ordem_servico=instance,
                    status_anterior=old_instance.status,
                    status_novo=instance.status,
                    data_mudanca=timezone.now(),
                    observacao='Alteração automática via sistema'
                )
        except OrdemServico.DoesNotExist:
            pass


@receiver(post_save, sender=OrdemServico)
def ordem_servico_post_save(sender, instance, created, **kwargs):
    """
    Executa ações após salvar uma ordem de serviço
    """
    if created:
        logger.info(f'Nova ordem de serviço criada: {instance.numero_os}')
        
        # Enviar notificação por e-mail se configurado
        if getattr(settings, 'OFICINA_CONFIG', {}).get('SEND_EMAIL_NOTIFICATIONS', False):
            enviar_notificacao_nova_os(instance)
    
    else:
        logger.info(f'Ordem de serviço atualizada: {instance.numero_os}')
        
        # Verificar se mudou para status "CONCLUIDA" ou "ENTREGUE"
        if instance.status in [OrdemServico.Status.CONCLUIDA, OrdemServico.Status.ENTREGUE]:
            enviar_notificacao_os_concluida(instance)


@receiver(post_save, sender=Cliente)
def cliente_post_save(sender, instance, created, **kwargs):
    """
    Executa ações após salvar um cliente
    """
    if created:
        logger.info(f'Novo cliente cadastrado: {instance.nome} - CPF: {instance.cpf}')
        
        # Aqui você poderia integrar com sistemas externos, enviar e-mail de boas-vindas, etc.


@receiver(post_save, sender=Veiculo)
def veiculo_post_save(sender, instance, created, **kwargs):
    """
    Executa ações após salvar um veículo
    """
    if created:
        logger.info(f'Novo veículo cadastrado: {instance.placa} para {instance.cliente.nome}')


@receiver(post_save, sender=Agendamento)
def agendamento_post_save(sender, instance, created, **kwargs):
    """
    Executa ações após salvar um agendamento
    """
    if created:
        logger.info(f'Novo agendamento criado para {instance.cliente.nome} em {instance.data_agendamento}')
        
        # Enviar notificação de confirmação de agendamento
        if getattr(settings, 'OFICINA_CONFIG', {}).get('SEND_EMAIL_NOTIFICATIONS', False):
            enviar_notificacao_agendamento(instance)


@receiver(post_delete, sender=OrdemServico)
def ordem_servico_post_delete(sender, instance, **kwargs):
    """
    Executa ações após deletar uma ordem de serviço
    """
    logger.warning(f'Ordem de serviço deletada: {instance.numero_os}')


def enviar_notificacao_nova_os(ordem_servico):
    """
    Envia notificação por e-mail quando uma nova OS é criada
    """
    try:
        cliente = ordem_servico.veiculo.cliente
        subject = f'Nova Ordem de Serviço #{ordem_servico.numero_os}'
        
        context = {
            'ordem_servico': ordem_servico,
            'cliente': cliente,
            'veiculo': ordem_servico.veiculo,
        }
        
        # Render do template de e-mail
        html_message = render_to_string('emails/nova_os.html', context)
        plain_message = render_to_string('emails/nova_os.txt', context)
        
        # Enviar e-mail para o cliente (se tiver e-mail)
        if cliente.email:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cliente.email],
                fail_silently=True,
            )
            logger.info(f'E-mail de nova OS enviado para {cliente.email}')
        
        # Enviar notificação para responsáveis da oficina
        admin_emails = User.objects.filter(
            is_staff=True, email__isnull=False
        ).exclude(email='').values_list('email', flat=True)
        
        if admin_emails:
            send_mail(
                subject=f'Nova OS #{ordem_servico.numero_os} - {cliente.nome}',
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                fail_silently=True,
            )
            logger.info(f'E-mail de nova OS enviado para administradores')
            
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de nova OS: {str(e)}')


def enviar_notificacao_os_concluida(ordem_servico):
    """
    Envia notificação quando uma OS é concluída
    """
    try:
        cliente = ordem_servico.veiculo.cliente
        subject = f'Serviço Concluído - OS #{ordem_servico.numero_os}'
        
        context = {
            'ordem_servico': ordem_servico,
            'cliente': cliente,
            'veiculo': ordem_servico.veiculo,
        }
        
        # Render do template de e-mail
        html_message = render_to_string('emails/os_concluida.html', context)
        plain_message = render_to_string('emails/os_concluida.txt', context)
        
        # Enviar e-mail para o cliente
        if cliente.email:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cliente.email],
                fail_silently=True,
            )
            logger.info(f'E-mail de OS concluída enviado para {cliente.email}')
            
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de OS concluída: {str(e)}')


def enviar_notificacao_agendamento(agendamento):
    """
    Envia notificação de confirmação de agendamento
    """
    try:
        subject = f'Agendamento Confirmado - {agendamento.data_agendamento.strftime("%d/%m/%Y %H:%M")}'
        
        context = {
            'agendamento': agendamento,
            'cliente': agendamento.cliente,
            'veiculo': agendamento.veiculo,
        }
        
        # Render do template de e-mail
        html_message = render_to_string('emails/agendamento_confirmado.html', context)
        plain_message = render_to_string('emails/agendamento_confirmado.txt', context)
        
        # Enviar e-mail para o cliente
        if agendamento.cliente.email:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agendamento.cliente.email],
                fail_silently=True,
            )
            logger.info(f'E-mail de agendamento enviado para {agendamento.cliente.email}')
            
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de agendamento: {str(e)}')


# Task para lembrete de agendamentos (seria executado via Celery em produção)
def enviar_lembretes_agendamento():
    """
    Envia lembretes de agendamentos para o próximo dia
    """
    from datetime import timedelta
    
    amanha = timezone.now().date() + timedelta(days=1)
    agendamentos = Agendamento.objects.filter(
        data_agendamento__date=amanha,
        confirmado=True,
        compareceu=False
    )
    
    for agendamento in agendamentos:
        try:
            subject = f'Lembrete: Agendamento Amanhã - {agendamento.data_agendamento.strftime("%H:%M")}'
            
            context = {
                'agendamento': agendamento,
                'cliente': agendamento.cliente,
            }
            
            html_message = render_to_string('emails/lembrete_agendamento.html', context)
            plain_message = render_to_string('emails/lembrete_agendamento.txt', context)
            
            if agendamento.cliente.email:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[agendamento.cliente.email],
                    fail_silently=True,
                )
                logger.info(f'Lembrete de agendamento enviado para {agendamento.cliente.email}')
                
        except Exception as e:
            logger.error(f'Erro ao enviar lembrete de agendamento: {str(e)}')


# Task para backup automático (seria executado via Celery em produção)
def fazer_backup_automatico():
    """
    Realiza backup automático do banco de dados
    """
    try:
        from django.core.management import call_command
        import os
        from datetime import datetime
        
        # Criar diretório de backup se não existir
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.json'
        backup_path = backup_dir / backup_filename
        
        # Executar dumpdata
        with open(backup_path, 'w') as backup_file:
            call_command('dumpdata', 
                        exclude=['contenttypes', 'auth.permission', 'sessions'],
                        stdout=backup_file,
                        indent=2)
        
        logger.info(f'Backup criado com sucesso: {backup_filename}')
        
        # Remover backups antigos (manter apenas os últimos 30 dias)
        retention_days = getattr(settings, 'OFICINA_CONFIG', {}).get('BACKUP_RETENTION_DAYS', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for backup_file in backup_dir.glob('backup_*.json'):
            file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_date < cutoff_date:
                backup_file.unlink()
                logger.info(f'Backup antigo removido: {backup_file.name}')
                
    except Exception as e:
        logger.error(f'Erro ao fazer backup automático: {str(e)}')


# Função para verificar ordens com prazo vencido
def verificar_prazos_vencidos():
    """
    Verifica ordens com prazo vencido e envia notificações
    """
    from datetime import datetime
    
    ordens_vencidas = OrdemServico.objects.filter(
        prazo_entrega__lt=timezone.now(),
        status__in=[
            OrdemServico.Status.ABERTA,
            OrdemServico.Status.EM_EXECUCAO,
            OrdemServico.Status.AGUARDANDO_PECA
        ]
    )
    
    if ordens_vencidas.exists():
        logger.warning(f'{ordens_vencidas.count()} ordens de serviço com prazo vencido')
        
        # Enviar notificação para administradores
        admin_emails = User.objects.filter(
            is_staff=True, email__isnull=False
        ).exclude(email='').values_list('email', flat=True)
        
        if admin_emails:
            subject = f'Alerta: {ordens_vencidas.count()} OS com prazo vencido'
            
            context = {
                'ordens_vencidas': ordens_vencidas[:10],  # Limitar a 10 para o e-mail
                'total_vencidas': ordens_vencidas.count(),
            }
            
            try:
                html_message = render_to_string('emails/prazos_vencidos.html', context)
                plain_message = render_to_string('emails/prazos_vencidos.txt', context)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(admin_emails),
                    fail_silently=True,
                )
                logger.info('Notificação de prazos vencidos enviada para administradores')
                
            except Exception as e:
                logger.error(f'Erro ao enviar notificação de prazos vencidos: {str(e)}')
