from django.db.models import QuerySet
from django.urls import reverse

from core.models import QuizAttempt, Subject
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class AttemptedQuizzesViewTest(BaseTestViews):

    def setUp(self, path=reverse('core:attempted-quizzes-view')) -> None:
        super(AttemptedQuizzesViewTest, self).setUp(path)
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.quizAttempts = [
            QuizAttempt(user=self.request.user, quiz_id=self.quiz.id)
            for _ in range(10)
        ]
        QuizAttempt.objects.bulk_create(self.quizAttempts)

    def testAttemptedQuizzesViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/attemptedQuizzesView.html')
        self.assertEqual(len(response.context['quizAttemptList']), 10)
        self.assertTrue(isinstance(response.context['quizAttemptList'], QuerySet))
