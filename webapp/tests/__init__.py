from unittest import TestCase
from webapp.extensions import db

from webapp import app
from webapp import models
import flask_login

import random
import string
import os
import io


def random_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(10))


class BaseTest(TestCase):
    def setUp(self):
        self.app = app
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = '127.0.0.1:5000'
        # it is too much extra work to handle CSRF tokens during testing so just disable them
        app.config['WTF_CSRF_ENABLED'] = False
        with self.app.app_context():
            self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login_user(self, email=None, password=None, **kwargs):
        if not email:
            email = f'{random_name()}@{random_name()}.com'
        if not password:
            password = random_name()

        data = dict(email=email, password=password, active=True)
        user = models.User(**data)
        db.session.add(user)
        db.session.commit()
        response = self.client.post('/login', data={'email': user.email, 'password': user.password},
                                    follow_redirects=True)
        assert len(models.User.query.all()) == 1
        user = models.User.query.first()
        assert response._status_code == 200
        assert flask_login.current_user.email == data['email']
        return user


class TestEnfranchisedUser(BaseTest):
    file_name = 'example_journal.txt'
    journal_path = os.path.join(os.path.dirname(__file__), file_name)

    def setUp(self):
        super().setUp()
        with self.client:
            with open(TestEnfranchisedUser.journal_path, 'rb') as f:
                user = self.login_user()
                data = dict(file=(f, TestEnfranchisedUser.file_name))
                response = self.client.post('/home', data=data, follow_redirects=True)
                self.assertEqual(response._status_code, 200)
                self.user = user
