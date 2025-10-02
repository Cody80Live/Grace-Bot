import sqlite3
import json
from datetime import datetime
from cryptography.fernet import Fernet
import os

class MemoryManager:
    def __init__(self, db_path='gracebot_memory.db'):
        self.db_path = db_path
        self.cipher = self._get_or_create_cipher()
        self._init_db()
    
    def _get_or_create_cipher(self):
        key_file = '.encryption_key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        return Fernet(key)
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                encrypted_value BLOB,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                bot_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_memory(self, key, value, category='general'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        encrypted_value = self.cipher.encrypt(json.dumps(value).encode())
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories (key, encrypted_value, category, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (key, encrypted_value, category, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_memory(self, key):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT encrypted_value FROM memories WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            decrypted_value = self.cipher.decrypt(result[0])
            return json.loads(decrypted_value.decode())
        return None
    
    def get_memories_by_category(self, category):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, encrypted_value FROM memories WHERE category = ?', (category,))
        results = cursor.fetchall()
        conn.close()
        
        memories = {}
        for key, encrypted_value in results:
            decrypted_value = self.cipher.decrypt(encrypted_value)
            memories[key] = json.loads(decrypted_value.decode())
        
        return memories
    
    def store_conversation(self, user_message, bot_response):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, bot_response, timestamp)
            VALUES (?, ?, ?)
        ''', (user_message, bot_response, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, timestamp 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'user': r[0], 'bot': r[1], 'timestamp': r[2]} for r in reversed(results)]
    
    def get_all_memories(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, encrypted_value, category FROM memories')
        results = cursor.fetchall()
        conn.close()
        
        memories = []
        for key, encrypted_value, category in results:
            try:
                decrypted_value = self.cipher.decrypt(encrypted_value)
                value = json.loads(decrypted_value.decode())
                memories.append({'key': key, 'value': value, 'category': category})
            except:
                pass
        
        return memories
    
    def get_memory_count(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM memories')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
