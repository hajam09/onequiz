import random

from django import forms
from django.http import QueryDict
from faker import Faker

from onequiz.operations import bakerOperations, generalOperations
from onequiz.tests.BaseTest import BaseTest
from quiz.forms import QuizUpdateForm
from quiz.models import Quiz


class QuizUpdateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        super(QuizUpdateFormTest, self).setUp('')
        self.subject = bakerOperations.createSubjects(1).first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)

    def testFieldsAndType(self):
        form = QuizUpdateForm(self.request, self.quiz)
        self.assertEqual(len(form.base_fields), 14)

        self.assertTrue(isinstance(form.base_fields.get('name'), forms.CharField))
        self.assertEqual(form.base_fields.get('name').label, 'Quiz Name')
        self.assertTrue(isinstance(form.base_fields.get('name').widget, forms.TextInput))

        self.assertTrue(isinstance(form.base_fields.get('description'), forms.CharField))
        self.assertEqual(form.base_fields.get('description').label, 'Description')
        self.assertTrue(isinstance(form.base_fields.get('description').widget, forms.Textarea))

        self.assertTrue(isinstance(form.base_fields.get('link'), forms.CharField))
        self.assertEqual(form.base_fields.get('link').label, 'Quiz link')
        self.assertTrue(isinstance(form.base_fields.get('link').widget, forms.TextInput))

        self.assertTrue(isinstance(form.base_fields.get('subject'), forms.MultipleChoiceField))
        self.assertEqual(form.base_fields.get('subject').label, 'Subject')
        self.assertTrue(isinstance(form.base_fields.get('subject').widget, forms.Select))

        self.assertTrue(isinstance(form.base_fields.get('quizDuration'), forms.IntegerField))
        self.assertEqual(form.base_fields.get('quizDuration').label, 'Quiz Duration (Minutes)')
        self.assertTrue(isinstance(form.base_fields.get('quizDuration').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.base_fields.get('maxAttempt'), forms.IntegerField))
        self.assertEqual(form.base_fields.get('maxAttempt').label, 'Quiz Max Attempt')
        self.assertTrue(isinstance(form.base_fields.get('maxAttempt').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.base_fields.get('difficulty'), forms.MultipleChoiceField))
        self.assertEqual(form.base_fields.get('difficulty').label, 'Quiz Difficulty')
        self.assertTrue(isinstance(form.base_fields.get('difficulty').widget, forms.Select))

        self.assertTrue(isinstance(form.base_fields.get('passMark'), forms.DecimalField))
        self.assertEqual(form.base_fields.get('passMark').label, 'Quiz Pass Mark')
        self.assertTrue(isinstance(form.base_fields.get('passMark').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.base_fields.get('successText'), forms.CharField))
        self.assertEqual(form.base_fields.get('successText').label, 'Text to display when passed')
        self.assertTrue(isinstance(form.base_fields.get('successText').widget, forms.TextInput))

        self.assertTrue(isinstance(form.base_fields.get('failText'), forms.CharField))
        self.assertEqual(form.base_fields.get('failText').label, 'Text to display when failed')
        self.assertTrue(isinstance(form.base_fields.get('failText').widget, forms.TextInput))

        self.assertTrue(isinstance(form.base_fields.get('inRandomOrder'), forms.BooleanField))
        self.assertEqual(form.base_fields.get('inRandomOrder').label, 'Questions in random order?')
        self.assertTrue(isinstance(form.base_fields.get('inRandomOrder').widget, forms.CheckboxInput))

        self.assertTrue(isinstance(form.base_fields.get('answerAtEnd'), forms.BooleanField))
        self.assertEqual(form.base_fields.get('answerAtEnd').label, 'Show answers at the end?')
        self.assertTrue(isinstance(form.base_fields.get('answerAtEnd').widget, forms.CheckboxInput))

        self.assertTrue(isinstance(form.base_fields.get('isExamPaper'), forms.BooleanField))
        self.assertEqual(form.base_fields.get('isExamPaper').label, 'Exam paper type?')
        self.assertTrue(isinstance(form.base_fields.get('isExamPaper').widget, forms.CheckboxInput))

        self.assertTrue(isinstance(form.base_fields.get('isDraft'), forms.BooleanField))
        self.assertEqual(form.base_fields.get('isDraft').label, 'Is draft?')
        self.assertTrue(isinstance(form.base_fields.get('isDraft').widget, forms.CheckboxInput))

    def testRaiseExceptionWhenNoneIsPassedForQuiz(self):
        with self.assertRaisesMessage(Exception, 'Quiz is none, or is not an instance of Quiz object.'):
            QuizUpdateForm(self.request, None)

    def testFormInitialValuesAndChoices(self):
        form = QuizUpdateForm(self.request, self.quiz)

        self.assertEqual(form.initial['name'], self.quiz.name)
        self.assertEqual(form.initial['description'], self.quiz.description)
        self.assertEqual(form.initial['link'], self.quiz.url)
        self.assertEqual(form.initial['subject'], self.quiz.subject.id)
        self.assertEqual(form.initial['quizDuration'], self.quiz.quizDuration)
        self.assertEqual(form.initial['maxAttempt'], self.quiz.maxAttempt)
        self.assertEqual(form.initial['difficulty'], self.quiz.difficulty)
        self.assertEqual(form.initial['passMark'], self.quiz.passMark)
        self.assertEqual(form.initial['successText'], self.quiz.successText)
        self.assertEqual(form.initial['failText'], self.quiz.failText)
        self.assertEqual(form.initial['inRandomOrder'], self.quiz.inRandomOrder)
        self.assertEqual(form.initial['answerAtEnd'], self.quiz.answerAtEnd)
        self.assertEqual(form.initial['isExamPaper'], self.quiz.isExamPaper)
        self.assertEqual(form.initial['isDraft'], self.quiz.isDraft)

    def testUpdateQuizNameIsEmpty(self):
        pass

    def testUpdateQuizUrlAlreadyUsed(self):
        quiz2 = bakerOperations.createQuiz(self.request.user, self.subject)
        testParams = self.TestParams(self.subject)
        testParams.link = quiz2.url

        form = QuizUpdateForm(self.request, self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('link'))
        self.assertEqual(f'Quiz already exists with link: {quiz2.url}', form.errors.get('link')[0])

    def testQuizUpdatedSuccessfully(self):
        testParams = self.TestParams(self.subject)
        testParams.name = 'New Quiz Name'
        testParams.link = 'New Quiz Link'
        testParams.quizDuration = 100
        testParams.difficulty = Quiz.Difficulty.MEDIUM
        testParams.successText = 'New Success Text'
        testParams.failText = 'New Fail Text'
        testParams.inRandomOrder = 'off'
        testParams.answerAtEnd = 'on'

        form = QuizUpdateForm(self.request, self.quiz, data=testParams.getData())
        self.assertTrue(form.is_valid())

        quiz = form.update()
        self.assertEqual(testParams.name, quiz.name)
        self.assertEqual(testParams.description, quiz.description)
        self.assertEqual(generalOperations.parseStringToUrl(testParams.link), quiz.url)
        self.assertEqual(self.subject, quiz.subject)
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
