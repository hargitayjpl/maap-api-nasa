import email.encoders
import logging
import smtplib
import os

from api import settings
from api.models.member import Member
from api.utils.environments import Environments
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

log = logging.getLogger(__name__)
CHARSET = "utf-8"

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


class EmailFormats(Enum):
    PLAIN = 'plain'
    HTML = 'html'


class Email(object):

    def __init__(self, from_, to, subject, html_message, text_message):

        self.from_ = from_
        self.to = to

        self.email = MIMEMultipart('mixed')
        self.email['From'] = from_
        self.email['To'] = ",".join(to)
        self.email['Subject'] = subject

        # Create Message Body
        message_body = MIMEMultipart('alternative')

        # Add text/plain message part
        text = MIMEText(text_message.encode(CHARSET), EmailFormats.PLAIN.value, CHARSET)
        message_body.attach(text)

        # Add text/html message part
        html = MIMEText(html_message.encode(CHARSET), EmailFormats.HTML.value, CHARSET)
        message_body.attach(html)

        # Add message body to parent container
        self.email.attach(message_body)

    def send(self):

        with smtplib.SMTP(settings.SMTP_HOSTNAME, settings.SMTP_PORT) as smtp_server:

            smtp_server.set_debuglevel(settings.SMTP_DEBUG_LEVEL)

            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.ehlo()

            try:
                smtp_server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            except smtplib.SMTPException as e:
                log.error("Unable to login to SMTP server: ", e.strerror)
                raise e

            try:
                smtp_server.send_message(self.email, self.from_, self.to)
            except smtplib.SMTPException as e:
                log.error("Unable to send email: ", e.strerror)
                raise e

    def __str__(self):
        return self.email.as_string()


def send_new_active_user_email(member: Member, base_url):

    environment_info = get_environment_info(base_url)
    email_message_subj = "MAAP ({}): New Registered User".format(environment_info['env'])

    # Build HTML body
    email_message_html = ""
    template_file = SCRIPT_PATH + "/email_templates/new_active_user_admin_alert.html"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_html = file.read().format(
            environment_info=environment_info,
            member_email=member.email,
            member_display_name=member.get_display_name(),
            title=email_message_subj
        )

    # Build Text body
    email_message_txt = ""
    template_file = SCRIPT_PATH + "/email_templates/new_active_user_admin_alert.txt"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_txt = file.read().format(
            environment_info=environment_info,
            member_email=member.email,
            member_display_name=member.get_display_name(),
            title=email_message_subj
        )

    # Create and send the email
    email_message = Email(
        settings.EMAIL_NO_REPLY,
        settings.EMAIL_JPL_ADMINS.split(","),
        email_message_subj,
        email_message_html,
        email_message_txt
    )
    log.info("Sending 'New Active User' email for {} to JPL Admins ({})".format(
        member.get_display_name(),
        settings.EMAIL_JPL_ADMINS
    ))
    email_message.send()
    log.info("Email Sent!")


def send_new_suspended_user_email(member: Member, base_url):

    environment_info = get_environment_info(base_url)
    email_message_subj = "MAAP ({}): New Registered User (Action Needed)".format(environment_info['env'])

    # Build HTML body
    email_message_html = ""
    template_file = SCRIPT_PATH + "/email_templates/new_suspended_user_admin_alert.html"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_html = file.read().format(
            environment_info=environment_info,
            member_email=member.email,
            member_display_name=member.get_display_name(),
            title=email_message_subj,
        )

    # Build Text body
    email_message_txt = ""
    template_file = SCRIPT_PATH + "/email_templates/new_suspended_user_admin_alert.txt"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_txt = file.read().format(
            environment_info=environment_info,
            member_email=member.email,
            member_display_name=member.get_display_name(),
            title=email_message_subj,
        )

    # Create and send the email
    email_message = Email(
        settings.EMAIL_NO_REPLY,
        settings.EMAIL_JPL_ADMINS.split(","),
        email_message_subj,
        email_message_html,
        email_message_txt
    )
    log.info("Sending 'New Suspended User' email for {} to JPL Admins ({})".format(
        member.get_display_name(),
        settings.EMAIL_JPL_ADMINS
    ))
    email_message.send()
    log.info("Email Sent!")


def send_user_status_update_active_user_email(member: Member, base_url):

    environment_info = get_environment_info(base_url)
    email_message_subj = "Your MAAP account has been activated"

    # Build HTML body
    email_message_html = ""
    template_file = SCRIPT_PATH + "/email_templates/user_status_update_active_user_alert.html"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_html = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            title=email_message_subj,
        )

    # Build Text body
    email_message_txt = ""
    template_file = SCRIPT_PATH + "/email_templates/user_status_update_active_user_alert.txt"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_txt = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            title=email_message_subj,
        )

    # Create and send the email
    email_message = Email(
        settings.EMAIL_SUPPORT,
        [member.email],
        email_message_subj,
        email_message_html,
        email_message_txt
    )
    log.info("Sending 'User Status Update (Active)' email for {} to {}".format(
        member.get_display_name(),
        member.email
    ))
    email_message.send()
    log.info("Email Sent!")


