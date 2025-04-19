# from django import forms
# from django.http import QueryDict
#
# from core.forms import MultipleChoiceQuestionCreateForm
# from core.models import Question
# from onequiz.tests.BaseTest import BaseTest
#
#
# class MultipleChoiceQuestionCreateFormTest(BaseTest):
#     # test update
#
#     def setUp(self, path=None) -> None:
#         self.basePath = path
#         super(MultipleChoiceQuestionCreateFormTest, self).setUp('')
#         # TODO: Search for 'Answer Order is empty.' and remove its usage.
#
#     def testFieldsAndType(self):
#         form = MultipleChoiceQuestionCreateForm()
#         self.assertEqual(len(form.fields), 5)
#
#         self.assertTrue(isinstance(form.fields.get('figure'), forms.ImageField))
#         self.assertEqual(form.fields.get('figure').label, 'Figure (Optional)')
#         self.assertTrue(isinstance(form.fields.get('figure').widget, forms.ClearableFileInput))
#
#         self.assertTrue(isinstance(form.fields.get('content'), forms.CharField))
#         self.assertEqual(form.fields.get('content').label, 'Content (Optional)')
#         self.assertTrue(isinstance(form.fields.get('content').widget, forms.Textarea))
#
#         self.assertTrue(isinstance(form.fields.get('explanation'), forms.CharField))
#         self.assertEqual(form.fields.get('explanation').label, 'Explanation (Optional)')
#         self.assertTrue(isinstance(form.fields.get('explanation').widget, forms.Textarea))
#
#         self.assertTrue(isinstance(form.fields.get('choiceOrder'), forms.MultipleChoiceField))
#         self.assertEqual(form.fields.get('choiceOrder').label, 'Choice Order')
#         self.assertTrue(isinstance(form.fields.get('choiceOrder').widget, forms.Select))
#
#         self.assertTrue(isinstance(form.fields.get('mark'), forms.IntegerField))
#         self.assertEqual(form.fields.get('mark').label, 'Mark')
#         self.assertTrue(isinstance(form.fields.get('mark').widget, forms.NumberInput))
#
#     def testInitialValues(self):
#         form = MultipleChoiceQuestionCreateForm()
#         CHOICE_ORDER = [
#             (None, '-- Select a value --'),
#             ('SEQUENTIAL', 'Sequential'),
#             ('RANDOM', 'Random'),
#             ('NONE', 'None'),
#         ]
#         ANSWER_OPTIONS = [
#             (1, '', False),
#             (2, '', False)
#         ]
#
#         self.assertIn('initialAnswerOptions', form.initial)
#         self.assertIn('choiceOrder', form.fields)
#         self.assertListEqual(form.fields.get('choiceOrder').choices, CHOICE_ORDER)
#         self.assertListEqual(form.initial.get('initialAnswerOptions'), ANSWER_OPTIONS)
#
#     def testFigureAndContentIsEmpty(self):
#         testParams = self.TestParams(
#             choiceOrder=Question.Order.SEQUENTIAL
#         )
#         form = MultipleChoiceQuestionCreateForm(data=testParams.getData())
#
#         self.assertFalse(form.is_valid())
#         self.assertEqual(2, len(form.errors))
#         self.assertTrue(form.has_error('figure'))
#         self.assertTrue(form.has_error('content'))
#         self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('figure')[0])
#         self.assertEqual('Cannot leave both figure and content empty.', form.errors.get('content')[0])
#
#     def testMarkIsLessThanZero(self):
#         testParams = self.TestParams(
#             content='test content',
#             mark=-1,
#             choiceOrder=Question.Order.SEQUENTIAL
#         )
#         form = MultipleChoiceQuestionCreateForm(data=testParams.getData())
#
#         self.assertFalse(form.is_valid())
#         self.assertEqual(1, len(form.errors))
#         self.assertTrue(form.has_error('mark'))
#         self.assertEqual('Mark cannot be a negative number.', form.errors.get('mark')[0])
#
#     def testChoiceOrderOptionIsUnSelected(self):
#         testParams = self.TestParams(
#             content='test content',
#         )
#         form = MultipleChoiceQuestionCreateForm(data=testParams.getData())
#
#         self.assertFalse(form.is_valid())
#         self.assertEqual(1, len(form.errors))
#         self.assertTrue(form.has_error('choiceOrder'))
#         self.assertEqual('Choice Order is empty.', form.errors.get('choiceOrder')[0])
#
#     def testMaintainChoiceOrderOptionWhenFormHasError(self):
#         testParams = self.TestParams(
#             choiceOrder=Question.Order.RANDOM
#         )
#         form = MultipleChoiceQuestionCreateForm(data=testParams.getData())
#
#         self.assertFalse(form.is_valid())
#         self.assertIn('choiceOrder', form.data)
#         self.assertIn(testParams.choiceOrder, form.data.get('choiceOrder'))
#
#     def testMaintainAnswerOptionsListWhenFormHasError(self):
#         testParams = self.TestParams(
#             content='test content',
#             choiceOrder=Question.Order.RANDOM,
#             choices=[(1, '', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
#         )
#         form = MultipleChoiceQuestionCreateForm(data=testParams.getData(True))
#
#         self.assertFalse(form.is_valid())
#         self.assertEqual(1, len(form.errors))
#         self.assertTrue(form.has_error('initialAnswerOptions'))
#         self.assertEqual('One of your answer options is empty or invalid. Please try again.', form.errors.get('initialAnswerOptions')[0])
#         self.assertIn('initialAnswerOptions', form.initial)
#         self.assertListEqual(form.initial.get('initialAnswerOptions'), testParams.choices)
#
#     def testMultipleChoiceQuestionAndAnswerObjectsCreated(self):
#         testParams = self.TestParams(
#             content='test content',
#             choiceOrder=Question.Order.RANDOM,
#             choices=[(1, 'Answer 1', True), (2, 'Answer 2', False), (3, 'Answer 3', True), (4, 'Answer 4', False)]
#         )
#         form = MultipleChoiceQuestionCreateForm(data=testParams.getData(True))
#
#         self.assertTrue(form.is_valid())
#         self.assertEqual(0, len(form.errors))
#         self.assertIn('initialAnswerOptions', form.initial)
#         self.assertListEqual(form.initial.get('initialAnswerOptions'), testParams.choices)
#
#         newMultipleChoiceQuestion = form.save()
#
#         # self.assertIsNone(newMultipleChoiceQuestion.question.figure)
#         self.assertEqual(testParams.content, newMultipleChoiceQuestion.content)
#         self.assertEqual('', newMultipleChoiceQuestion.explanation)
#         self.assertEqual(testParams.mark, newMultipleChoiceQuestion.mark)
#         self.assertEqual(Question.Type.MULTIPLE_CHOICE, newMultipleChoiceQuestion.questionType)
#         self.assertEqual(testParams.choiceOrder, newMultipleChoiceQuestion.choiceOrder)
#
#         choiceList = newMultipleChoiceQuestion.choices['choices']
#         self.assertListEqual(
#             [(i['content'], i['isChecked']) for i in choiceList], [(i[1], i[2]) for i in testParams.choices]
#         )
#
#     class TestParams:
#
#         def __init__(self, figure=None, content=None, explanation=None, mark=80, choiceOrder=None, choices=None):
#             self.figure = figure
#             self.content = content
#             self.explanation = explanation
#             self.mark = mark
#             self.choiceOrder = choiceOrder
#             self.choices = choices
#
#         def getData(self, withAnswerOptions=False):
#             data = {
#                 'figure': self.figure,
#                 'content': self.content,
#                 'explanation': self.explanation,
#                 'mark': self.mark,
#                 'choiceOrder': self.choiceOrder
#             }
#
#             queryDict = QueryDict('', mutable=True)
#
#             if withAnswerOptions:
#                 answerTextList = []
#                 answerTextCheckedDict = {}
#
#                 for answer in self.choices:
#                     if answer[2]:
#                         answerTextCheckedDict[f'answerChecked-{answer[0]}'] = 'on'
#                     answerTextList.append(answer[1])
#
#                 queryDict.setlist('answerOptions', answerTextList)
#                 data.update(answerTextCheckedDict)
#
#             queryDict.update(data)
#             return queryDict
