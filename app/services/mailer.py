from email.message import EmailMessage
from smtplib import SMTP

from app.config import get_settings

settings = get_settings()


class Mailer:
    @staticmethod
    def send_message(content: str, subject: str, mail_to: str):
        message = EmailMessage()
        message.set_content(content)
        message['Subject'] = subject
        message['From'] = settings.mail_sender
        message['To'] = mail_to
        SMTP(settings.smtp_server).send_message(message)

    @staticmethod
    def send_confirmation_message(token: str, mail_to: str):
        confirmation_url = f'{settings.base_url}{settings.api_prefix}/auth/activate_email/{token}'
        message = '''Hi!
    Please confirm your registration: {}.'''.format(confirmation_url)
        Mailer.send_message(
            message,
            'Please confirm your registration',
            mail_to
        )

    @staticmethod
    def send_password_reset_message(token: str, mail_to: str):
        confirmation_url = '{}{}/auth/verify/{}'.format(settings.base_url, settings.api_prefix, token)
        message = '''Hi!
    Please confirm your registration: {}.'''.format(confirmation_url)
        Mailer.send_message(
            message,
            'Please confirm your registration',
            mail_to
        )
