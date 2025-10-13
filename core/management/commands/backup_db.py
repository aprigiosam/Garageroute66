from django.core.management.base import BaseCommand, CommandError
from core.backup_utils import create_db_backup

class Command(BaseCommand):
    help = 'Cria um backup do banco de dados SQLite.'

    def handle(self, *args, **options):
        try:
            backup_path = create_db_backup()
            self.stdout.write(self.style.SUCCESS(f'Backup do banco de dados criado com sucesso em: {backup_path}'))
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f'Erro ao criar o backup: {e}'))
