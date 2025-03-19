from django.core.management import BaseCommand

from core.models import *

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Clean DB'

    def handle(self, *args, **kwargs):
        Question.objects.all().delete()
