from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=300)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


