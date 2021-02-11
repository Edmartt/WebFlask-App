from flask import render_template,session,redirect,url_for,request,flash,current_app
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import Formulario as LoginForm
from .forms import SignupForm
from ..users import User
from ..email import send_email


@auth.route('/login/',methods=['GET','POST'])
def login():
    form=LoginForm()

    '''form.validate_on_submit se encarga de valida todos los campos del formulario
    y además sabe que al envío de los datos el método es post'''
    if form.validate_on_submit():

        '''Asignamos los datos obtenidos de la db al objeto user,buscados con el email
        ingresado para comprobar su existencia'''
        user=User.select_user_by_email(form.email.data)
        next=request.args.get('next')

        '''El objeto de usuario contendrá una tupla con los datos consultados, si no es None y si el password envía en forma de hash, coincide con el password almacenado en la base de datos entonces se obtiene el acceso'''

        if user is not None and user.verify_password(form.password.data):

            '''login_user nos brinda el acceso y nos ayuda a iniciar sesión, y guarda el id de usuario en la sesión del usuario'''
            login_user(user,form.remember_me.data)


            '''next almacena la url a la que se intentó acceder sin autenticarse
            si se logra autenticar, el usuario será redirigido a esta url almacenada en next'''
            next=request.args.get('next')

            '''Si el valor de next es None o si la url guardada en next no inicia con / entonces solo nos debe redirigir a la función asignada o principal. Esta comprobación se hace también por seguridad y evitar que los usuarios sean redirigidos a sitios maliciosos'''
            if next is None or not next.startswith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid Username or Password')
    return render_template('auth/login.html',form=form)

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@auth.route('/register/',methods=["GET","POST"])
def register():
    form=SignupForm()
    if form.validate_on_submit():
        user=User(form.password.data,form.email.data,form.username.data)
        user.password=form.password.data #usamos la funcion de convertir password a hash
        user.insert_user(user.password_hash,user.email,user.username)
        user=User.select_user_by_email(user.email)
        token=user.generate_confirmation_token()
        print(token)
        from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
        s=Serializer(current_app.config['SECRET_KEY'])
        data=s.loads(token.encode('utf-8'))
        print(data.get('confirm'))
        send_email(user.email,'Confirma tu cuenta','auth/email/confirm',user=user,token=token)
        flash('Se te ha enviado un email de confirmación')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>/')
@login_required
def confirm(token):
    print(current_user.confirmed)
    print("Hola")
    user=User.select_user_by_email
    current_app.logger.info('entramos en confirm')
    if current_user.confirmed:
        print("Estado confirmed: ",current_user.confirmed)
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        print("Estado confirmed: ",current_user.confirmed)
        User.change_confirm_state(True)
        print(user.confirmed)
        flash('Has confirmado tu cuenta')
    else:
        flash('El enlace de confirmación no es válido o ha caducado')
    return redirect(url_for('main.index'))


