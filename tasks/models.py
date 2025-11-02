from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Task(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        RUNNING = 'RUNNING', _('Running')
        FAILED = 'FAILED', _('Failed')
        COMPLETED = 'COMPLETED', _('Completed')

    name = models.CharField(max_length=255)
    data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    tries = models.PositiveSmallIntegerField(default=0)
    maxTries = models.PositiveSmallIntegerField(default=3)
    priority = models.PositiveSmallIntegerField(default=0)

    scheduledAt = models.DateTimeField(default=timezone.now)
    startedAt = models.DateTimeField(null=True, blank=True)
    finishedAt = models.DateTimeField(null=True, blank=True)
    lastError = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'scheduledAt'], name='idx-task-status-scheduledAt'),
            models.Index(fields=['scheduledAt'], name='idx-quiz-scheduledAt'),
        ]
