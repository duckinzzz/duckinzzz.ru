from celery import shared_task
from .updater import update_database

@shared_task
def update_battles_task():
    try:
        update_database()
    except Exception as e:
        print(f"Ошибка обновления: {e}")
