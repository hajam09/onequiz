from onequiz.tests.BaseTest import BaseTest
from quiz.forms import TrueOrFalseQuestionCreateForm


class TrueOrFalseQuestionCreateFormTest(BaseTest):

    def setUp(self, path='') -> None:
        self.basePath = path
        super(TrueOrFalseQuestionCreateFormTest, self).setUp('')

    def testIsCorrectChoicesProvided(self):
        form = TrueOrFalseQuestionCreateForm()
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'False')]
        self.assertIn('isCorrectChoices', form.initial)
        self.assertListEqual(form.initial.get('isCorrectChoices'), IS_CORRECT_CHOICES)

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            isCorrect=True
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
            isCorrect=True
        )
        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
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
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'True'), ('isCorrect', 'False', 'False', 'False')]
        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertIn('isCorrectChoices', form.initial)
        self.assertListEqual(form.initial.get('isCorrectChoices'), IS_CORRECT_CHOICES)

    def testWhenFormHasErrorAndFalseIsSelectedTHenFalseOptionIsTicked(self):
        testParams = self.TestParams(
            content='test content',
            mark=-1,
            isCorrect=False
        )
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'True')]
        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertIn('isCorrectChoices', form.initial)
        self.assertListEqual(form.initial.get('isCorrectChoices'), IS_CORRECT_CHOICES)

    def testTrueOrFalseQuestionObjectCreated(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=80,
            isCorrect=False
        )

        form = TrueOrFalseQuestionCreateForm(data=testParams.getData())
        self.assertTrue(form.is_valid())

        newTrueOrFalseQuestion = form.save()
        # self.assertIsNone(newTrueOrFalseQuestion.figure)
        self.assertEqual(testParams.content, newTrueOrFalseQuestion.content)
        self.assertEqual(testParams.explanation, newTrueOrFalseQuestion.explanation)
        self.assertEqual(testParams.mark, newTrueOrFalseQuestion.mark)
        self.assertFalse(newTrueOrFalseQuestion.isCorrect)

    class TestParams:

        def __init__(self, figure=None, content=None, explanation=None, mark=None, isCorrect=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.isCorrect = isCorrect

            pass

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'isCorrect': self.isCorrect,
            }
            return data
