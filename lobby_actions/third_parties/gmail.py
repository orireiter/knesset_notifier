import io
import os
import smtplib

# Here are the email package modules we'll need.
from email.message import EmailMessage


class GmailSmtp:
    def __init__(self, smtp_server_url: str = os.environ.get('GMAIL_SMTP_SERVER_URL'),
                 smtp_server_port: int = int(os.environ.get('GMAIL_SMTP_SERVER_URL')),
                 user_id: str = os.environ.get('GMAIL_SMTP_USER_ID'),
                 password: str = os.environ.get('GMAIL_SMTP_PASSWORD')):
        self.smtp_server_url = smtp_server_url
        self.smtp_server_port = smtp_server_port
        self.user_id = user_id
        self.password = password

    def send_mail(self, receivers: list[str], subject: str, content: str, attachments: list[io.BytesIO]):
        email_to_send = self._build_email(receivers=receivers, subject=subject, content=content,
                                          attachments=attachments)

        with smtplib.SMTP(self.smtp_server_url, self.smtp_server_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(self.user_id, self.password)
            server.sendmail(self.user_id, receivers, email_to_send)

    def _build_email(self, receivers: list[str], subject: str, content: str, attachments: list[io.BytesIO]):
        # Create the container email message.
        msg = EmailMessage()
        msg['Subject'] = subject or ''

        msg['From'] = self.user_id
        msg['To'] = ', '.join(receivers)
        # msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        msg.set_content(content or '')

        # Open the files in binary mode.  You can also omit the subtype
        # if you want MIMEImage to guess it.
        for file in attachments:
            msg.add_attachment(file.read())

        return msg
