import os
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import atexit
from datetime import datetime

from modules.memory import MemoryManager
from modules.ai_brain import AIBrain
from modules.gmail_monitor import GmailMonitor
from modules.calendar_monitor import CalendarMonitor
from modules.notification_manager import NotificationManager
from modules.spotify_manager import SpotifyManager
from modules.weather_manager import WeatherManager
from modules.wyze_manager import WyzeManager
from modules.alexa_manager import AlexaManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'grace-bot-secret-key')

# Lazy-loaded manager instances
_memory_manager = None
_ai_brain = None
_notification_manager = None
_gmail_monitor = None
_calendar_monitor = None
_spotify_manager = None
_weather_manager = None
_wyze_manager = None
_alexa_manager = None
_scheduler = None
_monitoring_started = False

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

def get_ai_brain():
    global _ai_brain
    if _ai_brain is None:
        _ai_brain = AIBrain(get_memory_manager())
    return _ai_brain

def get_notification_manager():
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager

def get_gmail_monitor():
    global _gmail_monitor
    if _gmail_monitor is None:
        _gmail_monitor = GmailMonitor(get_memory_manager(), get_ai_brain(), get_notification_manager())
    return _gmail_monitor

def get_calendar_monitor():
    global _calendar_monitor
    if _calendar_monitor is None:
        _calendar_monitor = CalendarMonitor(get_memory_manager(), get_ai_brain(), get_notification_manager())
    return _calendar_monitor

def get_spotify_manager():
    global _spotify_manager
    if _spotify_manager is None:
        _spotify_manager = SpotifyManager()
    return _spotify_manager

def get_weather_manager():
    global _weather_manager
    if _weather_manager is None:
        _weather_manager = WeatherManager()
    return _weather_manager

def get_wyze_manager():
    global _wyze_manager
    if _wyze_manager is None:
        _wyze_manager = WyzeManager(get_memory_manager(), get_ai_brain(), get_notification_manager())
    return _wyze_manager

def get_alexa_manager():
    global _alexa_manager
    if _alexa_manager is None:
        _alexa_manager = AlexaManager()
    return _alexa_manager

def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler

def start_monitoring():
    global _monitoring_started
    if _monitoring_started:
        return
    
    scheduler = get_scheduler()
    
    scheduler.add_job(
        func=lambda: get_gmail_monitor().check_emails(),
        trigger=IntervalTrigger(minutes=10),
        id='email_monitor',
        name='Check emails every 10 minutes',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=lambda: get_calendar_monitor().check_events(),
        trigger=IntervalTrigger(minutes=30),
        id='calendar_monitor',
        name='Check calendar events every 30 minutes',
        replace_existing=True
    )
    
    scheduler.start()
    _monitoring_started = True
    print("🤖 GraceBot monitoring started! Watching your emails and calendar...")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    try:
        # Only initialize managers when status endpoint is accessed
        memory_mgr = get_memory_manager()
        gmail_mon = get_gmail_monitor()
        calendar_mon = get_calendar_monitor()
        
        stats = {
            'memory_count': memory_mgr.get_memory_count(),
            'last_email_check': gmail_mon.last_check_time,
            'last_calendar_check': calendar_mon.last_check_time,
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/trigger/email')
def trigger_email():
    try:
        result = get_gmail_monitor().check_emails()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger/calendar')
def trigger_calendar():
    try:
        result = get_calendar_monitor().check_events()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger/weather')
def trigger_weather():
    try:
        result = get_weather_manager().get_weather_suggestion()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '') if request.json else ''
        response = get_ai_brain().chat(user_message)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory')
def get_memory():
    try:
        memories = get_memory_manager().get_all_memories()
        return jsonify({'memories': memories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger/wyze')
def trigger_wyze():
    try:
        result = get_wyze_manager().check_camera_events()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger/wyze/simulate')
def trigger_wyze_simulate():
    try:
        result = get_wyze_manager().simulate_motion_event()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alexa/lights/<action>')
def alexa_lights(action):
    try:
        location = request.args.get('location', 'living room')
        
        alexa_mgr = get_alexa_manager()
        if action == 'on':
            result = alexa_mgr.turn_on_lights(location)
        elif action == 'off':
            result = alexa_mgr.turn_off_lights(location)
        elif action == 'game_time':
            result = alexa_mgr.game_time_lights()
        else:
            result = {'error': 'Invalid action'}
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alexa/status')
def alexa_status():
    try:
        result = get_alexa_manager().get_status()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Fast health check endpoint for deployment"""
    return jsonify({'status': 'healthy'}), 200

# Initialize monitoring when first request is made (works with gunicorn)
@app.before_request
def initialize_monitoring():
    """Start background monitoring on first request (gunicorn-safe)"""
    global _monitoring_started
    if not _monitoring_started:
        try:
            start_monitoring()
        except Exception as e:
            print(f"Warning: Could not start monitoring: {e}")

# Clean up scheduler on exit
def cleanup_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown()

atexit.register(cleanup_scheduler)

if __name__ == '__main__':
    print("💕 Starting GraceBot - Your AI Girlfriend Companion...")
    start_monitoring()
    app.run(host='0.0.0.0', port=5000, debug=False)
