logging_config = {
    'version': 1,
    'loggers': {
        'TagSrv': {
            'handlers':['tagsrv_file', 'tagsrv_console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'PylogicLogger': {
            'handlers': ['common_console'],
            'propagate': False,
            'level': 'INFO',
        },
        'top': {
            'handlers': ['common_console', 'top_file'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'supervisors': {
            'handlers': ['common_console'],
            'propagate': False,
            'level': 'INFO',
        },
        # 'modbus_tk': {
        #     'handlers': ['common_console'],
        #     'propagate': False,
        #     'level': 'DEBUG',
        # }
    },
    'handlers': {
        'tagsrv_file': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024,
            'backupCount': 100,
            'filename': 'logs/tagsrv.log'
        },
        'tagsrv_console': {
            'level': 'CRITICAL',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler'
        },
        'common_console': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler'
        },
        'top_file': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024,
            'backupCount': 3,
            'filename': 'logs/objects.log'
        },
        'tmp_file': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024,
            'backupCount': 3,
            'filename': 'logs/tmp.log'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        }
    }
}
