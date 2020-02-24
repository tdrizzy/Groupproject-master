from flask import abort, flash, redirect, render_template, url_for, current_app, request
from flask_login import current_user, login_required
from flask_mail import Message, Mail
from sqlalchemy import desc
from sqlalchemy.sql import text, func
from datetime import timedelta

import json
import plotly
import pandas as pd

from . import admin
from .forms import *
from app import scheduler
from app.models import *
from app.common import get_this_year, change_academic_year, sanitise
from app.scheduled_jobs import Jobs
from .charts import *

jobs = Jobs()

def check_admin():
    if not current_user.is_admin:
        abort(403)


@admin.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)

    form = ChangeAcademicYearForm()
    form.change_academic_year.choices = [(y.year, y.year) for y in AcademicYear.query.order_by(text('start_date'))]

    if form.validate_on_submit():
        try:
            change_academic_year(form.change_academic_year.data)
        except:
            flash('Could not change academic year')

    academic_year = session['academic_year']

    form.change_academic_year.data = session['academic_year']

    unconfirmed_companies = User.query.filter(User.company_confirmed == 0).all()
    projects = Project.query.filter(Project.academic_year == academic_year).order_by(Project.title).all()
    project_domain = Status.query.filter(Domain.name == 'project').first()
    status_new = Status.query.filter(Status.domain_id == project_domain.id).first()
    new_projects = Project.query.filter(and_(Project.status_id == status_new.id, Project.academic_year == academic_year)).all()
    years = AcademicYear.query.order_by(desc(AcademicYear.start_date)).all()

    this_year = get_this_year().start_date
    one_hour_ago = datetime.now() - timedelta(hours=1)
    midnight = datetime.now().date()

    # ToDo: Add facility to clear login history
    # ToDo: Only show logins this academic year
    logins = db.session.query(func.sum(User.login_count).label('sum')).first()
    logins_today = db.session.query(func.count(User.login_count).label('count')).filter(User.last_login > midnight).first()
    logins_this_hour = db.session.query(func.count(User.login_count).label('count')).filter(User.last_login > one_hour_ago).first()

    stats_data = stats_chart()
    projects_data = projects_chart()

    charts = [stats_data, projects_data]
    chart_JSON = json.dumps(charts, cls=plotly.utils.PlotlyJSONEncoder)


    chart_metadata = [{'id': 0, 'title': 'Stats'},
                      {'id': 1, 'title': 'Projects'}]

    return render_template('admin/dashboard.html',
                           title="Dashboard",
                           unconfirmed_companies=unconfirmed_companies,
                           logins=logins,
                           logins_today=logins_today,
                           logins_this_hour=logins_this_hour,
                           projects=projects,
                           years=years,
                           academic_year=academic_year,
                           form=form,
                           new_projects=new_projects,
                           chart_JSON=chart_JSON,
                           chart_metadata=chart_metadata
                           )


# --------  Academic year views ----------#

@admin.route('/academic_year', methods=['GET', 'POST'])
@login_required
def list_academic_years():
    check_admin()
    academic_years = AcademicYear.query.all()
    return render_template('admin/academic_years/academic_years.html', academic_years=academic_years, title="Academic Years")


@admin.route('/academic_years/add', methods=['GET', 'POST'])
@login_required
def add_academic_year():
    check_admin()
    add_academic_year = True

    form = AcademicYearForm()
    if form.validate_on_submit():
        academic_year = AcademicYear(year=sanitise(form.year.data),
                                     start_date=form.start_date.data,
                                     end_date=form.end_date.data)
        try:
            db.session.add(academic_year)
            db.session.commit()
            flash('You have successfully added a new academic year.')
        except:
            flash('Error: academic year already exists.')

        return redirect(url_for('admin.list_academic_years'))

    return render_template('admin/academic_years/academic_year.html', action="Add",
                           add_academic_year=add_academic_year, form=form,
                           title="Add Academic Year")


@admin.route('/academic_years/edit/<year>', methods=['GET', 'POST'])
@login_required
def edit_academic_year(year):
    check_admin()
    add_academic_year = False

    academic_year = AcademicYear.query.get_or_404(year)
    form = AcademicYearForm(obj=academic_year)
    if form.validate_on_submit():
        academic_year.Year = form.year.data
        academic_year.start_date = form.start_date.data
        academic_year.end_date = form.end_date.data
        db.session.commit()
        flash('You have successfully edited the academic year.')

        return redirect(url_for('admin.list_academic_years'))

    form.year.data = academic_year.year
    form.start_date.data = academic_year.start_date
    form.end_date.data = academic_year.end_date
    return render_template('admin/academic_years/academic_year.html', action="Edit",
                           add_academic_year=add_academic_year, form=form,
                           academic_year=academic_year, title="Edit Academic Year")


@admin.route('/academic_years/delete/<year>', methods=['GET', 'POST'])
@login_required
def delete_academic_year(year):
    check_admin()

    academic_year = AcademicYear.query.get_or_404(year)
    db.session.delete(academic_year)
    db.session.commit()
    flash('You have successfully deleted the academic year.')

    return redirect(url_for('admin.list_academic_years'))


#--------  Alert views ----------#

@admin.route('/alerts', methods=['GET', 'POST'])
@login_required
def alerts():
    check_admin()
    alerts = AlertText.query.order_by(AlertText.code).all()

    return render_template('admin/alerts/alerts.html', alerts=alerts, title="Alert messages")


