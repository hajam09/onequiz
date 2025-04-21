import random

from django.contrib.auth.models import User
from django.core.paginator import Page
from django.urls import reverse
from parameterized import parameterized

from core.models import Quiz
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizUserCreatedQuizzesViewTest(BaseTestViews):

    def setUp(self, path=reverse('core:user-created-quizzes-view')) -> None:
        super(QuizUserCreatedQuizzesViewTest, self).setUp(path)
        bakerOperations.createUsers(2)
        allUsers = User.objects.all()

        self.quizList = [
            bakerOperations.createQuiz(creator=random.choice(allUsers), save=False) for _ in range(5)
        ]
        Quiz.objects.bulk_create(self.quizList)

    def testUserCreatedQuizzesViewGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['quizList'], Page)
        self.assertEqual(len([q for q in self.quizList if q.creator == self.user]), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'core/quizListView.html')

    @parameterized.expand([
        'name',
        'description',
        'url',
        'topic',
        'subject',
    ])
    def testSearchQuizForQuizByField(self, field):
        query = getattr(self.quizList[0], field)
        quizWithQuery = [i for i in self.quizList if query in getattr(i, field) and i.creator == self.user]
        response = self.get(path=f'{self.path}?query={query}')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['quizList'], Page)
        self.assertEqual(len(quizWithQuery), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'core/quizListView.html')
