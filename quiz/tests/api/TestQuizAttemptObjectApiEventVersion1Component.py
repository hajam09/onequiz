import json

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic, QuizAttempt, Quiz


class QuizAttemptObjectApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path=None) -> None:
        super(QuizAttemptObjectApiEventVersion1ComponentTest, self).setUp(path)
        bakerOperations.createSubjectsAndTopics(1, 1)
        self.topic = Topic.objects.select_related('subject').first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.quiz.questions.add(*[
            bakerOperations.createEssayQuestion(),
            bakerOperations.createEssayQuestion(),
            bakerOperations.createEssayQuestion(),
            bakerOperations.createTrueOrFalseQuestion(),
            bakerOperations.createTrueOrFalseQuestion(),
            bakerOperations.createTrueOrFalseQuestion(),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(None),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(None),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(None),
        ])
        self.path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'

    def createQuizAttemptAndTheResponseObjects(self):
        response = self.post()
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        return ajaxResponse['redirectUrl'].split('/')[2]

    def testWhenAnotherAttemptIsInProgressThenReturnItsRedirectUrl(self):
        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        response = self.post()
        ajaxResponse = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(ajaxResponse['message'], 'You already have an attempt that is in progress.')

        self.assertIsNotNone(ajaxResponse['redirectUrl'])
        self.assertEqual(ajaxResponse['redirectUrl'], f'/quiz-attempt/{quizAttemptId}/')

    def testStartQuizAttemptForNonExistingQuiz(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId=0'
        with self.assertRaises(Quiz.DoesNotExist):
            response = self.post(path=path)

    def testStartQuizAttemptSuccessfully(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['redirectUrl'])

        quizAttemptId = ajaxResponse['redirectUrl'].split('/')[2]
        quizAttempt = QuizAttempt.objects.get(id=quizAttemptId)
        self.assertEqual(QuizAttempt.Status.IN_PROGRESS, quizAttempt.status)
        self.assertEqual(quizAttempt.quiz.getQuestions().count(), quizAttempt.responses.count())

        for q, r in zip(quizAttempt.quiz.getQuestions(), quizAttempt.responses.all()):
            self.assertEqual(q.id, r.question.id)
