import os
import requests
import json

class ReplitConnector:
    @staticmethod
    def get_connection_settings(connector_name):
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        
        repl_identity = os.environ.get('REPL_IDENTITY')
        web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
        
        if repl_identity:
            x_replit_token = f'repl {repl_identity}'
        elif web_repl_renewal:
            x_replit_token = f'depl {web_repl_renewal}'
        else:
            raise Exception('X_REPLIT_TOKEN not found for repl/depl')
        
        url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names={connector_name}'
        
        headers = {
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        if not items:
            raise Exception(f'{connector_name} not connected')
        
        return items[0]
    
    @staticmethod
    def get_gmail_credentials():
        settings = ReplitConnector.get_connection_settings('google-mail')
        access_token = settings.get('settings', {}).get('access_token')
        
        if not access_token:
            raise Exception('Gmail access token not found')
        
        return {'access_token': access_token}
    
    @staticmethod
    def get_calendar_credentials():
        settings = ReplitConnector.get_connection_settings('google-calendar')
        access_token = settings.get('settings', {}).get('access_token')
        
        if not access_token:
            raise Exception('Google Calendar access token not found')
        
        return {'access_token': access_token}
    
    @staticmethod
    def get_spotify_credentials():
        settings = ReplitConnector.get_connection_settings('spotify')
        settings_data = settings.get('settings', {})
        
        access_token = settings_data.get('access_token')
        refresh_token = settings_data.get('oauth', {}).get('credentials', {}).get('refresh_token')
        
        if not access_token:
            raise Exception('Spotify access token not found')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    @staticmethod
    def get_twilio_credentials():
        settings = ReplitConnector.get_connection_settings('twilio')
        settings_data = settings.get('settings', {})
        
        account_sid = settings_data.get('account_sid')
        api_key = settings_data.get('api_key')
        api_key_secret = settings_data.get('api_key_secret')
        phone_number = settings_data.get('phone_number')
        
        if not all([account_sid, api_key, api_key_secret]):
            raise Exception('Twilio credentials not found')
        
        return {
            'account_sid': account_sid,
            'api_key': api_key,
            'api_key_secret': api_key_secret,
            'phone_number': phone_number
        }
