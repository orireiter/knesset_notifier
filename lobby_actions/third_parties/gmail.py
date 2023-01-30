import os
import logging
import smtplib

# Here are the email package modules we'll need.
from email.message import EmailMessage


logger = logging.getLogger(__name__)


class GmailSmtp:
    def __init__(self, smtp_server_url: str = os.environ.get('GMAIL_SMTP_SERVER_URL'),
                 smtp_server_port: int = int(os.environ.get('GMAIL_SMTP_SERVER_PORT')),
                 user_id: str = os.environ.get('GMAIL_SMTP_USER_ID'),
                 password: str = os.environ.get('GMAIL_SMTP_PASSWORD')):
        self._smtp_server_url = smtp_server_url
        self._smtp_server_port = smtp_server_port
        self._user_id = user_id
        self._password = password

    def send_mail(self, receivers: list[str], subject: str, content: str, is_rtl: bool = False):
        email_to_send = self._build_email(receivers=receivers, subject=subject, content=content, is_rtl=is_rtl)

        with smtplib.SMTP(self._smtp_server_url, self._smtp_server_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(self._user_id, self._password)
            server.sendmail(self._user_id, receivers, email_to_send.as_string())

    def _build_email(self, receivers: list[str], subject: str, content: str, is_rtl: bool = False):
        # Create the container email message.
        msg = EmailMessage()
        msg['Subject'] = subject or ''

        msg['From'] = self._user_id
        msg['To'] = ', '.join(receivers)
        # msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        # todo fix rtl
        content = f'<div style="direction:rtl">{content}</div>' if content and is_rtl else ''
        logger.info(f'sending from {self._user_id} to {receivers=} {subject=} {content=}')
        msg.set_content(content)

        return msg
