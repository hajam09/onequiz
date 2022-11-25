import json

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic, QuizAttempt


class QuizAttemptObjectApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path=reverse('quiz:quizAttemptObjectApiEventVersion1Component')) -> None:
        super(QuizAttemptObjectApiEventVersion1ComponentTest, self).setUp(path)
        bakerOperations.createSubjectsAndTopics(1, 1)
        self.topic = Topic.objects.select_related('subject').first()
        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.quiz.questions.add(*[
            bakerOperations.createEssayQuestion(),
            bakerOperations.createEssayQuestion(),
            bakerOperations.createEssayQuestion(),
            bakerOperations.createTrueOrFalseQuestion(),
            bakerOperations.createTrueOrFalseQuestion(),
            bakerOperations.createTrueOrFalseQuestion(),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(None),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(None),
            bakerOperations.createMultipleChoiceQuestionAndAnswers(None),
        ])

    def testStartQuizAttemptForNonExistingQuiz(self):
        pass

    def testStartQuizAttemptSuccessfully(self):
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['redirectUrl'])

        quizAttemptId = ajaxResponse['redirectUrl'].split('/')[3]
        quizAttempt = QuizAttempt.objects.get(id=quizAttemptId)
        self.assertEqual(QuizAttempt.Status.IN_PROGRESS, quizAttempt.status)
        self.assertEqual(quizAttempt.quiz.getQuestions().count(), quizAttempt.responses.count())

        for q, r in zip(quizAttempt.quiz.getQuestions(), quizAttempt.responses.all()):
            self.assertEqual(q.id, r.question.id)
