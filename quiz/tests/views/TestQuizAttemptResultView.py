from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews
from quiz.models import QuizAttempt, Topic
from quiz.models import Result


class QuizAttemptResultViewTest(BaseTestViews):

    def setUp(self, path='') -> None:
        super(QuizAttemptResultViewTest, self).setUp('')
        bakerOperations.createSubjectsAndTopics(1, 2)
        self.topic = Topic.objects.select_related('subject').first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.topic)
        self.quiz.questions.add(*[
            bakerOperations.createEssayQuestion(),
            bakerOperations.createTrueOrFalseQuestion()
        ])

        self.quizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=self.quiz.id)
        self.result = Result.objects.create(
            quizAttempt=self.quizAttempt, timeSpent=100, numberOfCorrectAnswers=5, numberOfPartialAnswers=5,
            numberOfWrongAnswers=5, score=33.33
        )
        self.path = reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': self.quizAttempt.id})

    def testQuizAttemptResultDoesNotExist(self):
        path = reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': 0})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testQuizAttemptResultViewGet(self):
        data = [
            {'key': 'Quiz', 'value': self.result.quizAttempt.quiz.name},
            None,
            {'key': 'Total Questions', 'value': self.result.quizAttempt.quiz.questions.count},
            {'key': 'Correct Questions', 'value': self.result.numberOfCorrectAnswers},
            {'key': 'Partial Questions', 'value': self.result.numberOfPartialAnswers},
            {'key': 'Wrong Questions', 'value': self.result.numberOfWrongAnswers},
            {'key': 'Your Score', 'value': f'{self.result.score} %'},
            {'key': 'Your Time', 'value': self.result.getTimeSpent()},
        ]

        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/quizAttemptResultView.html')
        self.assertTrue(isinstance(response.context['result'], Result))
        self.assertTrue(isinstance(response.context['data'], list))
        self.assertEqual(len(response.context['data']), 8)
        self.assertListEqual(response.context['data'], data)
