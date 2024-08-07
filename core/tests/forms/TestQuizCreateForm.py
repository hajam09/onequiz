import random

from django import forms
from django.http import QueryDict
from faker import Faker

from core.forms import QuizCreateForm
from core.models import Quiz, Subject
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class QuizCreateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(QuizCreateFormTest, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()

    def testFieldsAndType(self):
        form = QuizCreateForm(self.request)
        self.assertEqual(len(form.fields), 14)

        self.assertTrue(isinstance(form.fields.get('name'), forms.CharField))
        self.assertEqual(form.fields.get('name').label, 'Quiz Name')
        self.assertTrue(isinstance(form.fields.get('name').widget, forms.TextInput))

        self.assertTrue(isinstance(form.fields.get('description'), forms.CharField))
        self.assertEqual(form.fields.get('description').label, 'Description')
        self.assertTrue(isinstance(form.fields.get('description').widget, forms.Textarea))

        self.assertTrue(isinstance(form.fields.get('subject'), forms.MultipleChoiceField))
        self.assertEqual(form.fields.get('subject').label, 'Subject')
        self.assertTrue(isinstance(form.fields.get('subject').widget, forms.Select))

        self.assertTrue(isinstance(form.fields.get('topic'), forms.CharField))
        self.assertEqual(form.fields.get('topic').label, 'Topic')
        self.assertTrue(isinstance(form.fields.get('topic').widget, forms.TextInput))

        self.assertTrue(isinstance(form.fields.get('quizDuration'), forms.IntegerField))
        self.assertEqual(form.fields.get('quizDuration').label, 'Quiz Duration (Minutes)')
        self.assertTrue(isinstance(form.fields.get('quizDuration').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.fields.get('maxAttempt'), forms.IntegerField))
        self.assertEqual(form.fields.get('maxAttempt').label, 'Quiz Max Attempt')
        self.assertTrue(isinstance(form.fields.get('maxAttempt').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.fields.get('difficulty'), forms.MultipleChoiceField))
        self.assertEqual(form.fields.get('difficulty').label, 'Quiz Difficulty')
        self.assertTrue(isinstance(form.fields.get('difficulty').widget, forms.Select))

        self.assertTrue(isinstance(form.fields.get('passMark'), forms.DecimalField))
        self.assertEqual(form.fields.get('passMark').label, 'Quiz Pass Mark')
        self.assertTrue(isinstance(form.fields.get('passMark').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.fields.get('successText'), forms.CharField))
        self.assertEqual(form.fields.get('successText').label, 'Text to display when passed')
        self.assertTrue(isinstance(form.fields.get('successText').widget, forms.TextInput))

        self.assertTrue(isinstance(form.fields.get('failText'), forms.CharField))
        self.assertEqual(form.fields.get('failText').label, 'Text to display when failed')
        self.assertTrue(isinstance(form.fields.get('failText').widget, forms.TextInput))

        self.assertTrue(isinstance(form.fields.get('inRandomOrder'), forms.BooleanField))
        self.assertEqual(form.fields.get('inRandomOrder').label, 'Questions in random order?')
        self.assertTrue(isinstance(form.fields.get('inRandomOrder').widget, forms.CheckboxInput))

        self.assertTrue(isinstance(form.fields.get('answerAtEnd'), forms.BooleanField))
        self.assertEqual(form.fields.get('answerAtEnd').label, 'Show answers at the end?')
        self.assertTrue(isinstance(form.fields.get('answerAtEnd').widget, forms.CheckboxInput))

        self.assertTrue(isinstance(form.fields.get('isExamPaper'), forms.BooleanField))
        self.assertEqual(form.fields.get('isExamPaper').label, 'Exam paper type?')
        self.assertTrue(isinstance(form.fields.get('isExamPaper').widget, forms.CheckboxInput))

        self.assertTrue(isinstance(form.fields.get('isDraft'), forms.BooleanField))
        self.assertEqual(form.fields.get('isDraft').label, 'Is draft?')
        self.assertTrue(isinstance(form.fields.get('isDraft').widget, forms.CheckboxInput))

    def testInitialDropdownChoices(self):
        form = QuizCreateForm(self.request)
        SUBJECT_CHOICES = [(subject.id, subject.name) for subject in Subject.objects.all()]
        SUBJECT_CHOICES.insert(0, ('', '-- Select a value --'))

        DIFFICULTY_CHOICES = [
            (Quiz.Difficulty.EASY, Quiz.Difficulty.EASY.label),
            (Quiz.Difficulty.MEDIUM, Quiz.Difficulty.MEDIUM.label),
            (Quiz.Difficulty.HARD, Quiz.Difficulty.HARD.label),
        ]

        self.assertIn('subject', form.fields)
        self.assertIn('difficulty', form.fields)
        self.assertListEqual(form.base_fields.get('subject').choices, SUBJECT_CHOICES)
        self.assertListEqual(form.base_fields.get('difficulty').choices, DIFFICULTY_CHOICES)
        self.assertEqual(3, len(form.base_fields.get('difficulty').choices))

    def testQuizWithNameAlreadyExists(self):
        quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        testParams = self.TestParams(self.subject)
        testParams.name = quiz.name
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('name'))
        self.assertEqual(f'Quiz already exists with name: {quiz.name}', form.errors.get('name')[0])

    def testSelectedSubjectDoesNotExists(self):
        testParams = self.TestParams(self.subject)
        testParams.subject = 0
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        # self.assertTrue(form.has_error('subject'))
        self.assertEqual(f'There\'s an error with the selected subject.', form.errors.get('__all__')[0])

    def testQuizDurationIsNegative(self):
        testParams = self.TestParams(self.subject)
        testParams.quizDuration = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('quizDuration'))
        self.assertEqual(f'Quiz Durations should be greater than 0.', form.errors.get('quizDuration')[0])

    def testQuizMaxAttemptIsNegative(self):
        testParams = self.TestParams(self.subject)
        testParams.maxAttempt = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('maxAttempt'))
        self.assertEqual(f'Quiz Max Attempt should be greater than 0.', form.errors.get('maxAttempt')[0])

    def testQuizDifficultyIsIncorrect(self):
        testParams = self.TestParams(self.subject)
        testParams.difficulty = 'NONE'
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        # self.assertTrue(form.has_error('difficulty'))
        self.assertEqual(
            f'Quiz Difficulty should either be {Quiz.Difficulty.EASY.label} or {Quiz.Difficulty.MEDIUM.label} or {Quiz.Difficulty.HARD.label}',
            form.errors.get('__all__')[0])

    def testQuizPassMarkIsLessThanZero(self):
        testParams = self.TestParams(self.subject)
        testParams.passMark = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('passMark'))
        self.assertEqual(f'Pass mark should be between 0 and 100.', form.errors.get('passMark')[0])

    def testQuizPassMarkIsGreaterThanHundred(self):
        testParams = self.TestParams(self.subject)
        testParams.passMark = 101
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('passMark'))
        self.assertEqual(f'Pass mark should be between 0 and 100.', form.errors.get('passMark')[0])

    def testQuizSuccessTextIsEmpty(self):
        testParams = self.TestParams(self.subject)
        testParams.successText = None
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('successText'))
        self.assertEqual(f'This field is required.', form.errors.get('successText')[0])

    def testQuizFailTextIsEmpty(self):
        testParams = self.TestParams(self.subject)
        testParams.failText = None
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('failText'))
        self.assertEqual(f'This field is required.', form.errors.get('failText')[0])

    def testQuizObjectCreatedCaseOne(self):
        testParams = self.TestParams(self.subject)
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertTrue(form.is_valid())

        newQuiz = form.save()
        self.assertEqual(testParams.name, newQuiz.name)
        self.assertEqual(testParams.description, newQuiz.description)
        self.assertEqual(self.subject, newQuiz.subject)
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
        self.assertEqual(self.request.user, newQuiz.creator)

    class TestParams:

        def __init__(self, subject):
            faker = Faker()
            CHECKBOX = ['on', 'off']

            self.name = faker.pystr_format()
            self.description = faker.paragraph()
            self.subject = subject.id
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
                'isDraft': self.isDraft
            }
            queryDict = QueryDict('', mutable=True)
            queryDict.update(data)
            return queryDict
