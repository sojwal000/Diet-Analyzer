# Diet Analyzer

A web application that helps users track their nutrition, analyze their diet, and generate personalized meal plans.

## Features

- Food search with nutritional information
- Daily meal logging and tracking
- Personalized diet plan generation
- Nutritional analytics and progress tracking
- User profile management
- Responsive dark-themed UI

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sojwal000/Diet-Analyzer.git
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
NUTRITIONIX_APP_ID=your_nutritionix_app_id
NUTRITIONIX_API_KEY=your_nutritionix_api_key
```

5. Initialize the database:
```bash
flask db upgrade
```

## Running the Application

1. Start the Flask server:
```bash
python run.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### 1. Account Creation
- Click "Register" to create a new account
- Fill in your profile details including age, gender, height, weight, and activity level

### 2. Food Search
- Navigate to "Food Search" in the sidebar
- Enter food items in natural language (e.g., "1 apple" or "grilled chicken breast")
- View detailed nutritional information for each food item

### 3. Logging Meals
- Search for a food item
- Click "Log This Food" to add it to your meal log
- Select meal type (breakfast, lunch, dinner, snack)
- Adjust serving size if needed
- Submit to log the meal

### 4. Viewing Meal Logs
- Go to "Meal Logs" to view your food diary
- Navigate between dates using the date selector
- View daily totals for calories and macronutrients
- Delete individual meal entries if needed

### 5. Diet Plans
- Visit "Diet Plans" to generate personalized meal plans
- View recommended daily intake based on your profile
- Track your progress towards daily goals

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Nutritionix API for providing nutritional data
- Flask framework and its contributors
- Bootstrap for the responsive UI components
