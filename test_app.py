from unittest import TestCase
from webapp import app
from webapp import models
from webapp.extensions import db
from flask_login import current_user
from flask_security.utils import hash_password


class BaseTest(TestCase):
    def setUp(self):
        self.app = app
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        # it is too much extra work to handle CSRF tokens during testing so just disable them
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()


class TestLogins(BaseTest):
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
            self.assertEquals(current_user.email, data['email'])
