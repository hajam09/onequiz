from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.models import QuizAttempt, Topic


class QuizAttemptViewTest(BaseTestViews):

    def setUp(self, path='') -> None:
        super(QuizAttemptViewTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 2)
        self.topic = Topic.objects.select_related('subject').first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.quiz.questions.add(*[
            bakerOperations.createEssayQuestion(),
            bakerOperations.createTrueOrFalseQuestion()
        ])

        self.quizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=self.quiz.id)
        self.path = reverse('quiz:quiz-attempt-view', kwargs={'attemptId': self.quizAttempt.id})

    def testCreateEssayQuestionViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quizAttemptView.html')
        self.assertTrue(isinstance(response.context['quizAttempt'], QuizAttempt))
        self.assertTrue(response.context['quizAttempt'], self.quizAttempt)

    def testQuizAttemptDoesNotExist(self):
        path = reverse('quiz:quiz-attempt-view', kwargs={'attemptId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testAttemptUserIsNotSameAsViewUser(self):
        anotherUser = bakerOperations.createUser()
        self.quizAttempt.user = anotherUser
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 401)
        self.assertEqual(response.content, str.encode('Unauthorized'))
        self.assertEqual(response.reason_phrase, 'Unauthorized')

    @patch('quiz.views.QuizAttempt.getQuizEndTime')
    def testUpdateStatusWhenDurationEndedAndNotSubmitted(self, mockGetQuizEndTime):
        mockGetQuizEndTime.return_value = timezone.now()
        self.assertEqual(QuizAttempt.Status.NOT_ATTEMPTED, self.quizAttempt.status)

        response = self.get()
        self.quizAttempt.refresh_from_db()

        self.assertEqual(QuizAttempt.Status.SUBMITTED, self.quizAttempt.status)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quizAttemptView.html')
        self.assertTrue(isinstance(response.context['quizAttempt'], QuizAttempt))
        self.assertTrue(response.context['quizAttempt'], self.quizAttempt)
