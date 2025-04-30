from django.http import QueryDict
from django.urls import reverse

from core.forms import EssayQuestionCreateForm
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizCreateEssayQuestionViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizCreateEssayQuestionViewTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.request.user)
        self.path = reverse('core:essay-question-create-view', kwargs={'url': self.quiz.url})

    def testCreateEssayQuestionViewGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], EssayQuestionCreateForm)
        self.assertTrue(response.context['formTitle'], 'Create Essay Question')
        self.assertTemplateUsed(response, 'core/essayQuestionTemplateView.html')

    def testQuizDoesNotExist(self):
        path = reverse('core:essay-question-create-view', kwargs={'url': 'non-existing-url'})
        response = self.get(path=path)
        self.assertEqual(response.status_code, 404)

    def testFormIsInvalidAndObjectIsNotCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            mark=-1,
            answer='test answer'
        )
        response = self.post(testParams.getData())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.quiz.getQuestions().count(), 0)
        self.assertIsInstance(response.context['form'], EssayQuestionCreateForm)
        self.assertTrue(response.context['formTitle'], 'Create Essay Question')
        self.assertTemplateUsed(response, 'core/essayQuestionTemplateView.html')

    def testFormIsValidAndObjectIsCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            mark=80,
            answer='test answer'
        )
        response = self.post(testParams.getData())
        question = self.quiz.getQuestions().first()
        self.assertEqual(self.quiz.getQuestions().count(), 1)

        self.assertEqual(question.figure, testParams.figure)
        self.assertEqual(question.content, testParams.content)
        self.assertEqual(question.explanation, testParams.explanation)
        self.assertEqual(question.mark, testParams.mark)
        self.assertEqual(question.answer, testParams.answer)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], EssayQuestionCreateForm)
        self.assertTrue(response.context['formTitle'], 'Create Essay Question')
        self.assertTemplateUsed(response, 'core/essayQuestionTemplateView.html')

    class TestParams:
        def __init__(self, figure=None, content=None, explanation=None, mark=None, answer=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.answer = answer

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'answer': self.answer,
            }

            queryDict = QueryDict('', mutable=True)
            queryDict.update(data)
            return queryDict
