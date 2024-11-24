from django.core.management import BaseCommand

from core.models import *

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Clean DB'

    def handle(self, *args, **kwargs):
        User.objects.exclude(is_superuser=True).delete()
        Subject.objects.all().delete()
        Question.objects.all().delete()
        Response.objects.all().delete()
        Quiz.objects.all().delete()
        QuizAttempt.objects.all().delete()
        Result.objects.all().delete()
