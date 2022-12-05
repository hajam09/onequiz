from django import forms

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest
from quiz.forms import EssayQuestionUpdateForm


class EssayQuestionUpdateFormTest(BaseTest):

    def setUp(self, path='') -> None:
        super(EssayQuestionUpdateFormTest, self).setUp('')
        self.essayQuestion = bakerOperations.createEssayQuestion()

    def testFieldsAndType(self):
        form = EssayQuestionUpdateForm()
        self.assertEqual(len(form.base_fields), 5)
        self.assertTrue(isinstance(form.base_fields.get('figure'), forms.ImageField))
        self.assertTrue(isinstance(form.base_fields.get('content'), forms.CharField))
        self.assertTrue(isinstance(form.base_fields.get('explanation'), forms.CharField))
        self.assertTrue(isinstance(form.base_fields.get('mark'), forms.IntegerField))
        self.assertTrue(isinstance(form.base_fields.get('answer'), forms.CharField))

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

            pass

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'answer': self.answer,
            }
            return data
