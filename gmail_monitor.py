from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from modules.replit_connector import ReplitConnector

class GmailMonitor:
    def __init__(self, memory_manager, ai_brain, notification_manager):
        self.memory_manager = memory_manager
        self.ai_brain = ai_brain
        self.notification_manager = notification_manager
        self.last_check_time = None
    
    def _get_gmail_service(self):
        try:
            creds_data = ReplitConnector.get_gmail_credentials()
            credentials = Credentials(token=creds_data['access_token'])
            service = build('gmail', 'v1', credentials=credentials)
            return service
        except Exception as e:
            print(f"Gmail service error: {e}")
            return None
    
    def check_emails(self):
        try:
            service = self._get_gmail_service()
            if not service:
                return {'error': 'Gmail service not available'}
            
            results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=5
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                self.last_check_time = datetime.now().isoformat()
                return {'count': 0, 'message': 'No new emails, babe! 💕'}
            
            urgent_emails = []
            
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject']
                ).execute()
                
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                snippet = msg_data.get('snippet', '')
                
                last_checked = self.memory_manager.get_memory(f'email_checked_{msg["id"]}')
                if last_checked:
                    continue
                
                decision = self.ai_brain.decide_email_urgency(subject, sender, snippet)
                
                self.memory_manager.store_memory(
                    f'email_checked_{msg["id"]}',
                    {'subject': subject, 'sender': sender, 'urgent': decision.get('urgent', False)},
                    category='emails'
                )
                
                if decision.get('urgent', False):
                    urgent_emails.append({
                        'subject': subject,
                        'sender': sender,
                        'message': decision.get('message', '')
                    })
                    
                    notification_text = f"📧 {decision.get('message', f'Urgent email from {sender}: {subject}')}"
                    self.notification_manager.send_notification(notification_text)
            
            self.last_check_time = datetime.now().isoformat()
            
            if urgent_emails:
                return {
                    'count': len(messages),
                    'urgent_count': len(urgent_emails),
                    'urgent_emails': urgent_emails
                }
            else:
                return {
                    'count': len(messages),
                    'message': f"Checked {len(messages)} emails - nothing urgent, you're good babe! 😊"
                }
        
        except Exception as e:
            print(f"Email check error: {e}")
            return {'error': str(e)}