@admin.route('/alerts/add', methods=['GET', 'POST'])
@login_required
def add_alert():
    check_admin()
    add_alert = True

    form = AlertForm()
    if form.validate_on_submit():
        alert = AlertText(code=form.code.data,
                          subject=form.subject.data,
                          message_text=form.message_text.data)
        try:
            db.session.add(alert)
            db.session.commit()
            flash('New alert added')
        except:
            flash('Error: alert code already exists.')

        return redirect(url_for('admin.alerts'))

    return render_template('admin/alerts/alert.html', action="Add",
                           add_alert=add_alert, form=form,
                           title="Add alert")


@admin.route('/alerts/edit/<code>', methods=['GET', 'POST'])
@login_required
def edit_alert(code):
    check_admin()
    add_alert = False

    alert = AlertText.query.get_or_404(code)
    form = AlertForm(obj=alert)
    if form.validate_on_submit():
        alert.code = form.code.data
        alert.subject = form.subject.data
        alert.message_text = form.message_text.data
        db.session.commit()
        flash('Alert updated')

        return redirect(url_for('admin.alerts'))

    return render_template('admin/alerts/alert.html', action="Edit",
                           add_alert=add_alert, form=form,
                           alert=alert, title="Edit alerts")


@admin.route('/alerts/delete/<code>', methods=['GET', 'POST'])
@login_required
def delete_alert(code):
    check_admin()

    alert = AlertText.query.get_or_404(code)
    try:
        db.session.delete(alert)
        db.session.commit()
        flash('Alert deleted')
    except Exception as e:
        flash(str(e), 'error')

    return redirect(url_for('admin.alerts'))



#--------  Programme views ----------#

@admin.route('/programmes', methods=['GET', 'POST'])
@login_required
def list_programmes():
    check_admin()
    programmes = Programme.query.all()

    return render_template('admin/programmes/programmes.html', programmes=programmes, title="Programmes")


@admin.route('/programmes/add', methods=['GET', 'POST'])
@login_required
def add_programme():
    check_admin()
    add_programme = True

    form = ProgrammeForm()
    if form.validate_on_submit():
        programme = Programme(code=form.code.data, title=form.title.data)
        try:
            db.session.add(programme)
            db.session.commit()
            flash('You have successfully added a new programme.')
        except:
            flash('Error: programme code already exists.')

        return redirect(url_for('admin.list_programmes'))

    return render_template('admin/programmes/programme.html', action="Add",
                           add_programme=add_programme, form=form,
                           title="Add Programme")


@admin.route('/programmes/edit/<code>', methods=['GET', 'POST'])
@login_required
def edit_programme(code):
    check_admin()
    add_programme = False

    programme = Programme.query.get_or_404(code)
    form = ProgrammeForm(obj=programme)
    if form.validate_on_submit():
        programme.code = form.code.data
        programme.title = form.title.data
        db.session.commit()
        flash('You have successfully edited the programme.')

        return redirect(url_for('admin.list_programmes'))

    form.title.data = programme.title
    form.code.data = programme.code
    return render_template('admin/programmes/programme.html', action="Edit",
                           add_programme=add_programme, form=form,
                           programme=programme, title="Edit Programme")


@admin.route('/programmes/delete/<code>', methods=['GET', 'POST'])
@login_required
def delete_programme(code):
    check_admin()

    programme = Programme.query.get_or_404(code)
    db.session.delete(programme)
    db.session.commit()
    flash('You have successfully deleted the programme.')

    return redirect(url_for('admin.list_programmes'))


#--------  Company views ----------#

@admin.route('/companies')
@login_required
def list_companies():
    check_admin()
    companies = Company.query.all()
    return render_template('admin/companies/companies.html',
                           companies=companies, title='Companies')


@admin.route('/companies/add', methods=['GET', 'POST'])
@login_required
def add_company():
    check_admin()
    add_company = True

    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(name=form.name.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            post_code=form.post_code.data,
            web=form.web.data,
            health_policy_flag=form.health_policy_flag.data,
            health_policy_link=form.health_policy_link.data,
            training_policy_flag=form.training_policy_flag.data,
            training_policy_link=form.training_policy_link.data,
            hse_registered=form.hse_registered.data,
            la_registered=form.la_registered.data,
            insured=form.insured.data,
            student_insured=form.student_insured.data,
            company_risk_assessed=form.company_risk_assessed.data,
            risks_reviewed=form.risks_reviewed.data,
            risks_mitigated=form.risks_mitigated.data,
            accident_procedure_flag=form.accident_procedure_flag.data,
            emergency_procedures_flag=form.emergency_procedures_flag.data,
            report_student_accidents_flag=form.report_student_accidents_flag.data,
            report_student_illness_flag=form.report_student_illness_flag.data,
            data_policy_flag=form.data_policy_flag.data,
            data_policy_link=form.data_policy_link.data,
            security_measures_flag=form.security_measures_flag.data,
            ico_registration_number=form.ico_registration_number.data,
            data_training_flag=form.data_training_flag.data,
            security_policy_flag=form.security_policy_flag.data,
            security_policy_link=form.security_policy_link.data,
            privacy_notice_flag=form.privacy_notice_flag.data,
            data_contact_first_name=form.data_contact_first_name.data,
            data_contact_last_name=form.data_contact_last_name.data,
            data_contact_position=form.data_contact_position.data,
            data_contact_telephone=form.data_contact_telephone.data)

        try:
            db.session.add(company)
            db.session.commit()
            flash('You have successfully added a new company.')
        except:
            flash('Error: company id already exists.')

        return redirect(url_for('admin.list_companies'))

    return render_template('admin/companies/company.html', add_company=add_company,
                           form=form, title='Add Company')


