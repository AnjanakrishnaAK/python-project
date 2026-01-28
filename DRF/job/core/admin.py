from django.contrib import admin

# Register your models here.
from .models import Job, User


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'posted_at')
    search_fields = ('title',)
    list_filter = ('posted_at',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)