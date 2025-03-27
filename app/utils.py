from datetime import date, datetime, timedelta
import random

def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation
    
    weight: in kg
    height: in cm
    age: in years
    gender: 'male' or 'female'
    """
    if gender.lower() == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure
    
    activity_level: sedentary, lightly_active, moderately_active, very_active, extra_active
    """
    activity_multipliers = {
        'sedentary': 1.2,  # Little or no exercise
        'lightly_active': 1.375,  # Light exercise/sports 1-3 days/week
        'moderately_active': 1.55,  # Moderate exercise/sports 3-5 days/week
        'very_active': 1.725,  # Hard exercise/sports 6-7 days/week
        'extra_active': 1.9  # Very hard exercise, physical job or training twice a day
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return bmr * multiplier

def calculate_macros(tdee, goal):
    """
    Calculate macronutrient targets based on TDEE and goal
    
    goal: weight_loss, maintenance, muscle_gain
    
    Returns: (protein_g, carbs_g, fats_g, adjusted_calories)
    """
    # Adjust calories based on goal
    if goal == 'weight_loss':
        adjusted_calories = tdee * 0.8  # 20% deficit
    elif goal == 'muscle_gain':
        adjusted_calories = tdee * 1.1  # 10% surplus
    else:  # maintenance
        adjusted_calories = tdee
    
    # Calculate macros
    if goal == 'weight_loss':
        # Higher protein for weight loss
        protein_ratio = 0.35  # 35% of calories from protein
        fat_ratio = 0.3  # 30% of calories from fat
        carb_ratio = 0.35  # 35% of calories from carbs
    elif goal == 'muscle_gain':
        # Higher protein and carbs for muscle gain
        protein_ratio = 0.3  # 30% of calories from protein
        fat_ratio = 0.25  # 25% of calories from fat
        carb_ratio = 0.45  # 45% of calories from carbs
    else:  # maintenance
        # Balanced macros
        protein_ratio = 0.3  # 30% of calories from protein
        fat_ratio = 0.3  # 30% of calories from fat
        carb_ratio = 0.4  # 40% of calories from carbs
    
    # Convert ratios to grams
    # Protein: 4 calories per gram
    # Carbs: 4 calories per gram
    # Fat: 9 calories per gram
    protein_g = (adjusted_calories * protein_ratio) / 4
    carbs_g = (adjusted_calories * carb_ratio) / 4
    fats_g = (adjusted_calories * fat_ratio) / 9
    
    return protein_g, carbs_g, fats_g, adjusted_calories

def generate_meal_plan(total_calories, protein_g, carbs_g, fats_g, goal):
    """
    Generate a simple meal plan based on nutritional targets
    
    Returns a dictionary with meal types and their nutritional breakdown
    """
    # Define meal distribution based on goal
    if goal == 'weight_loss':
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.3,
            'snack': 0.1
        }
    elif goal == 'muscle_gain':
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.3,
            'dinner': 0.3,
            'snack': 0.15
        }
    else:  # maintenance
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.3,
            'dinner': 0.3,
            'snack': 0.15
        }
    
    # Food suggestions for each meal type
    food_suggestions = {
        'breakfast': [
            'Oatmeal with berries and nuts',
            'Greek yogurt with honey and granola',
            'Whole grain toast with avocado and eggs',
            'Protein smoothie with banana and spinach',
            'Vegetable omelette with whole grain toast'
        ],
        'lunch': [
            'Grilled chicken salad with olive oil dressing',
            'Quinoa bowl with roasted vegetables and tofu',
            'Turkey and avocado wrap with mixed greens',
            'Lentil soup with whole grain bread',
            'Tuna salad sandwich on whole grain bread'
        ],
        'dinner': [
            'Grilled salmon with roasted vegetables',
            'Lean beef stir-fry with brown rice',
            'Baked chicken with sweet potato and broccoli',
            'Vegetable and bean chili',
            'Whole grain pasta with turkey meatballs and tomato sauce'
        ],
        'snack': [
            'Apple with almond butter',
            'Protein bar',
            'Handful of mixed nuts',
            'Greek yogurt with berries',
            'Cottage cheese with pineapple',
            'Hummus with carrot sticks'
        ]
    }
    
    # Create meal plan
    meal_plan = {}
    
    for meal_type, ratio in meal_distribution.items():
        meal_calories = total_calories * ratio
        meal_protein = protein_g * ratio
        meal_carbs = carbs_g * ratio
        meal_fats = fats_g * ratio
        
        # Select random food suggestions for this meal
        if meal_type == 'snack':
            num_suggestions = 2
        else:
            num_suggestions = 3
            
        foods = random.sample(food_suggestions[meal_type], min(num_suggestions, len(food_suggestions[meal_type])))
        
        meal_plan[meal_type] = {
            'calories': meal_calories,
            'protein': meal_protein,
            'carbs': meal_carbs,
            'fats': meal_fats,
            'foods': foods
        }
    
    return meal_plan

# Update the get_daily_totals function to handle empty logs

def get_daily_totals(meal_logs):
    """
    Calculate daily nutrition totals from meal logs
    """
    totals = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fats': 0
    }
    
    if not meal_logs:
        return totals
    
    for log in meal_logs:
        totals['calories'] += log.calories if log.calories else 0
        totals['protein'] += log.protein if log.protein else 0
        totals['carbs'] += log.carbs if log.carbs else 0
        totals['fats'] += log.fats if log.fats else 0
    
    return totals

def get_date_range(start_date=None, days=7):
    """
    Get a range of dates ending at the specified date
    
    start_date: datetime.date object, defaults to today
    days: number of days to include
    
    Returns a list of date objects
    """
    if start_date is None:
        start_date = date.today()
    
    date_range = []
    for i in range(days - 1, -1, -1):
        date_range.append(start_date - timedelta(days=i))
    
    return date_range

def format_date(date_obj):
    """Format date for display"""
    return date_obj.strftime('%Y-%m-%d')

def parse_date(date_str):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return date.today()