from django.contrib import admin

from audit.models import (
    ModelAuditLog
)


class ModelAuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'action',
        'user',
    ]


admin.site.register(ModelAuditLog, ModelAuditLogAdmin)
