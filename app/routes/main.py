from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import UserProfile, MealLog, DietPlan
from app.utils import get_daily_totals, calculate_bmr, calculate_tdee, calculate_macros

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get user profile
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    # Default values if no profile exists
    daily_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}
    targets = {'calories': 2000, 'protein': 150, 'carbs': 200, 'fats': 70}
    recent_logs = []
    meal_plans = []
    
    if profile:
        # Calculate nutrition targets
        bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.gender)
        tdee = calculate_tdee(bmr, profile.activity_level)
        protein_g, carbs_g, fats_g, adjusted_calories = calculate_macros(tdee, profile.goal)
        
        targets = {
            'calories': adjusted_calories,
            'protein': protein_g,
            'carbs': carbs_g,
            'fats': fats_g
        }
        
        # Get today's meal logs
        today = datetime.now().date()
        today_logs = MealLog.query.filter_by(
            user_id=current_user.id, 
            log_date=today
        ).all()
        
        # Calculate daily totals
        daily_totals = get_daily_totals(today_logs)
        
        # Get recent meal logs (last 5)
        recent_logs = MealLog.query.filter_by(
            user_id=current_user.id
        ).order_by(MealLog.created_at.desc()).limit(5).all()
        
        # Get user's diet plans
        meal_plans = DietPlan.query.filter_by(
            user_id=current_user.id
        ).order_by(DietPlan.created_at.desc()).limit(3).all()
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          profile=profile,
                          daily_totals=daily_totals,
                          targets=targets,
                          recent_logs=recent_logs,
                          meal_plans=meal_plans)

@main.route('/about')
def about():
    return render_template('about.html', title='About')