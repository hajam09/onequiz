from django import forms
from django.http import QueryDict

from core.forms import MultipleChoiceQuestionUpdateForm
from core.models import Question
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTest import BaseTest


class MultipleChoiceQuestionUpdateFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        super(MultipleChoiceQuestionUpdateFormTest, self).setUp('')
        self.quiz = bakerOperations.createQuiz(self.user)
        self.multipleChoiceQuestion = bakerOperations.createMultipleChoiceQuestionAndAnswers(self.quiz)
        self.choiceOrder = [
            (None, '-- Select a value --'), ('SEQUENTIAL', 'Sequential'), ('RANDOM', 'Random'), ('NONE', 'None')
        ]

    def testFieldsAndType(self):
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion)
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

    def testRaiseExceptionWhenNoneIsPassedForMultipleChoiceQuestion(self):
        exceptionMessage = 'Question object is none, or is not compatible with MultipleChoiceQuestionUpdateForm.'
        with self.assertRaisesMessage(Exception, exceptionMessage):
            MultipleChoiceQuestionUpdateForm(None)

    def testFormInitialValuesAndChoices(self):
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion)
        self.assertListEqual(form.fields.get('choiceOrder').choices, self.choiceOrder)

        # self.assertEqual(form.initial['figure'], self.multipleChoiceQuestion.question.figure)
        self.assertEqual(form.initial['content'], self.multipleChoiceQuestion.content)
        self.assertEqual(form.initial['explanation'], self.multipleChoiceQuestion.explanation)
        self.assertEqual(form.initial['mark'], self.multipleChoiceQuestion.mark)
        self.assertEqual(form.initial['choiceOrder'], self.multipleChoiceQuestion.choiceOrder)
        self.assertEqual(form.initial['choiceType'], self.multipleChoiceQuestion.choiceType)
        self.assertListEqual(form.initial['choices'], self.multipleChoiceQuestion.choices.get('choices'))

    def testFigureAndContentIsEmpty(self):
        testParams = self.TestParams(
            explanation='test explanation',
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
            choices=self.multipleChoiceQuestion.choices.get('choices')
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors))
        self.assertEqual('Cannot leave both figure and content empty.', form.errors['figure'][0])
        self.assertEqual('Cannot leave both figure and content empty.', form.errors['content'][0])

    def testMarkIsLessThanZero(self):
        testParams = self.TestParams(
            content='new content',
            mark=-1,
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
            choices=self.multipleChoiceQuestion.choices.get('choices')
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])

    def testChoiceOrderAndChoiceTypeOptionIsUnSelectedOrNotInList(self):
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            choiceOrder='INVALID',
            choiceType='INVALID',
            choices=self.multipleChoiceQuestion.choices.get('choices')
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
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
            choices=self.multipleChoiceQuestion.choices.get('choices')
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(testParams.choiceOrder, form.data.get('choiceOrder'))
        self.assertEqual(testParams.choiceType, form.data.get('choiceType'))
        self.assertEqual(testParams.choices, form.data.get('choices'))
        self.assertListEqual(testParams.choices, form.data.get('choices'))

    def testOneOfChoicesOptionsIsEmpty(self):
        choices = self.multipleChoiceQuestion.choices.get('choices')
        choices[0]['content'] = ''
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
            choices=choices
        )
        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual('One of the choice value is empty.', form.errors.get('choices')[0])

    def testAddNewAnswerOptionsToExistingList(self):
        choices = self.multipleChoiceQuestion.choices.get('choices')
        choices.append(
            {
                'content': 'New choice',
                'id': None,
                'isChecked': False
            }
        )
        testParams = self.TestParams(
            content='test content',
            explanation='test explanation',
            choiceOrder=Question.ChoiceOrder.SEQUENTIAL,
            choiceType=Question.ChoiceType.SINGLE,
            choices=choices
        )

        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
        self.assertTrue(form.is_valid())
        updatedChoices = form.data.get('choices')
        for choice in updatedChoices:
            self.assertIsNotNone(choice['id'])
            self.assertIsNotNone(choice['content'])
            self.assertIsNotNone(choice['isChecked'])

        self.assertEqual(updatedChoices[-1]['content'], 'New choice')
        self.assertEqual(updatedChoices[-1]['isChecked'], False)

    def testMultipleChoiceQuestionAndAnswerUpdatedSuccessfully(self):
        testParams = self.TestParams(
            content='new content',
            explanation='new explanation',
            mark=95,
            choiceOrder=Question.ChoiceOrder.RANDOM,
            choiceType=Question.ChoiceType.MULTIPLE,
        )

        form = MultipleChoiceQuestionUpdateForm(self.multipleChoiceQuestion, data=testParams.getData())
        self.assertTrue(form.is_valid())
        multipleChoiceQuestion = form.update()

        # self.assertEqual(testParams.figure, multipleChoiceQuestion.figure)
        self.assertEqual('new content', multipleChoiceQuestion.content)
        self.assertEqual('new explanation', multipleChoiceQuestion.explanation)
        self.assertEqual(95, multipleChoiceQuestion.mark)
        self.assertEqual(Question.ChoiceOrder.RANDOM, multipleChoiceQuestion.choiceOrder)
        self.assertEqual(Question.ChoiceType.MULTIPLE, multipleChoiceQuestion.choiceType)
        self.assertListEqual(testParams.choices, multipleChoiceQuestion.choices.get('choices'))

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
