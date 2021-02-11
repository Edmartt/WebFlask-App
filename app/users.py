from flask import request,current_app
from flask_login import UserMixin
from flask_mysqldb import MySQL
from .auth import forms
from app import login_manager,db
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class User(UserMixin):

    def __init__(self,password,email,username,id=None,confirmed=False):
        self.password_hash=password
        self.username=username
        self.email=email
        self.id=id
        self.confirmed=confirmed

    @staticmethod
    def select_user_by_email(email):
        cursor=db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email="{}"'.format(email))
        user=cursor.fetchone()
        if user:
            id=user[0]
            username=user[1]
            password=user[2]
            email=user[3]
            return User(password,email,username,id)

    @staticmethod
    def select_user_by_username(username):
        cursor=db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username="{}"'.format(username))
        user=cursor.fetchone()
        if user:
            id=user[0]
            username=user[1]
            password=user[2]
            email=user[3]
            return User(password,email,username,id)

    @staticmethod
    def select_user(id):
        cursor=db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id="{}"'.format(id))
        user=cursor.fetchone()
        if user:
            id=user[0]
            username=user[1]
            password=user[2]
            email=user[3]
            return User(password,email,username,id)

    def insert_user(self,username,password,email):
        cursor=db.connection.cursor()
        cursor.execute('INSERT INTO users(username,password,email) VALUES(%s,%s,%s)',(self.username,self.password_hash,self.email))
        db.connection.commit()

    @property
    def password(self):
        raise AttributeError('Este atributo no se puede leer')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')

    def confirm(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') !=self.id:
            return False
        self.confirmed=True
        change_confirm_state(self.confirmed)
        print("imprimiendo estado: ",self.confirmed)
        return True

@login_manager.user_loader
def load_user(user_id):
    return User.select_user(user_id)
