from django.contrib import admin

from project.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'email', 'is_active',)
