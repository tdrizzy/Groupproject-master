from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import and_
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash, pbkdf2_hex

from app import login_manager
from app import db


class AcademicYear(db.Model):
    __tablename__ = 'academic_year'

    year = db.Column(db.String(7), primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date  = db.Column(db.DateTime, nullable=False)
    projects = db.relationship('Project', backref='year', lazy='select')

    def __repr__(self):
        return '<Academic year: {}>'.format(self.year)


class AlertQueue(db.Model):
    __tablename__ = 'alert_queue'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    email = db.Column(db.String(60), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, index=True, default=datetime.now())
    sent_date = db.Column(db.DateTime, index=True)
    subject = db.Column(db.String(120), nullable=False)
    message_text = db.Column(db.Text, nullable=False)


class AlertText(db.Model):
    __tablename__ = 'alert_text'

    code = db.Column(db.String(20), primary_key=True)
    subject = db.Column(db.String(255))
    message_text = db.Column(db.Text)


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    description = db.Column(db.Text)
    address = db.Column(db.String(255), index=True)
    city = db.Column(db.String(60), index=True)
    post_code = db.Column(db.String(10))
    web = db.Column(db.String(255), index=True, unique=True)
    health_policy_flag = db.Column(db.Boolean, nullable=True)             # Does the company have a written H&S policy?
    health_policy_link = db.Column(db.String(255))                        # Link to policy
    training_policy_flag = db.Column(db.Boolean, nullable=True)           # Does the company have a H&S training policy?
    training_policy_link = db.Column(db.String(255))                      # Link to policy
    hse_registered = db.Column(db.Boolean, nullable=True)                 # Is the company registered with HSE?
    la_registered = db.Column(db.Boolean, nullable=True)                  # Is the company registered with local auth. environmental health dept?
    insured = db.Column(db.Boolean, nullable=True)                        # Does the company have public liability insurance?
    student_insured = db.Column(db.Boolean, nullable=True)                # Is the student covered by this policy?
    company_risk_assessed = db.Column(db.Boolean, nullable=True)          # Has a company risk assessment been carried out?
    risks_reviewed = db.Column(db.Boolean, nullable=True)                 # Are the risks reviewed regularly?
    risks_mitigated = db.Column(db.Boolean, nullable=True)                # Are the risk assessment results implemented?
    accident_procedure_flag = db.Column(db.Boolean, nullable=True)         # Is there a procedure for reporting accidents (RIDDOR)?
    emergency_procedures_flag = db.Column(db.Boolean, nullable=True)      # Are emergency procedures in place?
    report_student_accidents_flag = db.Column(db.Boolean, nullable=True)  # Will all accidents concerning students be reported to the University?
    report_student_illness_flag = db.Column(db.Boolean, nullable=True)    # Will any student illness attributable to the work be reported to the University?
    data_policy_flag = db.Column(db.Boolean, nullable=True)               # Is there a data protection policy?
    data_policy_link = db.Column(db.String(255))                          # Link to policy
    security_measures_flag = db.Column(db.Boolean, nullable=True)         # Are data protection/privacy measures in place?
    ico_registration_number = db.Column(db.String(20))                    # Registration No. with ICO
    data_training_flag = db.Column(db.Boolean, nullable=True)             # Do staff receive regular data protection training?
    security_policy_flag = db.Column(db.Boolean, nullable=True)           # Are information security policies in place?
    security_policy_link = db.Column(db.String(255))                      # Link to policy
    privacy_notice_flag = db.Column(db.Boolean, nullable=True)            # Is there a staff privacy notice that would cover the student?
    data_contact_first_name = db.Column(db.String(30))
    data_contact_last_name = db.Column(db.String(50))
    data_contact_position = db.Column(db.String(255))
    data_contact_telephone = db.Column(db.String(30))
    employees = db.relationship('User', backref='company', lazy='joined')

    def __repr__(self):
        return '<Company: {}>'.format(self.name)

    @property
    def percent_complete(self):
        attributes = [a for a in self.__dict__]
        null_attributes = [a for a in self.__dict__ if self.__getattribute__(a) is None]

        return (len(attributes) - len(null_attributes)) / len(attributes)

    @property
    def is_new(self):
        if self.name == 'New company':
            return True
        return False


class Domain(db.Model):
    __tablename__ = 'domain'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    statuses = db.relationship('Status', backref='domain', lazy='select')

    def __repr__(self):
        return '<Domain: {}>'.format(self.name)


class Faq(db.Model):
    __tablename__ = 'faq'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120), nullable=False)
    answer = db.Column(db.Text)
    rank = db.Column(db.Integer, default=0)
    external = db.Column(db.Boolean, default=False)
    student = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<FAQ: {}>'.format(self.question)


class Flag(db.Model):
    __tablename__ = 'flag'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text)

    def __repr__(self):
        return '<Flag: {} {}, {}>'.format(self.user.first_name, self.user.last_name, self.project.title)


class Interest(db.Model):
    __tablename__ = 'interest'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Interest: {} {}, {}>'.format(self.user.first_name, self.user.last_name, self.project.title)


