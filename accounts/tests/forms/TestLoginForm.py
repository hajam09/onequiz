from unittest.mock import patch

from accounts.forms import LoginForm
from onequiz.settings import TEST_PASSWORD
from onequiz.tests.BaseTest import BaseTest


class LoginFormTest(BaseTest):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(LoginFormTest, self).setUp('')
        self.client.logout()

    @patch('accounts.forms.login')
    def testFormIsValid(self, mockLogin):
        mockLogin.return_value = True
        testParams = self.TestParams(email=self.user.email, password=TEST_PASSWORD)
        form = LoginForm(request=self.request, data=testParams.getData())
        self.client.login(username=self.user.username, password=TEST_PASSWORD)
        self.assertTrue(form.is_valid())
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertEqual(form.errors.as_data(), {})

    def testFormIncorrectCredentials(self):
        testParams = self.TestParams(email=self.user.email, password='TEST_PASSWORD')
        form = LoginForm(request=self.request, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertNotIn('_auth_user_id', self.client.session)

        for message in form.errors.as_data()['password'][0]:
            self.assertEqual(message, 'Username or Password did not match!')

    class TestParams:
        def __init__(self, email, password):
            self.email = email
            self.password = password

        def getData(self):
            data = {
                'email': self.email,
                'password': self.password,
            }
            return data
