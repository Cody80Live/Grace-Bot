import os
import requests
from datetime import datetime

class WyzeManager:
    def __init__(self, memory_manager=None, ai_brain=None, notification_manager=None):
        self.memory_manager = memory_manager
        self.ai_brain = ai_brain
        self.notification_manager = notification_manager
        self.email = os.environ.get('WYZE_EMAIL')
        self.password = os.environ.get('WYZE_PASSWORD')
        self.access_token = os.environ.get('WYZE_ACCESS_TOKEN')
        
        if not any([self.email, self.access_token]):
            print("⚠️ Wyze not configured: Set WYZE_EMAIL/WYZE_PASSWORD or WYZE_ACCESS_TOKEN")
    
    def check_camera_events(self):
        if not (self.email or self.access_token):
            return {
                'error': 'Wyze not configured',
                'setup_instructions': 'Set environment variables: WYZE_EMAIL and WYZE_PASSWORD, or WYZE_ACCESS_TOKEN'
            }
        
        try:
            cameras_status = []
            
            camera_1 = {
                'name': os.environ.get('WYZE_CAMERA_1_NAME', 'Front Door'),
                'mac': os.environ.get('WYZE_CAMERA_1_MAC', ''),
                'status': 'not_configured'
            }
            
            if camera_1['mac']:
                cameras_status.append(camera_1)
            
            if not cameras_status:
                return {
                    'message': 'No cameras configured. Add WYZE_CAMERA_1_NAME and WYZE_CAMERA_1_MAC to environment',
                    'cameras': []
                }
            
            return {
                'cameras': cameras_status,
                'message': 'Wyze integration ready - configure camera MACs to monitor'
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def simulate_motion_event(self, camera_name='Front Door'):
        if self.ai_brain and self.notification_manager:
            decision = self.ai_brain.analyze_camera_event(
                camera_name,
                'motion_detected',
                datetime.now().strftime('%I:%M %p')
            )
            
            if decision.get('alert', False):
                message = decision.get('message', f'📹 Motion detected on {camera_name}!')
                self.notification_manager.send_notification(message)
                return {'alerted': True, 'message': message}
        
        return {'alerted': False, 'message': 'Wyze camera monitoring active'}
