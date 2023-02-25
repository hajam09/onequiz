import json
from unittest.mock import patch

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import QuizAttempt


class QuestionResponseUpdateApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path=reverse('quiz:questionResponseUpdateApiEventVersion1Component')) -> None:
        super(QuestionResponseUpdateApiEventVersion1ComponentTest, self).setUp(path)
        self.subject = bakerOperations.createSubjects(1).first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.eq = bakerOperations.createEssayQuestion().question
        self.tf = bakerOperations.createTrueOrFalseQuestion().question
        self.mc = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question
        self.quiz.questions.add(*[self.eq, self.tf, self.mc])

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        self.quizAttempt = QuizAttempt.objects.select_related('quiz').get(id=quizAttemptId)

    def createQuizAttemptAndTheResponseObjects(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        return ajaxResponse['redirectUrl'].split('/')[2]

    @patch('quiz.api.featureFlagOperations')
    def testWhenFeatureFlagIsOffReturnFalse(self, mockFeatureFlagOperations):
        mockFeatureFlagOperations.isEnabled.return_value = False
        testParams = self.TestParams(self.quizAttempt, self.eq)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ajaxResponse['success'])
        self.assertEqual(ajaxResponse['message'], 'Feature flag SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT not enabled.')

    @patch('quiz.api.featureFlagOperations')
    def testUpdateResponseForEssayQuestion(self, mockFeatureFlagOperations):
        mockFeatureFlagOperations.isEnabled.return_value = True
        testParams = self.TestParams(self.quizAttempt, self.eq)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)
        testParams.response.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(testParams.response.essayResponse.answer, payload['response']['text'])

    @patch('quiz.api.featureFlagOperations')
    def testUpdateResponseForTrueOrFalseQuestion(self, mockFeatureFlagOperations):
        mockFeatureFlagOperations.isEnabled.return_value = True
        testParams = self.TestParams(self.quizAttempt, self.tf)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)
        testParams.response.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(testParams.response.trueOrFalseResponse.trueSelected,
                         eval(payload['response']['selectedOption']))

    @patch('quiz.api.featureFlagOperations')
    def testUpdateResponseForMultipleChoiceQuestion(self, mockFeatureFlagOperations):
        mockFeatureFlagOperations.isEnabled.return_value = True
        testParams = self.TestParams(self.quizAttempt, self.mc)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)
        testParams.response.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertListEqual(
            testParams.response.multipleChoiceResponse.answers['answers'], payload['response']['choices']
        )

        for choice in testParams.response.multipleChoiceResponse.answers['answers']:
            self.assertTrue(isinstance(choice, dict))
            self.assertEqual(len(choice), 3)
            self.assertIn('id', choice)
            self.assertIn('content', choice)
            self.assertIn('isChecked', choice)
            self.assertTrue(isinstance(eval(choice['isChecked']), bool))

    class TestParams:
        def __init__(self, quizAttempt, question):
            self.quizAttempt = quizAttempt
            self.question = question
            self.response = self.getResponseObject()

        def getResponseForQuestion(self):
            if hasattr(self.question, 'essayQuestion'):
                return self.getEssayQuestionResponse()
            elif hasattr(self.question, 'trueOrFalseQuestion'):
                return self.getTrueOrFalseQuestionResponse()
            elif hasattr(self.question, 'multipleChoiceQuestion'):
                return self.getMultipleChoiceQuestionResponse()

        def getResponseObject(self):
            return next((o for o in self.quizAttempt.responses.all() if o.question.id == self.question.id))

        def getEssayQuestionResponse(self):
            data = {
                'quizAttemptId': self.quizAttempt.id,
                'question': {
                    'id': self.question.id,
                    'type': 'EssayQuestion',
                },
                'response': {
                    'id': self.response.id,
                    'text': 'New response text',
                }
            }
            return data

        def getTrueOrFalseQuestionResponse(self):
            data = {
                'quizAttemptId': self.quizAttempt.id,
                'question': {
                    'id': self.question.id,
                    'type': 'TrueOrFalseQuestion',
                },
                'response': {
                    'id': self.response.id,
                    'selectedOption': 'True',
                }
            }
            return data

        def getMultipleChoiceQuestionResponse(self):
            currentChoices = self.response.multipleChoiceResponse.answers['answers']
            for item in currentChoices:
                item['isChecked'] = 'True'
            data = {
                'quizAttemptId': self.quizAttempt.id,
                'question': {
                    'id': self.question.id,
                    'type': 'MultipleChoiceQuestion',
                },
                'response': {
                    'id': self.response.id,
                    'choices': currentChoices
                }
            }
            return data
