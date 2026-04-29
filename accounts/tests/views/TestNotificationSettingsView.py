from django.urls import reverse

from accounts.models import UserNotificationSettings
from onequiz.tests.BaseTestViews import BaseTestViews


class NotificationSettingsViewTest(BaseTestViews):
    def setUp(self, path=reverse('accounts:notifications-view')) -> None:
        super(NotificationSettingsViewTest, self).setUp(path)

    def testNotificationSettingsGet(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/notification.html')
        self.assertTrue(UserNotificationSettings.objects.filter(user=self.user).exists())

    def testNotificationSettingsPost(self):
        response = self.post(data={
            'emailOnQuizAttemptSubmitted': 'on',
            'emailOnQuizMarked': 'on',
            'emailOnPasswordChanged': 'on',
            'emailOnAccountSecurityUpdate': 'on',
        })

        settingsObject = UserNotificationSettings.objects.get(user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:notifications-view'))
        self.assertTrue(settingsObject.emailOnQuizAttemptSubmitted)
        self.assertTrue(settingsObject.emailOnQuizMarked)
        self.assertTrue(settingsObject.emailOnPasswordChanged)
        self.assertTrue(settingsObject.emailOnAccountSecurityUpdate)
        self.assertFalse(settingsObject.emailOnProductUpdates)
