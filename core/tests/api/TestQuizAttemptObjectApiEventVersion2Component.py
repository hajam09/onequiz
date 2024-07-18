# import json
#
# from django.urls import reverse
#
# from core.models import Subject
# from onequiz.operations import bakerOperations
# from onequiz.tests.BaseTestAjax import BaseTestAjax
#
#
# class QuizAttemptObjectApiEventVersion2ComponentTest(BaseTestAjax):
#
#     def setUp(self, path=None) -> None:
#         super(QuizAttemptObjectApiEventVersion2ComponentTest, self).setUp(path)
#         bakerOperations.createSubjects(1)
#         self.subject = Subject.objects.first()
#         self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
#         self.quiz.questions.add(*[
#             bakerOperations.createEssayQuestion(),
#             bakerOperations.createEssayQuestion(),
#             bakerOperations.createEssayQuestion(),
#             bakerOperations.createTrueOrFalseQuestion(),
#             bakerOperations.createTrueOrFalseQuestion(),
#             bakerOperations.createTrueOrFalseQuestion(),
#             bakerOperations.createMultipleChoiceQuestionAndAnswers(),
#             bakerOperations.createMultipleChoiceQuestionAndAnswers(),
#             bakerOperations.createMultipleChoiceQuestionAndAnswers(),
#         ])
#         self.path = reverse('core:quizAttemptObjectApiEventVersion2Component') + f'?quizId={self.quiz.id}'
#
#     def createQuizAttemptAndTheResponseObjects(self):
#         response = self.post()
#         ajaxResponse = json.loads(response.content)
#         self.assertEqual(200, response.status_code)
#         return ajaxResponse['redirectUrl'].split('/')[3]
#
#     def testWhenAnotherAttemptIsInProgressThenReturnItsRedirectUrl(self):
#         quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
#         response = self.post()
#         ajaxResponse = json.loads(response.content)
#
#         self.assertEqual(200, response.status_code)
#         self.assertTrue(ajaxResponse['success'])
#         self.assertIsNotNone(ajaxResponse['redirectUrl'])
#         self.assertEqual(ajaxResponse['redirectUrl'], f'/v2/quiz-attempt/{quizAttemptId}/')
