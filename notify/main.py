import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
sys.path.append('/opt/apps/soc09109/soc09109/')
from notify.models_background import  *


def log(message):
    with open("/tmp/flask_notification_log", "a") as f:
        f.write(str(message))


class Osmail(object):

    def __init__(self, sender, recipient, subject, text=None, html=None, cc=None):
        # Create message container - the correct MIME type is multipart/alternative.
        if html is None:
            msg = MIMEText(text)
        else:
            msg = MIMEMultipart('alternative')
            # Record the MIME types of both parts - text/plain and text/html.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            if text is not None:
                part1 = MIMEText(text)
                msg.attach(part1)
            if html is not None:
                part2 = MIMEText(html, 'html')
                msg.attach(part2)

        msg['Subject'] = subject
        msg['To'] = recipient
        msg['Cc'] = cc

        self.sender = sender
        self.recipient = recipient
        self.cc = cc
        self.subject = subject
        self.out = msg

    def send(self):
        os.system(
            "echo \"" + self.out.as_string() + "\"  | sendmail -f " + self.sender + " " + self.recipient)
        log(datetime.now().strftime('%y-%m-%d %H:%M') + ' EMAIL ' + self.recipient + ': ' + self.subject)

    def __repr__(self):
        return self.out


class Jobs(object):

    @staticmethod
    def notify():
        session = Session()
        settings = session.query(Settings)[0]

        log(datetime.now().strftime('%Y-%m-%d %H:%M') + ' Checking for new projects')
        new_projects = session.query(Project).filter(and_(Project.status_id == 3, Project.updated_date > settings.last_notification_check)).all()
        projects_message = ""
        if len(new_projects) > 0:
            projects_message += "There are some new projects available:\n\n"
            for project in new_projects:
                projects_message += project.title.upper() + "\n"
                if project.client.is_student:
                    projects_message += 'Student project proposal\n'
                else:
                    projects_message += project.client.company.name + "\n"
                projects_message += 'Skills required: '
                for i, skill_required in enumerate(project.skills_required):
                    if i > 0:
                        projects_message += ", "
                    projects_message += skill_required.skill_required.name
                projects_message += "\n\n"

        log(datetime.now().strftime('%Y-%m-%d %H:%M') + ' Checking for interest notifications')
        students = session.query(User).filter(User.is_external == False).all()
        for student in students:
            member = session.query(TeamMember).join(Team).join(Status). \
                filter(TeamMember.user_id == student.id). \
                filter(TeamMember.team_id == Team.id). \
                filter(Team.status_id == Status.id). \
                filter(Status.id == 'Accepted'). \
                first()
            # member = session.query(TeamMember).filter(and_(TeamMember.user_id == student.id, TeamMember.team.status.name == 'Accepted')).first()
            if member:
                continue

            message = ""
            if student.notify_new and projects_message != "":
                message += projects_message

            if student.notify_interest:
                projects = session.query(Project).join(Interest).join(Status).\
                    filter(Interest.user_id == student.id).\
                    filter(Interest.project_id == Project.id).\
                    filter(Project.status_id == Status.id).\
                    filter(Status.name == 'Live').all()
                # projects = [note.project for note in projects]
                if len(projects) > 0:
                    for i, project in enumerate(projects):
                        notes = session.query(Interest).join(Project).\
                            filter(Interest.project_id == Project.id).\
                            filter(Interest.created_date > settings.last_notification_check).\
                            filter(Interest.user_id != student.id).all()
                        if len(notes) > 0:
                            if i == 0:
                                message += "There are new notes of interest on projects that you are interested in:\n\n"
                            message += project.title
                            message += ": " + str(len(notes)) + " new note(s)\n"
                else:
                    message += "You have asked for a notification when someone else puts a note of interest on a project that you are interested in. "
                    message += "However, at the moment you have no notes of interest on any live projects. "
                    message += "To fix this, add some notes of interest on projects in the Projects Exchange system."

            if message != "":
                msg = Osmail("no_reply@projex.napier.ac.uk",
                             student.email,
                             "Projex notification",
                             text=message)
                msg.send()

        log(datetime.now().strftime('%Y-%m-%d %H:%M') + ' Checking for alerts')
        for alert in session.query(AlertQueue).filter(AlertQueue.sent_date == None):
            msg = Osmail("no_reply@projex.napier.ac.uk",
                         alert.email,
                         "Projex alert",
                         text=alert.message_text)

            msg.send()

            now = datetime.now()
            alert.sent_date = now.strftime('%Y-%m-%d %H:%M:%S')

        log(datetime.now().strftime('%Y-%m-%d %H:%M') + ' Updating last notification date')
        now = datetime.now()
        settings.last_notification_check = now.strftime('%Y-%m-%d %H:%M:%S')
        session.commit()


if __name__ == '__main__':
    jobs = Jobs()
    jobs.notify()
