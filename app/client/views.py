import logging
logger = logging.getLogger()

from flask import flash, redirect, render_template, url_for, abort
from flask_login import current_user, login_required
from sqlalchemy import and_
from sqlalchemy.sql import text

from . import client
from .forms import *
from app.models import *
from app.common import *


#--------  Profile views ----------#

@client.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    company_id = user.company_id
    new_company = user.company.is_new
    if new_company:
        form = ProfileFormWithCompany(obj=user)
        form.company_id.choices = [(user.company_id, user.company.name)] +\
                                  [(c.id, c.name) for c in Company.query.order_by(text('name')) if c.name != user.company.name]

        form.company_id.data = user.company_id
    else:
        form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.telephone = form.telephone.data
        user.display_name_flag = form.display_name_flag.data
        user.display_email_flag = form.display_email_flag.data
        user.display_phone_flag = form.display_phone_flag.data
        try:
            user.company_id = form.company_id.raw_data[0]
        except AttributeError:
            pass
        user.profile_comment = form.profile_comment.data
        db.session.commit()

        if user.company_id != company_id and new_company:
            db.session.expire_all()
            company = Company.query.get(company_id)
            db.session.delete(company)
            db.session.commit()
        flash('Profile updated')
        return redirect(url_for('client.projects'))

    if form.errors:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error, 'error')

    form.email.data = user.email
    form.username.data = user.username
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.telephone.data = user.telephone
    form.display_name_flag = user.display_name_flag
    form.display_email_flag = user.display_email_flag
    form.display_phone_flag = user.display_phone_flag
    if user.company.is_new:
        form.company_id.data = user.company_id
    form.profile_comment.data = user.profile_comment
    return render_template('client/profile/profile.html', user=user, form=form, title="Update profile")


@client.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    company = Company.query.filter(Company.id == current_user.company_id).first()
    form = CompanyForm(obj=company)

    if form.validate_on_submit():
        company.name = form.name.data
        company.description = form.description.data
        company.address = form.address.data
        company.city = form.city.data
        company.post_code = form.post_code.data
        if len(form.web.data) > 0:
            company.web = form.web.data                             # Avoids duplicate index values where the user has entered an empty string
        company.health_policy_flag = form.health_policy_flag.data
        company.health_policy_link = form.health_policy_link.data
        company.training_policy_flag = form.training_policy_flag.data
        company.training_policy_link = form.training_policy_link.data
        company.hse_registered = form.hse_registered.data
        company.la_registered = form.la_registered.data
        company.insured = form.insured.data
        company.student_insured = form.student_insured.data
        company.company_risk_assessed = form.company_risk_assessed.data
        company.risks_reviewed = form.risks_reviewed.data
        company.risks_mitigated = form.risks_mitigated.data
        company.accident_procedure_flag = form.accident_procedure_flag.data
        company.emergency_procedures_flag = form.emergency_procedures_flag.data
        company.report_student_accidents_flag = form.report_student_accidents_flag.data
        company.report_student_illness_flag = form.report_student_illness_flag.data
        company.data_policy_flag = form.data_policy_flag.data
        company.data_policy_link = form.data_policy_link.data
        company.security_measures_flag = form.security_measures_flag.data
        company.ico_registration_number = form.ico_registration_number.data
        company.data_training_flag = form.data_training_flag.data
        company.security_policy_flag = form.security_policy_flag.data
        company.security_policy_link = form.security_policy_link.data
        company.privacy_notice_flag = form.privacy_notice_flag.data
        company.data_contact_first_name = form.data_contact_first_name.data
        company.data_contact_last_name = form.data_contact_last_name.data
        company.data_contact_position = form.data_contact_position.data
        company.data_contact_telephone = form.data_contact_telephone.data

        db.session.add(company)
        db.session.commit()
        flash('Company details updated')

        return redirect(url_for('client.projects'))

    errors = form.errors
    if len(errors) > 0:
        for key, value in errors.items():
            flash(value[0], 'error')

    return render_template('client/profile/company.html',
                           company=company, form=form, title="Update company details")



#--------  Project views ----------#

