from flask import render_template,session,redirect,url_for,request,flash
from . import main
from .forms import Formulario
from flask_login import login_required

@main.route('/')
@login_required

def index():
    form=Formulario()
#    if form.validate_on_submit():
#        old_name=session.get('name')
#        if old_name is not None and old_name!=form.name.data:
#            flash('Has cambiado tu nombre de usuario')
#        session['name']=form.name.data
#        return redirect(url_for('.index'))
    return render_template('index.html')
