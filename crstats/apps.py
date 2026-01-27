from django.apps import AppConfig

class CrstatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crstats'

    def ready(self):
        from .updater import start_background_updater
        start_background_updater()
