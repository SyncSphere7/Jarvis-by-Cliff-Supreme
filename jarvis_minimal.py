"""
Jarvis 2.0 - Minimal Version for Free Hosting
Streamlined AI assistant with essential features only
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import json
from datetime import datetime
import hashlib

# Initialize Flask app
app = Flask(__name__)
CORS(app)

class MinimalBlockchainMemory:
    """Simplified blockchain memory for free hosting"""

    def __init__(self):
        self.chain = []
        self.difficulty = 2
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the first block"""
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'data': {'type': 'genesis', 'message': 'Jarvis Minimal Memory Genesis'},
            'previous_hash': '0' * 32,
            'hash': '',
            'nonce': 0
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)

    def calculate_hash(self, block):
        """Calculate block hash"""
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'data': block['data'],
            'previous_hash': block['previous_hash'],
            'nonce': block['nonce']
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_memory(self, data):
        """Add new memory to blockchain"""
        previous_block = self.chain[-1]

        new_block = {
            'index': previous_block['index'] + 1,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': previous_block['hash'],
            'hash': '',
            'nonce': 0
        }

        # Simple proof-of-work (reduced for free hosting)
        while not new_block['hash'].startswith('0' * self.difficulty):
            new_block['nonce'] += 1
            new_block['hash'] = self.calculate_hash(new_block)

        self.chain.append(new_block)
        return new_block

class MinimalJarvis:
    """Minimal Jarvis with essential AI features"""

    def __init__(self):
        self.memory = MinimalBlockchainMemory()
        self.conversation_history = []

    def process_message(self, message):
        """Process user message with Gemini AI"""
        try:
            import google.generativeai as genai

            # Get API key from environment
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                return "Error: GOOGLE_API_KEY not configured"

            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            # Generate response
            response = model.generate_content(message)
            ai_response = response.text

            # Store in blockchain memory
            memory_data = {
                'type': 'conversation',
                'user_message': message,
                'ai_response': ai_response,
                'timestamp': time.time()
            }

            self.memory.add_memory(memory_data)

            # Store in conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': message,
                'jarvis': ai_response
            })

            return ai_response

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

# Initialize Jarvis
jarvis = MinimalJarvis()

@app.route('/')
def index():
    """Serve basic HTML interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jarvis 2.0 - Minimal</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            .chat-box { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; margin-left: 50px; }
            .jarvis { background: #f3e5f5; margin-right: 50px; }
            .input-area { display: flex; gap: 10px; }
            input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
            button { padding: 10px 20px; background: #6200ea; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #3700b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Jarvis 2.0 - Minimal Edition</h1>
            <p>Your AI assistant is running on free hosting!</p>

            <div class="chat-box" id="chatBox">
                <div class="message jarvis">Hello! I'm Jarvis, your AI assistant. How can I help you today?</div>
            </div>

            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            function addMessage(text, className) {
                const chatBox = document.getElementById('chatBox');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                messageDiv.textContent = text;
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();

                if (!message) return;

                addMessage(message, 'user');
                input.value = '';

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });

                    const data = await response.json();

                    if (data.response) {
                        addMessage(data.response, 'jarvis');
                    } else {
                        addMessage('Sorry, I encountered an error.', 'jarvis');
                    }
                } catch (error) {
                    addMessage('Network error. Please try again.', 'jarvis');
                }
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        user_message = data['message']
        response = jarvis.process_message(user_message)

        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        return jsonify({
            'status': 'online',
            'version': 'Jarvis 2.0 - Minimal',
            'memory_blocks': len(jarvis.memory.chain),
            'conversations': len(jarvis.conversation_history),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🌐 Jarvis 2.0 Minimal - Starting...")
    print(f"📍 Local URL: http://localhost:{port}")
    print("🔗 API Endpoint: POST /api/chat"
    print("📊 Status: GET /api/status"
    app.run(host='0.0.0.0', port=port)
