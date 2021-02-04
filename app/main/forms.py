from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class Formulario(FlaskForm):
    name=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    button=SubmitField('Ingresar')
