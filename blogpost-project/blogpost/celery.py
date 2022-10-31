import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogpost.settings")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'week-report': {
        'task': 'diary.tasks.send_week_report',
        'schedule': crontab(hour=9, minute=40, day_of_week=1),
    },
}

