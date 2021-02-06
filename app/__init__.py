from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_mail import Mail
from config import config
import os

db=MySQL()
mail=Mail()

login_manager=LoginManager()
login_manager.login_view='auth.login'
login_manager.login_message=u'Inicia sesión para acceder a esta página'
def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    login_manager.init_app(app)
    app.config['MYSQL_HOST']=os.environ.get('HOST')
    app.config['MYSQL_USER']=os.environ.get('USER')
    app.config['MYSQL_PASSWORD']=os.environ.get('PASSWORD')
    app.config['MYSQL_DB']=os.environ.get('DATABASE')
    db=MySQL(app)
    mail=Mail(app)
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    from . import users

    return app
