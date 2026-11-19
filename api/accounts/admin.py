from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class ClinicUserAdmin(UserAdmin):
    """Django's full user admin (passwords, permissions, groups) plus our role field."""
    list_display = ["username", "email", "role", "is_staff", "is_superuser"]
    list_filter = ["role", "is_staff", "is_superuser", "groups"]
    fieldsets = UserAdmin.fieldsets + (("Clinic", {"fields": ["role"]}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Clinic", {"fields": ["role"]}),)
