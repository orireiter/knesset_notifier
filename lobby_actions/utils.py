import os


def load_env_vars():
    if os.path.exists("env.py"):
        import env

        env.load_env_from_config()
