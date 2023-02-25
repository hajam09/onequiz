import random

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.models import Quiz


class QuizIndexViewTest(BaseTestViews):
    def setUp(self, path=reverse('quiz:index-view')) -> None:
        super(QuizIndexViewTest, self).setUp(path)
        self.subject = bakerOperations.createSubjects(1).first()
        bakerOperations.createUsers(maxLimit=2)

        allUsers = User.objects.all()
        self.quizList = [
            bakerOperations.createQuiz(creator=random.choice(allUsers), subject=self.subject, save=False)
            for _ in range(allUsers.count())
        ]
        Quiz.objects.bulk_create(self.quizList)

    def testIndexViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(self.quizList), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')

    def testSearchQuizForQuizName(self):
        query = self.quizList[0].name
        quizWithName = [i for i in self.quizList if query in i.name]
        response = self.get(path=f"{self.path}?query={query}")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithName), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')

    def testSearchQuizForQuizDescription(self):
        query = self.quizList[0].description
        quizWithDescription = [i for i in self.quizList if query in i.description]
        response = self.get(path=f"{self.path}?query={query}")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithDescription), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')

    def testSearchQuizForSubjectName(self):
        query = self.quizList[0].subject.name
        quizWithSubjectName = [i for i in self.quizList if query in i.subject.name]
        response = self.get(path=f"{self.path}?query={query}")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithSubjectName), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')

    def testSearchQuizForSubjectDescription(self):
        query = self.quizList[0].subject.description
        quizWithSubjectDescription = [i for i in self.quizList if query in i.subject.description]
        response = self.get(path=f"{self.path}?query={query}")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithSubjectDescription), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')

    def testSearchQuizForSubjectName(self):
        query = self.quizList[0].subject.name
        quizWithSubjectName = [i for i in self.quizList if query in i.subject.name]
        response = self.get(path=f"{self.path}?query={query}")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithSubjectName), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')

    def testSearchQuizForSubjectDescription(self):
        query = self.quizList[0].subject.description
        quizWithSubjectDescription = [i for i in self.quizList if query in i.subject.description]
        response = self.get(path=f"{self.path}?query={query}")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithSubjectDescription), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/quizListView.html')
