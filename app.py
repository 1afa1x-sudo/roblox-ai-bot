from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

print("🚀 AI Bot Server запускается...")

@app.route('/', methods=['GET'])
def home():
    return '<h1>🤖 AI Bot Server</h1><p>✅ Сервер работает!</p>'

@app.route('/health', methods=['GET', 'POST', 'OPTIONS'])
def health():
    print("✅ Health check!")
    return jsonify({'status': 'online'}), 200

@app.route('/chat', methods=['POST', 'OPTIONS'])            
def chat():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('userId', 'unknown')
        
        print(f"📨 [{user_id}]: {message}")
        
        # Простые ответы
        response_text = generate_response(message)
        
        print(f"📤 Ответ: {response_text}")
        
        return jsonify({
            'success': True,
            'response': response_text
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_response(message):
    msg = message.lower().strip()
    
    if any(w in msg for w in ['привет', 'салам', 'хай', 'hello']):
        return "Привет! 👋 Чем могу помочь?"
    
    if any(w in msg for w in ['как дела', 'как ты']):
        return "Отлично! Готов помогать! 😊"
    
    if any(w in msg for w in ['пока', 'bye']):
        return "Пока! До встречи! 👋"
    
    if any(w in msg for w in ['спасибо', 'thanks']):
        return "Пожалуйста! 😄"
    
    return f"Ты написал: {message}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Порт: {port}")
    app.run(host='0.0.0.0', port=port)
