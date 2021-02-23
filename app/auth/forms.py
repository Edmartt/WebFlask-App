from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email,Length,Regexp,EqualTo
from flask_wtf import FlaskForm
from wtforms import ValidationError
from ..users import User

class Formulario(FlaskForm):
    email=StringField('Username',validators=[DataRequired(),Email(),Length(1,64)])
    password=PasswordField('Passsword',validators=[DataRequired()])
    button=SubmitField('Ingresar')
    remember_me=BooleanField('Mantener Sesión Iniciada')

class SignupForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Los nombres de usuarios solo pueden contener letras, números, puntos o guiones bajos')])
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='El password debe coincidir')])
    password2=PasswordField('Confirmar Password',validators=[DataRequired()])
    submit=SubmitField('Registrarse')

    def validate_email(self,field):
        if User.select_user_by_email(email=field.data.lower()):
            raise ValidationError('Este email ya está registrado')

    def validate_username(self,field):
        if User.select_user_by_username(username=field.data):
            raise ValidationError('Este nombre de usuario ya está registrado')

class PasswordForm(FlaskForm):
    current_password=PasswordField('Password',validators=[DataRequired()])
    newPassword=PasswordField('Nuevo Password',validators=[DataRequired()])
    submit=SubmitField('Actualizar')

