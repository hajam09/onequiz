# import json
#
# from django.urls import reverse
#
# from core.models import Subject, QuizAttempt
# from onequiz.operations import bakerOperations
# from onequiz.tests.BaseTestAjax import BaseTestAjax
#
#
# class QuizAttemptObjectApiEventVersion1ComponentTest(BaseTestAjax):
#
#     def setUp(self, path=None) -> None:
#         super(QuizAttemptObjectApiEventVersion1ComponentTest, self).setUp(path)
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
#         self.path = reverse('core:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
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
#         self.assertEqual(ajaxResponse['message'], 'You already have an attempt that is in progress.')
#
#         self.assertIsNotNone(ajaxResponse['redirectUrl'])
#         self.assertEqual(ajaxResponse['redirectUrl'], f'/v1/quiz-attempt/{quizAttemptId}/')
#
#     def testStartQuizAttemptForNonExistingQuiz(self):
#         path = reverse('core:quizAttemptObjectApiEventVersion1Component') + f'?quizId=0'
#         response = self.post(path=path)
#         ajaxResponse = json.loads(response.content)
#
#         self.assertEqual(200, response.status_code)
#         self.assertFalse(ajaxResponse['success'])
#         self.assertEqual(ajaxResponse['message'], 'No questions found for this quiz. Unable to create an attempt.')
#
#     def testStartQuizAttemptSuccessfully(self):
#         path = reverse('core:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
#         response = self.post(path=path)
#         ajaxResponse = json.loads(response.content)
#
#         self.assertEqual(200, response.status_code)
#         self.assertTrue(ajaxResponse['success'])
#         self.assertIsNotNone(ajaxResponse['redirectUrl'])
#
#         quizAttemptId = ajaxResponse['redirectUrl'].split('/')[3]
#         quizAttempt = QuizAttempt.objects.get(id=quizAttemptId)
#         self.assertEqual(QuizAttempt.Status.IN_PROGRESS, quizAttempt.status)
#         self.assertEqual(quizAttempt.quiz.getQuestions().count(), quizAttempt.responses.count())
#
#         for q, r in zip(quizAttempt.quiz.getQuestions(), quizAttempt.responses.all()):
#             self.assertEqual(q.id, r.question.id)
