from django.urls import reverse

from onequiz.tests.BaseTestViews import BaseTestViews


class ExtrasViewTest(BaseTestViews):

    def setUp(self, path=None) -> None:
        self.basePath = path
        super(ExtrasViewTest, self).setUp('')

    def testExtrasViewGetForPrivacyPolicy(self):
        path = reverse('accounts:extras') + '?page=privacy-policy'
        response = self.get(path=path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/privacyPolicy.html')

    def testExtrasViewGetForTermsAndConditions(self):
        path = reverse('accounts:extras') + '?page=terms-and-conditions'
        response = self.get(path=path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/termsAndConditions.html')

    def testExtrasPageDoesNotExist(self):
        path = reverse('accounts:extras') + '?page=non-existing-page'
        response = self.get(path=path)
        self.assertEqual(response.status_code, 404)
