from flask import render_template,session,redirect,url_for,request,flash
from . import main
from .forms import Formulario
from flask_login import login_required
@main.route('/')
@login_required
def index():
    return render_template('index.html')
