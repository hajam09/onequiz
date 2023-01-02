import json
import random

from django.urls import reverse
from faker import Faker

from onequiz.operations import bakerOperations
from onequiz.operations.generalOperations import QuestionAndResponse
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic, QuizAttempt


class QuizAttemptQuestionsApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path=None) -> None:
        super(QuizAttemptQuestionsApiEventVersion1ComponentTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 1)
        self.topic = Topic.objects.select_related('subject').first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.eq1 = bakerOperations.createEssayQuestion().question
        self.eq2 = bakerOperations.createEssayQuestion().question
        self.eq3 = bakerOperations.createEssayQuestion().question
        self.tf1 = bakerOperations.createTrueOrFalseQuestion().question
        self.tf2 = bakerOperations.createTrueOrFalseQuestion().question
        self.tf3 = bakerOperations.createTrueOrFalseQuestion().question
        self.mcq1 = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question
        self.mcq2 = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question
        self.mcq3 = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question

    def createQuizAttemptAndTheResponseObjects(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        return ajaxResponse['redirectUrl'].split('/')[2]

    def testGetQuizAttemptResponseComponents(self):
        self.quiz.questions.add(
            *[self.eq1, self.eq2, self.eq3, self.tf1, self.tf2, self.tf3, self.mcq1, self.mcq2, self.mcq3]
        )

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        response = self.get(path=path)
        ajaxResponse = json.loads(response.content)

        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').get(
            id=quizAttemptId
        )
        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        computedResponseList = QuestionAndResponse(questionList, responseList)

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
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
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

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            self.assertEqual(a.essayResponse.pk, b['response']['id'])
            self.assertEqual(a.essayResponse.answer, b['response']['text'])

    def testUpdateTrueOrFalseQuestionResponses(self):
        quizQuestionList = [self.tf1, self.tf2, self.tf3]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
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

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            self.assertEqual(a.trueOrFalseResponse.pk, b['response']['id'])
            self.assertEqual(a.trueOrFalseResponse.trueSelected, eval(b['response']['selectedOption']))

    def testUpdateMultipleChoiceQuestionResponses(self):
        quizQuestionList = [self.mcq1, self.mcq2, self.mcq3]
        self.quiz.questions.add(*quizQuestionList)

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
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

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            self.assertEqual(a.multipleChoiceResponse.pk, b['response']['id'])
            self.assertListEqual(a.multipleChoiceResponse.answers['answers'], b['response']['choices'])

    def testWhenQuizHasEssayQuestionThenDoNotMarkTheQuiz(self):
        quizQuestionList = [self.eq1, self.tf1, self.mcq1]
        self.quiz.questions.add(
            *quizQuestionList
        )

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
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

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            if b['type'] == 'EssayQuestion':
                self.assertEqual(a.essayResponse.pk, b['response']['id'])
                self.assertEqual(a.essayResponse.answer, b['response']['text'])
            elif b['type'] == 'TrueOrFalseQuestion':
                self.assertEqual(a.trueOrFalseResponse.pk, b['response']['id'])
                self.assertEqual(a.trueOrFalseResponse.trueSelected, eval(b['response']['selectedOption']))
            elif b['type'] == 'MultipleChoiceQuestion':
                self.assertEqual(a.multipleChoiceResponse.pk, b['response']['id'])
                self.assertListEqual(a.multipleChoiceResponse.answers['answers'], b['response']['choices'])

    def testWhenQuizDoesNotHaveEssayQuestionThenMarkTheQuiz(self):
        quizQuestionList = [self.tf1, self.tf2, self.tf3, self.mcq1, self.mcq2, self.mcq3]
        self.quiz.questions.add(
            *quizQuestionList
        )

        quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
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

        for a, b in zip(quizAttempt.responses.all(), responseListData):
            if b['type'] == 'TrueOrFalseQuestion':
                self.assertEqual(a.trueOrFalseResponse.pk, b['response']['id'])
                self.assertEqual(a.trueOrFalseResponse.trueSelected, eval(b['response']['selectedOption']))
            elif b['type'] == 'MultipleChoiceQuestion':
                self.assertEqual(a.multipleChoiceResponse.pk, b['response']['id'])
                self.assertListEqual(a.multipleChoiceResponse.answers['answers'], b['response']['choices'])

    class TestParams:
        def __init__(self, questionList, responseList):
            self.questionList = questionList
            self.responseList = responseList
            self.faker = Faker()

        def getResponse(self):
            computedResponseList = [
                self.getResponseForQuestion(question) for question in self.questionList
            ]
            return computedResponseList

        def getResponseForQuestion(self, question):
            if hasattr(question, 'essayQuestion'):
                return self.getEssayQuestionResponse(question)
            elif hasattr(question, 'trueOrFalseQuestion'):
                return self.getTrueOrFalseQuestionResponse(question)
            elif hasattr(question, 'multipleChoiceQuestion'):
                return self.getMultipleChoiceQuestionResponse(question)

        def getResponseObject(self, question):
            return next((o for o in self.responseList if o.question.id == question.id))

        def getEssayQuestionResponse(self, question):
            response = self.getResponseObject(question)
            data = {
                'id': question.id,
                'type': 'EssayQuestion',
                'response': {
                    'id': response.essayResponse.pk,
                    'text': self.faker.paragraph()
                }
            }
            return data

        def getTrueOrFalseQuestionResponse(self, question):
            response = self.getResponseObject(question)
            data = {
                'type': 'TrueOrFalseQuestion',
                'response': {
                    'id': response.trueOrFalseResponse.pk,
                    'selectedOption': random.choice(['True', 'False'])
                }
            }
            return data

        def getMultipleChoiceQuestionResponse(self, question):
            response = self.getResponseObject(question)
            data = {
                'type': 'MultipleChoiceQuestion',
                'response': {
                    'id': response.multipleChoiceResponse.pk,
                    'choices': [
                        {
                            'id': answer['id'],
                            'content': answer['content'],
                            'isChecked': random.choice(['True', 'False'])
                        }
                        for answer in response.multipleChoiceResponse.answers['answers']
                    ]
                }
            }
            return data
