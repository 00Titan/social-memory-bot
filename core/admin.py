from django.contrib import admin
from django.utils.html import format_html
from .models import Person

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('photo_tag', 'first_name', 'last_name', 'created_at')
    search_fields = ('first_name', 'last_name', 'description', 'facts')
    list_filter = ('created_at',)
    readonly_fields = ('photo_tag',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:6px;" />', obj.photo.url)
        return '-'
    photo_tag.short_description = 'Фото'
