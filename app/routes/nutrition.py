from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import requests
from app import db
from app.models import MealLog
from app.forms import FoodSearchForm, MealLogForm
from app.utils import get_daily_totals, parse_date
import os

nutrition = Blueprint('nutrition', __name__)

# Nutritionix API credentials
NUTRITIONIX_APP_ID = os.environ.get('NUTRITIONIX_APP_ID', 'f5a290e2')
NUTRITIONIX_API_KEY = os.environ.get('NUTRITIONIX_API_KEY', 'be4c8667bc8289c9e52cc0c205e96629')

# Update the food_search function to better handle API responses and errors

@nutrition.route('/food-search', methods=['GET', 'POST'])
@login_required
def food_search():
    form = FoodSearchForm()
    results = []
    
    if form.validate_on_submit():
        query = form.query.data
        
        # Call Nutritionix API
        headers = {
            'x-app-id': NUTRITIONIX_APP_ID,
            'x-app-key': NUTRITIONIX_API_KEY,
            'x-remote-user-id': '0',
            'Content-Type': 'application/json'
        }
        
        data = {
            'query': query
        }
        
        try:
            # Print API request details for debugging
            print(f"Sending request to Nutritionix API with query: {query}")
            print(f"API ID: {NUTRITIONIX_APP_ID}")
            print(f"API Key: {NUTRITIONIX_API_KEY[:5]}...")
            
            response = requests.post(
                'https://trackapi.nutritionix.com/v2/natural/nutrients',
                headers=headers,
                json=data
            )
            
            # Print response status and content for debugging
            print(f"API Response Status: {response.status_code}")
            print(f"API Response Content: {response.text[:200]}...")  # Print first 200 chars
            
            if response.status_code == 200:
                response_data = response.json()
                results = response_data.get('foods', [])
                
                if not results:
                    flash('No foods found for your query. Try a different search term.', 'info')
            else:
                error_message = f"Error from Nutritionix API: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_message += f" - {error_data['message']}"
                except:
                    pass
                
                flash(error_message, 'danger')
                print(error_message)
        except Exception as e:
            error_message = f"Error connecting to nutrition API: {str(e)}"
            flash(error_message, 'danger')
            print(error_message)
    
    return render_template('food_search.html', title='Food Search', form=form, results=results)

@nutrition.route('/food-details/<food_name>')
@login_required
def food_details(food_name):
    # Call Nutritionix API to get food details
    headers = {
        'x-app-id': NUTRITIONIX_APP_ID,
        'x-app-key': NUTRITIONIX_API_KEY,
        'x-remote-user-id': '0'
    }
    
    data = {
        'query': food_name,
        'detailed': True
    }
    
    try:
        response = requests.post(
            'https://trackapi.nutritionix.com/v2/natural/nutrients',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            foods = response.json().get('foods', [])
            if foods:
                food = foods[0]
                return render_template('food_details.html', title='Food Details', food=food)
        
        flash('Food details not found.', 'warning')
        return redirect(url_for('nutrition.food_search'))
    
    except Exception as e:
        flash(f'Error connecting to nutrition API: {str(e)}', 'danger')
        return redirect(url_for('nutrition.food_search'))

@nutrition.route('/log-meal', methods=['GET', 'POST'])
@login_required
def log_meal():
    form = MealLogForm()
    
    # Pre-populate form with data from URL parameters if available
    if request.method == 'GET':
        form.food_name.data = request.args.get('food_name', '')
        form.calories.data = float(request.args.get('calories', 0))
        form.protein.data = float(request.args.get('protein', 0))
        form.carbs.data = float(request.args.get('carbs', 0))
        form.fats.data = float(request.args.get('fats', 0))
        form.serving_size.data = 1.0
        form.serving_unit.data = 'serving'
        form.log_date.data = datetime.now().date()
    
    if form.validate_on_submit():
        meal_log = MealLog(
            user_id=current_user.id,
            food_name=form.food_name.data,
            serving_size=form.serving_size.data,
            serving_unit=form.serving_unit.data,
            meal_type=form.meal_type.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fats=form.fats.data,
            log_date=form.log_date.data
        )
        
        db.session.add(meal_log)
        db.session.commit()
        
        flash(f'Successfully logged {form.food_name.data}!', 'success')
        return redirect(url_for('nutrition.meal_logs'))
    
    return render_template('log_meal.html', title='Log Meal', form=form)

# Fix the meal_logs route to properly handle date parameters and timedelta

@nutrition.route('/meal-logs')
@login_required
def meal_logs():
    # Get date from query parameter or use today
    date_str = request.args.get('date')
    
    # Import timedelta directly in the function to avoid any import issues
    from datetime import timedelta
    
    try:
        if date_str:
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            log_date = datetime.now().date()
    except ValueError:
        log_date = datetime.now().date()
        flash('Invalid date format. Showing today\'s logs.', 'warning')
    
    # Get meal logs for the specified date
    logs = MealLog.query.filter_by(
        user_id=current_user.id,
        log_date=log_date
    ).order_by(MealLog.meal_type).all()
    
    # Calculate daily totals
    totals = get_daily_totals(logs)
    
    return render_template('meal_logs.html', 
                          title='Meal Logs',
                          logs=logs,
                          log_date=log_date,
                          totals=totals,
                          timedelta=timedelta)  # Pass timedelta directly

@nutrition.route('/delete-log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    log = MealLog.query.get_or_404(log_id)
    
    # Check if the log belongs to the current user
    if log.user_id != current_user.id:
        flash('You do not have permission to delete this log.', 'danger')
        return redirect(url_for('nutrition.meal_logs'))
    
    log_date = log.log_date
    db.session.delete(log)
    db.session.commit()
    
    flash('Meal log deleted successfully!', 'success')
    return redirect(url_for('nutrition.meal_logs', date=log_date.strftime('%Y-%m-%d')))