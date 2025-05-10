import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sxodimsdu.settings')

app = Celery('sxodimsdu')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Add this to make the app more easily discoverable