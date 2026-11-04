from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel


class UserNotificationSettings(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notificationSettings')
    emailOnQuizAttemptSubmitted = models.BooleanField(default=True)
    emailOnQuizMarked = models.BooleanField(default=True)
    emailOnPasswordChanged = models.BooleanField(default=True)
    emailOnAccountSecurityUpdate = models.BooleanField(default=True)
    emailOnProductUpdates = models.BooleanField(default=False)
