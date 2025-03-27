from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False)
    meal_logs = db.relationship('MealLog', backref='user', lazy=True)
    diet_plans = db.relationship('DietPlan', backref='user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    activity_level = db.Column(db.String(20), nullable=False)
    goal = db.Column(db.String(20), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"UserProfile(User: '{self.user_id}', Goal: '{self.goal}')"

class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    serving_size = db.Column(db.Float, nullable=False)
    serving_unit = db.Column(db.String(20), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    log_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"MealLog('{self.food_name}', {self.calories} cal, {self.log_date})"

class DietPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_calories = db.Column(db.Float, nullable=False)
    protein_target = db.Column(db.Float, nullable=False)
    carbs_target = db.Column(db.Float, nullable=False)
    fats_target = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    meals = db.relationship('PlanMeal', backref='diet_plan', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"DietPlan('{self.name}', {self.total_calories} cal)"

class PlanMeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plan.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    
    # Relationships
    food_items = db.relationship('PlanFoodItem', backref='plan_meal', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"PlanMeal('{self.meal_type}', {self.calories} cal)"

class PlanFoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_meal_id = db.Column(db.Integer, db.ForeignKey('plan_meal.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False, default=0)
    
    def __repr__(self):
        return f"PlanFoodItem('{self.food_name}')"