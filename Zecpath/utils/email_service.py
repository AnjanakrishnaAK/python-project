from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from notifications.models import EmailDeliveryLog
import logging
logger = logging.getLogger(__name__)

def send_email(template, subject, to_email, context):
    try:
        html_content = render_to_string(template, context)
        email = EmailMultiAlternatives(
            subject,
            "",
            "no-reply@zecpath.com",
            [to_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")

def send_application_email(user, job):

    subject = "Application Submitted"
    context = {
        "candidate_name": user.first_name,
        "job_title": job.title
    }
    try:
        html_content = render_to_string(
            "emails/application_submitted.html",
            context
        )
        email = EmailMultiAlternatives(
            subject,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
# DELIVERY LOG (SUCCESS)
        EmailDeliveryLog.objects.create(
            user=user,
            email=user.email,
            subject=subject,
            status="sent"
        )
    except Exception as e:
# DELIVERY LOG (FAILURE)
        EmailDeliveryLog.objects.create(
            user=user,
            email=user.email,
            subject=subject,
            status="failed",
            error_message=str(e)
        )



def send_shortlisted_email(user, job):

    subject = "You Have Been Shortlisted"

    context = {
        "candidate_name": user.first_name,
        "job_title": job.title
    }

    html_content = render_to_string(
        "emails/shortlisted.html",
        context
    )

    email = EmailMultiAlternatives(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()



def send_rejection_email(user, job):

    subject = "Application Status Update"

    context = {
        "candidate_name": user.first_name,
        "job_title": job.title
    }

    html_content = render_to_string(
        "emails/rejected.html",
        context
    )

    email = EmailMultiAlternatives(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()