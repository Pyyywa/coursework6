from django.contrib import admin

from mail.models import MailSettings


@admin.register(MailSettings)
class MailSettingsAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "message")
    list_filter = ("status",)
    search_fields = ("period",)
