from django.urls import reverse

from core.models import QuizAttempt, Subject, Result
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizAttemptResultViewTest(BaseTestViews):
    # test update

    def setUp(self, path=None) -> None:
        super(QuizAttemptResultViewTest, self).setUp('')
        bakerOperations.createSubjects(1)
        self.subject = Subject.objects.first()

        self.quiz = bakerOperations.createQuiz(self.request.user, self.subject)
        self.quiz.questions.add(*bakerOperations.createRandomQuestions(2))

        self.quizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=self.quiz.id)
        self.result = Result.objects.create(
            quizAttempt=self.quizAttempt, timeSpent=100, numberOfCorrectAnswers=5, numberOfPartialAnswers=5,
            numberOfWrongAnswers=5, score=33.33
        )
        self.path = reverse('core:quiz-attempt-result-view', kwargs={'url': self.quizAttempt.url})

    def testQuizAttemptResultDoesNotExist(self):
        path = reverse('core:quiz-attempt-result-view', kwargs={'url': 'non-existing-url'})
        response = self.get(path=path)
        self.assertEquals(response.status_code, 404)

    def testQuizAttemptResultViewGet(self):
        data = [
            {'key': 'Quiz', 'value': self.result.quizAttempt.quiz.name},
            None,
            {'key': 'Total Questions', 'value': self.result.quizAttempt.quiz.questions.count()},
            {'key': 'Correct Answers', 'value': self.result.numberOfCorrectAnswers},
            {'key': 'Partially Correct Answers', 'value': self.result.numberOfPartialAnswers},
            {'key': 'Wrong Answers', 'value': self.result.numberOfWrongAnswers},
            {'key': 'Your Score', 'value': f'{self.result.score} %'},
            {'key': 'Your Time', 'value': self.result.getTimeSpent()},
            {'key': 'Marked By', 'value': self.result.quizAttempt.quiz.creator.get_full_name()},
        ]

        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quizAttemptResultView.html')
        self.assertTrue(isinstance(response.context['result'], Result))
        self.assertTrue(isinstance(response.context['data'], list))
        self.assertEqual(len(response.context['data']), 9)
        self.assertListEqual(response.context['data'], data)

    def testQuizCreatorViewsResultThenReturnOK(self):
        self.quizAttempt.user = bakerOperations.createUser()
        self.quizAttempt.save()

        response = self.get()
        self.assertEquals(response.status_code, 200)

    def testQuizAttemptedUserViewsResultThenReturnOK(self):
        self.quizAttempt.quiz.creator = bakerOperations.createUser()
        self.quizAttempt.quiz.save()

        response = self.get()
        self.assertEquals(response.status_code, 200)

    def testUnrelatedUserViewsResultThenReturn404(self):
        anotherUser = bakerOperations.createUser()
        self.quizAttempt.user = anotherUser
        self.quizAttempt.quiz.creator = anotherUser
        self.quizAttempt.save()
        self.quizAttempt.quiz.save()

        response = self.get()
        self.assertEquals(response.status_code, 404)
        self.assertTemplateUsed(response, 'accounts/404.html')
