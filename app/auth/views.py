from flask import render_template,session,redirect,url_for,request,flash
from flask_login import login_user,logout_user,login_required
from . import auth
from .forms import Formulario as LoginForm
from ..users import User

@auth.route('/login/',methods=['GET','POST'])
def login():
    form=LoginForm() 
    if form.validate_on_submit():
        user=User.select_user()
        print('user is None?',user==None)
        print('Verify password is: ',user.verify_password(form.password.data))
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            next=request.args.get('next')
            print(next)
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
