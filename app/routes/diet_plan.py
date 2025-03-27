from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app import db
from app.models import UserProfile, DietPlan, PlanMeal, PlanFoodItem
from app.forms import DietPlanForm
from app.utils import calculate_bmr, calculate_tdee, calculate_macros, generate_meal_plan

diet_plan = Blueprint('diet_plan', __name__)

@diet_plan.route('/generate-plan')
@login_required
def generate_plan():
    # Get user profile
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        flash('Please complete your profile first to generate a diet plan.', 'warning')
        return redirect(url_for('auth.profile'))
    
    # Calculate nutrition targets
    bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.gender)
    tdee = calculate_tdee(bmr, profile.activity_level)
    protein_g, carbs_g, fats_g, adjusted_calories = calculate_macros(tdee, profile.goal)
    
    # Generate meal plan
    meal_plan = generate_meal_plan(adjusted_calories, protein_g, carbs_g, fats_g, profile.goal)
    
    return render_template('generate_plan.html',
                          title='Generate Diet Plan',
                          profile=profile,
                          total_calories=adjusted_calories,
                          total_protein=protein_g,
                          total_carbs=carbs_g,
                          total_fats=fats_g,
                          meal_plan=meal_plan)

@diet_plan.route('/save-plan', methods=['POST'])
@login_required
def save_plan():
    # Create new diet plan
    plan = DietPlan(
        user_id=current_user.id,
        name=request.form.get('plan_name'),
        description=request.form.get('plan_description'),
        total_calories=float(request.form.get('total_calories')),
        protein_target=float(request.form.get('protein_target')),
        carbs_target=float(request.form.get('carbs_target')),
        fats_target=float(request.form.get('fats_target'))
    )
    
    db.session.add(plan)
    db.session.commit()
    
    # Add meals to the plan
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for meal_type in meal_types:
        # Check if this meal type exists in the form
        if f'{meal_type}_calories' in request.form:
            # Create meal
            meal = PlanMeal(
                diet_plan_id=plan.id,
                meal_type=meal_type,
                name=meal_type.capitalize(),
                calories=float(request.form.get(f'{meal_type}_calories')),
                protein=float(request.form.get(f'{meal_type}_protein')),
                carbs=float(request.form.get(f'{meal_type}_carbs')),
                fats=float(request.form.get(f'{meal_type}_fats'))
            )
            
            db.session.add(meal)
            db.session.commit()
            
            # Add food items to the meal
            foods_str = request.form.get(f'{meal_type}_foods', '')
            if foods_str:
                foods = foods_str.split('|')
                for food in foods:
                    food_item = PlanFoodItem(
                        plan_meal_id=meal.id,
                        food_name=food
                    )
                    db.session.add(food_item)
    
    db.session.commit()
    flash('Diet plan saved successfully!', 'success')
    return redirect(url_for('diet_plan.view_plan', plan_id=plan.id))

@diet_plan.route('/view-plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    # Get the diet plan
    meal_plan = DietPlan.query.get_or_404(plan_id)
    
    # Check if the plan belongs to the current user
    if meal_plan.user_id != current_user.id:
        flash('You do not have permission to view this plan.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get all meals for this plan
    meals = PlanMeal.query.filter_by(diet_plan_id=plan_id).all()
    
    # Organize meal data
    meal_data = {}
    for meal in meals:
        food_items = PlanFoodItem.query.filter_by(plan_meal_id=meal.id).all()
        meal_data[meal.meal_type] = {
            'name': meal.name,
            'calories': meal.calories,
            'protein': meal.protein,
            'carbs': meal.carbs,
            'fats': meal.fats,
            'food_items': food_items
        }
    
    return render_template('view_plan.html',
                          title='View Diet Plan',
                          meal_plan=meal_plan,
                          meal_data=meal_data)

@diet_plan.route('/delete-plan/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = DietPlan.query.get_or_404(plan_id)
    
    # Check if the plan belongs to the current user
    if plan.user_id != current_user.id:
        flash('You do not have permission to delete this plan.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(plan)
    db.session.commit()
    
    flash('Diet plan deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))