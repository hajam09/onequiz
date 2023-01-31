from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.models import QuizAttempt, Topic


class QuizAttemptViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizAttemptViewTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 2)
        self.topic = Topic.objects.select_related('subject').first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.quiz.questions.add(*[
            bakerOperations.createEssayQuestion().question,
            bakerOperations.createTrueOrFalseQuestion().question
        ])

        self.quizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=self.quiz.id)
        self.path = reverse('quiz:quiz-attempt-view', kwargs={'attemptId': self.quizAttempt.id})

    def testCreateEssayQuestionViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quizAttemptView.html')
        self.assertTrue(isinstance(response.context['quizAttempt'], QuizAttempt))
        self.assertTrue(response.context['quizAttempt'], self.quizAttempt)
        self.assertEqual(response.context['mode'], QuizAttempt.Mode.EDIT)

    def testQuizAttemptDoesNotExist(self):
        path = reverse('quiz:quiz-attempt-view', kwargs={'attemptId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testQuizCreatorViewsQuizDuringInProgressThenReturnForbidden(self):
        self.quizAttempt.user = bakerOperations.createUser()
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 403)
        self.assertEqual(response.content, str.encode('Forbidden'))
        self.assertEqual(response.reason_phrase, 'Forbidden')

    def testQuizCreatorViewsQuizAfterSubmittedThenReturnOK(self):
        self.quizAttempt.user = bakerOperations.createUser()
        self.quizAttempt.status = QuizAttempt.Status.SUBMITTED
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 200)

    def testUnrelatedUserViewsQuizDuringInProgressThenReturnForbidden(self):
        anotherUser = bakerOperations.createUser()
        self.quizAttempt.user = anotherUser
        self.quizAttempt.quiz.creator = anotherUser
        self.quizAttempt.quiz.save()
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 403)
        self.assertEqual(response.content, str.encode('Forbidden'))
        self.assertEqual(response.reason_phrase, 'Forbidden')

    def testUnrelatedUserViewsQuizAfterSubmittedThenReturnForbidden(self):
        anotherUser = bakerOperations.createUser()
        self.quizAttempt.user = anotherUser
        self.quizAttempt.quiz.creator = anotherUser
        self.quizAttempt.status = QuizAttempt.Status.SUBMITTED
        self.quizAttempt.quiz.save()
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 403)
        self.assertEqual(response.content, str.encode('Forbidden'))
        self.assertEqual(response.reason_phrase, 'Forbidden')

    def testQuizAttemptedUserViewsQuizDuringInProgressThenReturnOK(self):
        anotherUser = bakerOperations.createUser()
        self.quizAttempt.quiz.creator = anotherUser
        self.quizAttempt.quiz.save()

        response = self.get()
        self.assertEquals(response.status_code, 200)

    def testQuizAttemptedUserViewsQuizAfterSubmittedThenReturnOK(self):
        anotherUser = bakerOperations.createUser()
        self.quizAttempt.quiz.creator = anotherUser
        self.quizAttempt.status = QuizAttempt.Status.SUBMITTED
        self.quizAttempt.quiz.save()
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 200)

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
        self.assertEqual(response.context['mode'], QuizAttempt.Mode.MARK)
