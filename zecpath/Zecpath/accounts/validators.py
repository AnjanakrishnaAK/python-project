from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


def validate_resume(file):
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Only PDF, DOC, DOCX files are allowed")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Invalid resume file type")

    if file.size > MAX_FILE_SIZE:
        raise ValidationError("Resume must be under 2MB")