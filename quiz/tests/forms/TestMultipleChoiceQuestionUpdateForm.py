from django import forms
from django.http import QueryDict

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest
from quiz.forms import MultipleChoiceQuestionUpdateForm
from quiz.models import MultipleChoiceQuestion


class MultipleChoiceQuestionUpdateFormTest(BaseTest):

    def setUp(self, path='') -> None:
        super(MultipleChoiceQuestionUpdateFormTest, self).setUp('')
        self.answerOrderChoices = [
            (None, '-- Select a value --'), ('SEQUENTIAL', 'Sequential'), ('RANDOM', 'Random'), ('NONE', 'None')
        ]
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers(None)
        self.choices = [
            (i, x['content'], x['isCorrect']) for i, x in enumerate(self.multipleChoiceQuestion.choices['choices'], 1)
        ]

    def testFieldsAndType(self):
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion)
        self.assertEqual(len(form.base_fields), 5)
        self.assertTrue(isinstance(form.base_fields.get('figure'), forms.ImageField))
        self.assertTrue(isinstance(form.base_fields.get('content'), forms.CharField))
        self.assertTrue(isinstance(form.base_fields.get('explanation'), forms.CharField))
        self.assertTrue(isinstance(form.base_fields.get('answerOrder'), forms.MultipleChoiceField))
        self.assertTrue(isinstance(form.base_fields.get('mark'), forms.IntegerField))

    def testFormInitialValuesAndChoices(self):
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion)
        self.assertIn('initialAnswerOptions', form.initial)
        self.assertIn('answerOrder', form.base_fields)
        self.assertListEqual(form.base_fields.get('answerOrder').choices, self.answerOrderChoices)
        self.assertListEqual(form.initial.get('initialAnswerOptions'), self.choices)

        # self.assertEqual(form.initial['figure'], self.multipleChoiceQuestion.figure)
        self.assertEqual(form.initial['content'], self.multipleChoiceQuestion.content)
        self.assertEqual(form.initial['explanation'], self.multipleChoiceQuestion.explanation)
        self.assertEqual(form.initial['mark'], self.multipleChoiceQuestion.mark)
        self.assertEqual(form.initial['answerOrder'], self.multipleChoiceQuestion.answerOrder)

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            answerOrder=MultipleChoiceQuestion.Order.SEQUENTIAL
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors))
        self.assertTrue(form.has_error('figure'))
        self.assertTrue(form.has_error('content'))
        self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('figure')[0])
        self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('content')[0])

    def testMarkIsLessThanZero(self):
        testParams = self.TestParams(
            content='new content',
            mark=-1,
            answerOrder=MultipleChoiceQuestion.Order.SEQUENTIAL
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testOneOfAnswerOptionIsEmpty(self):
        testParams = self.TestParams(
            content='new content',
            answerOrder=MultipleChoiceQuestion.Order.RANDOM,
            answerOptions=[(1, '', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData(True))

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('initialAnswerOptions'))
        self.assertEqual('One of your answer options is empty or invalid. Please try again.',
                         form.errors.get('initialAnswerOptions')[0])
        self.assertIn('initialAnswerOptions', form.initial)
        self.assertListEqual(form.initial.get('initialAnswerOptions'), testParams.answerOptions)

    def testMultipleChoiceQuestionAndAnswerUpdatedSuccessfully(self):
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            answerOrder=MultipleChoiceQuestion.Order.RANDOM,
            answerOptions=[(1, 'Answer 1', True), (2, 'Answer 2', False)]
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData(True))

        self.assertTrue(form.is_valid())
        self.assertEqual(0, len(form.errors))
        multipleChoiceQuestion = form.update()

        self.assertEqual(testParams.figure, multipleChoiceQuestion.figure)
        self.assertEqual(testParams.content, multipleChoiceQuestion.content)
        self.assertEqual(testParams.explanation, multipleChoiceQuestion.explanation)
        self.assertEqual(testParams.mark, multipleChoiceQuestion.mark)
        self.assertEqual(testParams.answerOrder, multipleChoiceQuestion.answerOrder)

        newChoiceList = multipleChoiceQuestion.choices['choices']
        self.assertEqual(2, len(newChoiceList))
        self.assertListEqual(
            [(i, x['content'], x['isCorrect']) for i, x in enumerate(newChoiceList, 1)], testParams.answerOptions
        )

    def testAddNewAnswerOptionsToExistingList(self):
        newAnswerOptions = [i for i in self.choices]
        newAnswerOptions.append((len(newAnswerOptions) + 1, 'New Option', True))
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            answerOrder=MultipleChoiceQuestion.Order.RANDOM,
            answerOptions=newAnswerOptions
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData(True))

        self.assertTrue(form.is_valid())
        self.assertEqual(0, len(form.errors))
        multipleChoiceQuestion = form.update()

        self.assertEqual(testParams.figure, multipleChoiceQuestion.figure)
        self.assertEqual(testParams.content, multipleChoiceQuestion.content)
        self.assertEqual(testParams.explanation, multipleChoiceQuestion.explanation)
        self.assertEqual(testParams.mark, multipleChoiceQuestion.mark)
        self.assertEqual(testParams.answerOrder, multipleChoiceQuestion.answerOrder)

        newChoiceList = multipleChoiceQuestion.choices['choices']
        self.assertEqual(len(newAnswerOptions), len(newChoiceList))
        self.assertListEqual(
            [(i, x['content'], x['isCorrect']) for i, x in enumerate(newChoiceList, 1)], testParams.answerOptions
        )

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
                        answerTextCheckedDict[f'answerChecked-{answer[0]}'] = 'on'
                    answerTextList.append(answer[1])

                queryDict.setlist('answerOptions', answerTextList)
                data.update(answerTextCheckedDict)

            queryDict.update(data)
            return queryDict
