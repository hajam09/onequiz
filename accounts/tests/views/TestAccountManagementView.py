from django.contrib.auth.models import User
from django.urls import reverse

from onequiz.tests.BaseTestViews import BaseTestViews


class AccountManagementViewTest(BaseTestViews):
    def setUp(self, path=reverse('accounts:account-management-view')) -> None:
        super(AccountManagementViewTest, self).setUp(path)

    def testAccountManagementGet(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/account-management.html')

    def testDeactivateAccount(self):
        response = self.post(data={'action': 'deactivate-account'})

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:login-view'))
        self.assertFalse(self.user.is_active)

    def testDeleteAccountRequiresConfirmation(self):
        response = self.post(data={'action': 'delete-account', 'deleteAccountConfirmation': 'WRONG'})

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:account-management-view'))
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def testDeleteAccount(self):
        userId = self.user.pk

        response = self.post(data={'action': 'delete-account', 'deleteAccountConfirmation': 'DELETE'})

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('registration'))
        self.assertFalse(User.objects.filter(pk=userId).exists())
