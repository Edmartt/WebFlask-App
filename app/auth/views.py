from flask import render_template,session,redirect,url_for,request,flash
from flask_login import login_user,logout_user,login_required
from . import auth
from .forms import Formulario as LoginForm
from ..users import User

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
        print(next)

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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))
