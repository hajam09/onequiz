from django.urls import reverse

from core.models import Quiz
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizIndexViewTest(BaseTestViews):
    def setUp(self, path=reverse('core:index-view')) -> None:
        super(QuizIndexViewTest, self).setUp(path)

    def testIndexViewGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertIn('subjects', response.context)
        subjects = response.context['subjects']

        self.assertIsInstance(subjects, list)
        self.assertEqual(subjects, list(Quiz.Subject.choices))
        self.assertEqual(len(subjects), 30)

        for subject in subjects:
            self.assertIsInstance(subject, tuple)
            self.assertEqual(len(subject), 2)
            self.assertIsInstance(subject[0], str)
            self.assertIsInstance(str(subject[1]), str)
            self.assertEqual(subject[0], subject[1])

        values = [s[0] for s in subjects]
        self.assertEqual(len(values), len(set(values)))

    def testIndexViewDoesNotRequireLogin(self):
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertIn('subjects', response.context)
