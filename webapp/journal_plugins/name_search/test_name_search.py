from webapp.tests import BaseTest
from webapp.journal_plugins.extensions import name_search


class TestNameSearchAccess(BaseTest):
    def test_with_auth(self):
        with self.client:
            user = self.login_user()
            response = self.client.get(name_search.url)
            self.assertEqual(response._status_code, 200)

    def test_without_auth(self):
        with self.client:
            response = self.client.get(name_search.url)
            self.assertEqual(response._status_code, 302)
