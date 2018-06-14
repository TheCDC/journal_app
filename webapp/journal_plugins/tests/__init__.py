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
            data = dict(email='test@test.com', password='password', active=True)
            user = models.User(**data)
            db.session.add(user)
            db.session.commit()
            response = self.client.post('/login', data={'email': user.email, 'password': user.password},
                                        follow_redirects=True)
            response = self.client.get('/plugins')
            print(response)
            self.assertEqual(response._status_code, 200)


