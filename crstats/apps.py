from django.apps import AppConfig
from django.db import connections
from .updater import start_background_updater

class CrstatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crstats'
    updater_started = False

    def ready(self):
        if not CrstatsConfig.updater_started:
            CrstatsConfig.updater_started = True
            start_background_updater()
            connections.close_all()
