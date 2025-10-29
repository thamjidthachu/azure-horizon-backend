import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_CONFIG = {
    'payment': 'payment.log',
    'booking': 'booking.log',
    'contact': 'contact.log',
    'email': 'email.log',
    'authentication': 'authentication.log',
    'server': 'server.log',
    'celery': 'celery.log',
}

LOG_FORMAT = '%(asctime)s - %(threadName)s - %(filename)s - %(funcName)s - %(lineno)d - [%(levelname)s] - %(message)s'
DATE_FORMAT = '%d-%m-%Y %H:%M:%S,%f'

loggers = {}


for key, filename in LOG_CONFIG.items():
    logger = logging.getLogger(key)
    logger.setLevel(logging.INFO)
    log_path = os.path.join(LOG_DIR, filename)
    # Remove any existing file handlers for this logger to avoid duplicate or wrong handlers
    for h in list(logger.handlers):
        if isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', None) == os.path.abspath(log_path):
            logger.removeHandler(h)
    file_handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    loggers[key] = logger

def get_logger(name):
    return loggers.get(name, loggers['server'])
