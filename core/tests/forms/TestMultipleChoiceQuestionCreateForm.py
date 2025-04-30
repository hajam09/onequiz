from django import forms
from django.http import QueryDict

from core.forms import MultipleChoiceQuestionCreateForm
from core.models import Question
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class MultipleChoiceQuestionCreateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(MultipleChoiceQuestionCreateFormTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.user)

    def testFieldsAndType(self):
        form = MultipleChoiceQuestionCreateForm(self.quiz)
        self.assertEqual(len(form.fields), 7)

        self.assertIsInstance(form.fields.get('figure'), forms.ImageField)
        self.assertEqual(form.fields.get('figure').label, 'Figure (Optional)')
        self.assertIsInstance(form.fields.get('figure').widget, forms.ClearableFileInput)

        self.assertIsInstance(form.fields.get('content'), forms.CharField)
        self.assertEqual(form.fields.get('content').label, 'Content (Optional)')
        self.assertIsInstance(form.fields.get('content').widget, forms.Textarea)

        self.assertIsInstance(form.fields.get('explanation'), forms.CharField)
        self.assertEqual(form.fields.get('explanation').label, 'Explanation (Optional)')
        self.assertIsInstance(form.fields.get('explanation').widget, forms.Textarea)

        self.assertIsInstance(form.fields.get('choiceOrder'), forms.ChoiceField)
        self.assertEqual(form.fields.get('choiceOrder').label, 'Choice Order')
        self.assertIsInstance(form.fields.get('choiceOrder').widget, forms.Select)

        self.assertIsInstance(form.fields.get('choiceType'), forms.ChoiceField)
        self.assertEqual(form.fields.get('choiceType').label, 'Choice Type')
        self.assertIsInstance(form.fields.get('choiceType').widget, forms.Select)

        self.assertIsInstance(form.fields.get('choices'), forms.JSONField)
        self.assertEqual(form.fields.get('choices').label, None)
        self.assertIsInstance(form.fields.get('choices').widget, forms.HiddenInput)

        self.assertIsInstance(form.fields.get('mark'), forms.IntegerField)
        self.assertEqual(form.fields.get('mark').label, 'Mark')
        self.assertIsInstance(form.fields.get('mark').widget, forms.NumberInput)

    def testInitialValues(self):
        form = MultipleChoiceQuestionCreateForm(self.quiz)
        CHOICE_ORDER = [
            (None, '-- Select a value --'),
            ('SEQUENTIAL', 'Sequential'),
            ('RANDOM', 'Random'),
            ('NONE', 'None'),
        ]
        CHOICE_TYPE = [
            (None, '-- Select a value --'),
            ('SINGLE', 'Single - Allows single choice to be selected'),
            ('MULTIPLE', 'Multiple - Allows multiple choices to be selected'),
        ]

        self.assertListEqual(form.fields['choiceOrder'].choices, CHOICE_ORDER)
        self.assertListEqual(form.fields['choiceType'].choices, CHOICE_TYPE)
        # todo: assert test for choices JSONField

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            explanation='test explanation',
            mark=50,
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
        )
        form = MultipleChoiceQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors))
        self.assertEqual('Cannot leave both figure and content empty.', form.errors['figure'][0])
        self.assertEqual('Cannot leave both figure and content empty.', form.errors['content'][0])

    def testMarkIsLessThanZero(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=-1,
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
        )
        form = MultipleChoiceQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testChoiceOrderAndChoiceTypeOptionIsUnSelectedOrNotInList(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=90,
            choiceOrder='INVALID',
            choiceType='INVALID',
        )
        form = MultipleChoiceQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors))
        self.assertEqual('Select a valid choice. INVALID is not one of the available choices.',
                         form.errors.get('choiceOrder')[0])
        self.assertEqual('Select a valid choice. INVALID is not one of the available choices.',
                         form.errors.get('choiceType')[0])

    def testChoiceOrderOptionAndChoiceTypeOptionAndChoicesOptionsMaintainedWhenFormHasError(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=-1,
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
        )
        form = MultipleChoiceQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(testParams.choiceOrder, form.data.get('choiceOrder'))
        self.assertEqual(testParams.choiceType, form.data.get('choiceType'))
        self.assertEqual(testParams.choices, form.data.get('choices'))
        self.assertListEqual(testParams.choices, form.data.get('choices'))

    def testMultipleChoiceQuestionAndAnswerObjectsCreated(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            mark=90,
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
        )
        form = MultipleChoiceQuestionCreateForm(self.quiz, data=testParams.getData())
        self.assertTrue(form.is_valid())

        newMultipleChoiceQuestion = form.save()
        self.assertEqual(self.quiz, newMultipleChoiceQuestion.quiz)
        # self.assertIsNone(newMultipleChoiceQuestion.question.figure)
        self.assertEqual(testParams.content, newMultipleChoiceQuestion.content)
        self.assertEqual(testParams.explanation, newMultipleChoiceQuestion.explanation)
        self.assertEqual(testParams.mark, newMultipleChoiceQuestion.mark)
        self.assertEqual(Question.Type.MULTIPLE_CHOICE, newMultipleChoiceQuestion.questionType)
        self.assertEqual(Question.ChoiceOrder.SEQUENTIAL, newMultipleChoiceQuestion.choiceOrder)
        self.assertEqual(Question.ChoiceType.SINGLE, newMultipleChoiceQuestion.choiceType)
        self.assertListEqual(testParams.choices, newMultipleChoiceQuestion.choices.get('choices'))

    class TestParams:
        def __init__(self, figure=None, content=None, explanation=None, mark=80, choiceOrder=None, choiceType=None,
                     choices=None):
            self.figure = figure
            self.content = content
            self.explanation = explanation
            self.mark = mark
            self.choiceOrder = choiceOrder
            self.choiceType = choiceType
            self.choices = choices or [{'id': None, 'content': f'Text - {_}', 'isChecked': True, } for _ in range(4)]

        def getData(self):
            data = {
                'figure': self.figure,
                'content': self.content,
                'explanation': self.explanation,
                'mark': self.mark,
                'choiceOrder': self.choiceOrder,
                'choiceType': self.choiceType,
                'choices': self.choices
            }
            queryDict = QueryDict('', mutable=True)
            queryDict.update(data)
            return queryDict
