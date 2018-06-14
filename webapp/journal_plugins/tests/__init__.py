from webapp.tests import BaseTest
from webapp.extensions import db
from webapp import models

class TestVisitPluginHome(BaseTest):
    def test_visit_without_auth(self):
        with self.client:
            response = self.client.get('/plugins')
            print(response._status_code)
            self.assertIn(response._status_code, [301,302])
    def test_visit_with_auth(self):
        with self.client:
            user = self.login_user('test@test.com','testpassword')
            response = self.client.get('/plugins')
            print(response)
            self.assertEqual(response._status_code, 200)


