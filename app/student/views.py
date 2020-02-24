from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from collections import Counter

from sqlalchemy import and_, or_, text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import case

from jinja2 import Markup
import re

from . import student
from .forms import *
from app.models import *
from app.common import *
import logging
logger = logging.getLogger()



@student.route('/student/projects/list')
@login_required
def projects():
    skill = request.args.get("skill")
    company = request.args.get("company")
    project_domain = Domain.query.filter(Domain.name == 'project').first()
    statuses = Status.query.filter(and_(Status.domain_id == project_domain.id,
                                        or_(Status.name == 'Live',
                                            Status.name == 'Withdrawn',
                                            Status.name == 'Taken',
                                            Status.name == 'Complete'))).with_entities(Status.id)

    accepted = get_status('team', 'Accepted')
    submitted = get_status('team', 'Submitted')
    team_ids = [m.team_id for m in TeamMember.query.filter(TeamMember.user_id == current_user.id).all()]
    accepted_for = [t.project_id for t in Team.query.filter(and_(Team.id.in_(team_ids), Team.status_id == accepted.id))]
    submitted_for = [t.project_id for t in Team.query.filter(and_(Team.id.in_(team_ids), Team.status_id == submitted.id))]

    projects = Project.query.filter(and_(Project.academic_year == session['academic_year'],
                                         or_(Project.status_id.in_(statuses),
                                             Project.client_id == current_user.id))).\
        order_by((Project.client_id == current_user.id).desc()).\
        order_by(Project.title)

    projects = sorted(projects, key=lambda x: (x.id not in accepted_for, x.id not in submitted_for))

    skills = []
    bids = {}
    for project in projects:
        bids[project.id] = len(get_bids(project))
        skills += [(s.skill_required.name, s.skill_required.name) for s in project.skills_required]
    skills = sorted(Counter(skills).items(), key=lambda x: x[0][0].lower())

    companies = []
    companies += [(p.client.company.name, p.client.company.name) for p in projects if p.client.company_id is not None]
    companies = sorted(Counter(companies).items(), key=lambda x: x[0][0].lower())
    return render_template('student/projects/list.html',
                           projects=projects,
                           bids=bids,
                           accepted_for=accepted_for,
                           submitted_for=submitted_for,
                           skills=skills,
                           skill=skill,
                           companies=companies,
                           company=company,
                           title="Projects")


@student.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    form = ProfileForm(obj=user)
    form.skills_offered.choices = [(s.id, s.name) for s in Skill.query.order_by(text('name'))]
    form.skills_offered.data = [s.skill_id for s in user.skills_offered]

    if form.validate_on_submit():
        # Check for javascript injection
        script_pattern = "<\s*script.*>.*<\s*\/\s*script.*>"
        pattern = ".*" + script_pattern
        string_match = re.match(pattern, form.profile_comment.data)
        if string_match:
            user.profile_comment = re.sub(script_pattern, "- SCRIPT REMOVED -", form.profile_comment.data)
            message = user.first_name + " " + user.last_name + " attempted to place a script into their profile"
            security_alert(message)
        else:
            user.profile_comment = form.profile_comment.data
        user.notify_new = form.notify_new.data
        user.notify_interest = form.notify_interest.data
        SkillOffered.query.filter(SkillOffered.user_id==current_user.id).delete()
        for skill in form.skills_offered.raw_data:
            skill_offered = SkillOffered(user_id=current_user.id, skill_id=skill)
            db.session.add(skill_offered)
        db.session.commit()
        flash('Profile updated')
        return redirect(url_for('student.projects'))

    if form.errors:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error, 'error')

    return render_template('student/profile/profile.html', user=user, form=form, title="Edit profile")


@student.route('/project/<int:id>')
@login_required
def project(id):
    parser = MyHTMLParser()
    project = Project.query.get(id)
    interest = Interest.query.filter(and_(Interest.project_id == id, Interest.user_id == current_user.id)).first()
    flag = Flag.query.filter(and_(Flag.project_id == id, Flag.user_id == current_user.id)).first()
    teams = Team.query.filter(Team.project_id == id)
    team_member = TeamMember.query.filter(and_(TeamMember.user_id == current_user.id,
                                               TeamMember.team_id.in_([t.id for t in teams]))).first()
    transitions = Transition.query.filter(Transition.from_status_id == project.status_id, Transition.admin_only == False).all()

    for n in project.notes_of_interest:
        parser.init()
        if n.user.profile_comment:
            parser.feed(n.user.profile_comment)
            n.user.profile_comment = parser.outstring
    return render_template('student/projects/project.html',
                           project=project,
                           interest=interest,
                           flag=flag,
                           team_member=team_member,
                           transitions=transitions,
                           title='View project')


