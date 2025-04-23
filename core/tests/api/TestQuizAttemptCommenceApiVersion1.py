import json

from django.core.cache import cache
from django.urls import reverse

from core.models import QuizAttempt, Response
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax


class QuizAttemptCommenceApiVersion1Test(BaseTestAjax):
    def setUp(self, path=reverse('core:quizAttemptCommenceApiVersion1')) -> None:
        super(QuizAttemptCommenceApiVersion1Test, self).setUp(path)
        self.quiz = bakerOperations.createQuiz(self.user)

    def testWhenAQuizAttemptIsInProgressThenRedirectToAttemptView(self):
        quizAttempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status=QuizAttempt.Status.IN_PROGRESS
        )
        response = self.post({'quizId': self.quiz.id})
        apiResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(apiResponse['success'])
        self.assertIsNotNone(apiResponse['redirectUrl'])
        self.assertEqual(apiResponse['redirectUrl'], f'/v1/quiz-attempt/{quizAttempt.url}/')

    def testWhenMaxQuizAttemptHasBeenReachedThenReturnMessage(self):
        self.quiz.maxAttempt = 1
        self.quiz.save(update_fields=['maxAttempt'])
        QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status=QuizAttempt.Status.SUBMITTED
        )
        response = self.post({'quizId': self.quiz.id})
        apiResponse = json.loads(response.content)
        messages = self.getMessages(response)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(apiResponse['success'])
        self.assertIsNotNone(apiResponse['message'])
        self.assertEqual(apiResponse['message'], 'Maximum attempts reached for this quiz.')

        for message in messages:
            self.assertEqual(
                str(message),
                'Maximum attempts reached for this quiz.'
            )

    def testCreateQuizAttemptAndResponses(self):
        bakerOperations.createRandomQuestions(self.quiz, 2, True)
        response = self.post({'quizId': self.quiz.id})
        apiResponse = json.loads(response.content)
        quizAttempt = QuizAttempt.objects.filter(quiz=self.quiz, user=self.user, status=QuizAttempt.Status.IN_PROGRESS)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(apiResponse['success'])
        self.assertIsNotNone(apiResponse['redirectUrl'])
        self.assertEqual(apiResponse['redirectUrl'], f'/v1/quiz-attempt/{quizAttempt.first().url}/')

        responses = Response.objects.filter(quizAttempt=quizAttempt.first())
        self.assertEqual(quizAttempt.count(), 1)
        self.assertEqual(responses.count(), 2)
        self.assertListEqual(
            [response.url for response in responses],
            cache.get(f'quiz-attempt-v1-{quizAttempt.first().url}')
        )
