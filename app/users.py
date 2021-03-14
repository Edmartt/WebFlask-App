from flask import request,current_app
from flask_login import UserMixin
from flask_mysqldb import MySQL
from .auth import forms
from app import login_manager,db
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class User(UserMixin):

    def __init__(self,password,email,username,confirmed,id=None,pending_email=None):
        self.password_hash=password
        self.username=username
        self.email=email
        self.id=id
        self.confirmed=confirmed
        self.pending_email=pending_email
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
            confirmed=user[4]
            return User(password,email,username,confirmed,id)

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
            confirmed=user[4]
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
            confirmed=user[4]
            pending_email=user[5]
            return User(password,email,username,confirmed,id,pending_email)

    def insert_user(self,user):
        cursor=db.connection.cursor()
        cursor.execute('INSERT INTO users(username,password,email,confirmed) VALUES(%s,%s,%s,%s)',(self.username,self.password_hash,self.email,self.confirmed))
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
        print("imprimiendo estado: ",self.confirmed)
        return True

    @staticmethod
    def id_decoder(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token.encode('utf-8'))
            return data.get('confirm')
        except:
            return None
    def change_confirm_state(self,id,confirmed):
        cursor=db.connection.cursor()
        cursor.execute('UPDATE users SET confirmed=%s WHERE id=%s',(id,confirmed))
        db.connection.commit()

    def update_password(self,id):
        cursor=db.connection.cursor()
        cursor.execute('UPDATE users SET password=%s WHERE id=%s',(self.password_hash,self.id))
        db.connection.commit()
    def update_email(self,id,email):
        cursor=db.connection.cursor()
        cursor.execute('UPDATE users SET email=%s WHERE id=%s',(email,id))
        db.connection.commit()

    def update_pending_email(self,email,id):
        cursor=db.connection.cursor()
        cursor.execute('UPDATE users SET pending_email=%s WHERE id=%s',(email,id))
        db.connection.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.select_user(user_id)
