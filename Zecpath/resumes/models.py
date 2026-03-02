from django.db import models

# Create your models here.

from django.conf import settings

User = settings.AUTH_USER_MODEL


class Resume(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    file = models.FileField(upload_to="resumes/")

    extracted_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Resume {self.id}"