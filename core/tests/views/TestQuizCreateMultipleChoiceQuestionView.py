from django.http import QueryDict
from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from core.forms import MultipleChoiceQuestionCreateForm
from core.models import Question


class QuizCreateMultipleChoiceQuestionViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        super(QuizCreateMultipleChoiceQuestionViewTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.request.user)
        self.path = reverse('core:multiple-choice-question-create-view', kwargs={'quizId': self.quiz.id})

    def testCreateMultipleChoiceQuestionViewGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Multiple Choice Question')
        self.assertTemplateUsed(response, 'core/multipleChoiceQuestionTemplateView.html')

    def testQuizDoesNotExist(self):
        path = reverse('core:multiple-choice-question-create-view', kwargs={'quizId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testFormIsInvalidAndObjectIsNotCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            mark=-1,
            answerOrder=Question.Order.RANDOM
        )
        response = self.post(testParams.getData())
        self.assertEquals(response.status_code, 200)
        self.assertEqual(0, self.quiz.getQuestions().count())
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Multiple Choice Question')
        self.assertTemplateUsed(response, 'core/multipleChoiceQuestionTemplateView.html')

    def testFormIsValidAndObjectIsCreated(self):
        testParams = self.TestParams(
            figure='',
            content='test content',
            explanation='test explanation',
            answerOrder=Question.Order.RANDOM,
            choices=[(1, 'Answer 1', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
        )

        response = self.post(testParams.getData(True))
        question = self.quiz.getQuestions().first()
        self.assertEqual(1, self.quiz.getQuestions().count())

        self.assertEquals(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], MultipleChoiceQuestionCreateForm))
        self.assertTrue(response.context['formTitle'], 'Create Multiple Choice Question')
        self.assertTemplateUsed(response, 'core/multipleChoiceQuestionTemplateView.html')

        self.assertEqual(question.figure, testParams.figure)
        self.assertEqual(question.content, testParams.content)
        self.assertEqual(question.explanation, testParams.explanation)
        self.assertEqual(question.mark, testParams.mark)
        self.assertEqual(question.choicesOrder, testParams.answerOrder)

        choiceList = question.choices['choices']
        self.assertListEqual(
            [(i['content'], i['isChecked']) for i in choiceList], [(i[1], i[2]) for i in testParams.choices]
        )

    class TestParams:

        def __init__(self, figure=None, content=None, explanation=None, mark=80, answerOrder=None, choices=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.answerOrder = answerOrder
            self.choices = choices

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

                for answer in self.choices:
                    if answer[2]:
                        data[f'answerChecked-{answer[0]}'] = 'on'
                    answerTextList.append(answer[1])

                data['answerOptions'] = answerTextList

            queryDict.update(data)
            return queryDict
