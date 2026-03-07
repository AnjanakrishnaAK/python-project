from celery import shared_task
from utils.email_service import send_email
from applications.models import Application


@shared_task(bind=True, max_retries=3)
def send_application_submitted_email(self, application_id):

    try:

        application = Application.objects.get(id=application_id)

        context = {
            "candidate_name": application.candidate.first_name,
            "job_title": application.job.title,
            "company": application.job.company.name
        }

        send_email(
            "emails/application_submitted.html",
            "Application Submitted",
            application.candidate.email,
            context
        )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)