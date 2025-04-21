from django.db.models import QuerySet
from django.urls import reverse

from core.models import QuizAttempt
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class AttemptedQuizzesViewTest(BaseTestViews):

    def setUp(self, path=reverse('core:attempted-quizzes-view')) -> None:
        super().setUp(path)
        self.quiz = bakerOperations.createQuiz(self.request.user)

    def testAttemptedQuizzesViewGet(self):
        quizAttempts = QuizAttempt.objects.bulk_create([
            QuizAttempt(quiz=self.quiz, user=self.request.user)
            for _ in range(4)
        ])

        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/attemptedQuizzesView.html')

        contextList = response.context['quizAttemptList']
        self.assertIsInstance(contextList, QuerySet)
        self.assertEqual(contextList.count(), len(quizAttempts))

        for attempt in contextList:
            self.assertEqual(attempt.user, self.request.user)

    def testAttemptedQuizzesViewWithNoAttempts(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/attemptedQuizzesView.html')

        contextList = response.context['quizAttemptList']
        self.assertIsInstance(contextList, QuerySet)
        self.assertEqual(contextList.count(), 0)

    def testAttemptedQuizzesViewDoesNotIncludeOtherUsersAttempts(self):
        newUser = bakerOperations.createUser()
        newUserQuizAttempts = [QuizAttempt(quiz=self.quiz, user=newUser) for _ in range(3)]
        currentUserQuizAttempts = [QuizAttempt(quiz=self.quiz, user=self.request.user) for _ in range(2)]
        QuizAttempt.objects.bulk_create(newUserQuizAttempts + currentUserQuizAttempts)

        response = self.get()
        contextList = response.context['quizAttemptList']
        self.assertEqual(contextList.count(), 2)

        for attempt in contextList:
            self.assertEqual(attempt.user, self.request.user)

    def testAttemptedQuizzesViewRequiresLogin(self):
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login?next=/my-attempted-quizzes/', response.url)