@admin.route('/companies/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    check_admin()
    add_company = False

    try:
        company = Company.query.get_or_404(id)
        form = CompanyForm(obj=company)
        if form.validate_on_submit():
            company.name = form.name.data
            company.description = form.description.data
            company.address = form.address.data
            company.city = form.city.data
            company.post_code = form.post_code.data
            company.web = form.web.data
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
            flash('You have successfully edited the company.')

            return redirect(url_for('admin.list_companies'))
    except Exception as e:
        flash(str(e), 'error')

    form.name.data = company.name
    form.description.data = company.description
    form.address.data = company.address
    form.city.data = company.city
    form.post_code.data = company.post_code
    form.web.data = company.web
    form.health_policy_flag.data = company.health_policy_flag
    form.health_policy_link.data = company.health_policy_link
    form.training_policy_flag.data = company.training_policy_flag
    form.training_policy_link.data = company.training_policy_link
    form.hse_registered.data = company.hse_registered
    form.la_registered.data = company.la_registered
    form.insured.data = company.insured
    form.student_insured.data = company.student_insured
    form.company_risk_assessed.data = company.company_risk_assessed
    form.risks_reviewed.data = company.risks_reviewed
    form.risks_mitigated.data = company.risks_mitigated
    form.accident_procedure_flag.data = company.accident_procedure_flag
    form.emergency_procedures_flag.data = company.emergency_procedures_flag
    form.report_student_accidents_flag.data = company.report_student_accidents_flag
    form.report_student_illness_flag.data = company.report_student_illness_flag
    form.data_policy_flag.data = company.data_policy_flag
    form.data_policy_link.data = company.data_policy_link
    form.security_measures_flag.data = company.security_measures_flag
    form.ico_registration_number.data = company.ico_registration_number
    form.data_training_flag.data = company.data_training_flag
    form.security_policy_flag.data = company.security_policy_flag
    form.security_policy_link.data = company.security_policy_link
    form.privacy_notice_flag.data = company.privacy_notice_flag
    form.data_contact_first_name.data = company.data_contact_first_name
    form.data_contact_last_name.data = company.data_contact_last_name
    form.data_contact_position.data = company.data_contact_position
    form.data_contact_telephone.data = company.data_contact_telephone
    return render_template('admin/companies/company.html', add_company=add_company,
                           form=form, title="Edit Company")


@admin.route('/companies/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_company(id):
    check_admin()

    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('You have successfully deleted the company.')

    return redirect(url_for('admin.list_companies'))


#--------  Domain views ----------#

@admin.route('/domains')
@login_required
def list_domains():
    check_admin()
    domains = Domain.query.all()
    return render_template('admin/domains/domains.html',
                           domains=domains, title='Domains')


@admin.route('/domains/add', methods=['GET', 'POST'])
@login_required
def add_domain():
    check_admin()
    add_domain = True

    form = DomainForm()
    if form.validate_on_submit():
        domain = Domain(name=form.name.data, description=form.description.data)

        try:
            db.session.add(domain)
            db.session.commit()
            flash('You have successfully added a new domain.')
        except:
            flash('Error: domain id already exists.')

        return redirect(url_for('admin.list_domains'))

    return render_template('admin/domains/domain.html', add_domain=add_domain,
                           form=form, title='Add Domain')


@admin.route('/domains/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_domain(id):
    check_admin()
    add_domain = False

    domain = Domain.query.get_or_404(id)
    form = DomainForm(obj=domain)
    if form.validate_on_submit():
        domain.id = form.id.data
        domain.name = form.name.data
        domain.description = form.description.data
        db.session.add(domain)
        db.session.commit()
        flash('You have successfully edited the domain.')

        return redirect(url_for('admin.list_domains'))

    form.name.id = domain.id
    form.name.data = domain.name
    form.description.data = domain.description
    return render_template('admin/domains/domain.html', add_domain=add_domain,
                           form=form, title="Edit Domain")


@admin.route('/domains/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_domain(id):
    check_admin()

    domain = Domain.query.get_or_404(id)
    db.session.delete(domain)
    db.session.commit()
    flash('You have successfully deleted the domain.')

    return redirect(url_for('admin.list_domains'))


#--------  FAQ views ----------#

@admin.route('/faqs')
@login_required
def list_faqs():
    check_admin()
    faqs = Faq.query.all()
    return render_template('admin/faqs/faqs.html', faqs=faqs, title='FAQs')


@admin.route('/faqs/add', methods=['GET', 'POST'])
@login_required
def add_faq():
    check_admin()
    add_faq = True

    form = FaqForm()
    if form.validate_on_submit():
        faq = Faq(question=form.question.data,
                  answer=form.answer.data,
                  rank=form.rank.data,
                  external=form.external.data,
                  student=form.student.data
                  )

        try:
            db.session.add(faq)
            db.session.commit()
            flash('You have successfully added a new FAQ.')
        except:
            flash('Error: FAQ id already exists.')

        return redirect(url_for('admin.list_faqs'))

    return render_template('admin/faqs/faq.html', add_faq=add_faq,
                           form=form, title='Add FAQ')


@admin.route('/faqs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_faq(id):
    check_admin()
    add_faq = False

    faq = Faq.query.get_or_404(id)
    form = FaqForm(obj=faq)
    if form.validate_on_submit():
        faq.question = form.question.data
        faq.answer = form.answer.data
        faq.rank = form.rank.data
        faq.external = form.external.data
        faq.student = form.student.data
        db.session.add(faq)
        db.session.commit()
        flash('You have successfully edited the faq.')

        return redirect(url_for('admin.list_faqs'))

    form.question.id = faq.question
    form.answer.data = faq.answer
    form.rank.data = faq.rank
    form.external.data = faq.external
    form.student.data = faq.student
    return render_template('admin/faqs/faq.html', add_faq=add_faq,
                           form=form, title="Edit FAQ")


@admin.route('/faqs/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_faq(id):
    check_admin()

    faq = Faq.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('You have successfully deleted the FAQ.')

    return redirect(url_for('admin.list_faqs'))


#--------  Flag views ----------#

@admin.route('/flags')
@login_required
def list_flags():
    check_admin()
    flags = Flag.query.all()
    return render_template('admin/flags/flags.html', flags=flags, title='Flags')


@admin.route('/flags/add', methods=['GET', 'POST'])
@login_required
def add_flag():
    check_admin()
    add_flag = True

    form = FlagForm()
    form.user_id.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in User.query.order_by(text('last_name'))]
    form.project_id.choices = [(p.id, p.title) for p in Project.query.order_by(text('title'))]
    if form.validate_on_submit():
        flag = Flag(user_id = form.user_id.data,
                    project_id=form.project_id.data,
                    message=form.message.data)
        try:
            db.session.add(flag)
            db.session.commit()
            flash('You have successfully added a new flag.')
        except:
            flash('Error: flag id already exists.')

        return redirect(url_for('admin.list_flags'))

    return render_template('admin/flags/flag.html', add_flag=add_flag,
                           form=form, title='Add flag')


@admin.route('/flags/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flag(id):
    check_admin()
    add_flag = False

    flag = Flag.query.get_or_404(id)
    form = FlagForm(obj=flag)
    form.user_id.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in User.query.order_by(text('last_name'))]
    form.project_id.choices = [(p.id, p.title) for p in Project.query.order_by(text('title'))]
    if form.validate_on_submit():
        flag.user_id = form.user_id.data
        flag.project_id = form.project_id.data
        flag.message = form.message.data
        db.session.add(flag)
        db.session.commit()
        flash('You have successfully edited the flag.')

        return redirect(url_for('admin.list_flags'))

    form.user_id.data = flag.user_id
    form.project_id.data = flag.project_id
    form.message.data = flag.message
    return render_template('admin/flags/flag.html', add_flag=add_flag,
                           form=form, title="Edit flag")


@admin.route('/flags/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_flag(id):
    check_admin()

    flag = Flag.query.get_or_404(id)
    db.session.delete(flag)
    db.session.commit()
    flash('You have successfully deleted the flag.')

    return redirect(url_for('admin.list_flags'))


#--------  Project views ----------#

@admin.route('/projects')
@login_required
def list_projects():
    check_admin()
    projects = Project.query.filter(Project.academic_year == session['academic_year']).all()
    domain = Domain.query.filter(Domain.name == 'project').first()
    statuses = Status.query.filter(Status.domain_id == domain.id).all()
    transitions = Transition.query.filter(Transition.to_status_id.in_([s.id for s in statuses])).all()
    return render_template('admin/projects/projects.html', projects=projects, transitions=transitions, title='Projects')


@admin.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    check_admin()
    add_project = True

    form = ProjectForm()
    form.client_id.choices = [(c.id, c.first_name + ' ' + c.last_name) for c in User.query.order_by(text('last_name'))]
    form.skills_required.choices = [(s.id, s.name) for s in Skill.query.order_by(text('name'))]
    project_domain = Domain.query.filter(Domain.name == 'project').first()
    form.status_id.choices = [(s.id, s.name) for s in Status.query.filter(Status.domain_id == project_domain.id).order_by(text('status.name'))]
    default_status = Status.query.filter(Status.domain_id == project_domain.id,
                                         Status.default_for_domain == True).first()
    form.status_id.default = default_status.id
    form.academic_year.choices = [(y.year, y.year) for y in AcademicYear.query.order_by(text('start_date'))]
    form.status_id.data = default_status.id
    if form.validate_on_submit():
        skills_required = form.skills_required.data
        project = Project(title = form.title.data,
                          client_id = form.client_id.data,
                          overview = form.overview.data,
                          deliverables = form.deliverables.data,
                          resources = form.resources.data,
                          academic_year = form.academic_year.data,
                          status_id = form.status_id.data)

        try:
            db.session.add(project)
            db.session.commit()
            db.session.refresh(project)
            for skill in skills_required:
                skill_required = SkillRequired(project_id=project.id, skill_id=skill)
                db.session.add(skill_required)
            db.session.commit()
            flash('You have successfully added a new project.')
        except:
            flash('Error: project id already exists.')

        return redirect(url_for('admin.list_projects'))

    return render_template('admin/projects/project.html', add_project=add_project,
                           form=form, title='Add project')


@admin.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    check_admin()
    add_project = False

    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    form.client_id.choices = [(c.id, c.first_name + ' ' + c.last_name) for c in User.query.order_by(text('last_name'), text('first_name'))]
    project_domain = Domain.query.filter(Domain.name == 'project').first()
    form.status_id.choices = [(s.id, s.name) for s in Status.query.filter(Status.domain_id == project_domain.id).order_by(text('status.name'))]
    form.academic_year.choices = [(y.year, y.year) for y in AcademicYear.query.order_by(text('start_date'))]
    form.skills_required.choices = [(s.id, s.name) for s in Skill.query.order_by(text('name'))]
    form.skills_required.data = [s.skill_id for s in project.skills_required]
    if form.validate_on_submit():
        project.title = form.title.data
        project.client_id = form.client_id.data
        project.overview = form.overview.data
        project.deliverables = form.deliverables.data
        project.resources = form.resources.data
        project.academic_year = form.academic_year.data
        project.status_id = form.status_id.data
        project.admin_notes = form.admin_notes.data
        project.updated_date = datetime.now()
        db.session.add(project)
        for skill in form.skills_required.raw_data:
            if skill not in [s.skill_id for s in project.skills_required]:
                skill_required = SkillRequired(project_id=project.id, skill_id=skill)
                db.session.add(skill_required)
        for skill in project.skills_required:
            if skill.skill_id not in form.skills_required.raw_data:
                skill_required = SkillRequired.query.get(skill.id)
                db.session.delete(skill_required)
        db.session.commit()
        flash('You have successfully edited the project.')

        return redirect(url_for('admin.list_projects'))

    return render_template('admin/projects/project.html', add_project=add_project,
                           project=project, form=form, title="Edit project")



@admin.route('/projects/clear/<int:id>', methods=['GET', 'POST'])
@login_required
def clear_notes(id):
    check_admin()

    project = Project.query.get_or_404(id)
    project.admin_notes = ""
    db.session.commit()
    flash('Notes cleared')

    return redirect(url_for('admin.list_projects'))


@admin.route('/projects/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project(id):
    check_admin()

    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('You have successfully deleted the project.')

    return redirect(url_for('admin.list_projects'))


@admin.route('/project/status/<int:id>/<status_id>', methods=['GET', 'POST'])
@login_required
def project_status(id, status_id):
    check_admin()

    project = Project.query.get_or_404(id)
    project.status_id = status_id
    project.updated_date = datetime.now()
    db.session.add(project)
    db.session.commit()
    flash('Project status updated')

    return redirect(url_for('admin.list_projects'))



#--------  Settings views ----------#

@admin.route('/settings', methods=['GET', 'POST'])
@login_required
def update_settings():
    check_admin()

    settings = Settings.query.first()
    all_jobs = [j for j in dir(Jobs) if type(getattr(Jobs, j)).__name__ == 'function']
    running = [j.id for j in scheduler.get_jobs()]
    form = SettingsForm(obj=settings)
    if form.validate_on_submit():
        settings.name=form.name.data,
        settings.subtitle=form.subtitle.data,
        settings.notification_period=form.notification_period.data,
        settings.last_notification_check=form.last_notification_check.data,
        settings.contact_name=form.contact_name.data,
        settings.contact_email=form.contact_email.data
        settings.minimum_team_size=form.minimum_team_size.data
        settings.maximum_team_size=form.maximum_team_size.data

        try:
            db.session.add(settings)
            db.session.commit()
            flash('You have successfully updated the settings.')
        except:
            flash('Error: settings not updated.')

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/settings/settings.html', form=form, title='Settings', all_jobs=all_jobs, running=running)

@admin.route('/add/<id>')
def add_scheduled_job(id):
    settings = Settings.query.first()
    period = 10
    if id == 'notify':
        period = settings.notification_period * 3600

    scheduler.add_job(func=eval('jobs.' + id), trigger="interval", seconds=period, id=id)
    flash(id + ' has been successfully started as a background job')
    return redirect(url_for('admin.update_settings'))


@admin.route('/remove/<id>')
def remove_scheduled_job(id):
    scheduler.remove_job(id)
    flash(id + ' has been successfully stopped')
    return redirect(url_for('admin.update_settings'))


#--------  Skill views ----------#

@admin.route('/skills')
@login_required
def list_skills():
    check_admin()
    skills = Skill.query.order_by(text('name')).all()
    return render_template('admin/skills/skills.html', skills=skills, title='skills')


@admin.route('/skills/add', methods=['GET', 'POST'])
@login_required
def add_skill():
    check_admin()
    add_skill = True

    form = SkillForm()
    if form.validate_on_submit():
        skill = Skill(name = form.name.data,
                      description = form.description.data)

        try:
            db.session.add(skill)
            db.session.commit()
            flash('You have successfully added a new skill.')
        except:
            flash('Error: skill id already exists.')

        return redirect(url_for('admin.list_skills'))

    return render_template('admin/skills/skill.html', add_skill=add_skill,
                           form=form, title='Add skill')


@admin.route('/skills/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_skill(id):
    check_admin()
    add_skill = False

    skill = Skill.query.get_or_404(id)
    form = SkillForm(obj=skill)
    if form.validate_on_submit():
        skill.name = form.name.data
        skill.description = form.description.data
        db.session.add(skill)
        db.session.commit()
        flash('You have successfully edited the skill.')

        return redirect(url_for('admin.list_skills'))

    form.name.data = skill.name
    form.description.data = skill.description

    return render_template('admin/skills/skill.html', add_skill=add_skill,
                           form=form, title="Edit skill")


@admin.route('/skills/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_skill(id):
    check_admin()

    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('You have successfully deleted the skill.')

    return redirect(url_for('admin.list_skills'))


#--------  Status views ----------#

@admin.route('/statuses')
@login_required
def list_statuses():
    check_admin()
    statuses = Status.query.all()
    return render_template('admin/statuses/statuses.html', statuses=statuses, title='Statuses')


@admin.route('/statuses/add', methods=['GET', 'POST'])
@login_required
def add_status():
    check_admin()
    add_status = True

    form = StatusForm()
    form.domain_id.choices = [(d.id, d.name) for d in Domain.query.order_by(text('name'))]
    if form.validate_on_submit():
        status = Status(name = form.name.data,
                        description = form.description.data,
                        domain_id = form.domain_id.data,
                        action_text = form.action_text.data,
                        default_for_domain = form.default_for_domain.data
                        )

        # try:
        db.session.add(status)
        db.session.commit()
        flash('You have successfully added a new status.')

        return redirect(url_for('admin.list_statuses'))

    return render_template('admin/statuses/status.html', add_status=add_status,
                           form=form, title='Add status')


@admin.route('/statuses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_status(id):
    check_admin()
    add_status = False

    status = Status.query.get_or_404(id)
    form = StatusForm(obj=status)
    form.domain_id.choices = [(d.id, d.name) for d in Domain.query.order_by(text('name'))]
    if form.validate_on_submit():
        status.name = form.name.data
        status.description = form.description.data
        status.domain_id = form.domain_id.data
        status.action_text = form.action_text.data
        status.default_for_domain = form.default_for_domain.data
        db.session.add(status)
        db.session.commit()
        flash('You have successfully edited the status.')

        return redirect(url_for('admin.list_statuses'))

    form.name.data = status.name
    form.description = status.description
    form.domain_id.data = status.domain_id
    form.action_text.data = status.action_text
    form.default_for_domain.data = status.default_for_domain

    return render_template('admin/statuses/status.html', add_status=add_status,
                           form=form, title="Edit status")


@admin.route('/statuses/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_status(id):
    check_admin()

    status = Status.query.get_or_404(id)
    db.session.delete(status)
    db.session.commit()
    flash('You have successfully deleted the status.')

    return redirect(url_for('admin.list_statuses'))


#--------  Team views ----------#

@admin.route('/teams')
@login_required
def list_teams():
    check_admin()
    teams = Team.query.all()
    return render_template('admin/teams/teams.html', teams=teams, title='teams')


@admin.route('/teams/add', methods=['GET', 'POST'])
@login_required
def add_team():
    check_admin()
    add_team = True

    form = TeamForm()
    form.project_id.choices = [(p.id, p.title) for p in Project.query.order_by(text('title'))]
    form.created_by.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in User.query.order_by(text('last_name'), text('first_name'))]
    form.members.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in User.query.order_by(text('last_name'), text('first_name'))]
    team_domain = Domain.query.filter(Domain.name == 'team').first()
    form.status_id.choices = [(s.id, s.name) for s in Status.query.filter(Status.domain_id == team_domain.id).order_by(text('status.name'))]
    default_status = Status.query.filter(Status.domain_id == team_domain.id,
                                         Status.default_for_domain == True).first()
    form.status_id.default = default_status.id
    form.status_id.data = default_status.id
    form.created_by.default = current_user.id
    form.created_by.data = current_user.id
    if form.validate_on_submit():
        team = Team(project_id = form.project_id.data,
                    created_by = form.created_by.data,
                    comment = form.comment.data,
                    vacancies = form.vacancies.data,
                    status_id = form.status_id.data)

        try:
            db.session.add(team)
            db.session.commit()
            db.session.refresh(team)
            for member in form.members.data:
                team_member = TeamMember(team_id=team.id, user_id=member)
                db.session.add(team_member)
            db.session.commit()
            flash('You have successfully added a new team.')
        except:
            flash('Error: team id already exists.')

        return redirect(url_for('admin.list_teams'))

    return render_template('admin/teams/team.html', add_team=add_team,
                           form=form, title='Add team')


@admin.route('/teams/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    check_admin()
    add_team = False

    team = Team.query.get_or_404(id)
    form = TeamForm(obj=team)
    form.project_id.choices = [(p.id, p.title) for p in Project.query.order_by(text('title'))]
    form.created_by.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in User.query.order_by(text('last_name'), text('first_name'))]
    form.members.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in User.query.filter(User.is_student == 1).order_by(text('last_name'), text('first_name'))]
    team_domain = Domain.query.filter(Domain.name == 'team').first()
    form.status_id.choices = [(s.id, s.name) for s in Status.query.filter(Status.domain_id == team_domain.id).order_by(text('status.name'))]
    form.members.data = [m.user.id for m in team.members]
    if form.validate_on_submit():
        team.project_id = form.project_id.data
        team.created_by = form.created_by.data
        team.comment = form.comment.data
        team.vacancies = form.vacancies.data
        team.status_id = form.status_id.data
        team.updated_date = datetime.now()
        db.session.add(team)
        for member in form.members.raw_data:
            if member not in [m.user_id for m in team.members]:
                team_member = TeamMember(team_id=team.id, user_id=member)
                db.session.add(team_member)
        for member in team.members:
            if member.user_id not in form.members.raw_data:
                team_member = TeamMember.query.get(member.id)
                db.session.delete(team_member)
        db.session.commit()
        flash('You have successfully edited the team.')

        return redirect(url_for('admin.list_teams'))

    form.project_id.data = team.project_id
    form.created_by.data = team.created_by
    form.comment.data = team.comment
    form.vacancies.data = team.vacancies
    form.status_id.data = team.status_id
    return render_template('admin/teams/team.html', add_team=add_team,
                           team=team, form=form, title="Edit team")


@admin.route('/teams/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_team(id):
    check_admin()

    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    flash('You have successfully deleted the team.')

    return redirect(url_for('admin.list_teams'))


#--------  Transition views ----------#

@admin.route('/transitions')
@login_required
def list_transitions():
    check_admin()
    transitions = Transition.query.all()
    return render_template('admin/transitions/transitions.html', transitions=transitions, title='transitions')


@admin.route('/transitions/add', methods=['GET', 'POST'])
@login_required
def add_transition():
    check_admin()
    add_transition = True

    form = TransitionForm()
    form.from_status_id.choices = [(s.id, s.domain.name + ' - ' + s.name) for s in Status.query.order_by(text('name'))]
    form.to_status_id.choices = [(s.id, s.domain.name + ' - ' + s.name) for s in Status.query.order_by(text('name'))]
    if form.validate_on_submit():
        transition = Transition(from_status_id = form.from_status_id.data,
                                to_status_id = form.to_status_id.data,
                                admin_only = form.admin_only.data
                                )

        try:
            db.session.add(transition)
            db.session.commit()
            flash('You have successfully added a new transition.')
        except:
            flash('Error: transition id already exists.')

        return redirect(url_for('admin.list_transitions'))

    return render_template('admin/transitions/transition.html', add_transition=add_transition,
                           form=form, title='Add transition')


@admin.route('/transitions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transition(id):
    check_admin()
    add_transition = False

    transition = Transition.query.get_or_404(id)
    form = TransitionForm(obj=transition)
    form.from_status_id.choices = [(s.id, s.domain.name + ' - ' + s.name) for s in Status.query.order_by(text('name'))]
    form.to_status_id.choices = [(s.id, s.domain.name + ' - ' + s.name) for s in Status.query.order_by(text('name'))]
    if form.validate_on_submit():
        transition.from_status_id = form.from_status_id.data
        transition.to_status_id = form.to_status_id.data
        transition.admin_only = form.admin_only.data
        db.session.add(transition)
        db.session.commit()
        flash('You have successfully edited the transition.')

        return redirect(url_for('admin.list_transitions'))

    form.from_status_id.data = transition.from_status_id
    form.to_status_id.data = transition.to_status_id
    form.admin_only.data = transition.admin_only

    return render_template('admin/transitions/transition.html', add_transition=add_transition,
                           form=form, title="Edit transition")


@admin.route('/transitions/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_transition(id):
    check_admin()

    transition = Transition.query.get_or_404(id)
    db.session.delete(transition)
    db.session.commit()
    flash('You have successfully deleted the transition.')

    return redirect(url_for('admin.list_transitions'))


#--------  User views ----------#

@admin.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    check_admin()
    filter = request.args.get("filter")
    one_hour_ago = datetime.now() - timedelta(hours=1)

    if filter is None or filter == 'all':
        title = "All users"
        users = User.query.order_by(User.is_admin.desc()).order_by(User.last_name).order_by(User.first_name).all()
    elif filter == 'students':
        title = filter.title()
        users = User.query.filter(User.is_student).order_by(User.is_admin.desc()).order_by(User.last_name).order_by(User.first_name).all()
    elif filter == 'staff':
        title = filter.title()
        users = User.query.filter(User.is_staff).order_by(User.is_admin.desc()).order_by(User.last_name).order_by(
            User.first_name).all()
    elif filter == 'clients':
        title = filter.title()
        users = User.query.filter(User.is_external).order_by(User.is_admin.desc()).order_by(User.last_name).order_by(User.first_name).all()
    elif filter == 'recent':
        title = filter.title()
        users = User.query.filter(User.last_login > one_hour_ago).order_by(User.is_admin.desc()).order_by(User.last_name).order_by(User.first_name).all()
    elif filter == 'confirm':
        title = filter.title()
        users = User.query.filter(~User.company_confirmed).order_by(User.is_admin.desc()).order_by(User.last_name).order_by(User.first_name).all()

    return render_template('admin/users/users.html', users=users, filter=filter, title=title)


@admin.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    check_admin()
    add_user = False

    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    programmes = Programme.query.all()
    form.programme_code.choices = [(p.code, p.title) for p in programmes]
    form.company_id.choices = [(c.id, c.name) for c in Company.query.order_by(Company.name).all()]
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.telephone = form.telephone.data
        user.company_id = form.company_id.raw_data[0]
        user.programme_code = form.programme_code.raw_data[0]
        user.profile_comment = form.profile_comment.data
        user.is_admin = form.is_admin.data
        user.is_external = form.is_external.data
        user.is_staff = form.is_staff.data
        user.is_student = form.is_student.data
        user.display_name_flag = form.display_name_flag.data
        user.display_email_flag = form.display_email_flag.data
        user.display_phone_flag = form.display_phone_flag.data
        user.notify_new = form.notify_new.data
        user.notify_interest = form.notify_interest.data
        db.session.commit()

        flash('User updated')

        return redirect(url_for('admin.users'))

    return render_template('admin/users/user.html', add_user=add_user,
                           user=user, form=form, title="Edit user")


@admin.route('/confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def confirm_user(id):
    check_admin()

    user = User.query.get_or_404(id)
    user.company_confirmed = True
    db.session.add(user)
    db.session.commit()
    flash('Company confirmed for ' + user.first_name + ' ' + user.last_name)

    users = User.query.filter(User.company_confirmed == 0).all()
    return render_template('admin/users/users.html',
                           users=users,
                           title='Confirm company')


@admin.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    check_admin()

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash(user.first_name + ' ' + user.last_name + ' deleted')

    users = User.query.filter(User.company_confirmed == 0).all()
    return render_template('admin/users/users.html',
                           users=users,
                           title='Confirm company')



@admin.route('/users/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_user(id):
    check_admin()
    user = User.query.get_or_404(id)

    if user.is_admin:
        abort(403)

    form = UserAssignForm(obj=user)
    if form.validate_on_submit():
        user.programme = form.programme.data
        user.company = form.company.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully assigned a programme/company.')

        return redirect(url_for('admin.list_users'))

    return render_template('admin/users/user.html',
                           user=user, form=form,
                           title='Assign User')


@admin.route('/email/<return_url>/<int:id>', methods=['GET', 'POST'])
@admin.route('/email/<return_url>/<int:id>/<int:return_id>', methods=['GET', 'POST'])
@login_required
def email(return_url, id, return_id=None):
    check_admin()
    user = User.query.get_or_404(id)

    form = EmailForm(obj=user)
    if form.validate_on_submit():
        msg = Message(subject=form.subject.data,
                      body=form.message.data,
                      sender=current_user.email,
                      cc=[current_user.email],
                      recipients=[user.email])
        mail = Mail(current_app)
        mail.send(msg)

        flash('Email sent')

        if return_id:
            return redirect(url_for(return_url, id=return_id))
        else:
            return redirect(url_for(return_url))

    return render_template('admin/users/email.html',
                           user=user, form=form,
                           title='Email')


@admin.route('/team_email/<return_url>/<int:id>', methods=['GET', 'POST'])
@admin.route('/team_email/<return_url>/<int:id>/<int:return_id>', methods=['GET', 'POST'])
@login_required
def team_email(return_url, id, return_id=None):
    check_admin()
    recipients = [m.user for m in TeamMember.query.filter(TeamMember.team_id == id).all()]

    form = EmailForm()
    if form.validate_on_submit():
        msg = Message(subject=form.subject.data,
                      body=form.message.data,
                      sender=current_user.email,
                      cc=[current_user.email],
                      recipients=[u.email for u in recipients])
        mail = Mail(current_app)
        mail.send(msg)

        flash('Email sent')

        if return_id:
            return redirect(url_for(return_url, id=return_id))
        else:
            return redirect(url_for(return_url))

    return render_template('admin/users/group_email.html',
                           recipients=recipients, form=form,
                           title='Email')


@admin.route('/students_email/<return_url>', methods=['GET', 'POST'])
@login_required
def students_email(return_url):
    check_admin()
    students = User.query.filter(User.is_student).all()

    form = EmailForm()
    if form.validate_on_submit():
        msg = Message(subject=form.subject.data,
                      body=form.message.data,
                      sender=current_user.email,
                      recipients=[current_user.email],
                      bcc=[u.email for u in students])
        mail = Mail(current_app)
        mail.send(msg)

        flash('Email sent')

        return redirect(url_for(return_url))

    return render_template('admin/users/group_email.html',
                           recipients=students, form=form,
                           title='Email all students')


@admin.route('/clients_email/<return_url>', methods=['GET', 'POST'])
@login_required
def clients_email(return_url):
    check_admin()
    this_year = get_this_year()

    projects = Project.query.filter(Project.academic_year == this_year.year).order_by(Project.client_id).all()
    if len(projects):
        clients = [projects[0].client]
        for p in projects:
            if p.client_id != clients[-1].id:
                clients.append(p.client)

        form = EmailForm()
        if form.validate_on_submit():
            msg = Message(subject=form.subject.data,
                          body=form.message.data,
                          sender=current_user.email,
                          recipients=[current_user.email],
                          bcc=[u.email for u in clients])
            mail = Mail(current_app)
            mail.send(msg)

            flash('Email sent')

            return redirect(url_for(return_url))

        return render_template('admin/users/group_email.html',
                               recipients=clients, form=form,
                               title='Email all clients')
    else:
        flash('No projects found for ' + this_year.year)
        return redirect(url_for(return_url))


@admin.route('/staff/profile/edit', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.profile_comment = form.profile_comment.data
        db.session.commit()
        flash('Profile updated')
        return redirect(url_for('admin.dashboard'))

    if form.errors:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error, 'error')

    return render_template('staff/profile/profile.html', user=user, form=form, title="Edit profile")

@admin.route('/admin/preview/<int:id>', methods=['GET', 'POST'])
@login_required
def preview(id):
    check_admin()
    team = Team.query.get(id)

    return render_template('admin/teams/preview.html',
                           team=team,
                           title='Preview')

# ToDo: Add function to archive old projects - ie. change status of live, relisted, taken, protected, new to old for all projects not in the current academic year
