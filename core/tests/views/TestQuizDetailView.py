# from unittest.mock import patch
#
# from django.db.models import QuerySet
# from django.urls import reverse
#
# from core.forms import QuizUpdateForm
# from core.models import Subject
# from onequiz.operations import bakerOperations
# from onequiz.settings import TEST_PASSWORD
# from onequiz.tests.BaseTestViews import BaseTestViews
#
#
# class QuizDetailViewTest(BaseTestViews):
#
#     def setUp(self, path=None) -> None:
#         super(QuizDetailViewTest, self).setUp('')
#         bakerOperations.createSubjects(1)
#         self.subject = Subject.objects.first()
#         self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
#         self.path = reverse('core:quiz-update-view', kwargs={'url': self.quiz.url})
#
#     def testQuizDetailViewGetForCreator(self):
#         response = self.get()
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['form'], QuizUpdateForm))
#         self.assertTrue(response.context['formTitle'], 'View or Update Quiz')
#         self.assertTrue(response.context['quiz'], self.quiz)
#         self.assertEqual(len(response.context['quizQuestions']), 0)
#         self.assertTrue(isinstance(response.context['quizQuestions'], QuerySet))
#         self.assertTemplateUsed(response, 'core/quizTemplateView.html')
#
#     def testQuizDetailViewGetForAnotherUser(self):
#         user2 = bakerOperations.createUser()
#         self.client.login(username=user2.username, password=TEST_PASSWORD)
#         response = self.get()
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['form'], QuizUpdateForm))
#         self.assertTrue(response.context['formTitle'], 'View Quiz')
#         self.assertTrue(response.context['quiz'], self.quiz)
#         self.assertEqual(len(response.context['quizQuestions']), 0)
#         self.assertTrue(isinstance(response.context['quizQuestions'], QuerySet))
#         self.assertTemplateUsed(response, 'core/quizTemplateView.html')
#
#     def testQuizDoesNotExist(self):
#         path = reverse('core:quiz-update-view', kwargs={'url': 'non-existing-url'})
#         response = self.get(path=path)
#         self.assertEqual(response.status_code, 404)
#
#     @patch('core.views.QuizUpdateForm.is_valid')
#     @patch('core.views.QuizUpdateForm.update')
#     def testSubmitQuizUpdateFormIsValid(self, form, update):
#         form.return_value = True
#         form.update = None
#         response = self.post()
#         self.assertEqual(response.status_code, 200)
