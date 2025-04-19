# from django.core.paginator import Page
# from django.urls import reverse
#
# from core.models import Subject, Quiz
# from onequiz.operations import bakerOperations
# from onequiz.tests.BaseTestViews import BaseTestViews
#
#
# class QuizUserCreatedQuizzesViewTest(BaseTestViews):
#
#     def setUp(self, path=reverse('core:user-created-quizzes-view')) -> None:
#         super(QuizUserCreatedQuizzesViewTest, self).setUp(path)
#         bakerOperations.createSubjects(1)
#         self.subject = Subject.objects.first()
#         self.quizList = [
#             bakerOperations.createQuiz(creator=self.request.user, subject=self.subject, save=False) for _ in range(5)
#         ]
#         Quiz.objects.bulk_create(self.quizList)
#
#     def testUserCreatedQuizzesViewGet(self):
#         response = self.get()
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['quizList'], Page))
#         self.assertEqual(len(self.quizList), len(response.context['quizList']))
#         self.assertTemplateUsed(response, 'core/quizListView.html')
#
#     def testSearchQuizForQuizName(self):
#         query = self.quizList[0].name
#         quizWithName = [i for i in self.quizList if query in i.name]
#         response = self.get(path=f"{self.path}?query={query}")
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['quizList'], Page))
#         self.assertEqual(len(quizWithName), len(response.context['quizList']))
#         self.assertTemplateUsed(response, 'core/quizListView.html')
#
#     def testSearchQuizForQuizDescription(self):
#         query = self.quizList[0].description
#         quizWithDescription = [i for i in self.quizList if query in i.description]
#         response = self.get(path=f"{self.path}?query={query}")
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['quizList'], Page))
#         self.assertEqual(len(quizWithDescription), len(response.context['quizList']))
#         self.assertTemplateUsed(response, 'core/quizListView.html')
#
#     def testSearchQuizForTopic(self):
#         query = self.quizList[0].topic
#         quizWithTopicName = [i for i in self.quizList if query in i.topic]
#         response = self.get(path=f"{self.path}?query={query}")
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['quizList'], Page))
#         self.assertEqual(len(quizWithTopicName), len(response.context['quizList']))
#         self.assertTemplateUsed(response, 'core/quizListView.html')
#
#     def testSearchQuizForSubjectName(self):
#         query = self.quizList[0].subject.name
#         quizWithSubjectName = [i for i in self.quizList if query in i.subject.name]
#         response = self.get(path=f"{self.path}?query={query}")
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['quizList'], Page))
#         self.assertEqual(len(quizWithSubjectName), len(response.context['quizList']))
#         self.assertTemplateUsed(response, 'core/quizListView.html')
#
#     def testSearchQuizForSubjectDescription(self):
#         query = self.quizList[0].subject.description
#         quizWithSubjectDescription = [i for i in self.quizList if query in i.subject.description]
#         response = self.get(path=f"{self.path}?query={query}")
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['quizList'], Page))
#         self.assertEqual(len(quizWithSubjectDescription), len(response.context['quizList']))
#         self.assertTemplateUsed(response, 'core/quizListView.html')
