import json

from django.urls import reverse

from onequiz.operations import bakerOperations
from onequiz.tests.BaseTestAjax import BaseTestAjax
from quiz.models import Topic


class TopicObjectApiEventVersion1ComponentTest(BaseTestAjax):

    def setUp(self, path=reverse('quiz:topicObjectApiEventVersion1Component')) -> None:
        bakerOperations.createSubjectsAndTopics(2, 10)
        super(TopicObjectApiEventVersion1ComponentTest, self).setUp(path)

    def testGetAllTopicsForAllSubjects(self):
        response = self.get()
        ajaxResponse = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['data']['topics'])
        self.assertEqual(20, len(ajaxResponse['data']['topics']))

        self.assertListEqual(
            [{'id': t.id, 'name': t.name, 'description': t.description} for t in Topic.objects.all()],
            ajaxResponse['data']['topics']
        )

    def testGetEmptyTopicsFromNonExistingSubject(self):
        path = reverse('quiz:topicObjectApiEventVersion1Component') + f'?subject_id={0}'
        response = self.get(path=path)
        ajaxResponse = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertTrue(ajaxResponse['success'])
        self.assertIsNotNone(ajaxResponse['data']['topics'])
        self.assertEqual(0, len(ajaxResponse['data']['topics']))
        self.assertListEqual([], ajaxResponse['data']['topics'])
