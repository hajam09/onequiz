from django.db.models import QuerySet
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.models import Topic, Quiz


class QuizUserCreatedQuizzesViewTest(BaseTestViews):

    def setUp(self, path=reverse('quiz:user-created-quizzes-view')) -> None:
        super(QuizUserCreatedQuizzesViewTest, self).setUp('')
        self.path = reverse('quiz:user-created-quizzes-view')
        bakerOperations.createSubjectsAndTopics()
        self.topic = Topic.objects.select_related('subject').first()
        self.quizList = [
            bakerOperations.createQuiz(creator=self.request.user, topic=self.topic, save=False) for _ in range(5)
        ]
        Quiz.objects.bulk_create(self.quizList)

    def testUserCreatedQuizzesViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(self.quizList), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')

    def testSearchQuizForQuizName(self):
        query = self.quizList[0].name
        quizWithName = [i for i in self.quizList if query in i.name]
        path = f"{reverse('quiz:user-created-quizzes-view')}?query={query}"
        response = self.get(path=path)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithName), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')

    def testSearchQuizForQuizDescription(self):
        query = self.quizList[0].description
        quizWithDescription = [i for i in self.quizList if query in i.description]
        path = f"{reverse('quiz:user-created-quizzes-view')}?query={query}"
        response = self.get(path=path)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithDescription), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')

    def testSearchQuizForTopicName(self):
        query = self.quizList[0].topic.name
        quizWithTopicName = [i for i in self.quizList if query in i.topic.name]
        path = f"{reverse('quiz:user-created-quizzes-view')}?query={query}"
        response = self.get(path=path)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithTopicName), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')

    def testSearchQuizForTopicDescription(self):
        query = self.quizList[0].topic.description
        quizWithTopicDescription = [i for i in self.quizList if query in i.topic.description]
        path = f"{reverse('quiz:user-created-quizzes-view')}?query={query}"
        response = self.get(path=path)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithTopicDescription), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')

    def testSearchQuizForSubjectName(self):
        query = self.quizList[0].topic.subject.name
        quizWithSubjectName = [i for i in self.quizList if query in i.topic.subject.name]
        path = f"{reverse('quiz:user-created-quizzes-view')}?query={query}"
        response = self.get(path=path)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithSubjectName), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')

    def testSearchQuizForSubjectDescription(self):
        query = self.quizList[0].topic.subject.description
        quizWithSubjectDescription = [i for i in self.quizList if query in i.topic.subject.description]
        path = f"{reverse('quiz:user-created-quizzes-view')}?query={query}"
        response = self.get(path=path)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['quizList'], QuerySet))
        self.assertEqual(len(quizWithSubjectDescription), len(response.context['quizList']))
        self.assertTemplateUsed(response, 'quiz/userCreatedQuizzesView.html')
