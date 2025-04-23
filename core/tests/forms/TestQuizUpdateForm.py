import random

from django import forms
from django.http import QueryDict
from faker import Faker

from core.forms import QuizUpdateForm
from core.models import Quiz
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class QuizUpdateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        super(QuizUpdateFormTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.request.user)

    def testFieldsAndTypeForQuizCreator(self):
        form = QuizUpdateForm(request=self.request, quiz=self.quiz)
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

    def testFieldsAndTypeForNonQuizCreator(self):
        self.quiz.creator = bakerOperations.createUser()
        form = QuizUpdateForm(request=self.request, quiz=self.quiz)
        self.assertEqual(len(form.fields), 8)

        self.assertTrue(form.fields.get('name').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('description').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('subject').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('topic').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('quizDuration').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('maxAttempt').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('difficulty').widget.attrs['disabled'])
        self.assertTrue(form.fields.get('passMark').widget.attrs['disabled'])

        self.assertIsNone(form.fields.get('successText'))
        self.assertIsNone(form.fields.get('failText'))
        self.assertIsNone(form.fields.get('inRandomOrder'))
        self.assertIsNone(form.fields.get('answerAtEnd'))
        self.assertIsNone(form.fields.get('isExamPaper'))
        self.assertIsNone(form.fields.get('isDraft'))
        self.assertIsNone(form.fields.get('enableAutoMarking'))

    def testRaiseExceptionWhenNoneIsPassedForQuiz(self):
        with self.assertRaisesMessage(Exception, 'Quiz is none, or is not an instance of Quiz object.'):
            QuizUpdateForm(request=self.request, quiz=None)

    def testFormInitialValuesAndChoices(self):
        form = QuizUpdateForm(request=self.request, quiz=self.quiz)

        INITIAL_SUBJECT_CHOICES = [(None, '-- Select a value --')] + Quiz.Subject.choices
        self.assertListEqual(form.base_fields.get('subject').choices, INITIAL_SUBJECT_CHOICES)

        self.assertEqual(self.quiz.name, form.initial['name'])
        self.assertEqual(self.quiz.description, form.initial['description'])
        self.assertEqual(self.quiz.subject, form.initial['subject'])
        self.assertEqual(self.quiz.topic, form.initial['topic'])
        self.assertEqual(self.quiz.quizDuration, form.initial['quizDuration'])
        self.assertEqual(self.quiz.maxAttempt, form.initial['maxAttempt'])
        self.assertEqual(self.quiz.difficulty, form.initial['difficulty'])
        self.assertEqual(self.quiz.passMark, form.initial['passMark'])
        self.assertEqual(self.quiz.successText, form.initial['successText'])
        self.assertEqual(self.quiz.failText, form.initial['failText'])
        self.assertEqual(self.quiz.inRandomOrder, form.initial['inRandomOrder'])
        self.assertEqual(self.quiz.answerAtEnd, form.initial['answerAtEnd'])
        self.assertEqual(self.quiz.isExamPaper, form.initial['isExamPaper'])
        self.assertEqual(self.quiz.isDraft, form.initial['isDraft'])
        self.assertEqual(self.quiz.enableAutoMarking, form.initial['enableAutoMarking'])

    def testUpdateQuizNameIsEmpty(self):
        testParams = self.TestParams()
        testParams.name = ''

        form = QuizUpdateForm(request=self.request, quiz=self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('name'))
        self.assertEqual(form.errors.get('name')[0], 'This field is required.')

    def testQuizUpdatedSuccessfully(self):
        testParams = self.TestParams()
        testParams.name = 'New Quiz Name'
        testParams.subject = 'Art'
        testParams.quizDuration = 100
        testParams.difficulty = Quiz.Difficulty.MEDIUM
        testParams.successText = 'New Success Text'
        testParams.failText = 'New Fail Text'
        testParams.inRandomOrder = ''
        testParams.answerAtEnd = 'on'

        form = QuizUpdateForm(request=self.request, quiz=self.quiz, data=testParams.getData())
        self.assertTrue(form.is_valid())

        quiz = form.update()
        self.assertEqual(quiz.name, 'New Quiz Name')
        self.assertEqual(quiz.description, testParams.description)
        self.assertEqual(quiz.subject, 'Art')
        self.assertEqual(quiz.topic, testParams.topic)
        self.assertEqual(quiz.quizDuration, 100)
        self.assertEqual(quiz.maxAttempt, testParams.maxAttempt)
        self.assertEqual(quiz.difficulty, 'MEDIUM')
        self.assertEqual(quiz.passMark, testParams.passMark)
        self.assertEqual(quiz.successText, 'New Success Text')
        self.assertEqual(quiz.failText, 'New Fail Text')
        self.assertEqual(quiz.inRandomOrder, testParams.inRandomOrder == 'on')
        self.assertEqual(quiz.answerAtEnd, testParams.answerAtEnd == 'on')
        self.assertEqual(quiz.isExamPaper, testParams.isExamPaper == 'on')
        self.assertEqual(quiz.isDraft, testParams.isDraft == 'on')
        self.assertEqual(quiz.enableAutoMarking, testParams.enableAutoMarking == 'on')

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
            self.difficulty = random.choice([Quiz.Difficulty.EASY, Quiz.Difficulty.MEDIUM, Quiz.Difficulty.HARD])
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
