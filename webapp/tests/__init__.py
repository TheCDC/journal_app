from unittest import TestCase
from webapp.extensions import db

from webapp import app
from webapp import models
import flask_login


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

    def login_user(self, email, password,**kwargs):
        data = dict(email=email, password=password, active=True)
        user = models.User(**data)

        db.session.add(user)
        db.session.commit()
        response = self.client.post('/login', data={'email': user.email, 'password': user.password},
                                    follow_redirects=True)
        assert response._status_code == 200
        assert flask_login.current_user.email == data['email']
        return user
