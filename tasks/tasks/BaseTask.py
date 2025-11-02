import traceback
from datetime import timedelta

from django.utils import timezone

from tasks.models import Task


class BaseTask:
    def run(self, *args, **kwargs):
        """Override this method in subclasses."""
        raise NotImplementedError('Subclasses must implement run method')

    def execute(self, taskInstance):
        """Wrapper to update DB status and handle retries."""

        taskInstance.status = Task.Status.RUNNING
        taskInstance.tries += 1
        taskInstance.startedAt = timezone.now()
        taskInstance.save(update_fields=['status', 'tries', 'startedAt'])

        try:
            self.run(taskInstance.data)
            taskInstance.status = Task.Status.COMPLETED
            taskInstance.lastError = None

        except Exception:

            taskInstance.lastError = traceback.format_exc()

            if taskInstance.tries >= taskInstance.maxTries:
                taskInstance.status = Task.Status.FAILED
            else:
                taskInstance.status = Task.Status.PENDING
                taskInstance.scheduledAt = timezone.now() + timedelta(minutes=5)
        finally:
            taskInstance.finishedAt = timezone.now()
            taskInstance.save(update_fields=['status', 'tries', 'lastError', 'finishedAt'])
