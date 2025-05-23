from django import forms
from parameterized import parameterized

from core.forms import TrueOrFalseQuestionUpdateForm
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class TrueOrFalseQuestionUpdateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        super(TrueOrFalseQuestionUpdateFormTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.user)
        self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion(self.quiz)

    def testFieldsAndType(self):
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion)
        self.assertEqual(len(form.fields), 5)

        self.assertIsInstance(form.fields.get('figure'), forms.ImageField)
        self.assertEqual(form.fields.get('figure').label, 'Figure (Optional)')
        self.assertIsInstance(form.fields.get('figure').widget, forms.ClearableFileInput)

        self.assertIsInstance(form.fields.get('content'), forms.CharField)
        self.assertEqual(form.fields.get('content').label, 'Content (Optional)')
        self.assertIsInstance(form.fields.get('content').widget, forms.Textarea)

        self.assertIsInstance(form.fields.get('explanation'), forms.CharField)
        self.assertEqual(form.fields.get('explanation').label, 'Explanation (Optional)')
        self.assertIsInstance(form.fields.get('explanation').widget, forms.Textarea)

        self.assertIsInstance(form.fields.get('mark'), forms.IntegerField)
        self.assertEqual(form.fields.get('mark').label, 'Mark')
        self.assertIsInstance(form.fields.get('mark').widget, forms.NumberInput)

        self.assertIsInstance(form.fields.get('trueOrFalse'), forms.ChoiceField)
        self.assertEqual(form.fields.get('trueOrFalse').label, 'Is the answer True or False?')
        self.assertIsInstance(form.fields.get('trueOrFalse').widget, forms.RadioSelect)
        self.assertListEqual(form.fields.get('trueOrFalse').choices, [('TRUE', 'True'), ('FALSE', 'False')])

    def testRaiseExceptionWhenNoneIsPassedForTrueOrFalseQuestion(self):
        exceptionMessage = 'Question object is none, or is not compatible with TrueOrFalseQuestionUpdateForm.'
        with self.assertRaisesMessage(Exception, exceptionMessage):
            TrueOrFalseQuestionUpdateForm(None)

    def testFormInitialValuesAndChoices(self):
        self.trueOrFalseQuestion.trueOrFalse = 'FALSE'
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion)

        # self.assertEqual(form.initial['figure'], self.trueOrFalseQuestion.question.figure)
        self.assertEqual(form.initial['content'], self.trueOrFalseQuestion.content)
        self.assertEqual(form.initial['explanation'], self.trueOrFalseQuestion.explanation)
        self.assertEqual(form.initial['mark'], self.trueOrFalseQuestion.mark)
        self.assertEqual(form.initial['trueOrFalse'], self.trueOrFalseQuestion.trueOrFalse)

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            trueOrFalse='TRUE'
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors))
        self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('figure')[0])
        self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('content')[0])

    def testMarkIsLessThanZero(self):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            trueOrFalse='TRUE'
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    @parameterized.expand([
        ['TRUE', 'TRUE'],
        ['FALSE', 'FALSE'],
    ])
    def testWhenFormHasAnErrorThenEnsureTrueOrFalseOptionIsUnchanged(self, selected, expectedValue):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            trueOrFalse=selected
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(expectedValue, form.data.get('trueOrFalse'))

    @parameterized.expand([
        ['TRUE', 'TRUE'],
        ['TRUE', 'FALSE'],
        ['FALSE', 'TRUE'],
        ['FALSE', 'FALSE'],
    ])
    def testTrueOrFalseQuestionUpdatedWithNewValueThenEnsureTrueOrFalseOptionIsUpdated(self, currentValue, newValue):
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            mark=50,
            trueOrFalse=newValue
        )
        self.trueOrFalseQuestion.trueSelected = currentValue
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertTrue(form.is_valid())
        trueOrFalseQuestion = form.update()

        self.assertEqual(testParams.figure, trueOrFalseQuestion.figure)
        self.assertEqual(testParams.content, trueOrFalseQuestion.content)
        self.assertEqual(testParams.explanation, trueOrFalseQuestion.explanation)
        self.assertEqual(testParams.mark, trueOrFalseQuestion.mark)
        self.assertEqual(testParams.trueOrFalse, trueOrFalseQuestion.trueOrFalse)

    class TestParams:
        def __init__(self, figure=None, content=None, explanation=None, mark=None, trueOrFalse=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.trueOrFalse = trueOrFalse

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'trueOrFalse': self.trueOrFalse,
            }
            return data
