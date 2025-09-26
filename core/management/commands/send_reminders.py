from django.core.management.base import BaseCommand

from core.signals import enviar_lembretes_agendamento


class Command(BaseCommand):
    help = 'Envia lembretes dos agendamentos do dia seguinte.'

    def handle(self, *args, **options):
        self.stdout.write('Enviando lembretes de agendamento...')
        enviar_lembretes_agendamento()
        self.stdout.write(self.style.SUCCESS('Lembretes enviados.'))
