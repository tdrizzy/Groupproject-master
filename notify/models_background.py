from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean, and_
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from instance.config import *

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class AcademicYear(Base):
    __tablename__ = 'academic_year'

    year = Column(String(7), primary_key=True)
    start_date = Column(DateTime, nullable=False)
    end_date  = Column(DateTime, nullable=False)
    projects = relationship('Project', backref='year', lazy='select')

    def __repr__(self):
        return '<Academic year: {}>'.format(self.year)


class AlertQueue(Base):
    __tablename__ = 'alert_queue'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    email = Column(String(60), nullable=False)
    created_date = Column(DateTime, nullable=False, index=True)
    sent_date = Column(DateTime, index=True)
    subject = Column(String(120), nullable=False)
    message_text = Column(Text, nullable=False)


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    description = Column(Text)
    address = Column(String(120), index=True)
    city = Column(String(60), index=True)
    post_code = Column(String(10))
    web = Column(String(120), index=True, unique=True)
    health_policy_flag = Column(Boolean, nullable=True)             # Does the company have a written H&S policy?
    health_policy_link = Column(String(120))                        # Link to policy
    training_policy_flag = Column(Boolean, nullable=True)           # Does the company have a H&S training policy?
    training_policy_link = Column(String(120))                      # Link to policy
    hse_registered = Column(Boolean, nullable=True)                 # Is the company registered with HSE?
    la_registered = Column(Boolean, nullable=True)                  # Is the company registered with local auth. environmental health dept?
    insured = Column(Boolean, nullable=True)                        # Does the company have public liability insurance?
    student_insured = Column(Boolean, nullable=True)                # Is the student covered by this policy?
    company_risk_assessed = Column(Boolean, nullable=True)          # Has a company risk assessment been carried out?
    risks_reviewed = Column(Boolean, nullable=True)                 # Are the risks reviewed regularly?
    risks_mitigated = Column(Boolean, nullable=True)                # Are the risk assessment results implemented?
    accident_procedure_flag = Column(Boolean, nullable=True)         # Is there a procedure for reporting accidents (RIDDOR)?
    emergency_procedures_flag = Column(Boolean, nullable=True)      # Are emergency procedures in place?
    report_student_accidents_flag = Column(Boolean, nullable=True)  # Will all accidents concerning students be reported to the University?
    report_student_illness_flag = Column(Boolean, nullable=True)    # Will any student illness attributable to the work be reported to the University?
    data_policy_flag = Column(Boolean, nullable=True)               # Is there a data protection policy?
    data_policy_link = Column(String(120))                          # Link to policy
    security_measures_flag = Column(Boolean, nullable=True)         # Are data protection/privacy measures in place?
    ico_registration_number = Column(String(20))                    # Registration No. with ICO
    data_training_flag = Column(Boolean, nullable=True)             # Do staff receive regular data protection training?
    security_policy_flag = Column(Boolean, nullable=True)           # Are information security policies in place?
    security_policy_link = Column(String(120))                      # Link to policy
    privacy_notice_flag = Column(Boolean, nullable=True)            # Is there a staff privacy notice that would cover the student?
    data_contact_first_name = Column(String(30))
    data_contact_last_name = Column(String(30))
    data_contact_position = Column(String(30))
    data_contact_telephone = Column(String(30))
    employees = relationship('User', backref='company', lazy='joined')

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


class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    description = Column(String(120), nullable=False)
    statuses = relationship('Status', backref='domain', lazy='select')

    def __repr__(self):
        return '<Domain: {}>'.format(self.name)


class Faq(Base):
    __tablename__ = 'faq'

    id = Column(Integer, primary_key=True)
    question = Column(String(120), nullable=False)
    answer = Column(Text)
    rank = Column(Integer, default=0)
    external = Column(Boolean, default=False)
    student = Column(Boolean, default=False)

    def __repr__(self):
        return '<FAQ: {}>'.format(self.question)


class Flag(Base):
    __tablename__ = 'flag'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    message = Column(Text)

    def __repr__(self):
        return '<Flag: {} {}, {}>'.format(self.user.first_name, self.user.last_name, self.project.title)


class Interest(Base):
    __tablename__ = 'interest'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return '<Interest: {} {}, {}>'.format(self.user.first_name, self.user.last_name, self.project.title)


