import json
import random

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.operations.generalOperations import QuestionAndResponse
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic, QuizAttempt, Result


class QuizMarkingOccurrenceApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path='') -> None:
        super(QuizMarkingOccurrenceApiEventVersion1ComponentTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 2)

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

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        self.quizAttempt = QuizAttempt.objects.select_related('quiz').prefetch_related(
            'responses__question', 'responses__essayresponse', 'responses__trueorfalseresponse',
            'responses__multiplechoiceresponse'
        ).get(id=quizAttemptId)
        self.path = reverse('quiz:quizMarkingOccurrenceApiEventVersion1Component', kwargs={'id': self.quizAttempt.id})

    def createQuizAttemptAndTheResponseObjects(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        return ajaxResponse['redirectUrl'].split('/')[3]

    def testAwardedMarkResponseHasMissingKeys(self):
        questionAndResponse = QuestionAndResponse(
            self.quizAttempt.quiz.getQuestions(), self.quizAttempt.responses.all()
        )
        testParams = self.TestParams(questionAndResponse.getResponse())
        data = testParams.getData()
        for item in data:
            del item['responseId']

        payload = {'response': data}
        response = self.put(data=payload)
        self.quizAttempt.refresh_from_db()
        ajaxResponse = json.loads(response.content)
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['redirectUrl'])
        self.assertEqual(
            ajaxResponse['redirectUrl'],
            reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})
        )
        self.assertNotEqual(self.quizAttempt.status, QuizAttempt.Status.MARKED)
        self.assertFalse(Result.objects.filter(quizAttempt=self.quizAttempt).exists())

    def testResponseObjectNotFound(self):
        questionAndResponse = QuestionAndResponse(
            self.quizAttempt.quiz.getQuestions(), self.quizAttempt.responses.all()
        )
        testParams = self.TestParams(questionAndResponse.getResponse())
        data = testParams.getData()
        for item in data:
            item['responseId'] = 0

        payload = {'response': data}
        response = self.put(data=payload)
        self.quizAttempt.refresh_from_db()
        ajaxResponse = json.loads(response.content)
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['redirectUrl'])
        self.assertEqual(
            ajaxResponse['redirectUrl'],
            reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})
        )
        self.assertNotEqual(self.quizAttempt.status, QuizAttempt.Status.MARKED)
        self.assertFalse(Result.objects.filter(quizAttempt=self.quizAttempt).exists())

    def testResponseObjectsUpdatedWithMarks(self):
        questionAndResponse = QuestionAndResponse(
            self.quizAttempt.quiz.getQuestions(), self.quizAttempt.responses.all()
        )
        testParams = self.TestParams(questionAndResponse.getResponse())
        payload = {'response': testParams.getData()}
        response = self.put(data=payload)
        self.quizAttempt.refresh_from_db()
        ajaxResponse = json.loads(response.content)
        createdResult = Result.objects.filter(quizAttempt=self.quizAttempt).first()
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['redirectUrl'])
        self.assertEqual(
            ajaxResponse['redirectUrl'],
            reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})
        )
        self.assertEqual(self.quizAttempt.status, QuizAttempt.Status.MARKED)
        self.assertIsNotNone(createdResult)
        self.assertEqual(createdResult.versionNo, 1)

    class TestParams:

        def __init__(self, responseList):
            self.responseList = responseList

        def getData(self):
            response = [
                {
                    'questionId': i['id'],
                    'responseId': i['response']['id'],
                    'awardedMark': random.randint(0, i['mark'])
                } for i in self.responseList
            ]
            return response
