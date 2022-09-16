from django.contrib import admin
from django.utils.html import format_html

from game.models import Chan, ChanAlternative, ChanImage


class ChanImageInline(admin.StackedInline):
    model = ChanImage
    fields = ['image_preview']
    readonly_fields = ('image_preview',)
    show_change_link = True
    can_delete = False
    max_num = 0

    def image_preview(self, instance):
        url = instance.image.url
        return format_html(f'<a href="{url}"><img src="{url}" width=200 high=200/></a>')

    image_preview.short_description = 'Preview'


class ChanAlternativeInline(admin.TabularInline):
    model = ChanAlternative
    fields = ['name', 'lang']
    extra = 1


@admin.register(Chan)
class ChanAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
    list_display = ('name',)
    inlines = [ChanAlternativeInline, ChanImageInline]


@admin.register(ChanImage)
class ChanImageAdmin(admin.ModelAdmin):
    list_display = ('hash', 'caption', 'chan', 'image_preview', 'author',)
    fields = ('image', 'chan', 'caption', 'author',)

    def image_preview(self, instance):
        url = instance.image.url
        return format_html(f'<a href="{url}"><img src="{url}" width=100 high=100/></a>')

    image_preview.short_description = 'Preview'


@admin.register(ChanAlternative)
class ChanAlternativeAdmin(admin.ModelAdmin):
    list_display = ('chan', 'name', 'lang',)
