from unittest.mock import patch

from django.urls import reverse
from model_utils.managers import InheritanceQuerySet

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.forms import QuizUpdateForm
from quiz.models import Topic


class QuizDetailViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizDetailViewTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 1)
        self.topic = Topic.objects.select_related('subject').first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.path = reverse('quiz:quiz-detail-view', kwargs={'quizId': self.quiz.id})

    def testQuizDetailViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], QuizUpdateForm))
        self.assertTrue(response.context['formTitle'], 'View or Update Quiz')
        self.assertTrue(response.context['quizId'], self.quiz.id)
        self.assertEqual(len(response.context['quizQuestions']), 0)
        self.assertTrue(isinstance(response.context['quizQuestions'], InheritanceQuerySet))
        self.assertTemplateUsed(response, 'quiz/quizTemplateView.html')

    def testQuizDoesNotExist(self):
        path = reverse('quiz:quiz-detail-view', kwargs={'quizId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    @patch('quiz.views.QuizUpdateForm.is_valid')
    @patch('quiz.views.QuizUpdateForm.update')
    def testSubmitQuizUpdateFormIsValid(self, form, update):
        form.return_value = True
        form.update = None
        response = self.post()
        self.assertEquals(response.status_code, 200)
