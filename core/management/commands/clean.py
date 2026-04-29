from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from core.models import (
    Question,
    QuizAttempt,
    Quiz,
    Response,
    Result
)
from tasks.models import (
    Task
)


class Command(BaseCommand):
    help = 'Clean DB'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Starting database cleanup...")

        try:
            with transaction.atomic():
                users = User.objects.exclude(is_superuser=True)
                self.stdout.write(f"✅ Deleted {users.count()} non-superuser users.")

                for model in [Question, Response, Quiz, QuizAttempt, Result, Task]:
                    count = model.objects.count()
                    model.objects.all().delete()
                    self.stdout.write(f"✅ Deleted {count} {model.__name__} objects.")

        except Exception as e:
            self.stderr.write(f"💥 Error during cleanup: {e}")
        else:
            self.stdout.write("🎉 Database cleanup completed successfully.")
