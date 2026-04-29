import importlib
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tasks.models import Task

CHECK_INTERVAL = 10  # seconds between loops
BATCH_SIZE = 10  # number of tasks to process per batch
MAX_WORKERS = 5  # number of threads for parallel execution


class Command(BaseCommand):
    help = "⚙️ Runs background tasks continuously (multi-threaded worker)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run one iteration and exit (for cron/testing).",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Task Worker Started (multi-threaded mode)!"))
        self.stdout.write(self.style.NOTICE(f"⚙️  Using {MAX_WORKERS} threads, batch size {BATCH_SIZE}\n"))

        runOnce = options["once"]

        while True:
            try:
                nowStr = timezone.now().strftime("%H:%M:%S")
                self.stdout.write(f"🕒 [{nowStr}] Fetching up to {BATCH_SIZE} pending tasks...")

                # Get a limited batch of pending tasks
                tasksBatch = list(
                    Task.objects.filter(
                        scheduledAt__lte=timezone.now(),
                        status=Task.Status.PENDING,
                    )
                    .order_by("priority", "scheduledAt")[:BATCH_SIZE]
                )

                taskCount = len(tasksBatch)

                if taskCount == 0:
                    self.stdout.write("💤 No tasks available right now.\n")
                else:
                    self.stdout.write(f"📋 {taskCount} task(s) fetched.")
                    startBatchTime = timezone.now()

                    # Run in parallel threads
                    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                        futures = {executor.submit(self._executeTask, t): t for t in tasksBatch}

                        completed = 0
                        for future in as_completed(futures):
                            task = futures[future]
                            try:
                                result = future.result()
                                if result:
                                    completed += 1
                            except Exception as e:
                                self.stderr.write(
                                    self.style.ERROR(f"🔥 Error in thread for task {task.id}: {e}")
                                )

                    endBatchTime = timezone.now()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Completed {completed}/{taskCount} tasks in "
                            f"{(endBatchTime - startBatchTime).total_seconds():.2f}s at "
                            f"{endBatchTime.strftime('%H:%M:%S')}\n"
                        )
                    )

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"💥 Worker loop error: {e}"))
                self.stderr.write(traceback.format_exc())

            if runOnce:
                break

            self.stdout.write(self.style.NOTICE(f"🔁 Sleeping for {CHECK_INTERVAL}s...\n"))
            time.sleep(CHECK_INTERVAL)

    def _executeTask(self, task):
        """Safely execute one task."""
        taskStart = timezone.now().strftime("%H:%M:%S")
        self.stdout.write(self.style.NOTICE(f"🚧 [{taskStart}] Executing: {task.name} (id={task.id})"))

        try:
            with transaction.atomic():
                # Lock this task row to avoid double-execution
                task = Task.objects.select_for_update().get(pk=task.pk)
                if task.status != Task.Status.PENDING:
                    self.stdout.write(f"⚠️ Skipping task {task.id} (status={task.status})")
                    return False

                module = importlib.import_module(f"tasks.tasks.{task.name}")
                clazz = getattr(module, task.name)
                instance = clazz()
                instance.execute(task)

            endTime = timezone.now().strftime("%H:%M:%S")
            self.stdout.write(self.style.SUCCESS(f"🎉 [{endTime}] Done: {task.name} (id={task.id})"))
            return True

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"🔥 Error executing {task.name} (id={task.id}): {e}")
            )
            self.stderr.write(traceback.format_exc())
            return False
