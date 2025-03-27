from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms import IntegerField, FloatField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=18, max=100)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    height = FloatField('Height', validators=[DataRequired(), NumberRange(min=100, max=250)])
    weight = FloatField('Weight', validators=[DataRequired(), NumberRange(min=30, max=300)])
    activity_level = SelectField('Activity Level', 
                                choices=[
                                    ('sedentary', 'Sedentary (little or no exercise)'),
                                    ('lightly_active', 'Lightly Active (light exercise 1-3 days/week)'),
                                    ('moderately_active', 'Moderately Active (moderate exercise 3-5 days/week)'),
                                    ('very_active', 'Very Active (hard exercise 6-7 days/week)'),
                                    ('extra_active', 'Extra Active (very hard exercise & physical job or training twice a day)')
                                ], 
                                validators=[DataRequired()])
    goal = SelectField('Goal', 
                      choices=[
                          ('weight_loss', 'Weight Loss'),
                          ('maintenance', 'Maintenance'),
                          ('muscle_gain', 'Muscle Gain')
                      ], 
                      validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class FoodSearchForm(FlaskForm):
    query = StringField('Search for a food', validators=[DataRequired()])
    submit = SubmitField('Search')

class MealLogForm(FlaskForm):
    food_name = StringField('Food Name', validators=[DataRequired()])
    serving_size = FloatField('Serving Size', validators=[DataRequired(), NumberRange(min=0.1)])
    serving_unit = StringField('Serving Unit', validators=[DataRequired()])
    meal_type = SelectField('Meal Type', 
                           choices=[
                               ('breakfast', 'Breakfast'),
                               ('lunch', 'Lunch'),
                               ('dinner', 'Dinner'),
                               ('snack', 'Snack')
                           ], 
                           validators=[DataRequired()])
    calories = FloatField('Calories', validators=[DataRequired(), NumberRange(min=0)])
    protein = FloatField('Protein (g)', validators=[DataRequired(), NumberRange(min=0)])
    carbs = FloatField('Carbs (g)', validators=[DataRequired(), NumberRange(min=0)])
    fats = FloatField('Fats (g)', validators=[DataRequired(), NumberRange(min=0)])
    log_date = DateField('Date', format='%Y-%m-%d')
    submit = SubmitField('Log Meal')

class DietPlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Plan')