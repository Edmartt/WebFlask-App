import os

class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev'
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    TESTING=True

config={'development':DevelopmentConfig,'testing':TestingConfig,'default':DevelopmentConfig}
