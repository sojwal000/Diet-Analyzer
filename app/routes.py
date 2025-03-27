from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, UserProfile, MealLog, DietPlan, Meal, FoodItem
from app.forms import RegistrationForm, LoginForm, ProfileForm, FoodSearchForm, MealLogForm, MealPlanForm
from app.api import search_food, get_nutrition_data
from app.utils import calculate_bmr, calculate_tdee, calculate_macros, generate_meal_plan
from datetime import datetime, date

# Blueprints
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
nutrition = Blueprint('nutrition', __name__)
diet_plan = Blueprint('diet_plan', __name__)

# Main routes
@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get user profile
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    # Get recent meal logs
    recent_logs = MealLog.query.filter_by(user_id=current_user.id).order_by(MealLog.created_at.desc()).limit(5).all()
    
    # Get meal plans
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).all()
    
    # Calculate daily totals if logs exist for today
    today = date.today()
    today_logs = MealLog.query.filter_by(user_id=current_user.id, log_date=today).all()
    
    daily_totals = {
        'calories': sum(log.calories for log in today_logs),
        'protein': sum(log.protein for log in today_logs),
        'carbs': sum(log.carbs for log in today_logs),
        'fats': sum(log.fats for log in today_logs)
    }
    
    # If profile exists, calculate targets
    targets = {}
    if profile:
        bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.gender)
        tdee = calculate_tdee(bmr, profile.activity_level)
        protein_g, carbs_g, fats_g, adjusted_calories = calculate_macros(tdee, profile.goal)
        
        targets = {
            'calories': round(adjusted_calories, 1),
            'protein': round(protein_g, 1),
            'carbs': round(carbs_g, 1),
            'fats': round(fats_g, 1)
        }
    
    return render_template('dashboard.html', title='Dashboard', 
                          profile=profile, recent_logs=recent_logs, 
                          meal_plans=meal_plans, daily_totals=daily_totals,
                          targets=targets)

# Auth routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
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
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        if user_profile:
            user_profile.age = form.age.data
            user_profile.height = form.height.data
            user_profile.weight = form.weight.data
            user_profile.gender = form.gender.data
            user_profile.activity_level = form.activity_level.data
            user_profile.goal = form.goal.data
        else:
            user_profile = UserProfile(
                user_id=current_user.id,
                age=form.age.data,
                height=form.height.data,
                weight=form.weight.data,
                gender=form.gender.data,
                activity_level=form.activity_level.data,
                goal=form.goal.data
            )
            db.session.add(user_profile)
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    
    elif request.method == 'GET' and user_profile:
        form.age.data = user_profile.age
        form.height.data = user_profile.height
        form.weight.data = user_profile.weight
        form.gender.data = user_profile.gender
        form.activity_level.data = user_profile.activity_level
        form.goal.data = user_profile.goal
    
    return render_template('profile.html', title='Profile', form=form)

# Nutrition routes
@nutrition.route('/food-search', methods=['GET', 'POST'])
@login_required
def food_search():
    form = FoodSearchForm()
    results = []
    
    if form.validate_on_submit():
        query = form.query.data
        search_results = search_food(query)
        
        if search_results:
            results = search_results.get('common', []) + search_results.get('branded', [])
    
    return render_template('food_search.html', title='Food Search', form=form, results=results)

@nutrition.route('/food-details/<food_name>')
@login_required
def food_details(food_name):
    nutrition_data = get_nutrition_data(food_name)
    
    if not nutrition_data or 'foods' not in nutrition_data:
        flash('Could not retrieve nutrition data for this food.', 'danger')
        return redirect(url_for('nutrition.food_search'))
    
    food = nutrition_data['foods'][0]
    
    return render_template('food_details.html', title='Food Details', food=food)

