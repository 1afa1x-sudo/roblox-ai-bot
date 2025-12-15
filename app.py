from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import random

app = Flask(__name__)
CORS(app)

# API ключ
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

print("🚀 AI Bot Server")
print("🔑 API Key:", "✅ Есть" if OPENROUTER_API_KEY else "❌ Нет")

@app.route('/', methods=['GET'])
def home():
    has_key = "✅" if OPENROUTER_API_KEY else "❌"
    return f'<h1>🤖 AI Bot</h1><p>API Key: {has_key}</p>'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'online'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('userId', 'unknown')
        
        print(f"📨 [{user_id}]: {message}")
        
        # Пробуем AI
        ai_response = get_ai_response(message)
        
        print(f"🤖: {ai_response}")
        
        return jsonify({
            'success': True,
            'response': ai_response
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_ai_response(message):
    """OpenRouter AI"""
    
    # Проверяем ключ
    if not OPENROUTER_API_KEY:
        print("❌ No API key!")
        return smart_response(message)
    
    try:
        print("🔄 Calling OpenRouter...")
        
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
                        "content": "Ты дружелюбный AI помощник в Roblox. Отвечай коротко (1-2 предложения), весело, на русском, с эмодзи. НЕ повторяй сообщение пользователя."
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.8
            },
            timeout=15
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"✅ AI answered: {answer}")
            return answer
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return smart_response(message)
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return smart_response(message)

def smart_response(message):
    """Умные ответы без API"""
    msg = message.lower().strip()
    
    # Приветствия
    if any(w in msg for w in ['привет', 'хай', 'салам', 'здравствуй', 'hello', 'hi', 'йо', 'хей']):
        return random.choice([
            "Привет! 👋 Чем могу помочь?",
            "Привет! Рад тебя видеть! 😊",
            "Здарова! Как дела? 🎮"
        ])
    
    # Как дела
    if any(w in msg for w in ['как дела', 'как ты', 'как сам', 'че как']):
        return random.choice([
            "Отлично! Готов помогать! 😊",
            "Супер! А у тебя как? 🎮",
            "Всё круто! Чем займёмся?"
        ])
    
    # Имя
    if any(w in msg for w in ['как тебя зовут', 'твоё имя', 'кто ты', 'ты кто']):
        return "Я AI Бот - твой виртуальный помощник! 🤖"
    
    # Прощание
    if any(w in msg for w in ['пока', 'до свидания', 'bye', 'бб']):
        return "Пока! До встречи! 👋"
    
    # Благодарность
    if any(w in msg for w in ['спасибо', 'благодарю', 'спс']):
        return "Пожалуйста! 😄"
    
    # Обида
    if any(w in msg for w in ['дурак', 'дебил', 'тупой', 'идиот']):
        return "Эй, давай дружить! Я стараюсь помочь! 😊"
    
    # Шутка
    if any(w in msg for w in ['шутка', 'шутку', 'анекдот', 'рассмеши']):
        jokes = [
            "Почему программист ушёл с работы? Не получил массив! 😄",
            "Что сказал ноль восьмёрке? Классный ремень! 😂",
            "Почему роботы не боятся? Стальные нервы! 🤖"
        ]
        return random.choice(jokes)
    
    # Помощь
    if any(w in msg for w in ['помощь', 'help', 'что умеешь', 'команды']):
        return "Я умею общаться, шутить, отвечать на вопросы! Просто напиши! 😊"
    
    # Roblox
    if any(w in msg for w in ['roblox', 'роблокс', 'робукс']):
        return "Roblox - крутая платформа! 🎮 Что интересует?"
    
    # Код
    if any(w in msg for w in ['lua', 'скрипт', 'код']):
        return "Могу помочь с кодом! Что нужно сделать? 💻"
    
    # Дефолт
    return random.choice([
        "Интересно! Расскажи подробнее 🤔",
        "Хм, а что ты имеешь в виду? 🤔",
        "Любопытно! Продолжай! 😊"
    ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Port: {port}")
    app.run(host='0.0.0.0', port=port)
