import requests
from flask import current_app

def search_food(query):
    """
    Search for food items using the Nutritionix API
    """
    headers = {
        'x-app-id': current_app.config['NUTRITIONIX_APP_ID'],
        'x-app-key': current_app.config['NUTRITIONIX_API_KEY'],
        'x-remote-user-id': '0'
    }
    
    endpoint = "https://trackapi.nutritionix.com/v2/search/instant"
    params = {
        'query': query,
        'detailed': True
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching for food: {e}")
        return None

def get_nutrition_data(query):
    """
    Get detailed nutrition information for a food item
    """
    headers = {
        'x-app-id': current_app.config['NUTRITIONIX_APP_ID'],
        'x-app-key': current_app.config['NUTRITIONIX_API_KEY'],
        'x-remote-user-id': '0',
        'Content-Type': 'application/json'
    }
    
    endpoint = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    data = {
        'query': query
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting nutrition data: {e}")
        return None