import hashlib
from django.db import transaction
from django.db.models import Max
from .models import Resume


def calculate_file_hash(file):
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()


@transaction.atomic
def upload_or_replace_resume(profile, file):
    file_hash = calculate_file_hash(file)

    last_version = (
        Resume.objects
        .filter(candidate=profile)
        .aggregate(max_version=Max('version'))
        ['max_version'] or 0
    )

    Resume.objects.filter(
        candidate=profile,
        is_active=True
    ).update(is_active=False)


    resume = Resume.objects.create(
        candidate=profile,
        file=file,
        file_hash=file_hash,
        version=last_version + 1,
        is_active=True
    )

   
    profile.current_resume = resume
    profile.save(update_fields=['current_resume'])

    return resume