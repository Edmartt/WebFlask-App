from flask import render_template,session,redirect,url_for,request,flash,current_app
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import Formulario as LoginForm
from .forms import SignupForm
from ..users import User
from ..email import send_email


'''

Gestiona el inicio de sesión, validando los datos que se enviarán, consultando la base de
datos a partir del email dado en el campo correspondiente, si se obtienen resultados
llamamos al método login_user, que recibe el objeto del usuario que iniciará sesión
y el objeto que permitirá guardar la sesión luego de que el usuario haya cerrado el navegador
si así lo desea.

next guarda la url que se desea visitar y que está restringida a usuarios registrados


'''

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.select_user_by_email(form.email.data)
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            next=request.args.get('next')
            if next is None or not next.startswith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid Username or Password')
    return render_template('auth/login.html',form=form)

'''

Termina la sesión de usuario y redirige al index, que a su vez, si ya no se
está autenticado, redirigirá a la página de inicio de sesión.

'''
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


'''

Esta vista gestiona el registro de nuevos usuarios, convierte el password
enviado por el usuario a hash y envía un email al usuario para corroborar que el email
es real y así poder confirmar su cuenta.

userFromDatabase corresponde a un objeto a partir de una consulta por medio del email
registrado y así poder hacer uso del método generate_confirmation_token que requiere de un id
de usuario

'''

@auth.route('/register',methods=["GET","POST"])
def register():
    form=SignupForm()
    if form.validate_on_submit():
        user=User(form.password.data,form.email.data,form.username.data,confirmed=False)
        user.password=form.password.data #usamos la funcion de convertir password a hash
        user.insert_user(user)
        userFromDatabase=User.select_user_by_email(user.email)
        token=userFromDatabase.generate_confirmation_token()
        send_email(user.email,'Confirma tu cuenta','auth/email/confirm',user=user,token=token)
        flash('Se te ha enviado un email de confirmación')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)


'''

Una vez se ha registrado el usuario y recibido el enlace de confirmación, al dar click
este será redirigido a esta vista que cambia el estado del atributo confirmed, haciendo
que el usuario actual tenga una cuenta confirmada y por ende dando acceso total a las funciones
permitidas

La vista recibe un argumento que viene a ser el token generado al registrarse, cuyo contenido
es el id de usuario guardado en la base de datos, con dicho id generamos una instancia y usamos el método para buscar al usuario por medio de dicho id, si la búsqueda da resultadosm se pregunta si el atributo confirmed es verdadero, y si no es así también se comprueba el valor booleano retornado
por el método confirm

'''
@auth.route('/confirm/<token>')
def confirm(token):
    user=User.select_user(User.id_decoder(token))
    if user is not None:
        if user.confirmed:
            flash('Tu cuenta ya ha sido confirmada')
            return redirect(url_for('main.index'))

        if user.confirm(token):
            user.confirmed=True
            user.change_confirm_state(user.id,user.confirmed)
            print(user.confirmed)
            flash('Has confirmado tu cuenta')
        else:
            flash('El enlace de confirmación no es válido o ha caducado')
    else:
        flash('El enlace no es válido')
        redirect(url_for('main.index'))
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed\
            and request.blueprint!='auth'\
            and request.endpoint!='static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirma tu cuenta','auth/email/confirm',user=current_user,token=token)
    flash('Se te ha enviado un nuevo correo electrónico')
    return redirect(url_for('main.index'))


