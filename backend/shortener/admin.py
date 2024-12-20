from django.contrib import admin

from .models import LinkKey


@admin.register(LinkKey)
class LinkKeyAdmin(admin.ModelAdmin):
    pass