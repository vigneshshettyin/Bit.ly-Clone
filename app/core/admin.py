from django.contrib import admin
from .models import Link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'long_url', 'clicks', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('short_code', 'long_url')
    ordering = ['-created_at']


admin.site.register(Link, LinkAdmin)
