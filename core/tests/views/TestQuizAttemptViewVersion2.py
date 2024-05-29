from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from parameterized import parameterized

from core.forms import EssayQuestionResponseForm, TrueOrFalseQuestionResponseForm, MultipleChoiceQuestionResponseForm
from core.models import QuizAttempt, Subject, Response, Question
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizAttemptViewVersion2Test(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizAttemptViewVersion2Test, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()

        self.quiz = bakerOperations.createQuiz(self.user, self.subject)
        self.essayQuestion = bakerOperations.createEssayQuestion()
        self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion()
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers()
        self.quizAttempt = QuizAttempt.objects.create(user=self.user, quiz_id=self.quiz.id)
        self.quiz.questions.add(*[self.essayQuestion, self.trueOrFalseQuestion, self.multipleChoiceQuestion])
        self.path = reverse('core:quiz-attempt-view-v2', kwargs={'attemptId': self.quizAttempt.id})

    def testGivenQuizAttemptDoesNotExistsThenReturn404(self):
        self.path = reverse('core:quiz-attempt-view-v2', kwargs={'attemptId': 0})
        response = self.get()
        self.assertEqual(response.status_code, 404)

    @patch.object(QuizAttempt, 'hasQuizEnded', return_value=True)
    def testOnAQuizAttemptIfQuizEndedThenUpdateStatus(self, mockHasQuizEnded):
        response = self.get()
        self.quizAttempt.refresh_from_db()
        self.assertEqual(self.quizAttempt.status, QuizAttempt.Status.SUBMITTED)
        self.assertEqual(response.status_code, 200)

    def testWhenARandomUserVisitsQuizAttemptThenRaiseForbiddenResponse(self):
        User.objects.create_user(username='random-user', password='random-password')
        self.client.login(username='random-user', password='random-password')
        response = self.get()
        self.assertEqual(response.status_code, 403)

    def testWhenAnEssayResponseIsSubmittedThenUpdateItSuccessfully(self):
        self.path += '?q=2'
        self.quizAttempt.status = QuizAttempt.Status.IN_PROGRESS

        responseObject = Response.objects.create(question=self.essayQuestion)
        self.quizAttempt.responses.add(responseObject)

        response = self.post({'answer': 'new-answer'})
        self.assertEqual(response.status_code, 200)
        responseObject.refresh_from_db()
        self.assertEqual(responseObject.answer, 'new-answer')

    @parameterized.expand([
        ['True', True],
        ['False', False],
    ])
    def testWhenATrueOrFalseResponseIsSubmittedThenUpdateItSuccessfully(self, selected, updated):
        self.path += '?q=3'
        self.quizAttempt.status = QuizAttempt.Status.IN_PROGRESS

        responseObject = Response.objects.create(question=self.trueOrFalseQuestion)
        self.quizAttempt.responses.add(responseObject)

        response = self.post({'trueOrFalse': selected})
        self.assertEqual(response.status_code, 200)
        responseObject.refresh_from_db()
        self.assertEqual(updated, responseObject.trueSelected)

    def testWhenAMultipleChoiceResponseIsSubmittedThenUpdateItSuccessfully(self):
        pass

    def testGivenTheQuestionIndexPassesNumberOfQuestionThenRedirectToQuizAttemptSubmissionView(self):
        self.path += '?q=100'
        self.quizAttempt.status = QuizAttempt.Status.IN_PROGRESS
        response = self.get()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/v2/quiz-attempt/{self.quizAttempt.id}/preview/')

    def testDuringQuizAttemptWhenUserLoadsNewQuestionThenCreateEssayResponseForm(self):
        self.path += '?q=1'
        response = self.get()
        responseObject = Response.objects.first()

        self.assertEqual(200, response.status_code)
        self.assertEqual(Question.Type.ESSAY, responseObject.question.questionType)

        self.assertIn('quizAttempt', response.context)
        self.assertIn('questionPaginator', response.context)
        self.assertIn('form', response.context)
        self.assertIn('progress', response.context)

        self.assertEqual(response.context['quizAttempt'], self.quizAttempt)
        self.assertEqual(response.context['questionPaginator'].number, 1)
        self.assertIsInstance(response.context['form'], EssayQuestionResponseForm)
        self.assertEqual(response.context['progress'], 33.0)
        self.assertTemplateUsed(response, 'core/quizAttemptViewVersion2.html')

    def testDuringQuizAttemptWhenUserLoadsNewQuestionThenCreateTrueOrFalseResponseForm(self):
        self.path += '?q=2'
        response = self.get()
        responseObject = Response.objects.first()

        self.assertEqual(200, response.status_code)
        self.assertEqual(Question.Type.TRUE_OR_FALSE, responseObject.question.questionType)

        self.assertIn('quizAttempt', response.context)
        self.assertIn('questionPaginator', response.context)
        self.assertIn('form', response.context)
        self.assertIn('progress', response.context)

        self.assertEqual(response.context['quizAttempt'], self.quizAttempt)
        self.assertEqual(response.context['questionPaginator'].number, 2)
        self.assertIsInstance(response.context['form'], TrueOrFalseQuestionResponseForm)
        self.assertEqual(response.context['progress'], 67.0)
        self.assertTemplateUsed(response, 'core/quizAttemptViewVersion2.html')

    def testDuringQuizAttemptWhenUserLoadsNewQuestionThenCreateMultipleChoiceResponseForm(self):
        self.path += '?q=3'
        response = self.get()
        responseObject = Response.objects.first()

        self.assertEqual(200, response.status_code)
        self.assertEqual(Question.Type.MULTIPLE_CHOICE, responseObject.question.questionType)

        self.assertIn('quizAttempt', response.context)
        self.assertIn('questionPaginator', response.context)
        self.assertIn('form', response.context)
        self.assertIn('progress', response.context)

        self.assertEqual(response.context['quizAttempt'], self.quizAttempt)
        self.assertEqual(response.context['questionPaginator'].number, 3)
        self.assertIsInstance(response.context['form'], MultipleChoiceQuestionResponseForm)
        self.assertEqual(response.context['progress'], 100.0)
        self.assertTemplateUsed(response, 'core/quizAttemptViewVersion2.html')
