import os
import ast

from dotenv import load_dotenv

from lobby_actions.data.models import ConfigModels


class EnvironmentConfig:
    _instance = None
    _is_instance_initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance

        cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._is_instance_initialized:
            return

        self.load_env_vars()

        # init values
        self.gmail_smtp = ConfigModels.GmailSmtp(
            server_url=os.environ.get("GMAIL_SMTP_SERVER_URL", ""),
            server_port=os.environ.get("GMAIL_SMTP_SERVER_PORT", ""),
            user_id=os.environ.get("GMAIL_SMTP_USER_ID", ""),
            password=os.environ.get("GMAIL_SMTP_PASSWORD", ""),
        )

        self.application = ConfigModels.App(
            lobby_actions_summary_emails_to_report_to=ast.literal_eval(
                os.environ.get("LOBBY_ACTIONS_SUMMARY_EMAILS_TO_REPORT_TO")
            )
        )

        self._is_instance_initialized = True

    @staticmethod
    def load_env_vars():
        if os.path.exists("env.py"):
            import env

            return env.load_env_from_config()

        load_dotenv()
