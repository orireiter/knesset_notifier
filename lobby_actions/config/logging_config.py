LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simpleFormatter': {
            'format': '%(asctime)s - %(process)d - %(levelname)s - %(name)s - %(message)s'
        },
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simpleFormatter',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
            'handlers': ['consoleHandler'],
            'level': 'DEBUG',
    }
}
