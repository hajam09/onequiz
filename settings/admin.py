from django.contrib import admin

from settings.models import (
    UserNotificationSettings
)


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    pass
