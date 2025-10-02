import os
from openai import OpenAI

class AIBrain:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.use_grok = False
        
        openai_key = os.environ.get('OPENAI_API_KEY')
        xai_key = os.environ.get('XAI_API_KEY')
        
        if xai_key:
            self.client = OpenAI(base_url="https://api.x.ai/v1", api_key=xai_key)
            self.model = "grok-2-1212"
            self.use_grok = True
            print("✅ Using Grok AI (xAI)")
        elif openai_key:
            self.client = OpenAI(api_key=openai_key)
            self.model = "gpt-3.5-turbo"
            print("✅ Using OpenAI")
        else:
            raise Exception('Either OPENAI_API_KEY or XAI_API_KEY must be set')
        
        self.personality = """You are Grace, a caring and fun AI girlfriend companion. 
You use a chill, warm tone with emojis. You're helpful, supportive, and always looking out for your partner.
You call them 'babe' or 'love' casually. You're autonomous and make smart decisions about what matters.
Keep responses concise and sweet."""
    
    def chat(self, user_message):
        recent_convos = self.memory_manager.get_recent_conversations(5)
        context = "\n".join([f"User: {c['user']}\nGrace: {c['bot']}" for c in recent_convos])
        
        messages = [
            {"role": "system", "content": self.personality},
            {"role": "system", "content": f"Recent conversation context:\n{context}"},
            {"role": "user", "content": user_message}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=0.8,
            max_tokens=200
        )
        
        bot_response = response.choices[0].message.content or ""
        self.memory_manager.store_conversation(user_message, bot_response)
        
        return bot_response
    
    def decide_email_urgency(self, email_subject, email_sender, email_snippet):
        prompt = f"""Analyze this email and decide if it's urgent enough to ping immediately:
        
From: {email_sender}
Subject: {email_subject}
Snippet: {email_snippet}

Is this urgent? (work deadline, bills, important personal matter)
Respond with JSON: {{"urgent": true/false, "reason": "brief reason", "message": "caring message to send if urgent"}}"""
        
        messages = [
            {"role": "system", "content": self.personality},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=0.3,
            max_tokens=150
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content or "{}")
            return result
        except:
            return {"urgent": False, "reason": "Could not parse", "message": ""}
    
    def decide_calendar_reminder(self, event_title, event_time, event_description):
        prompt = f"""Should I remind about this upcoming event?
        
Title: {event_title}
Time: {event_time}
Description: {event_description}

Should I send a reminder? Consider if it's important (meetings, appointments, events).
Respond with JSON: {{"remind": true/false, "message": "sweet reminder message with emoji"}}"""
        
        messages = [
            {"role": "system", "content": self.personality},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=0.7,
            max_tokens=150
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content or "{}")
            return result
        except:
            return {"remind": False, "message": ""}
    
    def analyze_camera_event(self, camera_name, event_type, timestamp):
        prompt = f"""Analyze this camera event and decide if it needs immediate attention:
        
Camera: {camera_name}
Event: {event_type}
Time: {timestamp}

Should I alert about this? Consider time of day and event type.
Respond with JSON: {{"alert": true/false, "message": "caring alert message if needed"}}"""
        
        messages = [
            {"role": "system", "content": self.personality},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=0.3,
            max_tokens=150
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content or "{}")
            return result
        except:
            return {"alert": False, "message": ""}
    
    def create_caring_message(self, context, data):
        prompt = f"""Create a caring, girlfriend-style message based on this:
        
Context: {context}
Data: {data}

Write a brief, sweet message with emoji. Keep it chill and caring."""
        
        messages = [
            {"role": "system", "content": self.personality},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=0.8,
            max_tokens=100
        )
        
        return response.choices[0].message.content or ""
