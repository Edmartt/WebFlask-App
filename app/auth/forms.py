from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email,Length
from flask_wtf import FlaskForm

class Formulario(FlaskForm):
    email=StringField('Username',validators=[DataRequired(),Email(),Length(1,64)])
    password=PasswordField('Passsword',validators=[DataRequired()])
    button=SubmitField('Ingresar')
    remember_me=BooleanField('Mantener Sesión Iniciada')

