import random

from django import forms
from django.http import QueryDict
from faker import Faker

from core.forms import QuizCreateForm
from core.models import Quiz
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class QuizCreateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(QuizCreateFormTest, self).setUp('')

    def testFieldsAndType(self):
        form = QuizCreateForm(self.request)
        self.assertEqual(len(form.fields), 15)

        self.assertIsInstance(form.fields.get('name'), forms.CharField)
        self.assertEqual(form.fields.get('name').label, 'Quiz Name')
        self.assertIsInstance(form.fields.get('name').widget, forms.TextInput)

        self.assertIsInstance(form.fields.get('description'), forms.CharField)
        self.assertEqual(form.fields.get('description').label, 'Description')
        self.assertIsInstance(form.fields.get('description').widget, forms.Textarea)

        self.assertIsInstance(form.fields.get('subject'), forms.ChoiceField)
        self.assertEqual(form.fields.get('subject').label, 'Subject')
        self.assertIsInstance(form.fields.get('subject').widget, forms.Select)

        self.assertIsInstance(form.fields.get('topic'), forms.CharField)
        self.assertEqual(form.fields.get('topic').label, 'Topic')
        self.assertIsInstance(form.fields.get('topic').widget, forms.TextInput)

        self.assertIsInstance(form.fields.get('quizDuration'), forms.IntegerField)
        self.assertEqual(form.fields.get('quizDuration').label, 'Quiz Duration (Minutes)')
        self.assertIsInstance(form.fields.get('quizDuration').widget, forms.NumberInput)

        self.assertIsInstance(form.fields.get('maxAttempt'), forms.IntegerField)
        self.assertEqual(form.fields.get('maxAttempt').label, 'Quiz Max Attempt')
        self.assertIsInstance(form.fields.get('maxAttempt').widget, forms.NumberInput)

        self.assertIsInstance(form.fields.get('difficulty'), forms.ChoiceField)
        self.assertEqual(form.fields.get('difficulty').label, 'Quiz Difficulty')
        self.assertIsInstance(form.fields.get('difficulty').widget, forms.Select)

        self.assertIsInstance(form.fields.get('passMark'), forms.DecimalField)
        self.assertEqual(form.fields.get('passMark').label, 'Quiz Pass Mark')
        self.assertIsInstance(form.fields.get('passMark').widget, forms.NumberInput)

        self.assertIsInstance(form.fields.get('successText'), forms.CharField)
        self.assertEqual(form.fields.get('successText').label, 'Text to display when passed')
        self.assertIsInstance(form.fields.get('successText').widget, forms.TextInput)

        self.assertIsInstance(form.fields.get('failText'), forms.CharField)
        self.assertEqual(form.fields.get('failText').label, 'Text to display when failed')
        self.assertIsInstance(form.fields.get('failText').widget, forms.TextInput)

        self.assertIsInstance(form.fields.get('inRandomOrder'), forms.BooleanField)
        self.assertEqual(form.fields.get('inRandomOrder').label, 'Questions in random order?')
        self.assertIsInstance(form.fields.get('inRandomOrder').widget, forms.CheckboxInput)

        self.assertIsInstance(form.fields.get('answerAtEnd'), forms.BooleanField)
        self.assertEqual(form.fields.get('answerAtEnd').label, 'Show answers at the end?')
        self.assertIsInstance(form.fields.get('answerAtEnd').widget, forms.CheckboxInput)

        self.assertIsInstance(form.fields.get('isExamPaper'), forms.BooleanField)
        self.assertEqual(form.fields.get('isExamPaper').label, 'Exam paper type?')
        self.assertIsInstance(form.fields.get('isExamPaper').widget, forms.CheckboxInput)

        self.assertIsInstance(form.fields.get('isDraft'), forms.BooleanField)
        self.assertEqual(form.fields.get('isDraft').label, 'Is draft?')
        self.assertIsInstance(form.fields.get('isDraft').widget, forms.CheckboxInput)

        self.assertIsInstance(form.fields.get('enableAutoMarking'), forms.BooleanField)
        self.assertEqual(form.fields.get('enableAutoMarking').label, 'Enabled auto marking?')
        self.assertIsInstance(form.fields.get('enableAutoMarking').widget, forms.CheckboxInput)

    def testInitialDropdownChoices(self):
        form = QuizCreateForm(self.request)
        SUBJECT_CHOICES = [(None, '-- Select a value --')] + Quiz.Subject.choices
        DIFFICULTY_CHOICES = [(None, '-- Select a value --')] + Quiz.Difficulty.choices

        self.assertIn('subject', form.fields)
        self.assertIn('difficulty', form.fields)
        self.assertListEqual(form.base_fields.get('subject').choices, SUBJECT_CHOICES)
        self.assertListEqual(form.base_fields.get('difficulty').choices, DIFFICULTY_CHOICES)
        self.assertEqual(len(form.base_fields.get('subject').choices), 31)
        self.assertEqual(len(form.base_fields.get('difficulty').choices), 4)

    def testQuizWithNameAlreadyExists(self):
        quiz = bakerOperations.createQuiz(self.request.user)
        testParams = self.TestParams()
        testParams.name = quiz.name
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('name'))
        self.assertEqual(form.errors.get('name')[0], f'Quiz already exists with name: {quiz.name}')

    def testSelectedSubjectDoesNotExists(self):
        testParams = self.TestParams()
        testParams.subject = 'INVALID'
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('subject'))
        self.assertEqual(form.errors.get('subject')[0],
                         f'Select a valid choice. INVALID is not one of the available choices.')

    def testQuizDurationIsNegative(self):
        testParams = self.TestParams()
        testParams.quizDuration = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('quizDuration'))
        self.assertEqual(form.errors.get('quizDuration')[0], f'Quiz Durations should be greater than 0.')

    def testQuizMaxAttemptIsNegative(self):
        testParams = self.TestParams()
        testParams.maxAttempt = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('maxAttempt'))
        self.assertEqual(form.errors.get('maxAttempt')[0], f'Quiz Max Attempt should be greater than 0.')

    def testQuizDifficultyIsIncorrect(self):
        testParams = self.TestParams()
        testParams.difficulty = 'NONE'
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('difficulty'))
        self.assertEqual(form.errors.get('difficulty')[0],
                         f'Select a valid choice. NONE is not one of the available choices.')

    def testQuizPassMarkIsLessThanZero(self):
        testParams = self.TestParams()
        testParams.passMark = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('passMark'))
        self.assertEqual(form.errors.get('passMark')[0], f'Pass mark should be between 0 and 100.')

    def testQuizPassMarkIsGreaterThanHundred(self):
        testParams = self.TestParams()
        testParams.passMark = 101
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('passMark'))
        self.assertEqual(form.errors.get('passMark')[0], f'Pass mark should be between 0 and 100.')

    def testQuizSuccessTextIsEmpty(self):
        testParams = self.TestParams()
        testParams.successText = None
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('successText'))
        self.assertEqual(form.errors.get('successText')[0], f'This field is required.')

    def testQuizFailTextIsEmpty(self):
        testParams = self.TestParams()
        testParams.failText = None
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('failText'))
        self.assertEqual(form.errors.get('failText')[0], f'This field is required.')

    def testQuizObjectCreatedCaseOne(self):
        testParams = self.TestParams()
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertTrue(form.is_valid())

        newQuiz = form.save()
        self.assertEqual(testParams.name, newQuiz.name)
        self.assertEqual(testParams.description, newQuiz.description)
        self.assertEqual(testParams.subject, newQuiz.subject)
        self.assertEqual(testParams.topic, newQuiz.topic)
        self.assertEqual(testParams.quizDuration, newQuiz.quizDuration)
        self.assertEqual(testParams.maxAttempt, newQuiz.maxAttempt)
        self.assertEqual(testParams.difficulty, newQuiz.difficulty)
        self.assertEqual(testParams.passMark, newQuiz.passMark)
        self.assertEqual(testParams.successText, newQuiz.successText)
        self.assertEqual(testParams.failText, newQuiz.failText)
        self.assertEqual(testParams.inRandomOrder == 'on', newQuiz.inRandomOrder)
        self.assertEqual(testParams.answerAtEnd == 'on', newQuiz.answerAtEnd)
        self.assertEqual(testParams.isExamPaper == 'on', newQuiz.isExamPaper)
        self.assertEqual(testParams.isDraft == 'on', newQuiz.isDraft)
        self.assertEqual(testParams.enableAutoMarking == 'on', newQuiz.enableAutoMarking)
        self.assertEqual(self.request.user, newQuiz.creator)

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
