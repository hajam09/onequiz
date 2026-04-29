from django.urls import reverse

from onequiz.tests.BaseTestViews import BaseTestViews
from tasks.models import Task


class AccountsPasswordForgottenTest(BaseTestViews):

    def setUp(self, path=reverse('accounts:password-forgotten')) -> None:
        self.basePath = path
        super(AccountsPasswordForgottenTest, self).setUp(self.basePath)
        self.client.logout()

    def testLoginGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/passwordForgotten.html')

    def testPasswordRequestExistingUser(self):
        testParams = self.TestParams(self.user.email)
        response = self.post(testParams.getData())
        messages = self.getMessages(response)

        for message in messages:
            self.assertEqual(
                str(message),
                'Check your email for a password change link.'
            )

        task = Task.objects.last()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'SendEmailToResetPasswordTask')
        self.assertEqual('testserver', task.data.get('domain'))
        self.assertEqual(1, task.data.get('user'))

    def testPasswordRequestNonExistingUser(self):
        testParams = self.TestParams('example@example.com')
        response = self.post(testParams.getData())
        messages = self.getMessages(response)

        for message in messages:
            self.assertEqual(
                str(message),
                'Check your email for a password change link.'
            )

        task = Task.objects.last()
        self.assertIsNone(task)

    class TestParams:
        def __init__(self, email):
            self.email = email

        def getData(self):
            data = {
                'email': self.email,
            }
            return data
