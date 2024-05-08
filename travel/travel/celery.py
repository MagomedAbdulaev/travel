from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel.settings')

app = Celery('travel', broker='redis://127.0.0.1:6379/0')
app.conf.enable_utc = False
app.conf.update(timezone='Europe/Moscow')
app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request, {self.request!r}')

from celery.schedules import crontab

app.conf.beat_schedule = {
    'run-every-5-minutes': {
        'task': 'travel_site.tasks.clear_cart',
        'schedule': 300.0,  # 5 минут
    },
}



