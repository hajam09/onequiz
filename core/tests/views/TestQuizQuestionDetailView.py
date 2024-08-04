from unittest.mock import patch

from django.urls import reverse

from core.forms import EssayQuestionUpdateForm, TrueOrFalseQuestionUpdateForm, MultipleChoiceQuestionUpdateForm
from core.models import Subject
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizQuestionDetailViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizQuestionDetailViewTest, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.essayQuestion = bakerOperations.createEssayQuestion()
        self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion()
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers()
        self.quiz.questions.add(*[
            self.essayQuestion,
            self.trueOrFalseQuestion,
            self.multipleChoiceQuestion,
        ])

    def testQuizDoesNotExist(self):
        path = reverse('core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': 'non-existing-url'})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testGetEssayQuestionUpdateForm(self):
        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url}
        )
        response = self.get(path=path)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], EssayQuestionUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update Essay Question')
        self.assertTemplateUsed(response, 'core/essayQuestionTemplateView.html')

    @patch('core.views.EssayQuestionUpdateForm.is_valid')
    @patch('core.views.EssayQuestionUpdateForm.update')
    def testSubmitEssayQuestionUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url}
        )
        response = self.post(path=path)
        self.assertEquals(response.status_code, 200)

    def testGetTrueOrFalseQuestionUpdateForm(self):
        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.trueOrFalseQuestion.url}
        )
        response = self.get(path=path)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], TrueOrFalseQuestionUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update True or False Question')
        self.assertTemplateUsed(response, 'core/trueOrFalseQuestionTemplateView.html')

    @patch('core.views.TrueOrFalseQuestionUpdateForm.is_valid')
    @patch('core.views.TrueOrFalseQuestionUpdateForm.update')
    def testSubmitTrueOrFalseQuestionUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.trueOrFalseQuestion.url}
        )
        response = self.post(path=path)
        self.assertEquals(response.status_code, 200)

    def testGetMultipleChoiceQuestionUpdateForm(self):
        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.multipleChoiceQuestion.url}
        )
        response = self.get(path=path)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update Multiple Choice Question')
        self.assertTemplateUsed(response, 'core/multipleChoiceQuestionTemplateView.html')

    @patch('core.views.MultipleChoiceQuestionUpdateForm.is_valid')
    @patch('core.views.MultipleChoiceQuestionUpdateForm.update')
    def testSubmitMultipleChoiceQuestionUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.multipleChoiceQuestion.url}
        )
        response = self.post(path=path)
        self.assertEquals(response.status_code, 200)

    def testUnrelatedUserViewsQuestionDetailThenReturnNotFound(self):
        self.quiz.creator = bakerOperations.createUser()
        self.quiz.save()

        path = reverse(
            'core:question-update-view', kwargs={'quizUrl': self.quiz.url, 'questionUrl': self.essayQuestion.url}
        )
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)
        self.assertEqual(response.reason_phrase, 'Not Found')