@student.route('/add_project', methods=['GET', 'POST'])
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
                logger.info('NEW STUDENT PROJECT: {:d}, {}, {:d}'.format(project.id, project.title, project.client_id))
                flash('You have successfully added a new project.')
                return redirect(url_for('student.projects'))
            else:
                raise RuntimeError

        except RuntimeError:
            flash('An unknown problem occurred while trying to save a new project', 'error')
            logger.error('PROJECT INSERT ERROR: {:d}, {}'.format(project.client_id, project.title))
        except:
            flash('There was a problem saving your project', 'error')

    return render_template('student/projects/edit_project.html', add_project=add_project,
                           form=form, title='Add project')


@student.route('/edit_project/<int:id>', methods=['GET', 'POST'])
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

        return redirect(url_for('student.projects'))

    return render_template('student/projects/edit_project.html', add_project=add_project,
                           project=project, form=form, title="Edit project")


@student.route('/projects/project_transition/<int:id>/<int:status_id>', methods=['GET', 'POST'])
@login_required
def transition(id, status_id):

    project = Project.query.get_or_404(id)
    check_client(project)

    status = Status.query.get(status_id)
    project.status_id = status.id
    db.session.add(project)
    db.session.commit()
    flash('The project status is now ' + status.name)

    return redirect(url_for('student.project', id=id))


@student.route('/interest/add/<int:id>', methods=['GET', 'POST'])
@login_required
def add_interest(id):
    interest = Interest(
        project_id=id,
        user_id=current_user.id
    )
    db.session.add(interest)
    db.session.commit()
    flash('Interest noted')

    return redirect(url_for('.project', id=id))


