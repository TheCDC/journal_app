from webapp.tests import BaseTest, TestEnfranchisedUser
from webapp.journal_plugins.extensions import date_recognizer
from webapp import models



class TestNameSearchAccess(BaseTest):
    def test_with_auth(self):
        with self.client:
            user = self.login_user()
            response = self.client.get(date_recognizer.url)
            self.assertEqual(response._status_code, 200)

    def test_without_auth(self):
        with self.client:
            response = self.client.get(date_recognizer.url)
            self.assertEqual(response._status_code, 302)

