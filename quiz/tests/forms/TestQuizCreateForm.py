import random

from django.http import QueryDict
from faker import Faker

from onequiz.operations import bakerOperations, generalOperations
from onequiz.tests.BaseTest import BaseTest
from quiz.forms import QuizCreateForm
from quiz.models import Quiz, Subject, Topic


class QuizCreateFormTest(BaseTest):

    def setUp(self, path='') -> None:
        self.basePath = path
        super(QuizCreateFormTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics()
        self.topic = Topic.objects.select_related('subject').first()

    def testInitialDropdownChoices(self):
        form = QuizCreateForm(self.request)
        SUBJECT_CHOICES = [(subject.id, subject.name) for subject in Subject.objects.all()]
        SUBJECT_CHOICES.insert(0, (0, '-- Select a value --'))

        INITIAL_TOPIC_CHOICES = [(0, '-- Select a subject first --')]

        DIFFICULTY_CHOICES = [
            (Quiz.Difficulty.EASY, Quiz.Difficulty.EASY.label),
            (Quiz.Difficulty.MEDIUM, Quiz.Difficulty.MEDIUM.label),
            (Quiz.Difficulty.HARD, Quiz.Difficulty.HARD.label),
        ]

        self.assertIn('subject', form.base_fields)
        self.assertIn('difficulty', form.base_fields)
        self.assertListEqual(form.base_fields.get('subject').choices, SUBJECT_CHOICES)
        self.assertListEqual(form.base_fields.get('topic').choices, INITIAL_TOPIC_CHOICES)
        self.assertListEqual(form.base_fields.get('difficulty').choices, DIFFICULTY_CHOICES)

    def testQuizWithNameAlreadyExists(self):
        quiz = bakerOperations.createQuiz(self.request.user)
        testParams = self.TestParams(self.topic)
        testParams.name = quiz.name
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('name'))
        self.assertEqual(f'Quiz already exists with name: {quiz.name}', form.errors.get('name')[0])

    def testQuizLinkAlreadyExists(self):
        quiz = bakerOperations.createQuiz(self.request.user)
        testParams = self.TestParams(self.topic)
        testParams.link = quiz.url
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('link'))
        self.assertEqual(f'Quiz already exists with link: {testParams.link}', form.errors.get('link')[0])

    def testSelectedSubjectDoesNotExists(self):
        testParams = self.TestParams(self.topic)
        testParams.subject = 0
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        # self.assertTrue(form.has_error('subject'))
        self.assertEqual(f'There\'s an error with the selected subject.', form.errors.get('__all__')[0])

    def testQuizDurationIsNegative(self):
        testParams = self.TestParams(self.topic)
        testParams.quizDuration = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('quizDuration'))
        self.assertEqual(f'Quiz Durations should be greater than 0.', form.errors.get('quizDuration')[0])

    def testQuizMaxAttemptIsNegative(self):
        testParams = self.TestParams(self.topic)
        testParams.maxAttempt = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('maxAttempt'))
        self.assertEqual(f'Quiz Max Attempt should be greater than 0.', form.errors.get('maxAttempt')[0])

    def testQuizDifficultyIsIncorrect(self):
        testParams = self.TestParams(self.topic)
        testParams.difficulty = 'NONE'
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        # self.assertTrue(form.has_error('difficulty '))
        self.assertEqual(
            f'Quiz Difficulty should either be {Quiz.Difficulty.EASY.label} or {Quiz.Difficulty.MEDIUM.label} or {Quiz.Difficulty.HARD.label}',
            form.errors.get('__all__')[0])

    def testQuizPassMarkIsLessThanZero(self):
        testParams = self.TestParams(self.topic)
        testParams.passMark = -1
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('passMark'))
        self.assertEqual(f'Pass mark should be between 0 and 100.', form.errors.get('passMark')[0])

    def testQuizPassMarkIsGreaterThanHundred(self):
        testParams = self.TestParams(self.topic)
        testParams.passMark = 101
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('passMark'))
        self.assertEqual(f'Pass mark should be between 0 and 100.', form.errors.get('passMark')[0])

    def testQuizSuccessTextIsEmpty(self):
        pass

    def testQuizFailTextIsEmpty(self):
        pass

    def testQuizObjectCreatedCaseOne(self):
        testParams = self.TestParams(self.topic)
        form = QuizCreateForm(self.request, data=testParams.getData())

        self.assertTrue(form.is_valid())

        newQuiz = form.save()
        self.assertEqual(testParams.name, newQuiz.name)
        self.assertEqual(testParams.description, newQuiz.description)
        self.assertEqual(generalOperations.parseStringToUrl(testParams.link), newQuiz.url)
        self.assertEqual(self.topic, newQuiz.topic)
        self.assertEqual(1, newQuiz.numberOfQuestions)
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

        def __init__(self, topic):
            faker = Faker()
            CHECKBOX = ['on', 'off']

            self.name = faker.pystr_format()
            self.description = faker.paragraph()
            self.link = faker.paragraph()
            self.subject = topic.subject.id
            self.topic = topic.id
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
