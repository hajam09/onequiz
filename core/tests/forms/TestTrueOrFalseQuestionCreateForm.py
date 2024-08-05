from django import forms
from parameterized import parameterized

from core.forms import TrueOrFalseQuestionCreateForm
from core.models import Question
from onequiz.tests.BaseTest import BaseTest


class TrueOrFalseQuestionCreateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(TrueOrFalseQuestionCreateFormTest, self).setUp('')

    def testFieldsAndType(self):
        form = TrueOrFalseQuestionCreateForm()
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

        self.assertTrue(isinstance(form.fields.get('mark'), forms.IntegerField))
        self.assertEqual(form.fields.get('mark').label, 'Mark')
        self.assertTrue(isinstance(form.fields.get('mark').widget, forms.NumberInput))

        self.assertTrue(isinstance(form.fields.get('trueOrFalse'), forms.ChoiceField))
        self.assertEqual(form.fields.get('trueOrFalse').label, 'Is the answer True or False?')
        self.assertTrue(isinstance(form.fields.get('trueOrFalse').widget, forms.RadioSelect))
        self.assertListEqual(form.fields.get('trueOrFalse').choices, [(True, 'True'), (False, 'False')])

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            trueOrFalse=True
        )
        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
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
            trueOrFalse=True
        )
        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    @parameterized.expand([
        [True, True],
        [False, False],
    ])
    def testWhenFormHasAnErrorThenEnsureTrueOrFalseOptionIsUnchanged(self, selected, expectedValue):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            trueOrFalse=selected
        )
        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(expectedValue, form.data.get('trueOrFalse'))

    def testTrueOrFalseQuestionObjectCreated(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=80,
            trueOrFalse=False
        )

        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
        self.assertTrue(form.is_valid())

        newTrueOrFalseQuestion = form.save()
        # self.assertIsNone(newTrueOrFalseQuestion.question.figure)
        self.assertEqual(testParams.content, newTrueOrFalseQuestion.content)
        self.assertEqual(testParams.explanation, newTrueOrFalseQuestion.explanation)
        self.assertEqual(testParams.mark, newTrueOrFalseQuestion.mark)
        self.assertEqual(Question.Type.TRUE_OR_FALSE, newTrueOrFalseQuestion.questionType)
        self.assertFalse(newTrueOrFalseQuestion.trueSelected)

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
