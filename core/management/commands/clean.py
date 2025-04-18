from django.contrib.auth.models import User
from django.core.management import BaseCommand

from core.models import (
    Question,
    QuizAttempt,
    Quiz,
    Response,
    Result
)

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Clean DB'

    def handle(self, *args, **kwargs):
        User.objects.exclude(is_superuser=True).delete()
        Question.objects.all().delete()
        Response.objects.all().delete()
        Quiz.objects.all().delete()
        QuizAttempt.objects.all().delete()
        Result.objects.all().delete()
