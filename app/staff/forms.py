from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired, Optional


class ProfileForm(FlaskForm):
    email = StringField('Email', render_kw={'disabled':''}, validators=[DataRequired()])
    username = StringField('Username', render_kw={'disabled':''}, validators=[DataRequired()])
    first_name = StringField('First name', render_kw={'disabled':''}, validators=[DataRequired()])
    last_name = StringField('Last name', render_kw={'disabled':''}, validators=[DataRequired()])
    profile_comment = TextAreaField('Profile comment')
    submit = SubmitField('Save')


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    academic_year = SelectField('Academic year')
    overview = TextAreaField('Overview', validators=[DataRequired()])
    deliverables = TextAreaField('Deliverables', validators=[DataRequired()])
    resources = TextAreaField('Resources', validators=[DataRequired()])
    skills_required = SelectMultipleField('Skills required', coerce=int)
    submit = SubmitField('Save')
