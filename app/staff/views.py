from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from collections import Counter, OrderedDict

from sqlalchemy import and_, or_, text

from . import staff
from .forms import *
from app.models import *
from app.common import *
import logging
logger = logging.getLogger()


@staff.route('/staff/projects')
@login_required
def projects():
    skill = request.args.get("skill")
    company = request.args.get("company")
    projects = Project.query.order_by((Project.client_id == current_user.id).desc()).order_by(Project.academic_year.desc(), Project.title)
    academic_years = [y.year for y in AcademicYear.query.order_by(text('start_date'))]
    academic_year = session['academic_year']

    # ToDo: Modify the dropdowns to show the correct values wen the projects are filtered
    skills = []
    bids = {}
    for project in projects:
        bids[project.id] = len(get_bids(project))
        skills += [(s.skill_required.name, s.skill_required.name) for s in project.skills_required]
    skills = sorted(Counter(skills).items(), key=lambda x: x[0][0].lower())

    companies = []
    companies += [(p.client.company.name, p.client.company.name) for p in projects if p.client.company_id is not None]
    companies = sorted(Counter(companies).items(), key=lambda x: x[0][0].lower())
    return render_template('staff/projects/projects.html',
                           academic_year=academic_year,
                           academic_years=academic_years,
                           projects=projects,
                           bids=bids,
                           skills=skills,
                           skill=skill,
                           companies=companies,
                           company=company,
                           title="Projects")


@staff.route('/staff/my_projects')
@login_required
def my_projects():
    projects = Project.query.filter(Project.client_id == current_user.id).all()
    bids={}
    for project in projects:
        bids[project.id] = len(get_bids(project))
    from_statuses = [p.status_id for p in projects]
    transitions = Transition.query.filter(Transition.from_status_id.in_(from_statuses), Transition.admin_only == False).all()
    return render_template('staff/projects/my_projects.html',
                           projects=projects,
                           bids=bids,
                           academic_year = get_this_year(),
                           transitions=transitions,
                           title="My projects")


@staff.route('/staff/add_project', methods=['GET', 'POST'])
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
                logger.info('NEW STAFF PROJECT: {:d}, {}, {:d}'.format(project.id, project.title, project.client_id))
                flash('You have successfully added a new project.')
                return redirect(url_for('staff.projects'))
            else:
                raise RuntimeError

        except RuntimeError:
            flash('An unknown problem occurred while trying to save a new project', 'error')
            logger.error('PROJECT INSERT ERROR: {:d}, {}'.format(project.client_id, project.title))
        except:
            flash('There was a problem saving your project', 'error')

    return render_template('staff/projects/edit_project.html', add_project=add_project,
                           form=form, title='Add project')


@staff.route('/staff/profile/edit', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.profile_comment = form.profile_comment.data
        db.session.commit()
        flash('Profile updated')
        return redirect(url_for('staff.projects'))

    if form.errors:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error, 'error')

    return render_template('staff/profile/profile.html', user=user, form=form, title="Edit profile")


@staff.route('/staff/project/<int:id>')
@login_required
def project(id):
    project = Project.query.get(id)
    interest = Interest.query.filter(and_(Interest.project_id == id, Interest.user_id == current_user.id)).first()
    flag = Flag.query.filter(and_(Flag.project_id == id, Flag.user_id == current_user.id)).first()
    teams = Team.query.filter(Team.project_id == id)
    team_member = TeamMember.query.filter(and_(TeamMember.user_id == current_user.id,
                                               TeamMember.team_id.in_([t.id for t in teams]))).first()
    return render_template('staff/projects/project.html',
                           project=project,
                           interest=interest,
                           flag=flag,
                           team_member=team_member,
                           title='View project')



@staff.route('/staff/edit_project/<int:id>', methods=['GET', 'POST'])
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

        return redirect(url_for('staff.projects'))

    return render_template('staff/projects/edit_project.html', add_project=add_project,
                           project=project, form=form, title="Edit project")


@staff.route('/staff/project/<int:id>/duplicate')
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

    return redirect(url_for('staff.my_projects'))


#--------  Bid management ----------#


@staff.route('/staff/bids/<int:id>', methods=['GET', 'POST'])
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

    return render_template('staff/bids/bids.html',
                           project=project,
                           bids=bids,
                           shortlist=shortlist,
                           transitions=transitions,
                           settings=settings,
                           title="Bids")


@staff.route('/staff/bids/transition/<int:id>/<int:status_id>', methods=['GET', 'POST'])
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
            delete_notes(member.id)
            delete_flags(member.id)
    elif status.id == declined.id:
        alert(team.id, 'decline', team=True, project=team.project)
    elif status.id == shortlisted.id:
        alert(team.id, 'short', team=True, project=team.project)

    db.session.commit()
    flash('The bid status is now ' + status.name)

    return redirect(url_for('staff.bids', id=team.project.id))


@staff.route('/staff/bids/accept_shortlist/<int:id>', methods=['GET', 'POST'])
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
            delete_notes(member.id)
            delete_flags(member.id)

    project = Project.query.get(id)
    taken = get_status('project', 'Taken')
    project.status_id = taken.id

    db.session.commit()
    flash('Shortlist accepted')

    return redirect(url_for('staff.bids', id=id))

