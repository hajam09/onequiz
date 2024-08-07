import json

from onequiz.tests.BaseTest import BaseTest


class BaseTestAjax(BaseTest):

    def setUp(self, path=None) -> None:
        super(BaseTestAjax, self).setUp(path)
        self.path = path

    def get(self, data=None, path=None):
        data = data or {}
        path = path or self.path
        return self.client.get(path, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def post(self, data=None, path=None):
        data = data or {}
        path = path or self.path
        return self.client.post(path, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def put(self, data=None, path=None):
        data = data or {}
        path = path or self.path
        return self.client.put(path, data=json.dumps(data), content_type='application/json', follow=True)

    def delete(self, data=None, path=None):
        data = data or {}
        path = path or self.path
        return self.client.delete(path, data=json.dumps(data), content_type='application/json', follow=True)
