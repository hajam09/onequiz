from django.db.models import QuerySet
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.models import QuizAttempt, Topic


class QuizAttemptsForQuizViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizAttemptsForQuizViewTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 2)
        self.topic = Topic.objects.select_related('subject').first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.quiz.questions.add(*[
            bakerOperations.createEssayQuestion().question,
            bakerOperations.createTrueOrFalseQuestion().question
        ])
        self.quizAttemptList = QuizAttempt.objects.bulk_create(
            [
                QuizAttempt(user=self.request.user, quiz_id=self.quiz.id),
                QuizAttempt(user=self.request.user, quiz_id=self.quiz.id),
            ]
        )

        self.path = reverse('quiz:quiz-attempts-for-quiz-view', kwargs={'quizId': self.quiz.id})

    def testQuizAttemptsForQuizViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quizAttemptsForQuizView.html')
        self.assertTrue(isinstance(response.context['quizAttemptList'], QuerySet))
        self.assertTrue(isinstance(response.context['quizId'], int))
        self.assertListEqual(list(response.context['quizAttemptList']), self.quizAttemptList)
        self.assertEqual(response.context['quizId'], self.quiz.id)
        self.assertEqual(len(response.context), 2)
