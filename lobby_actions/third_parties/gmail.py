import logging
import smtplib

from email.message import EmailMessage

from lobby_actions.config.env_conf import EnvironmentConfig


env_conf = EnvironmentConfig()
logger = logging.getLogger(__name__)


class GmailSmtp:
    def __init__(
        self,
        smtp_server_url: str = env_conf.gmail_smtp.server_url,
        smtp_server_port: int = int(env_conf.gmail_smtp.server_port),
        user_id: str = env_conf.gmail_smtp.user_id,
        password: str = env_conf.gmail_smtp.password,
    ):
        self._smtp_server_url = smtp_server_url
        self._smtp_server_port = smtp_server_port
        self._user_id = user_id
        self._password = password

    def send_mail(
        self, receivers: list[str], subject: str, content: str, is_rtl: bool = False
    ):
        email_to_send = self._build_email(
            receivers=receivers, subject=subject, content=content, is_rtl=is_rtl
        )

        with smtplib.SMTP(self._smtp_server_url, self._smtp_server_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(self._user_id, self._password)
            server.sendmail(
                self._user_id, receivers, email_to_send.as_string().encode("UTF-8")
            )

    def _build_email(
        self, receivers: list[str], subject: str, content: str, is_rtl: bool = False
    ):
        # Create the container email message.
        msg = EmailMessage()
        msg["Subject"] = subject or ""

        msg["From"] = self._user_id
        msg["To"] = ", ".join(receivers)
        # msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        if content and is_rtl:
            content = f'<div style="direction:rtl">{content}</div>'
            content = content.replace("\n", "<br>")
            msg.add_header("Content-Type", "text/html")

        logger.info(
            f"sending from {self._user_id} to {receivers=} {subject=} {content=}"
        )
        msg.set_payload(content)

        return msg
