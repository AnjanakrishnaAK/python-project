from notifications.tasks import (
    send_application_submitted_email
)


def notify_application_submitted(application):

    send_application_submitted_email.delay(application.id)


def notify_shortlisted(application):

    from notifications.tasks import send_shortlisted_email
    send_shortlisted_email.delay(application.id)


def notify_rejected(application):

    from notifications.tasks import send_rejected_email
    send_rejected_email.delay(application.id)