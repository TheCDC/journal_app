from unittest import TestCase
from webapp.extensions import db
from webapp import app


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

