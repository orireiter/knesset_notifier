from json import dumps


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "base_formatter": {
            "format": dumps(
                {
                    "timestamp": "%(asctime)s",
                    "process": "%(process)d",
                    "severity": "%(levelname)s",
                    "module": "%(module)s",
                    "content": "%(message)s",
                }
            )
        },
    },
    "handlers": {
        "stdout_handler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "base_formatter",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "handlers": ["stdout_handler"],
        "level": "DEBUG",
    },
}
