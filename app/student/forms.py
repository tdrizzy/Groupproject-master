from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional


class ProfileForm(FlaskForm):
    email = StringField('Email', render_kw={'disabled':''}, validators=[DataRequired()])
    username = StringField('Username', render_kw={'disabled':''}, validators=[DataRequired()])
    first_name = StringField('First name', render_kw={'disabled':''}, validators=[DataRequired()])
    last_name = StringField('Last name', render_kw={'disabled':''}, validators=[DataRequired()])
    profile_comment = TextAreaField('Profile comment')
    skills_offered = SelectMultipleField('Skills offered', coerce=int)
    notify_new = BooleanField('Receive email notification of new projects')
    notify_interest = BooleanField('Receive email notification of new notes of interest on projects you are interested in')
    submit = SubmitField('Save')


class FlagForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Save')


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    academic_year = SelectField('Academic year')
    overview = TextAreaField('Overview', validators=[DataRequired()])
    deliverables = TextAreaField('Deliverables', validators=[DataRequired()])
    resources = TextAreaField('Resources', validators=[DataRequired()])
    skills_required = SelectMultipleField('Skills required', coerce=int)
    submit = SubmitField('Save')


class TeamForm(FlaskForm):
    comment = TextAreaField('Team profile comment', validators=[DataRequired()])
    vacancies = TextAreaField('Vacancies message')
    matric = StringField('Add team member')
    submit = SubmitField('Save')


