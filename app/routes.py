from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User,Crop
from app import db
from datetime import datetime


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
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.login'))


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        retype_password = request.form['password_confirm']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not latitude or not longitude:
            flash('Field location is required.', 'danger')
            return render_template('signup.html')
        if password != retype_password:
            flash('Passwords do not match', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
        else:
            new_user = User(
                username=username,
                latitude=float(latitude),
                longitude=float(longitude)
                )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('routes.login'))

    return render_template('signup.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    crops = Crop.query.filter_by(user_id=current_user.id).order_by(Crop.date_planted.desc()).all()

    crop_data = []
    for crop in crops:
        age_days = (datetime.utcnow().date() - crop.date_planted).days
        crop_data.append({
            'id': crop.id,
            'name': crop.name,
            'soil_type': crop.soil_type,
            'age_days': age_days
        })

    return render_template('dashboard.html', crops=crop_data)

@bp.route('/add_crop', methods=['GET', 'POST'])
@login_required
def add_crop():
    if request.method == 'POST':
        name = request.form['name']
        date_str = request.form['date_planted']
        soil_type = request.form['soil_type']

        try:
            date_planted = datetime.strptime(date_str, '%Y-%m-%d').date()
            new_crop = Crop(
                user_id = current_user.id,
                name = name,
                date_planted =date_planted,
                soil_type=soil_type
            )
            db.session.add(new_crop)
            db.session.commit()
            flash('Crop added successfully!', 'success')
            return redirect(url_for('routes.dashboard'))
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
    return render_template('add_crop.html')

@bp.route('/delete_crop/<int:crop_id>', methods=['POST'])
@login_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.user_id != current_user.id:
        flash('You cannot delete this crop.', 'danger')
        return redirect(url_for('routes.dashboard'))

    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully!', 'success')
    return redirect(url_for('routes.dashboard'))
