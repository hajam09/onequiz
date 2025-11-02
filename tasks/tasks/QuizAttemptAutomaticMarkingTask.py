from django.shortcuts import get_object_or_404

from core.models import QuizAttempt
from onequiz.operations.generalOperations import QuizAttemptAutomaticMarking
from tasks.tasks.BaseTask import BaseTask


class QuizAttemptAutomaticMarkingTask(BaseTask):

    def run(self, *args, **kwargs):
        quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('quiz', 'user'), url=args[0].get('url'))
        responses = quizAttempt.responses.select_related('question').all()

        quizAttemptAutomaticMarking = QuizAttemptAutomaticMarking(quizAttempt, responses)
        marked = quizAttemptAutomaticMarking.mark()

        if marked:
            quizAttempt.status = QuizAttempt.Status.MARKED
            quizAttempt.save(update_fields=['status'])
