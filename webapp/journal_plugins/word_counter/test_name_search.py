from webapp.tests import BaseTest
from webapp.journal_plugins.extensions import word_counter


class TestWordCounterAccess(BaseTest):
    def test_with_auth(self):
        with self.client:
            user = self.login_user()
            response = self.client.get(word_counter.url)
            self.assertEqual(response._status_code, 200)

    def test_without_auth(self):
        with self.client:
            response = self.client.get(word_counter.url)
            self.assertEqual(response._status_code, 302)
