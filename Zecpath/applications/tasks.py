from celery import shared_task
from .models import Application
from .engine import auto_shortlist_engine


@shared_task
def process_application(application_id):

    try:
        application = Application.objects.get(id=application_id)
        auto_shortlist_engine(application)
    except Application.DoesNotExist:
        pass