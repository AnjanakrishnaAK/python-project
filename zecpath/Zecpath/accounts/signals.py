from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, CandidateProfile, EmployerProfile
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == "CANDIDATE":
        CandidateProfile.objects.get_or_create(user=instance)

    elif instance.role == "EMPLOYER":
        EmployerProfile.objects.get_or_create(
            user=instance,
            defaults={"company_name": ""}
        )