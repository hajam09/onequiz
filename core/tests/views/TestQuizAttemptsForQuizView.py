from django.db.models import QuerySet
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from core.models import QuizAttempt, Subject


class QuizAttemptsForQuizViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizAttemptsForQuizViewTest, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.quiz.questions.add(*bakerOperations.createRandomQuestions(2))

        self.quizAttemptList = QuizAttempt.objects.bulk_create(
            [
                QuizAttempt(user=self.request.user, quiz_id=self.quiz.id),
                QuizAttempt(user=self.request.user, quiz_id=self.quiz.id),
            ]
        )

        self.path = reverse('core:quiz-attempts-for-quiz-view', kwargs={'quizId': self.quiz.id})

    def testQuizAttemptsForQuizViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quizAttemptsForQuizView.html')
        self.assertTrue(isinstance(response.context['quizAttemptList'], QuerySet))
        self.assertTrue(isinstance(response.context['quizId'], int))
        self.assertListEqual(list(response.context['quizAttemptList']), self.quizAttemptList)
        self.assertEqual(response.context['quizId'], self.quiz.id)
        self.assertEqual(len(response.context), 2)
