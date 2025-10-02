from twilio.rest import Client
from modules.replit_connector import ReplitConnector
import os

class NotificationManager:
    def __init__(self):
        self.phone_number = os.environ.get('USER_PHONE_NUMBER')
        self.twilio_client = None
        self.from_number = None
        self._init_twilio()
    
    def _init_twilio(self):
        try:
            creds = ReplitConnector.get_twilio_credentials()
            self.twilio_client = Client(
                creds['api_key'],
                creds['api_key_secret'],
                creds['account_sid']
            )
            self.from_number = creds.get('phone_number')
            print(f"✅ Twilio initialized with phone: {self.from_number}")
        except Exception as e:
            print(f"⚠️ Twilio initialization warning: {e}")
    
    def send_notification(self, message, force_sms=False):
        print(f"📱 Notification: {message}")
        
        if not self.phone_number:
            print("⚠️ USER_PHONE_NUMBER not set - skipping SMS")
            return {'success': True, 'method': 'console', 'message': message}
        
        if self.twilio_client and self.from_number and force_sms:
            try:
                msg = self.twilio_client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=self.phone_number
                )
                print(f"✅ SMS sent: {msg.sid}")
                return {'success': True, 'method': 'sms', 'sid': msg.sid}
            except Exception as e:
                print(f"❌ SMS error: {e}")
                return {'success': False, 'error': str(e)}
        
        return {'success': True, 'method': 'console', 'message': message}