@client.route('/projects')
@login_required
def projects():
    projects = Project.query.filter(Project.client_id == current_user.id).all()
    bids = {}
    new = {}
    for project in projects:
        bids[project.id] = len(get_bids(project))
        new[project.id] = len(get_new_teams(project))
    settings = Settings.query.first()
    from_statuses = [p.status_id for p in projects]
    transitions = Transition.query.filter(Transition.from_status_id.in_(from_statuses), Transition.admin_only == False).all()
    return render_template('client/projects/projects.html',
                           projects=projects,
                           academic_year=get_this_year(),
                           bids=bids,
                           new=new,
                           transitions=transitions,
                           title="Projects")


@client.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    add_project = True

    form = ProjectForm()
    form.skills_required.choices = [(s.id, s.name) for s in Skill.query.order_by(text('name'))]
    project_domain = Domain.query.filter(Domain.name == 'project').first()
    default_status = Status.query.filter(Status.domain_id == project_domain.id,
                                         Status.default_for_domain == True).first()
    form.academic_year.choices = [(y.year, y.year) for y in AcademicYear.query.filter(AcademicYear.end_date > datetime.now()).order_by(text('start_date'))]

    if form.validate_on_submit():
        skills_required = form.skills_required.data
        project = Project(title = form.title.data,
                          client_id = current_user.id,
                          overview = form.overview.data,
                          deliverables = form.deliverables.data,
                          resources = form.resources.data,
                          academic_year = form.academic_year.data,
                          status_id = default_status.id)

        try:
            db.session.add(project)
            db.session.commit()
            db.session.refresh(project)
            if project.id:
                for skill in skills_required:
                    skill_required = SkillRequired(project_id=project.id, skill_id=skill)
                    db.session.add(skill_required)
                db.session.commit()
                logger.info('NEW CLIENT PROJECT: {:d}, {}, {:d}'.format(project.id, project.title, project.client_id))
                flash('You have successfully added a new project.')
                return redirect(url_for('client.projects'))
            else:
                raise RuntimeError

        except RuntimeError:
            flash('An unknown problem occurred while trying to save a new project', 'error')
            logger.error('PROJECT INSERT ERROR: {:d}, {}'.format(project.client_id, project.title))
        except:
            flash('There was a problem saving your project', 'error')


    return render_template('client/projects/project.html', add_project=add_project,
                           form=form, title='Add project')


@client.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    add_project = False

    project = Project.query.get_or_404(id)
    check_client(project)

    form = ProjectForm(obj=project)
    form.academic_year.choices = [(y.year, y.year) for y in AcademicYear.query.order_by(text('start_date'))]
    form.skills_required.choices = [(s.id, s.name) for s in Skill.query.order_by(text('name'))]
    form.skills_required.data = [s.skill_id for s in project.skills_required]
    if form.validate_on_submit():
        project.title = form.title.data
        project.overview = form.overview.data
        project.deliverables = form.deliverables.data
        project.resources = form.resources.data
        project.academic_year = form.academic_year.data
        project.updated_date = datetime.now()
        db.session.add(project)
        SkillRequired.query.filter(SkillRequired.project_id==project.id).delete()
        for skill in form.skills_required.raw_data:
            if skill not in [s.skill_id for s in project.skills_required]:
                skill_required = SkillRequired(project_id=project.id, skill_id=skill)
                db.session.add(skill_required)
        db.session.commit()
        flash('You have successfully edited the project.')

        return redirect(url_for('client.projects'))

    return render_template('client/projects/project.html', add_project=add_project,
                           project=project, form=form, title="Edit project")


