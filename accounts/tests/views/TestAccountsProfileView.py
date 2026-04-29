from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.signing import TimestampSigner

from onequiz.tests.BaseTestViews import BaseTestViews
from tasks.models import Task


class AccountsProfileViewTest(BaseTestViews):
    def setUp(self, path=reverse('accounts:profile-view')) -> None:
        super(AccountsProfileViewTest, self).setUp(path)

    def testProfileGet(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile-information.html')
        self.assertEqual(response.context['activeSectionKey'], 'profile')
        self.assertEqual(response.context['activeSection']['title'], 'Your Profile Information')
        self.assertTrue(any(item['label'] == 'Email Address' for item in response.context['sectionItems']))

    def testAccountSettingsGet(self):
        response = self.get(path=reverse('accounts:account-settings-view'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile-information.html')
        self.assertEqual(response.context['activeSectionKey'], 'account')
        self.assertEqual(response.context['activeSection']['title'], 'Account Settings')

    def testProfileIncludesProjectRelevantTabs(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reverse('accounts:password-settings-view'), '/accounts/password-settings/')
        self.assertEqual(reverse('accounts:security-settings-view'), '/accounts/security/')
        self.assertEqual(reverse('accounts:notification-settings-view'), '/accounts/notifications/')
        self.assertEqual(reverse('accounts:email-settings-view'), '/accounts/email-settings/')
        self.assertEqual(reverse('accounts:activity-log-view'), '/accounts/activity-log/')
        self.assertEqual(reverse('accounts:privacy-settings-view'), '/accounts/privacy-settings/')
        self.assertEqual(reverse('accounts:account-management-view'), '/accounts/account-management/')

    def testProfileUpdateQueuesVerificationWhenEmailChanges(self):
        response = self.post(data={
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'new-email@example.com',
        })
        self.user.refresh_from_db()
        task = Task.objects.last()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.email, self.user.username)
        self.assertNotEqual(self.user.email, 'new-email@example.com')
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'SendEmailToVerifyNewEmailTask')
        self.assertEqual(task.data.get('newEmail'), 'new-email@example.com')

    def testVerifyNewEmailUpdatesUserEmailAndUsername(self):
        newEmail = 'verified-email@example.com'
        signer = TimestampSigner()
        tokenGenerator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = tokenGenerator.make_token(self.user)
        path = reverse('accounts:verify-new-email', kwargs={'encodedId': uid, 'token': token})

        response = self.get(path=path, data={'email': signer.sign(newEmail)})
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:profile-view'))
        self.assertEqual(self.user.email, newEmail)
        self.assertEqual(self.user.username, newEmail)
