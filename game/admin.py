from django.contrib import admin

from game.models import Chan, ChanAlternative, ChanImage


class ChanImageInline(admin.TabularInline):
    model = ChanImage
    fields = ['id', 'caption', 'image']
    extra = 1


@admin.register(Chan)
class ChanAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ChanImageInline]


@admin.register(ChanImage)
class ChanImageAdmin(admin.ModelAdmin):
    list_display = ('hash', 'caption', 'chan', 'image', 'author',)
    fields = ('image', 'chan', 'caption', 'author',)


@admin.register(ChanAlternative)
class ChanAlternativeAdmin(admin.ModelAdmin):
    list_display = ('chan', 'name', 'lang',)
