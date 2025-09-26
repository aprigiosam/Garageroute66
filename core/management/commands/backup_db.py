import logging
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Realiza backup do banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Remove backups antigos apos criar o novo.',
        )
        parser.add_argument(
            '--retention-days',
            type=int,
            default=30,
            help='Numero de dias para manter os backups (padrao: 30).',
        )

    def handle(self, *args, **options):
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.json'
        backup_path = backup_dir / backup_filename

        self.stdout.write(f'Criando backup: {backup_filename}')

        try:
            with backup_path.open('w', encoding='utf-8') as backup_file:
                call_command(
                    'dumpdata',
                    exclude=['contenttypes', 'auth.permission', 'sessions', 'admin.logentry'],
                    stdout=backup_file,
                    indent=2,
                )
        except Exception as exc:
            message = f'Erro ao criar backup: {exc}'
            self.stderr.write(message)
            logger.error(message)
            if backup_path.exists():
                backup_path.unlink(missing_ok=True)
            return

        self.stdout.write(self.style.SUCCESS(f'Backup criado com sucesso: {backup_filename}'))
        logger.info('Backup criado: %s', backup_filename)

        if options['cleanup']:
            self.cleanup_old_backups(backup_dir, options['retention_days'])

    def cleanup_old_backups(self, backup_dir: Path, retention_days: int) -> None:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        removed = 0

        for backup_file in backup_dir.glob('backup_*.json'):
            file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_date < cutoff_date:
                backup_file.unlink()
                removed += 1
                logger.info('Backup antigo removido: %s', backup_file.name)

        if removed:
            self.stdout.write(self.style.SUCCESS(f'{removed} backup(s) antigos removidos.'))
        else:
            self.stdout.write('Nenhum backup antigo para remover.')
