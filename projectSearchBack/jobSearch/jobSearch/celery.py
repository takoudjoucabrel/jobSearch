import os
from celery import Celery

# Indique à Celery quel fichier settings utiliser
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobSearch.settings")

app = Celery("jobSearch")

# Charge la configuration depuis settings.py (clés préfixées CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Découvre automatiquement les tâches dans tous les INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
