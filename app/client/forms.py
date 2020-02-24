from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Optional, URL


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    academic_year = SelectField('Academic year')
    overview = TextAreaField('Overview', validators=[DataRequired()])
    deliverables = TextAreaField('Deliverables', validators=[DataRequired()])
    resources = TextAreaField('Resources', validators=[DataRequired()])
    skills_required = SelectMultipleField('Skills required', coerce=int)
    submit = SubmitField('Save')


class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    telephone = StringField('Telephone', validators=[DataRequired()])
    profile_comment = TextAreaField('Comment')
    display_name_flag = BooleanField('Display name to students', default=False)
    display_email_flag = BooleanField('Display email to students', default=False)
    display_phone_flag = BooleanField('Display phone to students', default=False)
    submit = SubmitField('Save')


class ProfileFormWithCompany(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    company_id = SelectField('Company - NB: For a new company, please complete the details separately under the profile link in the menu')
    telephone = StringField('Telephone', validators=[DataRequired()])
    profile_comment = TextAreaField('Comment')
    display_name_flag = BooleanField('Display name to students', default=False)
    display_email_flag = BooleanField('Display email to students', default=False)
    display_phone_flag = BooleanField('Display phone to students', default=False)
    submit = SubmitField('Save')


class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    post_code = StringField('Post code', validators=[DataRequired()])
    web = StringField('Web address', validators=[Optional(), URL(message='Please enter your web address including the prefix (eg. http:// or https://')], render_kw={"placeholder": "https://"})
    health_policy_flag = RadioField('Do you have a written Health and Safety policy?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    health_policy_link = StringField('Link to H&S policy')
    training_policy_flag = RadioField('Do you have a H&S training policy?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    training_policy_link = StringField('Link to H&S training policy')
    hse_registered = RadioField('Are you registered with the Health and Safety Executive?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    la_registered = RadioField('Are you registered with the local authority environmental health dept?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    insured = RadioField('Do you have public liability insurance?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    student_insured = RadioField('Does the PL policy cover the student(s)?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    company_risk_assessed = RadioField('Have you carried out a workplace risk assessment?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    risks_reviewed = RadioField('Are risks reviewed regularly?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    risks_mitigated = RadioField('Are risk assessment results implemented?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    accident_procedure_flag = RadioField('Do you have a procedure for reporting accidents?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    emergency_procedures_flag = RadioField('Do you have procedures for dealing with emergencies?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    report_student_accidents_flag = RadioField('Will all accidents involving the student be reported to the University?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    report_student_illness_flag = RadioField('Will any student illness attributable to the work be reported to the University?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    data_policy_flag = RadioField('Do you have a data protection policy?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    data_policy_link = StringField('Link to DP policy')
    security_measures_flag = RadioField('Do you have data protection/privacy measures in place?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    ico_registration_number = StringField('What is your registration number with the Information Commissioner\'s Office?')
    data_training_flag = RadioField('Do staff receive regular data protection training?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    security_policy_flag = RadioField('Do you have information security policies in place?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    security_policy_link = StringField('Link to information security policy')
    privacy_notice_flag = RadioField('Is there a staff privacy notice that would cover the student?', choices=[(1,'yes'),(0,'no')], coerce=int, validators=[Optional()])
    data_contact_first_name = StringField('First name')
    data_contact_last_name = StringField('Last name')
    data_contact_position = StringField('Position')
    data_contact_telephone = StringField('Telephone')
    submit = SubmitField('Save')
