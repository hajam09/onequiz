# import json
# import random
#
# from django.urls import reverse
#
# from core.models import Subject, QuizAttempt, Result
# from onequiz.operations import bakerOperations
# from onequiz.operations.generalOperations import QuestionAndResponse
# from onequiz.tests.BaseTestAjax import BaseTestAjax
#
#
# class QuizMarkingOccurrenceApiEventVersion1ComponentTest(BaseTestAjax):
#
#     def setUp(self, path=None) -> None:
#         super(QuizMarkingOccurrenceApiEventVersion1ComponentTest, self).setUp('')
#         bakerOperations.createSubjects(1)
#
#         self.subject = Subject.objects.first()
#         self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
#         self.quiz.questions.add(*bakerOperations.createRandomQuestions())
#
#         quizAttemptId = self.createQuizAttemptAndTheResponseObjects()
#         self.quizAttempt = QuizAttempt.objects.select_related('quiz').get(id=quizAttemptId)
#         Result.objects.create(
#             quizAttempt=self.quizAttempt, timeSpent=1, numberOfCorrectAnswers=0, numberOfPartialAnswers=0, score=0,
#             numberOfWrongAnswers=0
#         )
#         self.path = reverse('core:quizMarkingOccurrenceApiEventVersion1Component', kwargs={'id': self.quizAttempt.id})
#
#     def createQuizAttemptAndTheResponseObjects(self):
#         path = reverse('core:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
#         response = self.post(path=path)
#         ajaxResponse = json.loads(response.content)
#         self.assertEqual(200, response.status_code)
#         return ajaxResponse['redirectUrl'].split('/')[2]
#
#     def testAwardedMarkResponseHasMissingKeys(self):
#         questionAndResponse = QuestionAndResponse(self.quizAttempt.responses.all())
#         testParams = self.TestParams(questionAndResponse.getResponse())
#         data = testParams.getData()
#         for item in data:
#             del item['responseId']
#
#         payload = {'response': data}
#         response = self.put(data=payload)
#         self.quizAttempt.refresh_from_db()
#         ajaxResponse = json.loads(response.content)
#         self.assertTrue(ajaxResponse['success'])
#         self.assertIsNotNone(ajaxResponse['redirectUrl'])
#         self.assertEqual(
#             ajaxResponse['redirectUrl'],
#             reverse('core:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})
#         )
#         self.assertNotEqual(self.quizAttempt.status, QuizAttempt.Status.MARKED)
#         result = Result.objects.filter(quizAttempt=self.quizAttempt).last()
#         self.assertIsNotNone(result)
#
#     def testResponseObjectNotFound(self):
#         questionAndResponse = QuestionAndResponse(self.quizAttempt.responses.all())
#         testParams = self.TestParams(questionAndResponse.getResponse())
#         data = testParams.getData()
#         for item in data:
#             item['responseId'] = 0
#
#         payload = {'response': data}
#         response = self.put(data=payload)
#         self.quizAttempt.refresh_from_db()
#         ajaxResponse = json.loads(response.content)
#         self.assertTrue(ajaxResponse['success'])
#         self.assertIsNotNone(ajaxResponse['redirectUrl'])
#         self.assertEqual(
#             ajaxResponse['redirectUrl'],
#             reverse('core:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})
#         )
#         self.assertNotEqual(self.quizAttempt.status, QuizAttempt.Status.MARKED)
#         result = Result.objects.filter(quizAttempt=self.quizAttempt).last()
#         self.assertIsNotNone(result)
#
#     def testResponseObjectsUpdatedWithMarks(self):
#         questionAndResponse = QuestionAndResponse(self.quizAttempt.responses.all())
#         testParams = self.TestParams(questionAndResponse.getResponse())
#         payload = {'response': testParams.getData()}
#         response = self.put(data=payload)
#         self.quizAttempt.refresh_from_db()
#         ajaxResponse = json.loads(response.content)
#         createdResult = Result.objects.filter(quizAttempt=self.quizAttempt).first()
#         self.assertTrue(ajaxResponse['success'])
#         self.assertIsNotNone(ajaxResponse['redirectUrl'])
#         self.assertEqual(
#             ajaxResponse['redirectUrl'],
#             reverse('core:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})
#         )
#         self.assertEqual(self.quizAttempt.status, QuizAttempt.Status.MARKED)
#         self.assertIsNotNone(createdResult)
#
#     class TestParams:
#
#         def __init__(self, responseList):
#             self.responseList = responseList
#
#         def getData(self):
#             response = [
#                 {
#                     'questionId': i['id'],
#                     'responseId': i['response']['id'],
#                     'awardedMark': random.randint(0, i['mark'])
#                 } for i in self.responseList
#             ]
#             return response