def send_user_status_update_suspended_user_email(member: Member, base_url):

    environment_info = get_environment_info(base_url)
    email_message_subj = "Your MAAP account has been deactivated"

    # Build HTML body
    email_message_html = ""
    template_file = SCRIPT_PATH + "/email_templates/user_status_update_suspended_user_alert.html"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_html = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            support_email=settings.EMAIL_SUPPORT,
            title=email_message_subj,
        )

    # Build Text body
    email_message_txt = ""
    template_file = SCRIPT_PATH + "/email_templates/user_status_update_suspended_user_alert.txt"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_txt = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            support_email=settings.EMAIL_SUPPORT,
            title=email_message_subj,
        )

    # Create and send the email
    email_message = Email(
        settings.EMAIL_SUPPORT,
        [member.email],
        email_message_subj,
        email_message_html,
        email_message_txt
    )
    log.info("Sending 'User Status Update (Suspended)' email for {} to {}".format(
        member.get_display_name(),
        member.email
    ))
    email_message.send()
    log.info("Email Sent!")


def send_welcome_to_maap_active_user_email(member: Member, base_url):

    environment_info = get_environment_info(base_url)
    email_message_subj = "Welcome to the Multi-Mission Algorithm and Analysis Platform (MAAP)!"

    # Build HTML body
    email_message_html = ""
    template_file = SCRIPT_PATH + "/email_templates/welcome_to_maap_active_user_alert.html"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_html = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            title=email_message_subj,
        )

    # Build Text body
    email_message_txt = ""
    template_file = SCRIPT_PATH + "/email_templates/welcome_to_maap_active_user_alert.txt"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_txt = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            title=email_message_subj,
        )

    # Create and send the email
    email_message = Email(
        settings.EMAIL_SUPPORT,
        [member.email],
        email_message_subj,
        email_message_html,
        email_message_txt
    )
    log.info("Sending 'Welcome to MAAP (Active User)' email for {} to {}".format(
        member.get_display_name(),
        member.email
    ))
    email_message.send()
    log.info("Email Sent!")


def send_welcome_to_maap_suspended_user_email(member: Member, base_url):

    environment_info = get_environment_info(base_url)
    email_message_subj = "Welcome to the Multi-Mission Algorithm and Analysis Platform (MAAP)!"

    # Build HTML body
    email_message_html = ""
    template_file = SCRIPT_PATH + "/email_templates/welcome_to_maap_suspended_user_alert.html"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_html = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            support_email=settings.EMAIL_SUPPORT,
            title=email_message_subj,
        )

    # Build Text body
    email_message_txt = ""
    template_file = SCRIPT_PATH + "/email_templates/welcome_to_maap_suspended_user_alert.txt"
    with open(template_file, "r", encoding=CHARSET) as file:
        email_message_txt = file.read().format(
            environment_info=environment_info,
            member_first_name=member.first_name,
            support_email=settings.EMAIL_SUPPORT,
            title=email_message_subj,
        )

    # Create and send the email
    email_message = Email(
        settings.EMAIL_SUPPORT,
        [member.email],
        email_message_subj,
        email_message_html,
        email_message_txt
    )
    log.info("Sending 'Welcome to MAAP (Suspended User)' email for {} to {}".format(
        member.get_display_name(),
        member.email
    ))
    email_message.send()
    log.info("Email Sent!")


def get_environment_info(base_url):

    env = Environments.DIT

    if "0.0.0.0" in base_url or "127.0.0.1" in base_url or "LOCALHOST" in base_url.upper():
        env = Environments.DIT
    elif Environments.DIT.value in base_url.upper():
        env = Environments.DIT
    elif Environments.UAT.value in base_url.upper():
        env = Environments.UAT
    elif Environments.OPS.value in base_url.upper():
        env = Environments.OPS

    email_header = {
        EmailFormats.PLAIN: '',
        EmailFormats.HTML: '',
    }
    if env != Environments.OPS:
        email_header = {
            EmailFormats.PLAIN.value: "*** THIS EMAIL WAS SENT FROM THE MAAP {} ENVIRONMENT ***".format(
                env.value.upper()),
            EmailFormats.HTML.value: """
                    <div style="width:100%;padding:10px;margin-bottom:10px;text-align:center;background-color:#FFC107;color:#000000;">
                        <strong>*** THIS EMAIL WAS SENT FROM THE MAAP {} ENVIRONMENT ***</strong>
                    </div>
                """.format(env.value.upper())
        }

    portal_base_url = "https://{}.maap-project.org".format(env.value.lower())

    data = {
        'env': env.value.upper(),
        'template': {
            'header': email_header
        },
        'urls': {
            'logo': portal_base_url + '/wp-content/uploads/2021/10/nasamaaplogo3.png',
            'portal': {
                'base_url': portal_base_url,
                'maap_admin': portal_base_url + settings.PORTAL_ADMIN_DASHBOARD_PATH,
                'open_policies': portal_base_url + "/open-policies/",
                'privacy_policy': 'https://www.nasa.gov/about/highlights/HP_Privacy.html',
                'tos': portal_base_url + "/terms-of-service/",
                'user_guides': portal_base_url + "/user-guides/",
            },
            'github': {
                'issues': 'https://github.com/MAAP-Project/ZenHub/issues'
            },
        },
    }

    return data
