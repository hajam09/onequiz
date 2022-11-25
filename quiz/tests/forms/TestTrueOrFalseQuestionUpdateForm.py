from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest
from quiz.forms import TrueOrFalseQuestionUpdateForm


class TrueOrFalseQuestionUpdateFormTest(BaseTest):

    def setUp(self, path='') -> None:
        super(TrueOrFalseQuestionUpdateFormTest, self).setUp('')
        self.trueOrFalseQuestion = bakerOperations.createTrueOrFalseQuestion()
        self.trueOptionSelected = [('isCorrect', 'True', 'True', 'True'), ('isCorrect', 'False', 'False', 'False')]
        self.falseOptionSelected = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'True')]

    def testFormInitialValuesAndChoices(self):
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion)
        IS_CORRECT_CHOICES = self.trueOptionSelected if self.trueOrFalseQuestion.isCorrect else self.falseOptionSelected

        # self.assertEqual(form.initial['figure'], self.trueOrFalseQuestion.figure)
        self.assertEqual(form.initial['content'], self.trueOrFalseQuestion.content)
        self.assertEqual(form.initial['explanation'], self.trueOrFalseQuestion.explanation)
        self.assertEqual(form.initial['mark'], self.trueOrFalseQuestion.mark)
        self.assertEqual(form.initial['isCorrectChoices'], IS_CORRECT_CHOICES)

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            isCorrect=True
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
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
            isCorrect=True
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testWhenFormHasErrorAndTrueIsSelectedThenTrueOptionIsTicked(self):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            isCorrect=True
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertIn('isCorrectChoices', form.initial)
        self.assertListEqual(form.initial.get('isCorrectChoices'), self.trueOptionSelected)

    def testWhenFormHasErrorAndFalseIsSelectedTHenFalseOptionIsTicked(self):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            isCorrect=False
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())

        self.assertFalse(form.is_valid())
        self.assertIn('isCorrectChoices', form.initial)
        self.assertListEqual(form.initial.get('isCorrectChoices'), self.falseOptionSelected)

    def testTrueOrFalseQuestionUpdatedTrueSelected(self):
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            mark=50,
            isCorrect=True
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertTrue(form.is_valid())
        trueOrFalseQuestion = form.update()

        self.assertEqual(testParams.figure, trueOrFalseQuestion.figure)
        self.assertEqual(testParams.content, trueOrFalseQuestion.content)
        self.assertEqual(testParams.explanation, trueOrFalseQuestion.explanation)
        self.assertEqual(testParams.mark, trueOrFalseQuestion.mark)
        self.assertTrue(trueOrFalseQuestion.isCorrect)

    def testTrueOrFalseQuestionUpdatedFalseSelected(self):
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            mark=50,
            isCorrect=False
        )
        form = TrueOrFalseQuestionUpdateForm(self.trueOrFalseQuestion, data=testParams.getData())
        self.assertTrue(form.is_valid())
        trueOrFalseQuestion = form.update()

        self.assertEqual(testParams.figure, trueOrFalseQuestion.figure)
        self.assertEqual(testParams.content, trueOrFalseQuestion.content)
        self.assertEqual(testParams.explanation, trueOrFalseQuestion.explanation)
        self.assertEqual(testParams.mark, trueOrFalseQuestion.mark)
        self.assertFalse(trueOrFalseQuestion.isCorrect)

    class TestParams:

        def __init__(self, figure=None, content=None, explanation=None, mark=None, isCorrect=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.isCorrect = isCorrect

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'isCorrect': self.isCorrect,
            }
            return data
