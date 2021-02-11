import os

class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[FLASKER]'
    FLASKY_MAIL_SENDER = 'Flasker Admin <flasker@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKER_ADMIN')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    TESTING=True

config={'development':DevelopmentConfig,'testing':TestingConfig,'default':DevelopmentConfig}
