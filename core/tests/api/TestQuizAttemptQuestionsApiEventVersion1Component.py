import json
import random

from django.urls import reverse
from faker import Faker

from core.models import Subject, QuizAttempt, Question, Result
from onequiz.operations import bakerOperations
from onequiz.operations.generalOperations import QuestionAndResponse
from onequiz.tests.BaseTestAjax import BaseTestAjax


class QuizAttemptQuestionsApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path=None) -> None:
        super(QuizAttemptQuestionsApiEventVersion1ComponentTest, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.eq1 = bakerOperations.createEssayQuestion()
        self.eq2 = bakerOperations.createEssayQuestion()
        self.eq3 = bakerOperations.createEssayQuestion()
        self.tf1 = bakerOperations.createTrueOrFalseQuestion()
        self.tf2 = bakerOperations.createTrueOrFalseQuestion()
        self.tf3 = bakerOperations.createTrueOrFalseQuestion()
        self.mcq1 = bakerOperations.createMultipleChoiceQuestionAndAnswers()
        self.mcq2 = bakerOperations.createMultipleChoiceQuestionAndAnswers()
        self.mcq3 = bakerOperations.createMultipleChoiceQuestionAndAnswers()

    def createQuizAttemptAndTheResponseObjects(self):
        path = reverse('core:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        return ajaxResponse['redirectUrl'].split('/')[2]

    def testGetQuizAttemptResponseComponents(self):
        self.quiz.questions.add(
            *[self.eq1, self.eq2, self.eq3, self.tf1, self.tf2, self.tf3, self.mcq1, self.mcq2, self.mcq3]
        )

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('core:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        response = self.get(path=path)
        ajaxResponse = json.loads(response.content)

        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=quizAttemptId)
        responseList = quizAttempt.responses.all()
        computedResponseList = QuestionAndResponse(responseList)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertTrue(ajaxResponse['data']['quiz']['canEdit'])
        self.assertEqual(len(ajaxResponse['data']['questions']), 9)
        self.assertListEqual(ajaxResponse['data']['questions'], computedResponseList.getResponse())

        for item in ajaxResponse['data']['questions']:
            self.assertIn('id', item)
            self.assertIn('figure', item)
            self.assertIn('content', item)
            self.assertIn('explanation', item)
            self.assertIn('mark', item)
            self.assertIn('type', item)
            self.assertIn('response', item)
            self.assertTrue(isinstance(item['response'], dict))
            self.assertEqual(len(item), 7)
            self.assertEqual(len(item['response']), 3)

            if item['type'] == 'EssayQuestion':
                self.assertIn('id', item['response'])
                self.assertIn('text', item['response'])
                self.assertIn('mark', item['response'])
            elif item['type'] == 'TrueOrFalseQuestion':
                self.assertIn('id', item['response'])
                self.assertIn('selectedOption', item['response'])
                self.assertIn('mark', item['response'])
            elif item['type'] == 'MultipleChoiceQuestion':
                self.assertIn('id', item['response'])
                self.assertIn('choices', item['response'])
                self.assertIn('mark', item['response'])
                self.assertTrue(isinstance(item['response']['choices'], list))

                for choice in item['response']['choices']:
                    self.assertTrue(isinstance(choice, dict))
                    self.assertIn('id', choice)
                    self.assertIn('content', choice)
                    self.assertIn('isChecked', choice)
                    self.assertEqual(len(choice), 3)

    def testUpdateEssayQuestionResponses(self):
        quizQuestionList = [self.eq1, self.eq2, self.eq3]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('core:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=quizAttemptId)

        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        testParams = self.TestParams(questionList, responseList)
        responseListData = testParams.getResponse()
        payload = {'id': quizAttemptId, 'response': responseListData}

        response = self.put(data=payload, path=path)
        ajaxResponse = json.loads(response.content)
        quizAttempt.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(quizAttempt.status, QuizAttempt.Status.SUBMITTED)
        self.assertTrue(len(quizQuestionList) == quizAttempt.responses.count() == len(responseListData))

        result = Result.objects.filter(quizAttempt_id=quizAttemptId).last()
        self.assertIsNotNone(result)

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            self.assertEqual(a.pk, b['response']['id'])
            self.assertEqual(a.answer, b['response']['text'])

    def testUpdateTrueOrFalseQuestionResponses(self):
        quizQuestionList = [self.tf1, self.tf2, self.tf3]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('core:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=quizAttemptId)

        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        testParams = self.TestParams(questionList, responseList)
        responseListData = testParams.getResponse()
        payload = {'id': quizAttemptId, 'response': responseListData}

        response = self.put(data=payload, path=path)
        ajaxResponse = json.loads(response.content)
        quizAttempt.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(quizAttempt.status, QuizAttempt.Status.MARKED)
        self.assertTrue(len(quizQuestionList) == quizAttempt.responses.count() == len(responseListData))

        result = Result.objects.filter(quizAttempt_id=quizAttemptId).last()
        self.assertIsNotNone(result)

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            self.assertEqual(a.pk, b['response']['id'])
            self.assertEqual(a.trueSelected, eval(b['response']['selectedOption']))

    def testUpdateMultipleChoiceQuestionResponses(self):
        quizQuestionList = [self.mcq1, self.mcq2, self.mcq3]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('core:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=quizAttemptId)

        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        testParams = self.TestParams(questionList, responseList)
        responseListData = testParams.getResponse()
        payload = {'id': quizAttemptId, 'response': responseListData}

        response = self.put(data=payload, path=path)
        ajaxResponse = json.loads(response.content)
        quizAttempt.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(quizAttempt.status, QuizAttempt.Status.MARKED)
        self.assertTrue(len(quizQuestionList) == quizAttempt.responses.count() == len(responseListData))

        result = Result.objects.filter(quizAttempt_id=quizAttemptId).last()
        self.assertIsNotNone(result)

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            self.assertEqual(a.pk, b['response']['id'])
            self.assertListEqual(a.choices['choices'], b['response']['choices'])

    def testWhenQuizHasEssayQuestionThenDoNotMarkTheQuiz(self):
        quizQuestionList = [self.eq1, self.tf1, self.mcq1]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('core:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=quizAttemptId)

        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        testParams = self.TestParams(questionList, responseList)
        responseListData = testParams.getResponse()
        payload = {'id': quizAttemptId, 'response': responseListData}

        response = self.put(data=payload, path=path)
        ajaxResponse = json.loads(response.content)
        quizAttempt.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(quizAttempt.status, QuizAttempt.Status.SUBMITTED)
        self.assertTrue(len(quizQuestionList) == quizAttempt.responses.count() == len(responseListData))

        result = Result.objects.filter(quizAttempt_id=quizAttemptId).last()
        self.assertIsNotNone(result)

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            if b['type'] == 'EssayQuestion':
                self.assertEqual(a.pk, b['response']['id'])
                self.assertEqual(a.answer, b['response']['text'])
            elif b['type'] == 'TrueOrFalseQuestion':
                self.assertEqual(a.pk, b['response']['id'])
                self.assertEqual(a.trueSelected, eval(b['response']['selectedOption']))
            elif b['type'] == 'MultipleChoiceQuestion':
                self.assertEqual(a.pk, b['response']['id'])
                self.assertListEqual(a.choices['choices'], b['response']['choices'])

    def testWhenQuizDoesNotHaveEssayQuestionThenMarkTheQuiz(self):
        quizQuestionList = [self.tf1, self.tf2, self.tf3, self.mcq1, self.mcq2, self.mcq3]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('core:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=quizAttemptId)

        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        testParams = self.TestParams(questionList, responseList)
        responseListData = testParams.getResponse()
        payload = {'id': quizAttemptId, 'response': responseListData}

        response = self.put(data=payload, path=path)
        ajaxResponse = json.loads(response.content)
        quizAttempt.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ajaxResponse['success'])
        self.assertEqual(quizAttempt.status, QuizAttempt.Status.MARKED)
        self.assertTrue(len(quizQuestionList) == quizAttempt.responses.count() == len(responseListData))

        result = Result.objects.filter(quizAttempt_id=quizAttemptId).last()
        self.assertIsNotNone(result)

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            if b['type'] == 'TrueOrFalseQuestion':
                self.assertEqual(a.pk, b['response']['id'])
                self.assertEqual(a.trueSelected, eval(b['response']['selectedOption']))
            elif b['type'] == 'MultipleChoiceQuestion':
                self.assertEqual(a.pk, b['response']['id'])
                self.assertListEqual(a.choices['choices'], b['response']['choices'])

    class TestParams:
        def __init__(self, questionList, responseList):
            self.questionList = questionList
            self.responseList = responseList
            self.faker = Faker()

        def getResponse(self):
            computedResponseList = [
                self.getResponseForList(response) for response in self.responseList
            ]
            return computedResponseList

        def getResponseForList(self, response):
            if response.question.questionType == Question.Type.ESSAY:
                return self.getEssayQuestionResponse(response)
            elif response.question.questionType == Question.Type.TRUE_OR_FALSE:
                return self.getTrueOrFalseQuestionResponse(response)
            elif response.question.questionType == Question.Type.MULTIPLE_CHOICE:
                return self.getMultipleChoiceQuestionResponse(response)

        def getEssayQuestionResponse(self, response):
            data = {
                'id': response.question.id,
                'type': 'EssayQuestion',
                'response': {
                    'id': response.pk,
                    'text': self.faker.paragraph()
                }
            }
            return data

        def getTrueOrFalseQuestionResponse(self, response):
            data = {
                'type': 'TrueOrFalseQuestion',
                'response': {
                    'id': response.pk,
                    'selectedOption': random.choice(['True', 'False'])
                }
            }
            return data

        def getMultipleChoiceQuestionResponse(self, response):
            data = {
                'type': 'MultipleChoiceQuestion',
                'response': {
                    'id': response.pk,
                    'choices': [
                        {
                            'id': answer['id'],
                            'content': answer['content'],
                            'isChecked': random.choice(['True', 'False'])
                        }
                        for answer in response.choices['choices']
                    ]
                }
            }
            return data
