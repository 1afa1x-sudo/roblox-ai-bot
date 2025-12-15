from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import requests
import random
import base64
import asyncio
import edge_tts
import io
import re
import uuid
import time

app = Flask(__name__)
CORS(app)

# OpenRouter API
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

# Голос
VOICE = "ru-RU-DmitryNeural"

# Хранилище аудио (временное)
audio_storage = {}

print("🚀 AI Bot Server запускается...")
print("🤖 AI: OpenRouter")
print("🔊 TTS: Edge + Audio Streaming")

@app.route('/', methods=['GET'])
def home():
    return '<h1>🤖 AI Bot Server</h1><p>✅ Онлайн!</p>'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'online'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('userId', 'unknown')
        need_voice = data.get('voice', False)
        
        print(f"📨 [{user_id}]: {message}")
        
        ai_response = get_ai_response(message)
        print(f"🤖 AI: {ai_response}")
        
        result = {
            'success': True,
            'response': ai_response
        }
        
        # Генерируем аудио и сохраняем
        if need_voice:
            try:
                audio_data = asyncio.run(get_voice(ai_response))
                if audio_data:
                    # Создаём уникальный ID
                    audio_id = str(uuid.uuid4())[:8]
                    audio_storage[audio_id] = {
                        'data': audio_data,
                        'time': time.time()
                    }
                    
                    # Очищаем старые аудио (старше 5 минут)
                    cleanup_old_audio()
                    
                    # Отправляем URL для воспроизведения
                    result['audioUrl'] = f"/audio/{audio_id}"
                    print(f"🔊 Аудио готово: {audio_id}")
            except Exception as e:
                print(f"Voice error: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/audio/<audio_id>', methods=['GET'])
def get_audio(audio_id):
    """Отдача аудио файла"""
    if audio_id in audio_storage:
        audio_data = audio_storage[audio_id]['data']
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=False
        )
    return "Audio not found", 404

def cleanup_old_audio():
    """Удаляем старые аудио файлы"""
    current_time = time.time()
    to_delete = []
    for audio_id, data in audio_storage.items():
        if current_time - data['time'] > 300:  # 5 минут
            to_delete.append(audio_id)
    for audio_id in to_delete:
        del audio_storage[audio_id]

def get_ai_response(message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://railway.app",
                "X-Title": "Roblox AI Bot"
            },
            json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": """Ты дружелюбный AI помощник в Roblox игре.
Правила:
- Отвечай КОРОТКО (1-3 предложения)
- Будь весёлым
- Используй эмодзи
- Отвечай на русском
- Помогай с Roblox/Lua"""
                    },
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return fallback_response(message)
            
    except Exception as e:
        print(f"AI Error: {e}")
        return fallback_response(message)

def fallback_response(msg):
    msg = msg.lower()
    if any(w in msg for w in ['привет', 'хай']): return "Привет! 👋"
    if any(w in msg for w in ['как дела']): return "Отлично! 😊"
    if any(w in msg for w in ['пока']): return "Пока! 👋"
    return "Интересно! 🤔"

async def get_voice(text):
    try:
        clean = re.sub(r'[^\w\s\.,!?;:\-\(\)]', '', text)[:400]
        if not clean.strip():
            return None
        
        communicate = edge_tts.Communicate(clean, VOICE)
        audio = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
        
        audio.seek(0)
        return audio.read()
        
    except Exception as e:
        print(f"Voice Error: {e}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
