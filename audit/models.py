from django.contrib.auth.models import User
from django.db import models


class ModelAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('DELETED', 'Deleted'),
    ]

    model_name = models.CharField(max_length=255)
    instance_id = models.PositiveBigIntegerField(blank=True, null=True)
    action = models.CharField(max_length=8, choices=ACTION_CHOICES)
    fields_changed = models.JSONField(null=True, blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.model_name} - {self.action} - {self.timestamp}'
