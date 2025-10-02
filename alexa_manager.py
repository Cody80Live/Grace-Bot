import os
import requests
from datetime import datetime

class AlexaManager:
    def __init__(self):
        self.api_endpoint = os.environ.get('ALEXA_API_ENDPOINT')
        self.api_key = os.environ.get('ALEXA_API_KEY')
        
        if not self.api_endpoint:
            print("⚠️ Alexa not configured: For full control, set up AWS Lambda Smart Home Skill")
    
    def control_light(self, device_name, action='turn_on', brightness=None):
        if not self.api_endpoint:
            return {
                'error': 'Alexa not configured',
                'setup_instructions': '''To control Alexa devices:
                
Option 1 - AWS Lambda Smart Home Skill (Full Control):
1. Create Smart Home Skill at developer.amazon.com/alexa
2. Deploy Lambda function with Python handler
3. Set ALEXA_API_ENDPOINT to your backend API
4. Configure OAuth account linking

Option 2 - Local Device Control (Limited):
Set up device-specific libraries:
- Philips Hue: pip install phue
- Yeelight: pip install yeelight  
- Smart Home Hub: Use Home Assistant REST API

Option 3 - Simple Commands:
For basic control, you can send commands to specific devices if they have APIs'''
            }
        
        try:
            payload = {
                'device': device_name,
                'action': action
            }
            
            if brightness is not None:
                payload['brightness'] = brightness
            
            response = requests.post(
                f"{self.api_endpoint}/control",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            
            return response.json()
        
        except Exception as e:
            return {'error': str(e)}
    
    def turn_on_lights(self, location='living room'):
        result = self.control_light(f'{location} light', 'turn_on')
        return result
    
    def turn_off_lights(self, location='living room'):
        result = self.control_light(f'{location} light', 'turn_off')
        return result
    
    def set_brightness(self, location='living room', level=50):
        result = self.control_light(f'{location} light', 'set_brightness', brightness=level)
        return result
    
    def game_time_lights(self):
        results = []
        results.append(self.control_light('living room light', 'turn_on', brightness=80))
        results.append(self.control_light('bedroom light', 'turn_off'))
        
        return {
            'action': 'game_time_setup',
            'results': results,
            'message': 'Game time lights set! Living room bright, bedroom off 🎮'
        }
    
    def get_status(self):
        if not self.api_endpoint:
            return {
                'status': 'not_configured',
                'message': 'Alexa integration needs AWS Lambda Smart Home Skill setup'
            }
        
        return {
            'status': 'configured',
            'endpoint': self.api_endpoint,
            'message': 'Alexa ready to control your devices! 🔌'
        }
