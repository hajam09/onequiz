from django import forms

from core.forms import EssayQuestionCreateForm
from core.models import Question
from onequiz.tests.BaseTest import BaseTest


class EssayQuestionCreateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(EssayQuestionCreateFormTest, self).setUp('')

    def testFieldsAndType(self):
        form = EssayQuestionCreateForm()
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

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            mark=50,
            answer='test answer',
        )
        form = EssayQuestionCreateForm(data=testParams.getData())
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
            answer='test answer',
        )
        form = EssayQuestionCreateForm(data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('mark'))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testAnswerFieldIsEmpty(self):
        testParams = self.TestParams(
            content='test content',
            mark=80,
        )
        form = EssayQuestionCreateForm(data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form.has_error('answer'))
        self.assertEqual('Answer cannot be left empty.', form.errors.get('answer')[0])

    def testEssayQuestionObjectCreated(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=80,
            answer='test answer',
        )

        form = EssayQuestionCreateForm(data=testParams.getData())
        self.assertTrue(form.is_valid())

        newEssayQuestion = form.save()
        # self.assertIsNone(newEssayQuestion.question.figure)
        self.assertEqual(testParams.content, newEssayQuestion.content)
        self.assertEqual(testParams.explanation, newEssayQuestion.explanation)
        self.assertEqual(testParams.mark, newEssayQuestion.mark)
        self.assertEqual(Question.Type.ESSAY, newEssayQuestion.questionType)
        self.assertEqual(testParams.answer, newEssayQuestion.answer)

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
