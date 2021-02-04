from flask import request
from flask_login import UserMixin
from flask_mysqldb import MySQL
from .auth import forms
from app import login_manager,db
from werkzeug.security import generate_password_hash,check_password_hash


class User(UserMixin):

    def __init__(self,password,email):
        self.password=password
        self.email=email


    
    def select_user(self,email):
        cursor=db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email="{}"'.format(email))
        user=cursor.fetchone()
        if user:
            id=user[0]
            return user
    
    def get_id(email):
        cursor=db.connection.cursor()
        cursor.execute('SELECT id FROM users WHERE email="{}"'.format(email))
        user_id=cursor.fetchone()
        if user_id:
            return user_id

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
    return User.get_id(user_id)
