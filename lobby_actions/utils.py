import os

from dotenv import load_dotenv


def load_env_vars():
    if os.path.exists("env.py"):
        import env

        env.load_env_from_config()
        return

    load_dotenv()
