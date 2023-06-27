from django.contrib import admin

from project.models import Lang, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'email', 'lang', 'is_active', 'energy',)


@admin.register(Lang)
class LangAdmin(admin.ModelAdmin):
    list_display = ('name', 'alpha2',)
