from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from modules.replit_connector import ReplitConnector

class CalendarMonitor:
    def __init__(self, memory_manager, ai_brain, notification_manager):
        self.memory_manager = memory_manager
        self.ai_brain = ai_brain
        self.notification_manager = notification_manager
        self.last_check_time = None
    
    def _get_calendar_service(self):
        try:
            creds_data = ReplitConnector.get_calendar_credentials()
            credentials = Credentials(token=creds_data['access_token'])
            service = build('calendar', 'v3', credentials=credentials)
            return service
        except Exception as e:
            print(f"Calendar service error: {e}")
            return None
    
    def check_events(self):
        try:
            service = self._get_calendar_service()
            if not service:
                return {'error': 'Calendar service not available'}
            
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(hours=4)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                self.last_check_time = datetime.now().isoformat()
                return {'count': 0, 'message': 'No upcoming events in the next 4 hours! 📅'}
            
            reminders_sent = []
            
            for event in events:
                event_id = event['id']
                event_title = event.get('summary', 'No Title')
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_description = event.get('description', '')
                
                reminder_key = f'calendar_reminder_{event_id}'
                already_reminded = self.memory_manager.get_memory(reminder_key)
                
                if already_reminded:
                    continue
                
                event_time_str = event_start.split('T')[1].split('-')[0] if 'T' in event_start else event_start
                
                decision = self.ai_brain.decide_calendar_reminder(
                    event_title,
                    event_time_str,
                    event_description
                )
                
                if decision.get('remind', False):
                    self.memory_manager.store_memory(
                        reminder_key,
                        {'title': event_title, 'time': event_start, 'reminded': True},
                        category='calendar'
                    )
                    
                    message = decision.get('message', f"Hey babe, you have '{event_title}' coming up soon! 📅✨")
                    self.notification_manager.send_notification(message)
                    
                    reminders_sent.append({
                        'title': event_title,
                        'time': event_start,
                        'message': message
                    })
            
            self.last_check_time = datetime.now().isoformat()
            
            if reminders_sent:
                return {
                    'count': len(events),
                    'reminders_sent': len(reminders_sent),
                    'events': reminders_sent
                }
            else:
                return {
                    'count': len(events),
                    'message': f"Found {len(events)} events - no urgent reminders needed! 😊"
                }
        
        except Exception as e:
            print(f"Calendar check error: {e}")
            return {'error': str(e)}
