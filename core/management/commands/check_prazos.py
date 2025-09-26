from django.core.management.base import BaseCommand

from core.signals import verificar_prazos_vencidos


class Command(BaseCommand):
    help = 'Verifica ordens de servico com prazo vencido.'

    def handle(self, *args, **options):
        self.stdout.write('Verificando prazos vencidos...')
        verificar_prazos_vencidos()
        self.stdout.write(self.style.SUCCESS('Verificacao concluida.'))
