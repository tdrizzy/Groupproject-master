import unittest
from flask_testing import TestCase
from flask import abort, url_for
from app.models import Programme, Company

from app import create_app, db
from app.models import User

from app import common


class TestBase(TestCase):

    def create_app(self):

        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql://soc09109:groupproject@localhost:3306/soc09109_test'
        )
        return app

    def setUp(self):
        db.create_all()
        admin = User(username="admin", password="admin2016", is_admin=True)
        user = User(username="test_user", password="test2016")

        # save users to database
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestModels(TestBase):

    def test_user_model(self):
        self.assertEqual(User.query.count(), 2)

    def test_programme_model(self):
        programme = Programme(code="BSc Comp", title="BSc Computing")
        db.session.add(programme)
        db.session.commit()
        self.assertEqual(Programme.query.count(), 1)

    def test_company_model(self):
        company = Company(name="RBS", description="International bank", address="36 St Andrew Square", city="Edinburgh", post_code="EH2 2YB")
        db.session.add(company)
        db.session.commit()
        self.assertEqual(Company.query.count(), 1)
        self.assertFalse(company.is_new)
        company = Company(name="New company", description="placeholder", address="placeholder", city="placeholder", post_code="placehldr")
        db.session.add(company)
        db.session.commit()
        self.assertEqual(Company.query.count(), 2)
        self.assertTrue(company.is_new)


class TestViews(TestBase):

    def test_homepage_view(self):
        response = self.client.get(url_for('home.homepage'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        target_url = url_for('auth.logout')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_dashboard_view(self):
        target_url = url_for('home.dashboard')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_admin_dashboard_view(self):
        target_url = url_for('home.admin_dashboard')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_programmes_view(self):
        target_url = url_for('admin.list_programmes')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_companies_view(self):
        target_url = url_for('admin.list_companies')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_employees_view(self):
        target_url = url_for('admin.list_users')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class TestErrorPages(TestBase):

    def test_403_forbidden(self):
        @self.app.route('/403')
        def forbidden_error():
            abort(403)

        response = self.client.get('/403')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(b"403 Error" in response.data)

    def test_404_not_found(self):
        response = self.client.get('/nothinghere')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(b"404 Error" in response.data)

    def test_500_internal_server_error(self):
        @self.app.route('/500')
        def internal_server_error():
            abort(500)

        response = self.client.get('/500')
        self.assertEqual(response.status_code, 500)
        self.assertTrue(b"500 Error" in response.data)


class TestOther(TestBase):

    def test_sanitise(self):
        text = "HTML with <script> tags, \"quotes\" & \'apostrophes\' and forward/slashes"
        text2 = "HTML with &lt;script&gt; tags, &quot;quotes&quot; &amp; &#x27;apostrophes&#x27; and forward&#x2F;slashes"
        self.assertEqual(common.sanitise(text), text2)


if __name__ == '__main__':
    unittest.main()
