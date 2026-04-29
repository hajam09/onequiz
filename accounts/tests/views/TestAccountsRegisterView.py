from django.http import QueryDict
from django.urls import reverse

from accounts.forms import RegistrationForm
from onequiz.settings import TEST_PASSWORD
from onequiz.tests.BaseTestViews import BaseTestViews
from tasks.models import Task


class AccountsRegisterViewTest(BaseTestViews):

    def setUp(self, path=reverse('accounts:register')) -> None:
        self.basePath = path
        super(AccountsRegisterViewTest, self).setUp(self.basePath)
        self.client.logout()

    def testRegisterGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')
        self.assertIsInstance(response.context['form'], RegistrationForm)

    def testRegistrationValidForm(self):
        testParams = self.TestParams('user@example.com', TEST_PASSWORD, 'Django', 'Admin')
        response = self.post(testParams.getData())
        messages = self.getMessages(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(messages))
        self.assertRedirects(response, '/accounts/login/')

        for message in messages:
            self.assertEqual(
                str(message),
                'We\'ve sent you an activation link. Please check your email.'
            )

    def testRegisterSendEmailToActivateAccountTaskCreated(self):
        testParams = self.TestParams('user@example.com', TEST_PASSWORD, 'Django', 'Admin')
        self.post(testParams.getData())

        task = Task.objects.last()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'SendEmailToActivateAccountTask')
        self.assertEqual('testserver', task.data.get('domain'))
        self.assertEqual(2, task.data.get('user'))

    class TestParams:
        def __init__(self, email, password, firstName, lastName):
            self.email = email
            self.password = password
            self.firstName = firstName
            self.lastName = lastName

        def getData(self):
            data = {
                'first_name': self.firstName,
                'last_name': self.lastName,
                'email': self.email,
                'password1': self.password,
                'password2': self.password,

            }
            queryDict = QueryDict('', mutable=True)
            queryDict.update(data)
            return queryDict
