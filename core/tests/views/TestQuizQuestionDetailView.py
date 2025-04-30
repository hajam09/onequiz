from unittest.mock import patch, MagicMock

from django.urls import reverse

from core.forms import EssayQuestionUpdateForm, TrueOrFalseQuestionUpdateForm, MultipleChoiceQuestionUpdateForm
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizQuestionDetailViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super().setUp('')
        self.quiz = bakerOperations.createQuiz(self.request.user)
        self.essayQuestion = bakerOperations.createEssayQuestion(self.quiz)
        self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion(self.quiz)
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers(self.quiz)

    def testQuizDoesNotExist(self):
        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': 'non-existing-url'})
        response = self.get(path=path)
        self.assertEqual(response.status_code, 404)

    def testUnrelatedUserViewsQuestionDetailThenReturnNotFound(self):
        self.quiz.creator = bakerOperations.createUser()
        self.quiz.save()

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url})
        response = self.get(path=path)
        self.assertEqual(response.status_code, 404)

    def testGetEssayQuestionUpdateForm(self):
        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url})
        response = self.get(path=path)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], EssayQuestionUpdateForm)
        self.assertEqual(response.context['formTitle'], 'View or Update Essay Question')
        self.assertTemplateUsed(response, 'core/essayQuestionTemplateView.html')

    @patch('core.views.EssayQuestionUpdateForm')
    def testSubmitEssayQuestionUpdateFormIsValid(self, MockForm):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        MockForm.return_value = mock_form

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url})
        response = self.post(path=path)
        self.assertEqual(response.status_code, 200)

    @patch('core.views.EssayQuestionUpdateForm')
    def testSubmitEssayQuestionUpdateFormIsInvalid(self, MockForm):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = False
        MockForm.return_value = mock_form

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url})
        response = self.post(path=path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/essayQuestionTemplateView.html')

    def testGetTrueOrFalseQuestionUpdateForm(self):
        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.trueOrFalseQuestion.url})
        response = self.get(path=path)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TrueOrFalseQuestionUpdateForm)
        self.assertEqual(response.context['formTitle'], 'View or Update True or False Question')
        self.assertTemplateUsed(response, 'core/trueOrFalseQuestionTemplateView.html')

    @patch('core.views.TrueOrFalseQuestionUpdateForm')
    def testSubmitTrueOrFalseQuestionUpdateFormIsValid(self, MockForm):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        MockForm.return_value = mock_form

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.trueOrFalseQuestion.url})
        response = self.post(path=path)
        self.assertEqual(response.status_code, 200)

    @patch('core.views.TrueOrFalseQuestionUpdateForm')
    def testSubmitTrueOrFalseQuestionUpdateFormIsInvalid(self, MockForm):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = False
        MockForm.return_value = mock_form

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.trueOrFalseQuestion.url})
        response = self.post(path=path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/trueOrFalseQuestionTemplateView.html')

    def testGetMultipleChoiceQuestionUpdateForm(self):
        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.multipleChoiceQuestion.url})
        response = self.get(path=path)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], MultipleChoiceQuestionUpdateForm)
        self.assertEqual(response.context['formTitle'], 'View or Update Multiple Choice Question')
        self.assertTemplateUsed(response, 'core/multipleChoiceQuestionTemplateView.html')

    @patch('core.views.MultipleChoiceQuestionUpdateForm')
    def testSubmitMultipleChoiceQuestionUpdateFormIsValid(self, MockForm):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        MockForm.return_value = mock_form

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.multipleChoiceQuestion.url})
        response = self.post(path=path)
        self.assertEqual(response.status_code, 200)

    @patch('core.views.MultipleChoiceQuestionUpdateForm')
    def testSubmitMultipleChoiceQuestionUpdateFormIsInvalid(self, MockForm):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = False
        MockForm.return_value = mock_form

        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.multipleChoiceQuestion.url})
        response = self.post(path=path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/multipleChoiceQuestionTemplateView.html')
