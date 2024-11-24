from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from core.models import QuizAttempt, Subject
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizAttemptViewVersion1Test(BaseTestViews):
    # test update

    def setUp(self, path=None) -> None:
        super(QuizAttemptViewVersion1Test, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.quiz.questions.add(*bakerOperations.createRandomQuestions(2))

        self.quizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=self.quiz.id)
        self.path = reverse('core:quiz-attempt-view-v1', kwargs={'url': self.quizAttempt.url})

    def testCreateEssayQuestionViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quizAttemptViewVersion1.html')
        self.assertTrue(isinstance(response.context['quizAttempt'], QuizAttempt))
        self.assertTrue(response.context['quizAttempt'], self.quizAttempt)
        self.assertEqual(response.context['mode'], QuizAttempt.Mode.EDIT)

    def testQuizAttemptDoesNotExist(self):
        path = reverse('core:quiz-attempt-view-v1', kwargs={'url': 'non-existing-url'})
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

    @patch('core.views.QuizAttempt.getQuizEndTime')
    def testUpdateStatusWhenDurationEndedAndNotSubmitted(self, mockGetQuizEndTime):
        mockGetQuizEndTime.return_value = timezone.now()
        self.assertEqual(QuizAttempt.Status.NOT_ATTEMPTED, self.quizAttempt.status)

        response = self.get()
        self.quizAttempt.refresh_from_db()

        self.assertEqual(QuizAttempt.Status.SUBMITTED, self.quizAttempt.status)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quizAttemptViewVersion1.html')
        self.assertTrue(isinstance(response.context['quizAttempt'], QuizAttempt))
        self.assertTrue(response.context['quizAttempt'], self.quizAttempt)
        self.assertEqual(response.context['mode'], QuizAttempt.Mode.MARK)
