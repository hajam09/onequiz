import json

from django.core.cache import cache
from django.urls import reverse

from core.models import QuizAttempt, Response, Quiz
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax


class QuizAttemptCommenceApiVersion1Test(BaseTestAjax):
    def setUp(self, path=reverse('core:quizAttemptCommenceApiVersion1')) -> None:
        super(QuizAttemptCommenceApiVersion1Test, self).setUp(path)
        self.quiz = bakerOperations.createQuiz(self.user)
        self.quiz.isDraft = False
        self.quiz.save()

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
        self.quiz.save()
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
        questions = bakerOperations.createRandomQuestions(self.quiz, 2, True)
        response = self.post({'quizId': self.quiz.id})
        apiResponse = json.loads(response.content)
        quizAttempt = QuizAttempt.objects.filter(quiz=self.quiz, user=self.user, status=QuizAttempt.Status.IN_PROGRESS)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(apiResponse['success'])
        self.assertIsNotNone(apiResponse['redirectUrl'])
        self.assertEqual(apiResponse['redirectUrl'], f'/v1/quiz-attempt/{quizAttempt.first().url}/')

        responseList = list(Response.objects.filter(quizAttempt=quizAttempt.first()).values_list('url', flat=True))
        self.assertEqual(quizAttempt.count(), 1)
        self.assertEqual(len(responseList), len([question.url for question in questions]))

        cacheList = cache.get(f'quiz-attempt-v1-{quizAttempt.first().url}')
        for item in responseList:
            self.assertIn(item, cacheList)

    def testRandomOrderShufflingOfResponses(self):
        self.quiz.inRandomOrder = True
        self.quiz.save()
        bakerOperations.createRandomQuestions(self.quiz, 5, True)

        self.post({'quizId': self.quiz.id})
        quizAttempt = QuizAttempt.objects.get(quiz=self.quiz, user=self.user, status=QuizAttempt.Status.IN_PROGRESS)
        responses = Response.objects.filter(quizAttempt=quizAttempt)
        cachedUrls = cache.get(f'quiz-attempt-v1-{quizAttempt.url}')

        actualUrls = [response.url for response in responses]
        self.assertCountEqual(actualUrls, cachedUrls)
        self.assertNotEqual(actualUrls, cachedUrls)

    def testWhenExceptionOccurredDuringAtomicEnsureNoObjectsAreCreated(self):
        pass

    def testWhenQuizIdIsMissingThenRaiseDoesNotExistException(self):
        with self.assertRaises(Quiz.DoesNotExist):
            self.post({})

    def testWhenInvalidQuizIdThenReturnNotFound(self):
        with self.assertRaises(Quiz.DoesNotExist):
            self.post({'quizId': 999999})
