from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import random
import base64
import asyncio
import edge_tts
import io
import re

app = Flask(__name__)
CORS(app)

# OpenRouter API
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')

# Голос для озвучки
VOICE = "ru-RU-DmitryNeural"

print("🚀 AI Bot Server запускается...")
print("🤖 AI: OpenRouter (Llama 3.2)")
print("🔊 TTS: Microsoft Edge")

@app.route('/', methods=['GET'])
def home():
    return '<h1>🤖 AI Bot Server</h1><p>✅ Онлайн!</p><p>AI: OpenRouter | TTS: Edge</p>'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'ai': 'openrouter', 'tts': 'edge'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('userId', 'unknown')
        need_voice = data.get('voice', False)
        
        print(f"📨 [{user_id}]: {message}")
        
        # Получаем ответ от AI
        ai_response = get_ai_response(message)
        print(f"🤖 AI: {ai_response}")
        
        result = {
            'success': True,
            'response': ai_response
        }
        
        # Генерируем голос если нужно
        if need_voice:
            try:
                audio = asyncio.run(get_voice(ai_response))
                if audio:
                    result['audio'] = audio
                    print("🔊 Аудио готово!")
            except Exception as e:
                print(f"Voice error: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_ai_response(message):
    """Получение ответа от OpenRouter AI"""
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
- Отвечай КОРОТКО (1-3 предложения максимум)
- Будь весёлым и дружелюбным
- Используй эмодзи в ответах
- Отвечай ТОЛЬКО на русском языке
- Можешь помогать с Roblox и Lua кодом
- Если просят код - давай короткие примеры
- Не повторяй вопрос пользователя"""
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenRouter Error: {response.status_code} - {response.text}")
            return fallback_response(message)
            
    except Exception as e:
        print(f"AI Error: {e}")
        return fallback_response(message)

def fallback_response(message):
    """Запасные ответы если AI недоступен"""
    msg = message.lower().strip()
    
    if any(w in msg for w in ['привет', 'хай', 'салам', 'hello']):
        return random.choice([
            "Привет! 👋 Чем могу помочь?",
            "Привет! Рад тебя видеть! 😊",
            "Здарова! Как дела?"
        ])
    
    if any(w in msg for w in ['как дела', 'как ты']):
        return random.choice([
            "Отлично! Готов помогать! 😊",
            "Супер! А у тебя как?",
            "Всё круто! 🎮"
        ])
    
    if any(w in msg for w in ['пока', 'bye', 'до свидания']):
        return "Пока! До встречи! 👋"
    
    if any(w in msg for w in ['спасибо', 'thanks']):
        return "Пожалуйста! 😄"
    
    if any(w in msg for w in ['шутка', 'шутку', 'анекдот']):
        jokes = [
            "Почему программист ушёл с работы? Не получил массив! 😄",
            "Что сказал ноль восьмёрке? Классный ремень! 😂",
            "Почему роботы не боятся? Стальные нервы! 🤖"
        ]
        return random.choice(jokes)
    
    return "Интересно! Расскажи подробнее 🤔"

async def get_voice(text):
    """Генерация голоса через Edge TTS"""
    try:
        # Убираем эмодзи и ограничиваем длину
        clean_text = re.sub(r'[^\w\s\.,!?;:\-\(\)]', '', text)
        clean_text = clean_text[:500]
        
        if not clean_text.strip():
            return None
        
        communicate = edge_tts.Communicate(clean_text, VOICE)
        
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        audio_base64 = base64.b64encode(audio_data.read()).decode('utf-8')
        
        return audio_base64
        
    except Exception as e:
        print(f"Voice Error: {e}")
        return None

@app.route('/voice', methods=['POST'])
def voice_only():
    """Отдельный эндпоинт для озвучки"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text'}), 400
        
        audio = asyncio.run(get_voice(text))
        
        if audio:
            return jsonify({'success': True, 'audio': audio}), 200
        else:
            return jsonify({'success': False, 'error': 'Voice failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
