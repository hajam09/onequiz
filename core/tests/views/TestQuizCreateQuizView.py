import random

from django.http import QueryDict
from django.urls import reverse
from faker import Faker

from core.forms import QuizCreateForm
from core.models import Quiz
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizCreateQuizViewTest(BaseTestViews):

    def setUp(self, path=reverse('core:quiz-create-view')) -> None:
        super(QuizCreateQuizViewTest, self).setUp(path)

    def testCreateQuizViewGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuizCreateForm)
        self.assertTrue(response.context['formTitle'], 'Create Quiz')
        self.assertTemplateUsed(response, 'core/quizTemplateView.html')

    def testFormIsInvalidAndObjectIsNotCreated(self):
        testParams = self.TestParams()
        testParams.passMark = 101

        response = self.post(testParams.getData())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertIsInstance(response.context['form'], QuizCreateForm)
        self.assertTrue(response.context['formTitle'], 'Create Quiz')
        self.assertTemplateUsed(response, 'core/quizTemplateView.html')

    def testFormIsValidAndObjectIsCreated(self):
        testParams = self.TestParams()
        response = self.post(testParams.getData())
        quiz = Quiz.objects.first()
        self.assertEqual(Quiz.objects.count(), 1)

        self.assertEqual(testParams.name, quiz.name)
        self.assertEqual(testParams.description, quiz.description)
        self.assertEqual(testParams.subject, quiz.subject)
        self.assertEqual(testParams.topic, quiz.topic)
        self.assertEqual(testParams.quizDuration, quiz.quizDuration)
        self.assertEqual(testParams.maxAttempt, quiz.maxAttempt)
        self.assertEqual(testParams.difficulty, quiz.difficulty)
        self.assertEqual(testParams.passMark, quiz.passMark)
        self.assertEqual(testParams.successText, quiz.successText)
        self.assertEqual(testParams.failText, quiz.failText)
        self.assertEqual(testParams.inRandomOrder == 'on', quiz.inRandomOrder)
        self.assertEqual(testParams.answerAtEnd == 'on', quiz.answerAtEnd)
        self.assertEqual(testParams.isExamPaper == 'on', quiz.isExamPaper)
        self.assertEqual(testParams.isDraft == 'on', quiz.isDraft)
        self.assertEqual(testParams.enableAutoMarking == 'on', quiz.enableAutoMarking)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuizCreateForm)
        self.assertTrue(response.context['formTitle'], 'Create Quiz')
        self.assertTemplateUsed(response, 'core/quizTemplateView.html')

    class TestParams:
        def __init__(self):
            faker = Faker()
            CHECKBOX = ['on', '']

            self.name = faker.pystr_format()
            self.description = faker.paragraph()
            self.subject = random.choice(Quiz.Subject.values)
            self.topic = faker.pystr_format()
            self.quizDuration = faker.random_number(digits=2)
            self.maxAttempt = faker.random_number(digits=1)
            self.difficulty = random.choice(Quiz.Difficulty.values)
            self.passMark = faker.random_number(digits=2)
            self.successText = faker.paragraph()
            self.failText = faker.paragraph()
            self.inRandomOrder = random.choice(CHECKBOX)
            self.answerAtEnd = random.choice(CHECKBOX)
            self.isExamPaper = random.choice(CHECKBOX)
            self.isDraft = random.choice(CHECKBOX)
            self.enableAutoMarking = random.choice(CHECKBOX)

        def getData(self):
            data = {
                'name': self.name,
                'description': self.description,
                'subject': self.subject,
                'topic': self.topic,
                'quizDuration': self.quizDuration,
                'maxAttempt': self.maxAttempt,
                'difficulty': self.difficulty,
                'passMark': self.passMark,
                'successText': self.successText,
                'failText': self.failText,
                'inRandomOrder': self.inRandomOrder,
                'answerAtEnd': self.answerAtEnd,
                'isExamPaper': self.isExamPaper,
                'isDraft': self.isDraft,
                'enableAutoMarking': self.enableAutoMarking
            }
            queryDict = QueryDict('', mutable=True)
            queryDict.update(data)
            return queryDict
