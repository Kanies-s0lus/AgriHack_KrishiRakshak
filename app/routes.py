from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db


bp = Blueprint('routes', __name__,template_folder='template',static_folder='static')

@bp.route('/')
@bp.route('/home')
def home():
    print("Server Started") 
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))  #LOGGED IN 
        flash('Invalid username or password', 'danger')
    return render_template('login.html')
@bp.route('/logout')
def logout():
    pass


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        retype_password = request.form['password_confirm']

        if password != retype_password:
            flash('Passwords do not match', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('routes.login'))

    return render_template('signup.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