class Programme(Base):
    __tablename__ = 'programme'

    code = Column(String(10), unique=True, primary_key=True)
    title = Column(String(200))
    students = relationship('User', backref='programme', lazy='select')

    def __repr__(self):
        return '<Programme: {}>'.format(self.title)


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now)
    academic_year = Column(String(7), ForeignKey('academic_year.year'), nullable=False, index=True)
    overview = Column(Text)
    deliverables = Column(Text)
    resources = Column(Text)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    admin_notes = Column(Text)
    flags = relationship('Flag', backref='project', lazy='joined', cascade="all, delete", passive_deletes=True)
    notes_of_interest = relationship('Interest', backref='project', lazy='joined', cascade="all, delete", passive_deletes=True)
    skills_required = relationship('SkillRequired', backref='project', lazy='joined', cascade="all, delete", passive_deletes=True)
    teams = relationship('Team', backref='project', lazy='select', cascade="all, delete", passive_deletes=True)

    @property
    def status(self):
        return

    def __repr__(self):
        return '<Project: {}>'.format(self.title)


class Settings(Base):
    __tablename__ = 'settings'

    name = Column(String(60), primary_key=True)
    subtitle = Column(String(120))
    notification_period = Column(Integer, nullable=False, default=4)
    last_notification_check = Column(DateTime, nullable=False)
    contact_name = Column(String(60))
    contact_email = Column(String(60))
    minimum_team_size = Column(Integer, default=4)
    maximum_team_size = Column(Integer, default=6)


class Skill(Base):
    __tablename__ = 'skill'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    description = Column(String(120), nullable=False)
    offered = relationship('SkillOffered', backref='skill_offered', lazy='select')
    required = relationship('SkillRequired', backref='skill_required', lazy='select')

    def __repr__(self):
        return '<Skill: {}>'.format(self.name)


class SkillOffered(Base):
    __tablename__ = 'skill_offered'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey('skill.id'), nullable=False, index=True)

    def __repr__(self):
        return '<Skill offered: {} {}, {}>'.format(self.user.first_name, self.user.last_name, self.skill.name)


class SkillRequired(Base):
    __tablename__ = 'skill_required'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id', ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey('skill.id'), nullable=False, index=True)

    def __repr__(self):
        return '<Skill required: {}, {}>'.format(self.project.title, self.skill_required.name)


class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    description = Column(String(120))
    domain_id = Column(Integer, ForeignKey('domain.id'), nullable=False, index=True)
    action_text = Column(String(10), nullable=False)
    css_class = Column(String(10), nullable=False)
    default_for_domain = Column(Boolean, nullable=False)
    projects = relationship('Project', backref='status', lazy='joined')
    teams = relationship('Team', backref='status', lazy='joined')
    # transitions_from = relationship('Transition', backref='from_status', lazy='select')
    # transitions_to = relationship('Transition', backref='to_status', lazy='select')

    def __repr__(self):
        return '<Status: {}>'.format(self.name)


class Transition(Base):
    __tablename__ = 'transition'

    id = Column(Integer, primary_key=True)
    admin_only = Column(Boolean, default=False)
    from_status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    to_status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    from_status = relationship("Status", foreign_keys=[from_status_id])
    to_status = relationship("Status", foreign_keys=[to_status_id])

    def __repr__(self):
        return '<Status transition: {} - {}>'.format(self.from_status.name, self.to_status.name)


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    comment = Column(Text)
    vacancies = Column(Text)
    members = relationship('TeamMember', backref='team', lazy='joined', cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Team: {:d} {}>'.format(self.id, self.project.title)


class TeamMember(Base):
    __tablename__ = 'team_member'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return '<Team member: {} {} in team {:d}>'.format(self.user.first_name, self.user.last_name, self.id)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(60), index=True, unique=True)
    username = Column(String(60), index=True, unique=True)
    first_name = Column(String(60), index=True)
    last_name = Column(String(60), index=True)
    password_hash = Column(String(128))
    confirmation_token = Column(String(120))
    telephone = Column(String(60), index=True, unique=True)
    company_id = Column(Integer, ForeignKey('company.id'))
    display_name_flag = Column(Boolean, default=False)
    display_email_flag = Column(Boolean, default=False)
    display_phone_flag = Column(Boolean, default=False)
    company_confirmed = Column(Boolean, default=False)
    programme_code = Column(String(10), ForeignKey('programme.code'))
    profile_comment = Column(Text)
    is_admin = Column(Boolean, default=False)
    is_external = Column(Boolean, default=True)
    notify_new = Column(Boolean, default=False)
    notify_interest = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)
    online_flag = Column(Boolean, default=False)
    alerts = relationship('AlertQueue', backref='user', lazy='select')
    notes_of_interest = relationship('Interest', backref='user', lazy='select')
    projects_offered = relationship('Project', backref='client', lazy='joined')
    skills_offered = relationship('SkillOffered', backref='user', lazy='joined')
    flags = relationship('Flag', backref='user', lazy='select')
    members = relationship('TeamMember', backref='user', lazy='select')

    @property
    def is_student(self):
        if 'live.napier.ac.uk' in self.email:
            return True
        return False

    def __repr__(self):
        return '<User: {}>'.format(self.username)