class Programme(db.Model):
    __tablename__ = 'programme'

    code = db.Column(db.String(10), unique=True, primary_key=True)
    title = db.Column(db.String(200))
    students = db.relationship('User', backref='programme', lazy='select')

    def __repr__(self):
        return '<Programme: {}>'.format(self.title)


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    updated_date = db.Column(db.DateTime, default=datetime.now)
    academic_year = db.Column(db.String(7), db.ForeignKey('academic_year.year'), nullable=False, index=True)
    overview = db.Column(db.Text)
    deliverables = db.Column(db.Text)
    resources = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False, index=True)
    admin_notes = db.Column(db.Text)
    flags = db.relationship('Flag', backref='project', lazy='joined', cascade="all, delete", passive_deletes=True)
    notes_of_interest = db.relationship('Interest', backref='project', lazy='joined', cascade="all, delete", passive_deletes=True)
    skills_required = db.relationship('SkillRequired', backref='project', lazy='joined', cascade="all, delete", passive_deletes=True)
    teams = db.relationship('Team', backref='project', lazy='select', cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Project: {}>'.format(self.title)


class Settings(db.Model):
    __tablename__ = 'settings'

    name = db.Column(db.String(60), primary_key=True)
    subtitle = db.Column(db.String(120))
    notification_period = db.Column(db.Float, nullable=False, default=4.0)
    last_notification_check = db.Column(db.DateTime, nullable=False)
    contact_name = db.Column(db.String(60))
    contact_email = db.Column(db.String(60))
    minimum_team_size = db.Column(db.Integer, default=4)
    maximum_team_size = db.Column(db.Integer, default=6)


class Skill(db.Model):
    __tablename__ = 'skill'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    offered = db.relationship('SkillOffered', backref='skill_offered', lazy='select')
    required = db.relationship('SkillRequired', backref='skill_required', lazy='select')

    def __repr__(self):
        return '<Skill: {}>'.format(self.name)


class SkillOffered(db.Model):
    __tablename__ = 'skill_offered'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False, index=True)

    def __repr__(self):
        return '<Skill offered: {} {}, {}>'.format(self.user.first_name, self.user.last_name, self.skill.name)


class SkillRequired(db.Model):
    __tablename__ = 'skill_required'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete="CASCADE"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False, index=True)

    def __repr__(self):
        return '<Skill required: {}, {}>'.format(self.project.title, self.skill_required.name)


class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(120))
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), nullable=False, index=True)
    action_text = db.Column(db.String(10), nullable=False)
    default_for_domain = db.Column(db.Boolean, nullable=False)
    projects = db.relationship('Project', backref='status', lazy='joined')
    teams = db.relationship('Team', backref='status', lazy='joined')

    def __repr__(self):
        return '<Status: {}>'.format(self.name)


class Transition(db.Model):
    __tablename__ = 'transition'

    id = db.Column(db.Integer, primary_key=True)
    admin_only = db.Column(db.Boolean, default=False)
    from_status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False, index=True)
    to_status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False, index=True)
    from_status = relationship("Status", foreign_keys=[from_status_id])
    to_status = relationship("Status", foreign_keys=[to_status_id])

    def __repr__(self):
        return '<Status transition: {} - {}>'.format(self.from_status.name, self.to_status.name)


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    updated_date = db.Column(db.DateTime, default=datetime.now)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False, index=True)
    comment = db.Column(db.Text)
    vacancies = db.Column(db.Text)
    members = db.relationship('TeamMember', backref='team', lazy='joined', cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Team: {:d} {}>'.format(self.id, self.project.title)


class TeamMember(db.Model):
    __tablename__ = 'team_member'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False, index=True)
    project_manager = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Team member: {} {} in team {:d}>'.format(self.user.first_name, self.user.last_name, self.id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    confirmation_token = db.Column(db.String(120))
    telephone = db.Column(db.String(60), index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    display_name_flag = db.Column(db.Boolean, default=False)
    display_email_flag = db.Column(db.Boolean, default=False)
    display_phone_flag = db.Column(db.Boolean, default=False)
    company_confirmed = db.Column(db.Boolean, default=False)
    programme_code = db.Column(db.String(10), db.ForeignKey('programme.code'))
    profile_comment = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_student = db.Column(db.Boolean, default=False)
    is_external = db.Column(db.Boolean, default=True)
    notify_new = db.Column(db.Boolean, default=False)
    notify_interest = db.Column(db.Boolean, default=False)
    login_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    online_flag = db.Column(db.Boolean, default=False)
    alerts = db.relationship('AlertQueue', backref='user', lazy='select')
    notes_of_interest = db.relationship('Interest', backref='user', lazy='select')
    projects_offered = db.relationship('Project', backref='client', lazy='joined')
    skills_offered = db.relationship('SkillOffered', backref='user', lazy='joined')
    flags = db.relationship('Flag', backref='user', lazy='select')
    members = db.relationship('TeamMember', backref='user', lazy='select')

    @staticmethod
    def generate_token(source):
        return pbkdf2_hex(source, 'email-confirmation', iterations=1000, keylen=20)

    @property
    def token(self):
        raise AttributeError('token is not a readable attribute.')

    @token.setter
    def token(self, email):
        self.confirmation_token = self.generate_token(email)

    def verify_token(self, token):
        if token == self.generate_token(self.email):
            self.confirmation_token = None
            return True
        return False

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
