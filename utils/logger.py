import os

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

