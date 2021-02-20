from flask import render_template,session,redirect,url_for,request,flash,current_app
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import Formulario as LoginForm
from .forms import SignupForm
from ..users import User
from ..email import send_email


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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=["GET","POST"])
def register():
    form=SignupForm()
    if form.validate_on_submit():
        user=User(form.password.data,form.email.data,form.username.data,confirmed=False)
        user.password=form.password.data #usamos la funcion de convertir password a hash
        user.insert_user(user.password_hash,user.email,user.username,confirmed=False)
        userFromDatabase=User.select_user_by_email(user.email)
        token=userFromDatabase.generate_confirmation_token()
        send_email(user.email,'Confirma tu cuenta','auth/email/confirm',user=user,token=token)
        flash('Se te ha enviado un email de confirmación')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    id=User.id_decoder(token)
    print(id)
    user=User.select_user(id)
    if current_user.confirmed:
        print("Estado confirmed: ",current_user.confirmed)
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        print(current_user.confirmed)
        user.confirmed=True
        user.change_confirm_state(id,user.confirmed)
        print(user.confirmed)
        flash('Has confirmado tu cuenta')
    else:
        flash('El enlace de confirmación no es válido o ha caducado')
    return redirect(url_for('main.index'))


