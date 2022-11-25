from unittest.mock import patch

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.forms import EssayQuestionUpdateForm, TrueOrFalseQuestionUpdateForm, MultipleChoiceQuestionUpdateForm
from quiz.models import Topic


class QuizQuestionDetailViewTest(BaseTestViews):

    def setUp(self, path='') -> None:
        super(QuizQuestionDetailViewTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics()
        self.topic = Topic.objects.select_related('subject').first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.essayQuestion = bakerOperations.createEssayQuestion()
        self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion()
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers(None)
        self.quiz.questions.add(*[
            self.essayQuestion,
            self.trueOrFalseQuestion,
            self.multipleChoiceQuestion,
        ])

    def testQuizDoesNotExist(self):
        path = reverse('quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testGetEssayQuestionUpdateForm(self):
        path = reverse(
            'quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': self.essayQuestion.id}
        )
        response = self.get(path=path)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], EssayQuestionUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update Essay Question')
        self.assertTemplateUsed(response, 'quiz/essayQuestionTemplateView.html')

    @patch('quiz.views.EssayQuestionUpdateForm.is_valid')
    @patch('quiz.views.EssayQuestionUpdateForm.update')
    def testSubmitEssayQuestionUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        path = reverse(
            'quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': self.essayQuestion.id}
        )
        response = self.post(path=path)
        self.assertEquals(response.status_code, 200)

    def testGetTrueOrFalseQuestionUpdateForm(self):
        path = reverse(
            'quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': self.trueOrFalseQuestion.id}
        )
        response = self.get(path=path)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], TrueOrFalseQuestionUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update True or False Question')
        self.assertTemplateUsed(response, 'quiz/trueOrFalseQuestionTemplateView.html')

    @patch('quiz.views.TrueOrFalseQuestionUpdateForm.is_valid')
    @patch('quiz.views.TrueOrFalseQuestionUpdateForm.update')
    def testSubmitTrueOrFalseQuestionUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        path = reverse(
            'quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': self.trueOrFalseQuestion.id}
        )
        response = self.post(path=path)
        self.assertEquals(response.status_code, 200)

    def testGetMultipleChoiceQuestionUpdateForm(self):
        path = reverse(
            'quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': self.multipleChoiceQuestion.id}
        )
        response = self.get(path=path)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update Multiple Choice Question')
        self.assertTemplateUsed(response, 'quiz/multipleChoiceQuestionTemplateView.html')

    @patch('quiz.views.MultipleChoiceQuestionUpdateForm.is_valid')
    @patch('quiz.views.MultipleChoiceQuestionUpdateForm.update')
    def testSubmitMultipleChoiceQuestionUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        path = reverse(
            'quiz:question-detail-view', kwargs={'quizId': self.quiz.id, 'questionId': self.multipleChoiceQuestion.id}
        )
        response = self.post(path=path)
        self.assertEquals(response.status_code, 200)