@client.route('/projects/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project(id):

    project = Project.query.get_or_404(id)
    check_client(project)

    db.session.delete(project)
    db.session.commit()
    flash('You have successfully deleted the project.')

    return redirect(url_for('client.projects'))


@client.route('/projects/transition/<int:id>/<int:status_id>', methods=['GET', 'POST'])
@login_required
def transition(id, status_id):

    project = Project.query.get_or_404(id)
    check_client(project)

    status = Status.query.get(status_id)
    project.status_id = status.id

    relisted = get_status('project', 'Relisted')
    declined = get_status('team', 'Declined')
    accepted = get_status('team', 'Accepted')

    if status_id == relisted.id:
        teams = Team.query.filter(and_(Team.project_id == id, Team.status_id == declined.id)).all()
        for team in teams:
            alert(team.id, 'relist', team=True, project=team.project)

        teams = Team.query.filter(and_(Team.project_id == id, Team.status_id == accepted.id)).all()
        for team in teams:
            team.status_id = declined.id
            alert(team.id, 'decline', team=True, project=team.project)

    db.session.commit()
    flash('The project is now ' + status.name)

    return redirect(url_for('client.projects'))


@client.route('/staff/project/<int:id>/duplicate')
@login_required
def duplicate(id):
    old_project = Project.query.get_or_404(id)
    check_client(old_project)

    new_project = Project(
        title = old_project.title,
        client_id = current_user.id,
        academic_year = get_this_year().year,
        overview = old_project.overview,
        deliverables = old_project.deliverables,
        resources = old_project.resources,
        status_id = get_status('project', 'New').id
    )

    db.session.add(new_project)
    db.session.commit()
    db.session.refresh(new_project)

    for skill in old_project.skills_required:
        db.session.add(SkillRequired(project_id=new_project.id, skill_id=skill.skill_id))
    db.session.commit()

    return redirect(url_for('client.projects'))


#--------  Bid management ----------#


@client.route('/projects/bids/<int:id>', methods=['GET', 'POST'])
@login_required
def bids(id):

    project = Project.query.get_or_404(id)
    check_client(project)
    bids = get_bids(project)
    from_statuses = [t.status_id for t in project.teams]
    domain = Domain.query.filter(Domain.name == 'team').first()
    shortlisted = Status.query.filter(and_(Status.domain==domain, Status.name=='Shortlisted')).first()
    shortlist = False
    if shortlisted.id in from_statuses:
        shortlist = True
    settings = Settings.query.first()

    transitions = Transition.query.filter(Transition.from_status_id.in_(from_statuses), Transition.admin_only == False).all()

    return render_template('client/bids/bids.html',
                           project=project,
                           bids=bids,
                           shortlist=shortlist,
                           transitions=transitions,
                           settings=settings,
                           title="Bids")


@client.route('/bids/transition/<int:id>/<int:status_id>', methods=['GET', 'POST'])
@login_required
def bid_transition(id, status_id):

    team = Team.query.get_or_404(id)
    check_client(team.project)

    status = Status.query.get(status_id)
    team.status_id = status.id
    accepted = get_status('team', 'Accepted')
    declined = get_status('team', 'Declined')
    shortlisted = get_status('team', 'Shortlisted')

    if status.id == accepted.id:
        alert(team.id, 'accept', team=True, project=team.project)
        teams = Team.query.filter(and_(Team.project_id==team.project_id, Team.id != team.id)).all()
        for other_team in teams:
            if other_team.status_id != declined.id:
                other_team.status_id = declined.id
                alert(other_team.id, 'decline', team=True, project=team.project)
        project = Project.query.get(team.project_id)
        taken = get_status('project', 'Taken')
        project.status_id = taken.id
        for member in TeamMember.query.filter(TeamMember.team_id==team.id):
            delete_notes(member.user_id)
            delete_flags(member.user_id)
    elif status.id == declined.id:
        alert(team.id, 'decline', team=True, project=team.project)
    elif status.id == shortlisted.id:
        alert(team.id, 'short', team=True, project=team.project)

    db.session.commit()
    flash('The bid status is now ' + status.name)

    return redirect(url_for('client.bids', id=team.project.id))


@client.route('/bids/accept_shortlist/<int:id>', methods=['GET', 'POST'])
@login_required
def accept_shortlist(id):
    project = Project.query.get_or_404(id)
    check_client(project)

    teams = Team.query.filter(Team.project_id==id).all()
    shortlisted = get_status('team', 'Shortlisted')
    accepted = get_status('team', 'Accepted')
    declined = get_status('team', 'Declined')

    for team in teams:
        if team.status_id == shortlisted.id:
            team.status_id = accepted.id
            alert(team.id, 'accept', team=True, project=team.project)
        elif team.status_id != declined.id:
            team.status_id = declined.id
            alert(team.id, 'decline', team=True, project=team.project)
        for member in TeamMember.query.filter(TeamMember.team_id==team.id):
            delete_notes(member.user_id)
            delete_flags(member.user_id)

    project = Project.query.get(id)
    taken = get_status('project', 'Taken')
    project.status_id = taken.id

    db.session.commit()
    flash('Shortlist accepted')

    return redirect(url_for('client.bids', id=id))
