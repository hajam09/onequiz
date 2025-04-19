# from django.urls import reverse
#
# from core.forms import TrueOrFalseQuestionCreateForm
# from onequiz.operations import bakerOperations
# from onequiz.tests.BaseTestViews import BaseTestViews
#
#
# class QuizCreateTrueOrFalseQuestionViewTest(BaseTestViews):
#
#     def setUp(self, path=None) -> None:
#         super(QuizCreateTrueOrFalseQuestionViewTest, self).setUp('')
#         self.quiz = bakerOperations.createQuiz(self.request.user)
#         self.path = reverse('core:true-or-false-question-create-view', kwargs={'url': self.quiz.url})
#
#     def testCreateTrueOrFalseQuestionViewGet(self):
#         response = self.get()
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['form'], TrueOrFalseQuestionCreateForm))
#         self.assertTrue(response.context['formTitle'], 'Create True or False Question')
#         self.assertTemplateUsed(response, 'core/trueOrFalseQuestionTemplateView.html')
#
#     def testQuizDoesNotExist(self):
#         path = reverse('core:true-or-false-question-create-view', kwargs={'url': 'non-existing-url'})
#         response = self.get(path=path)
#         self.assertEqual(response.status_code, 404)
#
#     def testFormIsInvalidAndObjectIsNotCreated(self):
#         testParams = self.TestParams(
#             figure='',
#             content='test content',
#             explanation='test explanation',
#             mark=-1,
#             trueOrFalse=True,
#         )
#         response = self.post(testParams.getData())
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(0, self.quiz.getQuestions().count())
#         self.assertTrue(isinstance(response.context['form'], TrueOrFalseQuestionCreateForm))
#         self.assertTrue(response.context['formTitle'], 'Create True or False Question')
#         self.assertTemplateUsed(response, 'core/trueOrFalseQuestionTemplateView.html')
#
#     def testFormIsValidAndObjectIsCreated(self):
#         testParams = self.TestParams(
#             figure='',
#             content='test content',
#             explanation='test explanation',
#             mark=80,
#             trueOrFalse=True,
#         )
#         response = self.post(testParams.getData())
#         question = self.quiz.getQuestions().first()
#         self.assertEqual(1, self.quiz.getQuestions().count())
#
#         self.assertEqual(question.figure, testParams.figure)
#         self.assertEqual(question.content, testParams.content)
#         self.assertEqual(question.explanation, testParams.explanation)
#         self.assertEqual(question.mark, testParams.mark)
#         self.assertTrue(question.trueSelected)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(isinstance(response.context['form'], TrueOrFalseQuestionCreateForm))
#         self.assertTrue(response.context['formTitle'], 'Create True or False Question')
#         self.assertTemplateUsed(response, 'core/trueOrFalseQuestionTemplateView.html')
#
#     class TestParams:
#
#         def __init__(self, figure=None, content=None, explanation=None, mark=None, trueOrFalse=None):
#             self.figure = figure
#             self.content = content
#             self.explanation = explanation
#             self.mark = mark
#             self.trueOrFalse = trueOrFalse
#
#         def getData(self):
#             data = {
#                 'figure': self.figure,
#                 'content': self.content,
#                 'explanation': self.explanation,
#                 'mark': self.mark,
#                 'trueOrFalse': self.trueOrFalse,
#             }
#             return data
