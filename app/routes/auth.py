from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, UserProfile
from app.forms import RegistrationForm, LoginForm, ProfileForm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    # Get existing profile if it exists
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        if user_profile:
            # Update existing profile
            user_profile.age = form.age.data
            user_profile.gender = form.gender.data
            user_profile.height = form.height.data
            user_profile.weight = form.weight.data
            user_profile.activity_level = form.activity_level.data
            user_profile.goal = form.goal.data
        else:
            # Create new profile
            user_profile = UserProfile(
                user_id=current_user.id,
                age=form.age.data,
                gender=form.gender.data,
                height=form.height.data,
                weight=form.weight.data,
                activity_level=form.activity_level.data,
                goal=form.goal.data
            )
            db.session.add(user_profile)
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Pre-populate form with existing data if profile exists
    elif request.method == 'GET' and user_profile:
        form.age.data = user_profile.age
        form.gender.data = user_profile.gender
        form.height.data = user_profile.height
        form.weight.data = user_profile.weight
        form.activity_level.data = user_profile.activity_level
        form.goal.data = user_profile.goal
    
    return render_template('profile.html', title='Profile', form=form)