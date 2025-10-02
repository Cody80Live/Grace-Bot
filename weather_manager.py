import requests
import os
from datetime import datetime

class WeatherManager:
    def __init__(self):
        self.api_key = os.environ.get('OPENWEATHER_API_KEY')
        self.city = os.environ.get('WEATHER_CITY', 'Portland')
        self.base_url = 'https://api.openweathermap.org/data/2.5/weather'
    
    def get_weather(self):
        if not self.api_key:
            return {
                'error': 'OPENWEATHER_API_KEY not set',
                'suggestion': 'Set your OpenWeather API key to get weather updates!'
            }
        
        try:
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'imperial'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'city': data['name']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_weather_suggestion(self):
        weather_data = self.get_weather()
        
        if 'error' in weather_data:
            return weather_data
        
        temp = float(weather_data['temp'])
        description = str(weather_data['description'])
        
        suggestion = ""
        
        if 'rain' in description.lower():
            suggestion = f"☔ It's rainy in {weather_data['city']}! Grab an umbrella, babe. Maybe a cozy movie night? 💕"
        elif temp < 50:
            suggestion = f"🧥 It's {temp:.0f}°F - bundle up, love! Perfect weather for hot cocoa ☕"
        elif temp > 80:
            suggestion = f"☀️ Hot day at {temp:.0f}°F! Stay hydrated and maybe hit the pool? 🏊‍♀️"
        else:
            suggestion = f"✨ Nice {temp:.0f}°F weather! Great day to get out there, babe! 😊"
        
        return {
            'weather': weather_data,
            'suggestion': suggestion
        }
