import random
from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from parameterized import parameterized

from core.forms import (
    EssayQuestionResponseForm,
    TrueOrFalseQuestionResponseForm,
    MultipleChoiceQuestionResponseForm
)
from core.models import (
    Question,
    Response
)
from core.models import QuizAttempt
from onequiz.operations import bakerOperations
from onequiz.settings import TEST_PASSWORD
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizAttemptViewVersion1Test(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizAttemptViewVersion1Test, self).setUp('')
        self.user2 = bakerOperations.createUser()
        self.quiz = bakerOperations.createQuiz(self.user2)
        self.quiz.inRandomOrder = False
        self.quiz.save()

        self.quizAttempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.request.user,
            status=QuizAttempt.Status.IN_PROGRESS
        )

        self.questions = [
            bakerOperations.createEssayQuestion(self.quiz),
            bakerOperations.createEssayQuestion(self.quiz),
            bakerOperations.createTrueOrFalseQuestion(self.quiz),
            bakerOperations.createTrueOrFalseQuestion(self.quiz),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(self.quiz),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(self.quiz)
        ]

        self.responses = [
            Response(question=question, quizAttempt=self.quizAttempt) for question in self.questions
        ]
        Response.objects.bulk_create(self.responses)
        self.path = reverse('core:quiz-attempt-view-v1', kwargs={'url': self.quizAttempt.url})

    def testUpdateQuizStatusPastEnding(self):
        self.quizAttempt.createdAt = self.quizAttempt.createdAt - timedelta(days=7)
        self.quizAttempt.save()
        self.get()
        self.quizAttempt.refresh_from_db()
        self.assertEqual(QuizAttempt.Status.SUBMITTED, self.quizAttempt.status)

    def testUnrelatedUserViewsQuizAttemptThenReturnForbidden(self):
        user = bakerOperations.createUser()
        self.client.login(username=user.username, password=TEST_PASSWORD)

        response = self.get()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, str.encode('Forbidden'))

    def testSetQuizAttemptResponseUrlsToCache(self):
        self.assertIsNone(cache.get(f'quiz-attempt-v1-{self.quizAttempt.url}'))
        self.get()
        self.assertCountEqual([r.url for r in self.responses], cache.get(f'quiz-attempt-v1-{self.quizAttempt.url}'))

    def testCurrentUrlNotInResponseUrlsCache(self):
        cache.set(f'quiz-attempt-v1-{self.quizAttempt.url}', [r.url for r in self.responses])

        response = self.get()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/v1/quiz-attempt/{self.quizAttempt.url}/?r={self.responses[0].url}')

    def testSubmitEssayResponseAndViewNextQuestion(self):
        data = {
            'answer': 'essay-response-answer',
            'submitResponse': 'next',
        }

        response = self.post(data=data, path=f'{self.path}?r={self.responses[0].url}')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'/v1/quiz-attempt/{self.quizAttempt.url}/?r={self.responses[1].url}')

        responseObject = self.responses[0]
        responseObject.refresh_from_db()
        self.assertEqual(responseObject.answer, 'essay-response-answer')

    def testSubmitTrueOrFalseResponseAndViewNextQuestion(self):
        data = {
            'trueOrFalse': Question.TrueOrFalse.FALSE,
            'submitResponse': 'next',
        }

        response = self.post(data=data, path=f'{self.path}?r={self.responses[2].url}')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'/v1/quiz-attempt/{self.quizAttempt.url}/?r={self.responses[3].url}')

        responseObject = self.responses[2]
        responseObject.refresh_from_db()
        self.assertEqual(responseObject.trueOrFalse, Question.TrueOrFalse.FALSE)

    def testSubmitFinalQuestionAndRedirectToQuizAttemptSubmissionPreview(self):
        data = {
            'submitResponse': 'next',
        }

        response = self.post(data=data, path=f'{self.path}?r={self.responses[5].url}')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'/quiz-attempt/{self.quizAttempt.url}/preview/')

    def testSubmitMCQAndViewPreviousQuestion(self):
        data = {
            'options': [c.get('id') for c in random.sample(self.responses[5].choices, 2)],
            'submitResponse': 'previous',
        }

        response = self.post(data=data, path=f'{self.path}?r={self.responses[5].url}')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'/v1/quiz-attempt/{self.quizAttempt.url}/?r={self.responses[4].url}')

        responseObject = self.responses[5]
        responseObject.refresh_from_db()
        self.assertCountEqual(data['options'], [c.get('id') for c in responseObject.choices if c.get('isChecked')])

    @parameterized.expand([
        [EssayQuestionResponseForm, 1],
        [TrueOrFalseQuestionResponseForm, 3],
        [MultipleChoiceQuestionResponseForm, 5],
    ])
    def testCreateEssayQuestionViewGet(self, form, index):
        response = self.get(path=f'{self.path}?r={self.responses[index].url}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quizAttemptViewVersion1.html')

        self.assertEqual(self.quizAttempt, response.context['quizAttempt'])
        self.assertListEqual([r.url for r in self.responses], response.context['responseUrls'])
        self.assertIsInstance(response.context['form'], form)
        self.assertTrue(response.context['has_previous'])
        self.assertEqual(index + 1, response.context['progress']['current'])
        self.assertEqual(6, response.context['progress']['total'])
        self.assertEqual(round(((index + 1) / 6) * 100, 0), response.context['progress']['percentage'])

    def testQuizAttemptDoesNotExist(self):
        path = reverse('core:quiz-attempt-view-v1', kwargs={'url': 'non-existing-url'})
        response = self.get(path=path)
        self.assertEqual(response.status_code, 404)

    def testQuizCreatorViewsAttemptAfterSubmittedThenViewPreviewPage(self):
        self.client.login(username=self.user2.username, password=TEST_PASSWORD)
        self.quizAttempt.status = QuizAttempt.Status.SUBMITTED
        self.quizAttempt.save()

        response = self.get()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/quiz-attempt/{self.quizAttempt.url}/preview/')

    @patch('core.views.QuizAttempt.getQuizEndTime')
    def testUpdateStatusWhenDurationEndedAndNotSubmitted(self, mockGetQuizEndTime):
        mockGetQuizEndTime.return_value = timezone.now()
        self.assertEqual(QuizAttempt.Status.IN_PROGRESS, self.quizAttempt.status)
        self.get()
        self.quizAttempt.refresh_from_db()
        self.assertEqual(QuizAttempt.Status.SUBMITTED, self.quizAttempt.status)
