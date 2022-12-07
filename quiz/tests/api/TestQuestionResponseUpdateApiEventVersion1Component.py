import json

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic, QuizAttempt, EssayQuestion, TrueOrFalseQuestion, MultipleChoiceQuestion


class QuestionResponseUpdateApiEventVersion1Component(BaseTestAjax):

    def setUp(self, path=reverse('quiz:questionResponseUpdateApiEventVersion1Component')) -> None:
        super(QuestionResponseUpdateApiEventVersion1Component, self).setUp(path)
        bakerOperations.createSubjectsAndTopics(1, 1)
        self.topic = Topic.objects.select_related('subject').first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.eq = bakerOperations.createEssayQuestion()
        self.tf = bakerOperations.createTrueOrFalseQuestion()
        self.mc = bakerOperations.createMultipleChoiceQuestionAndAnswers(None)
        self.quiz.questions.add(*[self.eq, self.tf, self.mc])

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        self.quizAttempt = QuizAttempt.objects.select_related('quiz').prefetch_related(
            'responses__question', 'responses__essayresponse', 'responses__trueorfalseresponse',
            'responses__multiplechoiceresponse'
        ).get(id=quizAttemptId)

    def createQuizAttemptAndTheResponseObjects(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        return ajaxResponse['redirectUrl'].split('/')[3]

    def testUpdateResponseForEssayQuestion(self):
        testParams = self.TestParams(self.quizAttempt, self.eq)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)
        testParams.response.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(testParams.response.essayresponse.answer, payload['response']['text'])

    def testUpdateResponseForTrueOrFalseQuestion(self):
        testParams = self.TestParams(self.quizAttempt, self.tf)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)
        testParams.response.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(testParams.response.trueorfalseresponse.isChecked, eval(payload['response']['selectedOption']))

    def testUpdateResponseForMultipleChoiceQuestion(self):
        testParams = self.TestParams(self.quizAttempt, self.mc)
        payload = testParams.getResponseForQuestion()

        response = self.put(data=payload)
        ajaxResponse = json.loads(response.content)
        testParams.response.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertListEqual(
            testParams.response.multiplechoiceresponse.answers['answers'], payload['response']['choices']
        )

    class TestParams:
        def __init__(self, quizAttempt, question):
            self.quizAttempt = quizAttempt
            self.question = question
            self.response = self.getResponseObject()

        def getResponseForQuestion(self):
            if isinstance(self.question, EssayQuestion):
                return self.getEssayQuestionResponse()
            elif isinstance(self.question, TrueOrFalseQuestion):
                return self.getTrueOrFalseQuestionResponse()
            elif isinstance(self.question, MultipleChoiceQuestion):
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
            currentChoices = self.response.multiplechoiceresponse.answers['answers']
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