from flask import request
from flask_login import UserMixin
from flask_mysqldb import MySQL
from .auth import forms
from app import login_manager,db
from werkzeug.security import generate_password_hash,check_password_hash


class User(UserMixin):

    def __init__(self,password,email,id=None,username=None):
        self.id=id
        self.username=username
        self.password=password
        self.email=email

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

@login_manager.user_loader
def load_user(user_id):
    return User.select_user(user_id)
