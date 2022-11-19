from django.http import QueryDict
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.forms import MultipleChoiceQuestionCreateForm
from quiz.models import MultipleChoiceQuestion


class QuizCreateMultipleChoiceQuestionViewTest(BaseTestViews):

    def setUp(self, path='') -> None:
        super(QuizCreateMultipleChoiceQuestionViewTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.request.user)
        self.path = reverse('quiz:create-multiple-choice-question-view', kwargs={'quizId': self.quiz.id})

    def testCreateMultipleChoiceQuestionViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Multiple Choice Question')
        self.assertTemplateUsed(response, 'quiz/multipleChoiceQuestionTemplateView.html')

    def testQuizDoesNotExist(self):
        path = reverse('quiz:create-multiple-choice-question-view', kwargs={'quizId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testFormIsInvalidAndObjectIsNotCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            mark=-1,
            answerOrder=MultipleChoiceQuestion.Order.RANDOM
        )
        response = self.post(testParams.getData())
        self.assertEquals(response.status_code, 200)
        self.assertEqual(0, self.quiz.getQuestions().count())
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Multiple Choice Question')
        self.assertTemplateUsed(response, 'quiz/multipleChoiceQuestionTemplateView.html')

    def testFormIsValidAndObjectIsCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            answerOrder=MultipleChoiceQuestion.Order.RANDOM,
            answerOptions=[(1, 'Answer 1', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
        )

        response = self.post(testParams.getData(True))
        newMultipleChoiceQuestion = self.quiz.getQuestions().first()
        self.assertEqual(1, self.quiz.getQuestions().count())

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Multiple Choice Question')
        self.assertTemplateUsed(response, 'quiz/multipleChoiceQuestionTemplateView.html')

        self.assertEqual(newMultipleChoiceQuestion.figure, testParams.figure)
        self.assertEqual(newMultipleChoiceQuestion.content, testParams.content)
        self.assertEqual(newMultipleChoiceQuestion.explanation, testParams.explanation)
        self.assertEqual(newMultipleChoiceQuestion.mark, testParams.mark)
        self.assertEqual(newMultipleChoiceQuestion.answerOrder, testParams.answerOrder)

        answerList = newMultipleChoiceQuestion.getAnswers()
        self.assertListEqual([(i.content, i.isCorrect) for i in answerList],
                             [(i[1], i[2]) for i in testParams.answerOptions])

    class TestParams:

        def __init__(self, figure=None, content=None, explanation=None, mark=80, answerOrder=None, answerOptions=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.answerOrder = answerOrder
            self.answerOptions = answerOptions

        def getData(self, withAnswerOptions=False):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'answerOrder': self.answerOrder
            }

            queryDict = QueryDict('', mutable=True)

            if withAnswerOptions:
                answerTextList = []

                for answer in self.answerOptions:
                    if answer[2]:
                        data[f'answerChecked{answer[0]}'] = 'on'
                    answerTextList.append(answer[1])

                data['answerOptions'] = answerTextList

            queryDict.update(data)
            return queryDict
