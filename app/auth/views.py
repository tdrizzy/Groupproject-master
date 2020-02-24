from flask import flash, redirect, render_template, url_for, current_app, abort, Flask, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message, Mail
from datetime import datetime

from . import auth
from .forms import *
from .. import db
from app.models import User, Company
from app.common import get_this_year
import logging

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        company = Company(
            name='New company',
            description='placeholder',
            address='placeholder',
            city='placeholder',
            post_code='placehldr'
        )
        db.session.add(company)
        db.session.commit()

        user = User(email=form.email.data,
                    username=form.username.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data,
                    token=form.email.data,
                    company_id=company.id)

        db.session.add(user)
        db.session.commit()

        company.created_by = user.id
        db.session.commit()

        body = """
        Thank you for registering on the Edinburgh Napier University student project exchange.
         
        To confirm your email address and unlock your account, please click the link below.
        
        https://projex.napier.ac.uk/auth/confirm/"""

        body += User.generate_token(user.email)

        body += """
        
        
        
        """

        msg = Message(subject="Edinburgh Napier project exchange",
                      body=body,
                      sender="no-reply@projex.napier.ac.uk",
                      recipients=[user.email])
        mail = Mail(current_app)
        mail.send(msg)

        flash('Please check your email inbox')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    try:
        user = User.query.filter_by(confirmation_token=token).first_or_404()
    except:
        flash('Confirmation token does not match', 'error')
        abort(404)

    user.confirmation_token = None
    db.session.add(user)
    db.session.commit()
    flash('Your account is confirmed - please log in')
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.confirmation_token is not None:
            flash('Unconfirmed. Please check your email inbox', 'error')

        elif user is not None and user.verify_password(form.password.data):
            login_user(user)
            user.login_count = user.login_count + 1
            user.last_login = datetime.now()
            db.session.commit()
            logging.info('{} {} logged in at {}'.format(user.first_name, user.last_name, datetime.now().strftime('%y-%m-%d %H:%M')))

            session['academic_year'] = get_this_year().year

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_external:
                return redirect(url_for('client.projects'))
            elif user.is_staff:
                return redirect(url_for('staff.projects'))
            else:
                return redirect(url_for('student.projects'))

        else:
            flash('Invalid email or password', 'error')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    user = User.query.get(current_user.id)
    session.clear()
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('home.homepage'))


@auth.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    user = User.query.get(current_user.id)
    form = PasswordForm()
    if form.validate_on_submit():
        if user.verify_password(form.current.data):
            user.password=form.password.data
            db.session.commit()

            flash('Password updated')
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('client.projects'))
        else:
            flash('Incorrect current password entered', 'error')

    return render_template('auth/password.html', form=form, title='Change your password')


@auth.route('/forgotten', methods=['GET', 'POST'])
def forgotten():
    form = ForgottenForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email = form.email.data).first()
            user.token = user.email
            db.session.add(user)
            db.session.commit()

            body = """
            The Edinburgh Napier Projects Exchange has received a password reset request for your account.

            To create a new password, please click the link below.

            https://projex.napier.ac.uk/auth/reset/"""

            body += User.generate_token(user.email)

            body += """
            
            
            
            """

            msg = Message(subject="Edinburgh Napier project exchange",
                          body=body,
                          sender="no-reply@projex.napier.ac.uk",
                          recipients=[user.email])
            mail = Mail(current_app)
            mail.send(msg)

            flash('Please check your email inbox')
        except:
            logging.info('Password reset: {} not recognised at {}'.format(form.email.data, datetime.now().strftime('%y-%m-%d %H:%M')))
            flash('Email not recognised', 'error')

    return render_template('auth/forgotten.html', form=form, title='Request password reset')


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    try:
        user = User.query.filter_by(confirmation_token=token).first()
    except:
        flash('Confirmation token does not match', 'error')
        abort(404)

    form = ResetForm()
    if form.validate_on_submit():
        user.password=form.password.data
        user.confirmation_token = None
        db.session.add(user)
        db.session.commit()
        flash('Password updated - please log in')
        return redirect(url_for('auth.login'))

    return render_template('auth/password.html', form=form, title='Reset your password')
