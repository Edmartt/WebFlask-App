from flask import render_template,session,redirect,url_for,request,flash,current_app
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import Formulario as LoginForm
from .forms import SignupForm,PasswordForm,ResetPassword,ChangePassword,ChangeEmail
from ..users import User
from ..email import send_email


@auth.route('/login',methods=['GET','POST'])
def login():
    """Gestiona el inicio de sesión, validando los datos que se enviarán, consultando la base de datos a partir del email dado en el campo correspondiente, 
    si se obtienen resultados llamamos al método login_user, que recibe el objeto del usuario que iniciará sesión y el objeto que permitirá guardar la sesión luego de que el usuario haya cerrado el
    navegador si así lo desea.
    next guarda la url que se desea visitar y que está restringida a usuarios registrados"""

    form=LoginForm()
    if form.validate_on_submit():
        user=User.select_user_by_email(form.email.data)
        if user is not None and user.verify_password(form.password.data):
            next=request.args.get('next')
            login_user(user,form.remember_me.data)
            print(next)
            if next is None or not next.startswith('/'):
                next=url_for('main.index')
                return redirect(next)
            else:
                return redirect(next)
        flash('Invalid Username or Password')
    return render_template('auth/login.html',form=form)

    """
    Termina la sesión de usuario y redirige al index, que a su vez, si ya no se
    está autenticado, redirigirá a la página de inicio de sesión.
    """

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=["GET","POST"])
def register():
    """
    Esta vista gestiona el registro de nuevos usuarios, convierte el password
    enviado por el usuario a hash y envía un email al usuario para corroborar que el email
    es real y así poder confirmar su cuenta.

    userFromDatabase corresponde a un objeto a partir de una consulta por medio del email
    registrado y así poder hacer uso del método generate_confirmation_token que requiere de un id
    de usuario"""

    #Si el usuario está logueado, solo redirigimos al inicio
    if current_user.is_authenticated:
       return redirect(url_for('main.index'))
    else:
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


    """
    Una vez se ha registrado el usuario y recibido el enlace de confirmación, al dar click
    este será redirigido a esta vista que cambia el estado del atributo confirmed, haciendo
    que el usuario actual tenga una cuenta confirmada y por ende dando acceso total a las funciones permitidas
    
    La vista recibe un argumento que viene a ser el token generado al registrarse, cuyo contenido
    es el id de usuario guardado en la base de datos, con dicho id generamos una instancia y usam
    os el método para buscar al usuario por medio de dicho id, si la búsqueda da resultadosm se 
    pregunta si el atributo confirmed es verdadero, y si no es así también se comprueba 
    el valor booleano retornado por el método confirm
    """

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
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    else:
        token=current_user.generate_confirmation_token()
        send_email(current_user.email,'Confirma tu cuenta','auth/email/confirm',user=current_user,token=token)
        flash('Se te ha enviado un nuevo correo electrónico')
        return redirect(url_for('main.index'))



@auth.route('/update_password',methods=['GET','POST'])
@login_required
def update_password():
    pasform=PasswordForm()
    if pasform.validate_on_submit():
        user=User.select_user(current_user.id)
        if user.verify_password(pasforms.current_password.data):
            user.password=pasform.newPassword.data
            user.update_password(current_user.id)
            flash('Password actualizado')
            return redirect(url_for('main.index'))
        else:
            flash('El password no coincide')
    return render_template('update_password.html',form=pasform)



@auth.route('/request_password_reset',methods=['GET','POST'])
def request_password_reset():
    form=ResetPassword()
    if form.validate_on_submit():
        user=User.select_user_by_email(form.email.data)
        token=user.generate_confirmation_token()
        send_email(form.email.data,'Solicitud de reinicio de password','auth/email/reset_password',user=user,token=token)
        print("Token: ",token)
        flash('Se ha enviado un email con instrucciones pare reiniciar tu password')
    return render_template('request_password_reset.html',form=form)



@auth.route('/reset/<token>',methods=["GET","POST"])
def reset(token):
    user=User.select_user(User.id_decoder(token))
    form=ChangePassword()
    if user is not None and user.id==User.id_decoder(token):
        if form.validate_on_submit():
            user.password=form.newPassword.data
            user.update_password(user.id)
            flash('El password ha sido cambiado correctamente')

        return render_template('reset_password.html',form=form,token=token)
    else:
        flash("El token no es válido o ha caducado")
        return redirect(url_for('main.index'))



@auth.route('/change_email',methods=["GET","POST"])
@login_required
def change_email_request():
    form=ChangeEmail()
    user=User.select_user_by_email(form.current_email.data)
    if form.validate_on_submit():
        token=user.generate_confirmation_token()
        user.update_pending_email(form.new_email.data,user.id)
        send_email(form.new_email.data,'Solicitud para cambio de email','auth/email/change_email',user=user,token=token)
        flash('Se ha enviado un email de confirmación para realizar el cambio al nuevo email')
    return render_template('change_email.html',form=form)



@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    user=User.select_user(User.id_decoder(token))
    if user is not None:
        user.update_email(user.id,user.pending_email)
        flash('El email ha sido modificado correctamente')
        return redirect(url_for('main.index'))
    else:
        flash('El token no es válido o ha caducado')
        return redirect(url_for('main.index'))
