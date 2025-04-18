from django.db.models import QuerySet
from django.urls import reverse

from core.models import Subject
from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestViews import BaseTestViews


class QuizIndexViewTest(BaseTestViews):
    def setUp(self, path=reverse('core:index-view')) -> None:
        super(QuizIndexViewTest, self).setUp(path)
        bakerOperations.createSubjects()

    def testIndexViewGet(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['subjects'], QuerySet))
        self.assertEqual(Subject.objects.count(), len(response.context['subjects']))
        self.assertTemplateUsed(response, 'core/index.html')
