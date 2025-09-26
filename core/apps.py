from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Sistema da Oficina'

    def ready(self):
        # Importar sinais quando a aplicação estiver pronta
        try:
            import core.signals
        except ImportError:
            pass