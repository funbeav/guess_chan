from django.contrib import admin
from django.utils.html import format_html

from game.models import Chan, CharacterName, ChanImage, Character, CharacterImage


class ImagePreviewInline(admin.StackedInline):
    fields = ['image', 'caption', 'image_preview']
    readonly_fields = ('image_preview',)
    show_change_link = True
    can_delete = False
    extra = 1

    def image_preview(self, instance):
        url = instance.image.url
        return format_html(f'<a href="{url}"><img src="{url}" width=200 height=200/></a>')

    image_preview.short_description = 'Preview'


class ImageAdmin(admin.ModelAdmin):
    def image_preview(self, instance):
        url = instance.image.url
        return format_html(f'<a href="{url}"><img src="{url}" width=100 height=100/></a>')

    image_preview.short_description = 'Preview'


class ChanImageInline(ImagePreviewInline):
    model = ChanImage


@admin.register(Chan)
class ChanAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
    list_display = ('name', 'character',)
    inlines = [ChanImageInline]


@admin.register(ChanImage)
class ChanImageAdmin(ImageAdmin):
    list_display = ('hash', 'caption', 'chan', 'image_preview', 'author',)
    fields = ('image', 'chan', 'caption', 'author',)


class CharacterNameInline(admin.TabularInline):
    model = CharacterName
    fields = ['name', 'lang']
    extra = 1


class CharacterImageInline(ImagePreviewInline):
    model = CharacterImage


@admin.register(CharacterImage)
class CharacterImageAdmin(ImageAdmin):
    list_display = ('hash', 'caption', 'character', 'image_preview', 'author',)
    fields = ('image', 'character', 'caption', 'author',)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
    list_display = ('name',)
    inlines = [CharacterNameInline, CharacterImageInline]


@admin.register(CharacterName)
class CharacterNameAdmin(admin.ModelAdmin):
    list_display = ('character', 'name', 'lang',)
