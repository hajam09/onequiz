from django import forms
from parameterized import parameterized

from core.forms import TrueOrFalseQuestionCreateForm
from core.models import Question
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class TrueOrFalseQuestionCreateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(TrueOrFalseQuestionCreateFormTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.user)

    def testFieldsAndType(self):
        form = TrueOrFalseQuestionCreateForm(self.quiz)
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

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            trueOrFalse='TRUE'
        )
        form = TrueOrFalseQuestionCreateForm(self.quiz, data=testParams.getData())
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
        form = TrueOrFalseQuestionCreateForm(self.quiz, data=testParams.getData())
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
        form = TrueOrFalseQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(expectedValue, form.data.get('trueOrFalse'))

    def testTrueOrFalseQuestionObjectCreated(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=80,
            trueOrFalse='FALSE'
        )

        form = TrueOrFalseQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertTrue(form.is_valid())

        newTrueOrFalseQuestion = form.save()
        self.assertEqual(self.quiz, newTrueOrFalseQuestion.quiz)
        # self.assertIsNone(newTrueOrFalseQuestion.question.figure)
        self.assertEqual(testParams.content, newTrueOrFalseQuestion.content)
        self.assertEqual(testParams.explanation, newTrueOrFalseQuestion.explanation)
        self.assertEqual(testParams.mark, newTrueOrFalseQuestion.mark)
        self.assertEqual(Question.Type.TRUE_OR_FALSE, newTrueOrFalseQuestion.questionType)
        self.assertEqual(testParams.trueOrFalse, newTrueOrFalseQuestion.trueOrFalse)

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
