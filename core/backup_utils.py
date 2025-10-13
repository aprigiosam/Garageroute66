import os
import shutil
from datetime import datetime
from django.conf import settings
from django.core.management.base import CommandError

def create_db_backup():
    """
    Cria um backup do banco de dados SQLite.
    Retorna o caminho do arquivo de backup em caso de sucesso, ou lança uma exceção em caso de erro.
    """
    db_path = settings.DATABASES['default']['NAME']

    if not os.path.isabs(db_path):
        db_path = os.path.join(settings.BASE_DIR, db_path)

    backup_dir = os.path.join(settings.BASE_DIR, 'backups')

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'db_backup_{timestamp}.sqlite3'
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        shutil.copy2(db_path, backup_path)
        return backup_path
    except Exception as e:
        raise CommandError(f'Erro ao criar o backup: {e}')
