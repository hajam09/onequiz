# from unittest.mock import patch
#
# from django.contrib.auth.models import User
# from django.urls import reverse
#
# from core.forms import EssayQuestionResponseForm, TrueOrFalseQuestionResponseForm, MultipleChoiceQuestionResponseForm
# from core.models import QuizAttempt, Subject, Question
# from onequiz.operations import bakerOperations
# from onequiz.tests.BaseTestViews import BaseTestViews
#
#
# class QuizAttemptSubmissionPreviewTest(BaseTestViews):
#     # test update
#
#     def setUp(self, path=None) -> None:
#         super(QuizAttemptSubmissionPreviewTest, self).setUp('')
#         bakerOperations.createSubjects(1)
#         self.subject = Subject.objects.first()
#
#         self.quiz = bakerOperations.createQuiz(self.user, self.subject)
#         self.essayQuestion = bakerOperations.createEssayQuestion()
#         self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion()
#         self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers()
#         self.quizAttempt = QuizAttempt.objects.create(user=self.user, quiz_id=self.quiz.id)
#         self.quiz.questions.add(*[self.essayQuestion, self.trueOrFalseQuestion, self.multipleChoiceQuestion])
#         self.path = reverse('core:quiz-attempt-submission-preview', kwargs={'url': self.quizAttempt.url})
#
#     def testGivenQuizAttemptDoesNotExistsThenReturn404(self):
#         self.path = reverse('core:quiz-attempt-submission-preview', kwargs={'url': 'non-existing-url'})
#         response = self.get()
#         self.assertEqual(response.status_code, 404)
#
#     @patch.object(QuizAttempt, 'hasQuizEnded', return_value=True)
#     def testOnAQuizAttemptIfQuizEndedThenUpdateStatus(self, mockHasQuizEnded):
#         response = self.get()
#         self.quizAttempt.refresh_from_db()
#         self.assertEqual(self.quizAttempt.status, QuizAttempt.Status.SUBMITTED)
#         self.assertEqual(response.status_code, 200)
#
#     def testWhenARandomUserVisitsQuizAttemptThenRaiseForbiddenResponse(self):
#         User.objects.create_user(username='random-user', password='random-password')
#         self.client.login(username='random-user', password='random-password')
#         response = self.get()
#         self.assertEqual(response.status_code, 403)
#
#     def testWhenResponseDoesNotExistForQuestionsThenCreateResponse(self):
#         response = self.get()
#         self.assertEqual(3, self.quizAttempt.responses.count())
#         self.quizAttempt.responses.filter(question__questionType=Question.Type.ESSAY)
#         self.assertTrue(self.quizAttempt.responses.filter(question__questionType=Question.Type.ESSAY).exists())
#         self.assertTrue(self.quizAttempt.responses.filter(question__questionType=Question.Type.TRUE_OR_FALSE).exists())
#         self.assertTrue(
#             self.quizAttempt.responses.filter(question__questionType=Question.Type.MULTIPLE_CHOICE).exists()
#         )
#
#         self.assertEqual(response.status_code, 200)
#         e = next(form for form in response.context['forms'] if isinstance(form, EssayQuestionResponseForm))
#         self.assertIsNotNone(e)
#         self.assertEqual('disabled', e.fields.get('answer').widget.attrs.get('disabled'))
#
#         t = next(form for form in response.context['forms'] if isinstance(form, TrueOrFalseQuestionResponseForm))
#         self.assertIsNotNone(e)
#         self.assertEqual('disabled', t.fields.get('trueOrFalse').widget.attrs.get('disabled'))
#
#         m = next(form for form in response.context['forms'] if isinstance(form, MultipleChoiceQuestionResponseForm))
#         self.assertIsNotNone(m)
#         self.assertEqual('disabled', m.fields.get('options').widget.attrs.get('disabled'))
#
#         self.assertEqual(self.quizAttempt, response.context['quizAttempt'])
#         self.assertTemplateUsed(response, 'core/quizAttemptReviewView.html')
