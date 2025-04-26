import random

from django.contrib.auth.models import User
from django.core.paginator import Page
from django.urls import reverse
from parameterized import parameterized

from core.models import Quiz
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizListViewTest(BaseTestViews):
    def setUp(self, path=reverse('core:quiz-list-view')) -> None:
        super(QuizListViewTest, self).setUp(path)
        bakerOperations.createUser()
        allUsers = User.objects.all()

        self.quizList = []
        for _ in range(15):
            quiz = bakerOperations.createQuiz(creator=random.choice(allUsers), save=False)
            quiz.isDraft = False
            self.quizList.append(quiz)
        Quiz.objects.bulk_create(self.quizList)

    def testQuizListViewGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['quizList'], Page)
        self.assertEqual(len(response.context['quizList']), 10)
        self.assertTemplateUsed(response, 'core/quizListView.html')

    @parameterized.expand([
        [1, 10],
        [2, 5],
        ['abc', 10],
        [100, 5],
    ])
    def testPaginationPages(self, pageNumber, numberOfQuizzes):
        response = self.get(path=f'{self.path}?page={pageNumber}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizList']), numberOfQuizzes)

    def testOnlyNonDraftQuizzesDisplayed(self):
        draftQuiz = bakerOperations.createQuiz(self.request.user)
        draftQuiz.isDraft = True
        draftQuiz.save()
        response = self.get()
        self.assertNotIn(draftQuiz, response.context['quizList'])

    def testSearchEmptyQueryReturnsAllNonDraft(self):
        response = self.get(path=f'{self.path}?query=')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['quizList'].paginator.count, len(self.quizList))

    def testSearchWhitespaceQueryReturnsAllNonDraft(self):
        response = self.get(path=f'{self.path}?query=   ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['quizList'].paginator.count, len(self.quizList))

    @parameterized.expand([
        'name',
        'description',
        'url',
        'topic',
        'subject',
    ])
    def testSearchQuizForQuizByField(self, field):
        query = getattr(self.quizList[0], field)
        expected = [i for i in self.quizList if query.lower() in getattr(i, field).lower()]
        response = self.get(path=f'{self.path}?query={query}')
        self.assertEqual(response.status_code, 200)
        actualQuizzes = list(response.context['quizList'].object_list)
        self.assertEqual(len(expected), len(actualQuizzes))
        for quiz in actualQuizzes:
            self.assertIn(query.lower(), getattr(quiz, field).lower())
