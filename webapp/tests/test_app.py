from webapp import models
from webapp.extensions import db
from flask_login import current_user
from webapp.tests import BaseTest

class TestLoginRegistration(BaseTest):
    def test_register(self):
        with self.client:
            data = dict(email='test@test.com', password='blahblahblah', password_confirm='blahblahblah')
            response = self.client.post('/register', data=data, follow_redirects=True)
            user = models.User.query.first()
            self.assertEqual(response._status_code, 200)
            self.assertEqual( len(models.User.query.all()), 1)
            self.assertEqual(data['email'], user.email)

    def test_that_something_works(self):
        with self.client:
            data = dict(email='test@test.com', password='password', active=True)
            user = models.User(**data)
            db.session.add(user)
            db.session.commit()
            response = self.client.post('/login', data={'email': user.email, 'password': user.password},
                                        follow_redirects=True)
            self.assertEqual(response._status_code, 200)
            self.assertEqual(current_user.email, data['email'])
