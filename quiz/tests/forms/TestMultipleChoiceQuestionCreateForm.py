from django.http import QueryDict

from onequiz.tests.BaseTest import BaseTest
from quiz.forms import MultipleChoiceQuestionCreateForm
from quiz.models import MultipleChoiceQuestion


class MultipleChoiceQuestionCreateFormTest(BaseTest):

    def setUp(self, path='') -> None:
        self.basePath = path
        super(MultipleChoiceQuestionCreateFormTest, self).setUp('')

    def testInitialValues(self):
        form = MultipleChoiceQuestionCreateForm()
        ANSWER_ORDER_CHOICES = [
            (None, '-- Select a value --'),
            ('SEQUENTIAL', 'Sequential'),
            ('RANDOM', 'Random'),
            ('NONE', 'None'),
        ]
        ANSWER_OPTIONS = [
            (1, '', False),
            (2, '', False)
        ]

        self.assertIn('initialAnswerOptions', form.initial)
        self.assertIn('answerOrder', form.base_fields)
        self.assertListEqual(form.base_fields.get('answerOrder').choices, ANSWER_ORDER_CHOICES)
        self.assertListEqual(form.initial.get('initialAnswerOptions'), ANSWER_OPTIONS)

    def testFigureAndColumnIsEmpty(self):
        testParams = self.TestParams(
            answerOrder=MultipleChoiceQuestion.Order.SEQUENTIAL
        )
        form = MultipleChoiceQuestionCreateForm(data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors))
        self.assertTrue(form.has_error('figure'))
        self.assertTrue(form.has_error('content'))
        self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('figure')[0])
        self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('content')[0])

    def testMarkIsLessThanZero(self):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            answerOrder=MultipleChoiceQuestion.Order.SEQUENTIAL
        )
        form = MultipleChoiceQuestionCreateForm(data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testAnswerOrderOptionIsUnSelected(self):
        testParams = self.TestParams(
            content='test content',
        )
        form = MultipleChoiceQuestionCreateForm(data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('answerOrder'))
        self.assertEqual('Answer Order is empty.', form.errors.get('answerOrder')[0])

    def testMaintainAnswerOrderOptionWhenFormHasError(self):
        testParams = self.TestParams(
            answerOrder=MultipleChoiceQuestion.Order.RANDOM
        )
        form = MultipleChoiceQuestionCreateForm(data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertIn('answerOrder', form.data)
        self.assertIn(testParams.answerOrder, form.data.get('answerOrder'))

    def testMaintainAnswerOptionsListWhenFormHasError(self):
        testParams = self.TestParams(
            content='test content',
            answerOrder=MultipleChoiceQuestion.Order.RANDOM,
            answerOptions=[(1, '', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
        )
        form = MultipleChoiceQuestionCreateForm(data=testParams.getData(True))

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('initialAnswerOptions'))
        self.assertEqual('One of your answer options is empty or invalid. Please try again.', form.errors.get('initialAnswerOptions')[0])
        self.assertIn('initialAnswerOptions', form.initial)
        self.assertListEqual(form.initial.get('initialAnswerOptions'), testParams.answerOptions)

    def testMultipleChoiceQuestionAndAnswerObjectsCreated(self):
        testParams = self.TestParams(
            content='test content',
            answerOrder=MultipleChoiceQuestion.Order.RANDOM,
            answerOptions=[(1, 'Answer 1', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
        )
        form = MultipleChoiceQuestionCreateForm(data=testParams.getData(True))

        self.assertTrue(form.is_valid())
        self.assertEqual(0, len(form.errors))
        self.assertIn('initialAnswerOptions', form.initial)
        self.assertListEqual(form.initial.get('initialAnswerOptions'), testParams.answerOptions)

        newMultipleChoiceQuestion = form.save()

        # self.assertIsNone(newMultipleChoiceQuestion.figure)
        self.assertEqual(testParams.content, newMultipleChoiceQuestion.content)
        self.assertEqual('', newMultipleChoiceQuestion.explanation)
        self.assertEqual(testParams.mark, newMultipleChoiceQuestion.mark)
        self.assertEqual(testParams.answerOrder, newMultipleChoiceQuestion.answerOrder)

        answerList = newMultipleChoiceQuestion.getAnswers()
        self.assertListEqual([(i.content, i.isCorrect) for i in answerList], [(i[1], i[2]) for i in testParams.answerOptions])

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
                answerTextCheckedDict = {}

                for answer in self.answerOptions:
                    if answer[2]:
                        answerTextCheckedDict[f'answerChecked{answer[0]}'] = 'on'
                    answerTextList.append(answer[1])

                queryDict.setlist('answerOptions', answerTextList)
                data.update(answerTextCheckedDict)

            queryDict.update(data)
            return queryDict