@nutrition.route('/log-meal', methods=['GET', 'POST'])
@login_required
def log_meal():
    form = MealLogForm()
    
    if form.validate_on_submit():
        meal_log = MealLog(
            user_id=current_user.id,
            food_name=form.food_name.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fats=form.fats.data,
            meal_type=form.meal_type.data,
            serving_size=form.serving_size.data,
            serving_unit=form.serving_unit.data,
            log_date=date.today()
        )
        db.session.add(meal_log)
        db.session.commit()
        flash('Meal logged successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Pre-fill form if coming from food details
    food_name = request.args.get('food_name')
    calories = request.args.get('calories')
    protein = request.args.get('protein')
    carbs = request.args.get('carbs')
    fats = request.args.get('fats')
    
    if food_name:
        form.food_name.data = food_name
    if calories:
        form.calories.data = float(calories)
    if protein:
        form.protein.data = float(protein)
    if carbs:
        form.carbs.data = float(carbs)
    if fats:
        form.fats.data = float(fats)
    
    return render_template('log_meal.html', title='Log Meal', form=form)

@nutrition.route('/meal-logs')
@login_required
def meal_logs():
    # Get date filter from query params, default to today
    date_str = request.args.get('date')
    if date_str:
        try:
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            log_date = date.today()
    else:
        log_date = date.today()
    
    # Get logs for the selected date
    logs = MealLog.query.filter_by(user_id=current_user.id, log_date=log_date).order_by(MealLog.created_at).all()
    
    # Calculate totals
    totals = {
        'calories': sum(log.calories for log in logs),
        'protein': sum(log.protein for log in logs),
        'carbs': sum(log.carbs for log in logs),
        'fats': sum(log.fats for log in logs)
    }
    
    return render_template('meal_logs.html', title='Meal Logs', logs=logs, log_date=log_date, totals=totals)

@nutrition.route('/delete-log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    log = MealLog.query.get_or_404(log_id)
    
    # Check if the log belongs to the current user
    if log.user_id != current_user.id:
        flash('You do not have permission to delete this log.', 'danger')
        return redirect(url_for('nutrition.meal_logs'))
    
    db.session.delete(log)
    db.session.commit()
    flash('Meal log deleted successfully!', 'success')
    return redirect(url_for('nutrition.meal_logs'))

# Diet Plan routes
@diet_plan.route('/generate-plan')
@login_required
def generate_plan():
    # Check if user has a profile
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        flash('Please complete your profile first to generate a diet plan.', 'warning')
        return redirect(url_for('auth.profile'))
    
    # Calculate nutritional needs
    bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.gender)
    tdee = calculate_tdee(bmr, profile.activity_level)
    protein_g, carbs_g, fats_g, adjusted_calories = calculate_macros(tdee, profile.goal)
    
    # Generate meal plan
    meal_plan_data = generate_meal_plan(adjusted_calories, protein_g, carbs_g, fats_g, profile.goal)
    
    return render_template('generate_plan.html', title='Diet Plan', 
                          profile=profile, meal_plan=meal_plan_data,
                          total_calories=adjusted_calories,
                          total_protein=protein_g,
                          total_carbs=carbs_g,
                          total_fats=fats_g)

@diet_plan.route('/save-plan', methods=['POST'])
@login_required
def save_plan():
    # Get form data
    plan_name = request.form.get('plan_name')
    plan_description = request.form.get('plan_description')
    total_calories = float(request.form.get('total_calories'))
    protein_target = float(request.form.get('protein_target'))
    carbs_target = float(request.form.get('carbs_target'))
    fats_target = float(request.form.get('fats_target'))
    
    # Create meal plan
    meal_plan = MealPlan(
        user_id=current_user.id,
        name=plan_name,
        description=plan_description,
        total_calories=total_calories,
        protein_target=protein_target,
        carbs_target=carbs_target,
        fats_target=fats_target
    )
    db.session.add(meal_plan)
    db.session.flush()  # Get the meal_plan.id without committing
    
    # Create meals and food items
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for meal_type in meal_types:
        meal_calories = float(request.form.get(f'{meal_type}_calories', 0))
        meal_protein = float(request.form.get(f'{meal_type}_protein', 0))
        meal_carbs = float(request.form.get(f'{meal_type}_carbs', 0))
        meal_fats = float(request.form.get(f'{meal_type}_fats', 0))
        
        # Create meal
        meal = Meal(
            meal_plan_id=meal_plan.id,
            name=meal_type.capitalize(),
            meal_type=meal_type
        )
        db.session.add(meal)
        db.session.flush()
        
        # Get food suggestions
        food_items_str = request.form.get(f'{meal_type}_foods', '')
        if food_items_str:
            food_items_list = food_items_str.split('|')
            
            for food_item_str in food_items_list:
                # Simple parsing - in a real app, you'd have a better structure
                food_name = food_item_str.strip()
                
                # Create food item with estimated values
                # In a real app, you'd have actual nutritional data
                food_item = FoodItem(
                    meal_id=meal.id,
                    food_name=food_name,
                    calories=meal_calories / len(food_items_list),
                    protein=meal_protein / len(food_items_list),
                    carbs=meal_carbs / len(food_items_list),
                    fats=meal_fats / len(food_items_list),
                    serving_size=1.0,
                    serving_unit='serving'
                )
                db.session.add(food_item)
    
    db.session.commit()
    flash('Diet plan saved successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@diet_plan.route('/view-plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    meal_plan = MealPlan.query.get_or_404(plan_id)
    
    # Check if the plan belongs to the current user
    if meal_plan.user_id != current_user.id:
        flash('You do not have permission to view this plan.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get meals and food items
    meals = Meal.query.filter_by(meal_plan_id=plan_id).all()
    
    meal_data = {}
    for meal in meals:
        food_items = FoodItem.query.filter_by(meal_id=meal.id).all()
        meal_data[meal.meal_type] = {
            'name': meal.name,
            'food_items': food_items,
            'calories': sum(item.calories for item in food_items),
            'protein': sum(item.protein for item in food_items),
            'carbs': sum(item.carbs for item in food_items),
            'fats': sum(item.fats for item in food_items)
        }
    
    return render_template('view_plan.html', title='View Diet Plan', 
                          meal_plan=meal_plan, meal_data=meal_data)

@diet_plan.route('/delete-plan/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    meal_plan = MealPlan.query.get_or_404(plan_id)
    
    # Check if the plan belongs to the current user
    if meal_plan.user_id != current_user.id:
        flash('You do not have permission to delete this plan.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get all meals
    meals = Meal.query.filter_by(meal_plan_id=plan_id).all()
    
    # Delete food items and meals
    for meal in meals:
        FoodItem.query.filter_by(meal_id=meal.id).delete()
    
    Meal.query.filter_by(meal_plan_id=plan_id).delete()
    
    # Delete meal plan
    db.session.delete(meal_plan)
    db.session.commit()
    
    flash('Diet plan deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))