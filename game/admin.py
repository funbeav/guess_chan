from django.contrib import admin

from game.models import ChanImage


@admin.register(ChanImage)
class ChanImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'image', 'author',)

