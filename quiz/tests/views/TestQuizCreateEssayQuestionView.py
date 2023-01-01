from django.http import QueryDict
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.forms import EssayQuestionCreateForm


class QuizCreateEssayQuestionViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizCreateEssayQuestionViewTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.request.user)
        self.path = reverse('quiz:create-essay-question-view', kwargs={'quizId': self.quiz.id})

    def testCreateEssayQuestionViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/essayQuestionTemplateView.html')
        self.assertTrue(isinstance(response.context['form'], EssayQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Essay Question')

    def testQuizDoesNotExist(self):
        path = reverse('quiz:create-essay-question-view', kwargs={'quizId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testFormIsInvalidAndObjectIsNotCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            mark=-1,
            answer='test answer'
        )
        response = self.post(testParams.getData())
        self.assertEquals(response.status_code, 200)
        self.assertEqual(0, self.quiz.getQuestions().count())
        self.assertTrue(isinstance(response.context['form'], EssayQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Essay Question')
        self.assertTemplateUsed(response, 'quiz/essayQuestionTemplateView.html')

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
        self.assertEqual(1, self.quiz.getQuestions().count())

        self.assertEqual(question.figure, testParams.figure)
        self.assertEqual(question.content, testParams.content)
        self.assertEqual(question.explanation, testParams.explanation)
        self.assertEqual(question.mark, testParams.mark)
        self.assertEqual(question.essayQuestion.answer, testParams.answer)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], EssayQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Essay Question')
        self.assertTemplateUsed(response, 'quiz/essayQuestionTemplateView.html')

    class TestParams:

        def __init__(self, figure=None, content=None, explanation=None, mark=None, answer=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.answer = answer

            pass

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
