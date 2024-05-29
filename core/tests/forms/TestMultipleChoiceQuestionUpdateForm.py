from django import forms
from django.http import QueryDict

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest
from core.forms import MultipleChoiceQuestionUpdateForm
from core.models import Question


class MultipleChoiceQuestionUpdateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        super(MultipleChoiceQuestionUpdateFormTest, self).setUp('')
        self.answerOrderChoices = [
            (None, '-- Select a value --'), ('SEQUENTIAL', 'Sequential'), ('RANDOM', 'Random'), ('NONE', 'None')
        ]
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers(None)
        self.choices = [
            (i, x['content'], x['isChecked']) for i, x in enumerate(self.multipleChoiceQuestion.choices['choices'], 1)
        ]

    def testFieldsAndType(self):
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion)
        self.assertEqual(len(form.fields), 5)

        self.assertTrue(isinstance(form.fields.get('figure'), forms.ImageField))
        self.assertEqual(form.fields.get('figure').label, 'Figure (Optional)')
        self.assertTrue(isinstance(form.fields.get('figure').widget, forms.ClearableFileInput))

        self.assertTrue(isinstance(form.fields.get('content'), forms.CharField))
        self.assertEqual(form.fields.get('content').label, 'Content (Optional)')
        self.assertTrue(isinstance(form.fields.get('content').widget, forms.Textarea))

        self.assertTrue(isinstance(form.fields.get('explanation'), forms.CharField))
        self.assertEqual(form.fields.get('explanation').label, 'Explanation (Optional)')
        self.assertTrue(isinstance(form.fields.get('explanation').widget, forms.Textarea))

        self.assertTrue(isinstance(form.fields.get('answerOrder'), forms.MultipleChoiceField))
        self.assertEqual(form.fields.get('answerOrder').label, 'Answer Order')
        self.assertTrue(isinstance(form.fields.get('answerOrder').widget, forms.Select))

        self.assertTrue(isinstance(form.fields.get('mark'), forms.IntegerField))
        self.assertEqual(form.fields.get('mark').label, 'Mark')
        self.assertTrue(isinstance(form.fields.get('mark').widget, forms.NumberInput))

    def testRaiseExceptionWhenNoneIsPassedForMultipleChoiceQuestion(self):
        exceptionMessage = 'Question object is none, or is not compatible with MultipleChoiceQuestionUpdateForm.'
        with self.assertRaisesMessage(Exception, exceptionMessage):
            MultipleChoiceQuestionUpdateForm(None)

    def testFormInitialValuesAndChoices(self):
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion)
        self.assertIn('initialAnswerOptions', form.initial)
        self.assertIn('answerOrder', form.fields)
        self.assertListEqual(form.fields.get('answerOrder').choices, self.answerOrderChoices)
        self.assertListEqual(form.initial.get('initialAnswerOptions'), self.choices)

        # self.assertEqual(form.initial['figure'], self.multipleChoiceQuestion.question.figure)
        self.assertEqual(form.initial['content'], self.multipleChoiceQuestion.content)
        self.assertEqual(form.initial['explanation'], self.multipleChoiceQuestion.explanation)
        self.assertEqual(form.initial['mark'], self.multipleChoiceQuestion.mark)
        self.assertEqual(form.initial['answerOrder'], self.multipleChoiceQuestion.choicesOrder)

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            answerOrder=Question.Order.SEQUENTIAL
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
            answerOrder=Question.Order.SEQUENTIAL
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testOneOfAnswerOptionIsEmpty(self):
        testParams = self.TestParams(
            content='new content',
            answerOrder=Question.Order.RANDOM,
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
            answerOrder=Question.Order.RANDOM,
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
        self.assertEqual(testParams.answerOrder, multipleChoiceQuestion.choicesOrder)

        newChoiceList = multipleChoiceQuestion.choices['choices']
        self.assertEqual(2, len(newChoiceList))
        self.assertListEqual(
            [(i, x['content'], x['isChecked']) for i, x in enumerate(newChoiceList, 1)], testParams.answerOptions
        )

    def testAddNewAnswerOptionsToExistingList(self):
        newAnswerOptions = [i for i in self.choices]
        newAnswerOptions.append((len(newAnswerOptions) + 1, 'New Option', True))
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            answerOrder=Question.Order.RANDOM,
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
        self.assertEqual(testParams.answerOrder, multipleChoiceQuestion.choicesOrder)

        newChoiceList = multipleChoiceQuestion.choices['choices']
        self.assertEqual(len(newAnswerOptions), len(newChoiceList))
        self.assertListEqual(
            [(i, x['content'], x['isChecked']) for i, x in enumerate(newChoiceList, 1)], testParams.answerOptions
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
