from wtforms import form, fields, validators
from models import User
import flask_login as login
from configuration import app
import flask_admin as admin
from flask import Flask, url_for, redirect, render_template, request
from flask_admin import helpers, expose


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = User.objects(username=self.login.data).first()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if not User.validate_login(user.hashed_password, self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return User.objects(username=self.login.data).first()


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(username):
        return User.objects(username=username).first()


class SecureAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(SecureAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = 'If you need admin access, see Jason or Thomas'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(SecureAdminIndexView, self).index()

init_login()