@student.route('/interest/delete/<int:project_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_interest(project_id, id):
    interest = Interest.query.get(id)
    check_owner(interest)

    db.session.delete(interest)
    db.session.commit()
    flash('Interest deleted')

    return redirect(url_for('.project', id=project_id))


@student.route('/team/create/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_team(project_id):
    add_team = True

    domain = Domain.query.filter(Domain.name == 'team').first()
    new_status = Status.query.filter(and_(Status.domain_id==domain.id, Status.name=='New')).first()

    form = TeamForm()
    settings = Settings.query.first()

    if form.validate_on_submit():
        team = Team(project_id = project_id,
                    created_by = current_user.id,
                    comment = form.comment.data,
                    vacancies = form.vacancies.data,
                    status_id = new_status.id)

        try:
            db.session.add(team)
            db.session.commit()
            db.session.refresh(team)
            team_member = TeamMember(user_id=current_user.id, team_id=team.id)
            db.session.add(team_member)
            delete_notes(current_user.id, project_id)
            delete_flags(current_user.id, project_id)
            db.session.commit()
            flash('Team created')
        except:
            flash('There was a problem creating the team', 'error')

        return redirect(url_for('student.edit_team', project_id=project_id, id=team.id))

    return render_template('student/teams/team.html',
                           settings=settings,
                           add_team=add_team,
                           form=form,
                           title='Create team')


@student.route('/team/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    add_team = False
    settings = Settings.query.first()

    team = Team.query.get(id)
    check_member(team)
    form = TeamForm(obj=team)

    if form.validate_on_submit():
        error = False
        team.comment=form.comment.data
        team.vacancies=form.vacancies.data

        if form.matric.data != '':
            members = TeamMember.query.filter(TeamMember.team_id == team.id).all()
            if len(members) < settings.maximum_team_size:
                try:
                    member = User.query.filter(User.username==form.matric.data).first()
                    if member.id in [m.user_id for m in members]:
                        flash('Already on the team', 'error')
                        error=True
                    else:
                        team_member = TeamMember(user_id=member.id, team_id=team.id)
                        db.session.add(team_member)
                        delete_notes(member.id, team.project_id)
                        delete_flags(member.id, team.project_id)
                except AttributeError:
                    flash('Matric number not recognised', 'error')
                    error=True
            else:
                flash("Your team is already at the maximum size", "error")
                error = True

        if not error:
            try:
                db.session.commit()
                flash('Team updated')
            except:
                flash('There was a problem updating the team', 'error')

            return redirect(url_for('student.edit_team', id=team.id))

    return render_template('student/teams/team.html',
                           settings=settings,
                           add_team=add_team,
                           team=team,
                           form=form,
                           title='Manage bid')


@student.route('/member/pm/<int:team_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def make_pm(team_id, id):
    members = TeamMember.query.filter(TeamMember.team_id==team_id).all()
    team = Team.query.get(team_id)
    check_member(team)

    for member in members:
        if member.id == id:
            member.project_manager = True
        else:
            member.project_manager = False

    db.session.commit()
    flash('Project manager updated')

    return redirect(url_for('.edit_team', id=team_id))


@student.route('/member/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_member(id):
    team_member = TeamMember.query.get(id)
    team = team_member.team
    check_member(team)
    if len(team.members) == 1:
        return redirect(url_for('student.delete_team', id=team.id))

    db.session.delete(team_member)
    db.session.commit()
    flash('Team member deleted')

    return redirect(url_for('.edit_team', id=team.id))


@student.route('/team/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_team(id):
    team = Team.query.get(id)
    check_member(team)
    project_id = team.project_id
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted')

    return redirect(url_for('.project', id=project_id))


@student.route('/team/preview/<int:id>', methods=['GET', 'POST'])
@login_required
def preview(id):
    team = Team.query.get(id)
    check_member(team)

    return render_template('student/teams/preview.html',
                           team=team,
                           title='Preview')


@student.route('/flag/set/<int:id>', methods=['GET', 'POST'])
@login_required
def set_flag(id):
    form = FlagForm()
    add_flag = True
    parser = MyHTMLParser()

    if form.validate_on_submit():
        parser.init()
        parser.feed(form.message.data)
        flag = Flag(user_id = current_user.id,
                    project_id = id,
                    message = parser.outstring)
        try:
            db.session.add(flag)
            db.session.commit()
            flash('Flag set')
            return redirect(url_for('student.project', id=id))
        except Exception as e:
            flash('Error: ' + str(e))

    if form.errors:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error, 'error')

    return render_template('student/flags/flag.html', form=form, add_flag=add_flag, title="Flag project")


@student.route('/flag/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flag(id):
    flag = Flag.query.get(id)
    check_owner(flag)
    form = FlagForm(obj=flag)
    add_flag = False

    if form.validate_on_submit():
        flag.message = form.message.data
        try:
            db.session.add(flag)
            db.session.commit()
            flash('Flag updated')
            return redirect(url_for('student.project', id=flag.project_id))
        except Exception as e:
            flash('Error: ' + str(e))

    if form.errors:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error, 'error')

    return render_template('student/flags/flag.html', form=form, add_flag=add_flag, flag=flag, title="Edit flag")


@student.route('/flag/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_flag(id):
    flag = Flag.query.get(id)
    check_owner(flag)
    project_id = flag.project_id
    db.session.delete(flag)
    db.session.commit()
    flash('Flag deleted')

    return redirect(url_for('.project', id=project_id))


@student.route('/vacancies', methods=['GET', 'POST'])
@login_required
def vacancies():
    declined = get_status('team', 'Declined')
    teams = Team.query.filter(and_(Team.vacancies != '', Team.status_id != declined.id)).all()
    return render_template('student/projects/vacancies.html', teams=teams, title="Vacancies")


#--------  Bid management ----------#


@student.route('/student/complete/<int:id>', methods=['GET', 'POST'])
@login_required
def complete_team(id):

    settings = Settings.query.first()
    team = Team.query.get_or_404(id)
    check_client(team.project)
    if check_members(team, settings):
        accepted = get_status('team', 'Accepted')
        team.status_id = accepted.id
        for member in TeamMember.query.filter(TeamMember.team_id==team.id):
            delete_notes(member.id)
            delete_flags(member.id)
        db.session.commit()
        flash('The team has been marked complete')
        return redirect(url_for('student.project', id=team.project.id))
    else:
        flash('Your team needs at least {:d} members'.format(settings.minimum_team_size), 'error')
        return redirect(url_for('student.edit_team', id=id))


@student.route('/student/submit/<int:id>', methods=['GET', 'POST'])
@login_required
def submit(id):

    settings = Settings.query.first()
    team = Team.query.get_or_404(id)
    check_member(team)

    if not check_members(team, settings):
        flash('Your team needs at least {:d} members'.format(settings.minimum_team_size), 'error')
        return redirect(url_for('student.edit_team', id=id))

    if not check_programmes(team):
        flash('Team members must be from more than one programme', 'error')
        return redirect(url_for('student.edit_team', id=id))

    if not check_pm(team):
        flash('Your team must have a project manager', 'error')
        return redirect(url_for('student.edit_team', id=id))

    submitted = get_status('team', 'Submitted')
    team.status_id = submitted.id
    alert(team.project.client_id, 'submit', project=team.project)
    db.session.commit()
    flash('Your bid has been submitted')
    return redirect(url_for('student.project', id=team.project.id))

