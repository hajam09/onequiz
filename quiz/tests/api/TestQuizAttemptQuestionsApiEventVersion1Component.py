import json

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.operations.generalOperations import QuestionAndResponse
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic, QuizAttempt


class QuizAttemptQuestionsApiEventVersion1Component(BaseTestAjax):

    def setUp(self, path='') -> None:
        super(QuizAttemptQuestionsApiEventVersion1Component, self).setUp('')
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

    def testGetQuizAttemptResponseComponents(self):
        # Create QuizAttempt and the response objects
        path = reverse('quiz:quizAttemptObjectApiEventVersion1Component') + f'?quizId={self.quiz.id}'
        response = self.post(path=path)
        ajaxResponse = json.loads(response.content)
        self.assertEqual(200, response.status_code)

        quizAttemptId = ajaxResponse['redirectUrl'].split('/')[3]
        path = reverse('quiz:quizAttemptQuestionsApiEventVersion1Component', kwargs={'id': quizAttemptId})
        response = self.get(path=path)
        ajaxResponse = json.loads(response.content)

        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').prefetch_related(
            'responses__question'
        ).get(id=quizAttemptId)
        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()

        computedResponseList = QuestionAndResponse(questionList, responseList)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertTrue(ajaxResponse['data']['quiz']['canEdit'])
        self.assertListEqual(ajaxResponse['data']['questions'], computedResponseList.getResponse())
