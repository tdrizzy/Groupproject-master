from flask import abort, flash, redirect, url_for, session
from flask_login import current_user, login_required
from sqlalchemy import and_, or_
from app.models import *
import html.parser


def check_client(project):
    if project.client_id != current_user.id:
        abort(403)


def check_member(team):
    member = TeamMember.query.filter(and_(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id)).first()
    if member is None:
        abort(403)


def check_owner(item):
    if item.user_id != current_user.id:
        abort(403)


def check_members(team, settings):
    if len(team.members) < settings.minimum_team_size:
        return False
    return True


def check_programmes(team):
    programmes = set([m.user.programme_code for m in TeamMember.query.filter(TeamMember.team_id == team.id).all()])
    if len(programmes) > 1:
        return True
    return False


def check_pm(team):
    project_manager = TeamMember.query.filter(and_(TeamMember.team_id == team.id, TeamMember.project_manager == True)).first()
    if project_manager:
        return True
    return False


def get_status(domain_name, status_name):
    domain = Domain.query.filter(Domain.name == domain_name).first()
    return Status.query.filter(and_(Status.domain==domain, Status.name==status_name)).first()


def get_bids(project):
    return Team.query.filter(and_(Team.project_id == project.id)).join(Status).\
                      filter(or_(Status.name=='Submitted', Status.name=='Accepted', Status.name=='Shortlisted')).all()


def get_new_teams(project):
    return Team.query.filter(and_(Team.project_id == project.id)).join(Status).\
                      filter(Status.name=='New').all()


def get_this_year():
    return AcademicYear.query.filter(and_(datetime.now() > AcademicYear.start_date, datetime.now() < AcademicYear.end_date)).first()


def change_academic_year(year):
    session['academic_year'] = year
    return session['academic_year']


def delete_notes(user_id, project_id=None):
    if project_id is None:
        notes = Interest.query.filter(Interest.user_id == user_id).all()
    else:
        notes = Interest.query.filter(and_(Interest.user_id == user_id, Interest.project_id == project_id)).all()
    for note in notes:
        db.session.delete(note)


def delete_flags(user_id, project_id=None):
    if project_id is None:
        flags = Flag.query.filter(Flag.user_id == user_id).all()
    else:
        flags = Flag.query.filter(and_(Flag.user_id == user_id, Flag.project_id == project_id)).all()
    for flag in flags:
        db.session.delete(flag)


def alert(id, code, team=False, project=None):
    message = AlertText.query.get_or_404(code)
    text = message.message_text

    if "{project}" in text:
        text = text.replace("{project}", "'"+project.title+"'")
    if "{client}" in text:
        text = text.replace("{client}", project.client.first_name + ' ' + project.client.last_name)
    if "{client_email}" in text:
        text = text.replace("{client_email}", project.client.email)

    if team:
        recipients = [m.user for m in TeamMember.query.filter(TeamMember.team_id == id).all()]
    else:
        recipients = User.query.filter(User.id==id).all()

    for recipient in recipients:
        queued = AlertQueue(
            user_id = recipient.id,
            email = recipient.email,
            subject = message.subject,
            message_text = text
        )
        db.session.add(queued)
        db.session.commit()


def security_alert(text):
    recipients = [u for u in User.query.filter(User.is_admin == 1).all()]

    for recipient in recipients:
        queued = AlertQueue(
            user_id = recipient.id,
            email = recipient.email,
            subject = "Security alert",
            message_text = text
        )
        db.session.add(queued)
        db.session.commit()


def sanitise(text):
    text2 = text.replace('&', '&amp;')
    text2 = text2.replace('<', '&lt;')
    text2 = text2.replace('>', '&gt;')
    text2 = text2.replace('"', '&quot;')
    text2 = text2.replace("'", '&#x27;')
    # text2 = text2.replace('/', '&#x2F;')   Don't remove slashes so that the text can still contain URLs
    return text2


class MyHTMLParser(html.parser.HTMLParser):
    good_tags = ['a', 'b', 'body', 'br', 'head', 'html', 'i', 'img', 'p', 'h1', 'h2', 'h3', 'style', 'u']
    close_tags = ['br', 'img']
    good_attrs = ['href', 'src']
    outstring = ""

    def handle_starttag(self, tag, attrs):
        if tag in self.good_tags:
            self.outstring += "<{}".format(tag)
            for aname, avalue in attrs:
                if aname in self.good_attrs:
                    self.outstring += " {}=\"{}\"".format(aname, avalue)
            if tag == 'a':
                self.outstring += " target=\"_blank\""
            if tag == 'img':
                self.outstring += " style=\"max-width: 100px; max-height: 100px;\""
            if tag not in self.close_tags:
                self.outstring += ">"

    def handle_endtag(self, tag):
        if tag in self.good_tags:
            if tag in self.close_tags:
                self.outstring += "/>"
            else:
                self.outstring += "</{}>".format(tag)

    def handle_data(self, data):
        self.outstring += data

    def init(self):
        self.outstring = ""

    # Usage
    # parser = MyHTMLParser()
    # parser.feed('<html><head><title>Test</title></head>'
    #             '<body><h1>Parse me!</h1><img src="a.png" onclick="alert(\'running\');"/>'
    #             '<a href="https://www.napier.ac.uk">Napier</a>'
    #             '</body></html>')
    # print(parser.outstring)
