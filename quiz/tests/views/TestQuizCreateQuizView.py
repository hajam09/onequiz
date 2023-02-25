import random

from django.http import QueryDict
from django.urls import reverse
from faker import Faker

from onequiz.operations import bakerOperations, generalOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.forms import QuizCreateForm
from quiz.models import Quiz


class QuizCreateQuizViewTest(BaseTestViews):

    def setUp(self, path=reverse('quiz:create-quiz')) -> None:
        super(QuizCreateQuizViewTest, self).setUp(path)
        self.subject = bakerOperations.createSubjects(1).first()

    def testCreateQuizViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], QuizCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Quiz')
        self.assertTemplateUsed(response, 'quiz/quizTemplateView.html')

    def testFormIsInvalidAndObjectIsNotCreated(self):
        testParams = self.TestParams(self.subject)
        testParams.passMark = 101

        response = self.post(testParams.getData())
        self.assertEquals(response.status_code, 200)
        self.assertEqual(0, Quiz.objects.count())
        self.assertTrue(isinstance(response.context['form'], QuizCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Quiz')
        self.assertTemplateUsed(response, 'quiz/quizTemplateView.html')

    def testFormIsValidAndObjectIsCreated(self):
        testParams = self.TestParams(self.subject)
        response = self.post(testParams.getData())
        quiz = Quiz.objects.first()
        self.assertEqual(1, Quiz.objects.count())

        self.assertEqual(quiz.name, testParams.name)
        self.assertEqual(quiz.description, testParams.description)
        self.assertEqual(quiz.url, generalOperations.parseStringToUrl(testParams.link))
        self.assertEqual(quiz.subject, self.subject)
        self.assertEqual(quiz.numberOfQuestions, 1)
        self.assertEqual(quiz.quizDuration, testParams.quizDuration)
        self.assertEqual(quiz.maxAttempt, testParams.maxAttempt)
        self.assertEqual(quiz.difficulty, testParams.difficulty)
        self.assertEqual(quiz.passMark, testParams.passMark)
        self.assertEqual(quiz.successText, testParams.successText)
        self.assertEqual(quiz.failText, testParams.failText)
        self.assertEqual(quiz.inRandomOrder, testParams.inRandomOrder == 'on')
        self.assertEqual(quiz.answerAtEnd, testParams.answerAtEnd == 'on')
        self.assertEqual(quiz.isExamPaper, testParams.isExamPaper == 'on')
        self.assertEqual(quiz.isDraft, testParams.isDraft == 'on')

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], QuizCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Quiz')
        self.assertTemplateUsed(response, 'quiz/quizTemplateView.html')

    class TestParams:

        def __init__(self, subject):
            faker = Faker()
            CHECKBOX = ['on', 'off']

            self.name = faker.pystr_format()
            self.description = faker.paragraph()
            self.link = faker.paragraph()
            self.subject = subject.id
            self.quizDuration = faker.random_number(digits=2)
            self.maxAttempt = faker.random_number(digits=1)
            self.difficulty = random.choice([Quiz.Difficulty.EASY, Quiz.Difficulty.MEDIUM, Quiz.Difficulty.HARD])
            self.passMark = faker.random_number(digits=2)
            self.successText = faker.paragraph()
            self.failText = faker.paragraph()
            self.inRandomOrder = random.choice(CHECKBOX)
            self.answerAtEnd = random.choice(CHECKBOX)
            self.isExamPaper = random.choice(CHECKBOX)
            self.isDraft = random.choice(CHECKBOX)

        def getData(self):
            data = {
                'name': self.name,
                'description': self.description,
                'link': self.link,
                'subject': self.subject,
                'quizDuration': self.quizDuration,
                'maxAttempt': self.maxAttempt,
                'difficulty': self.difficulty,
                'passMark': self.passMark,
                'successText': self.successText,
                'failText': self.failText,
                'inRandomOrder': self.inRandomOrder,
                'answerAtEnd': self.answerAtEnd,
                'isExamPaper': self.isExamPaper,
                'isDraft': self.isDraft
            }
            queryDict = QueryDict('', mutable=True)
            queryDict.update(data)
            return queryDict
