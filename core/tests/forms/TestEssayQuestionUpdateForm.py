from django import forms

from core.forms import EssayQuestionUpdateForm
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class EssayQuestionUpdateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        super(EssayQuestionUpdateFormTest, self).setUp('')
        self.essayQuestion = bakerOperations.createEssayQuestion()

    def testFieldsAndType(self):
        form = EssayQuestionUpdateForm(self.essayQuestion)
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

        self.assertTrue(isinstance(form.fields.get('answer'), forms.CharField))
        self.assertEqual(form.fields.get('answer').label, 'Answer')
        self.assertTrue(isinstance(form.fields.get('answer').widget, forms.Textarea))

    def testRaiseExceptionWhenNoneIsPassedForEssayQuestion(self):
        exceptionMessage = 'Question object is none, or is not compatible with EssayQuestionUpdateForm.'
        with self.assertRaisesMessage(Exception, exceptionMessage):
            EssayQuestionUpdateForm(None)

    def testFormInitialValuesAndChoices(self):
        form = EssayQuestionUpdateForm(self.essayQuestion)

        # self.assertEqual(form.initial['figure'], self.essayQuestion.figure)
        self.assertEqual(form.initial['content'], self.essayQuestion.content)
        self.assertEqual(form.initial['explanation'], self.essayQuestion.explanation)
        self.assertEqual(form.initial['mark'], self.essayQuestion.mark)
        self.assertEqual(form.initial['answer'], self.essayQuestion.answer)

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            answer='new answer',
        )
        form = EssayQuestionUpdateForm(self.essayQuestion, data=testParams.getData())
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
            answer='new answer',
        )
        form = EssayQuestionUpdateForm(self.essayQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testAnswerFieldIsEmpty(self):
        testParams = self.TestParams(
            content='new content',
            mark=80,
        )
        form = EssayQuestionUpdateForm(self.essayQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('answer'))
        self.assertEqual('Answer cannot be left empty.', form.errors.get('answer')[0])

    def testEssayQuestionUpdatedSuccessfully(self):
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            mark=70,
            answer='new answer',
        )
        form = EssayQuestionUpdateForm(self.essayQuestion, data=testParams.getData())
        self.assertTrue(form.is_valid())
        essayQuestion = form.update()

        self.assertEqual(testParams.figure, essayQuestion.figure)
        self.assertEqual(testParams.content, essayQuestion.content)
        self.assertEqual(testParams.explanation, essayQuestion.explanation)
        self.assertEqual(testParams.mark, essayQuestion.mark)
        self.assertEqual(testParams.answer, essayQuestion.answer)

    class TestParams:

        def __init__(self, figure=None, content=None, explanation=None, mark=None, answer=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.answer = answer

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'answer': self.answer,
            }
            return data
