# import random
#
# from django.contrib.auth.models import User
# from django.core.paginator import Page
# from django.urls import reverse
#
# from core.models import Subject, Quiz
# from onequiz.operations import bakerOperations
# from onequiz.tests.BaseTestViews import BaseTestViews
#
#
# class QuizListViewTest(BaseTestViews):
#     def setUp(self, path=reverse('core:quiz-list-view')) -> None:
#         super(QuizListViewTest, self).setUp(path)
#         bakerOperations.createSubjects(1)
#         bakerOperations.createUsers(maxLimit=2)
#
#         allUsers = User.objects.all()
#         self.subject = Subject.objects.first()
#         self.quizList = []
#         for _ in range(allUsers.count()):
#             quiz = bakerOperations.createQuiz(creator=random.choice(allUsers), subject=self.subject, save=False)
#             quiz.isDraft = False
#             self.quizList.append(quiz)
#         Quiz.objects.bulk_create(self.quizList)
#
#     def testQuizListViewGet(self):
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
