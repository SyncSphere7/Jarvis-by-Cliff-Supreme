"""
Jarvis 2.0 Web Application
Flask-based web interface for the Supreme AI Assistant
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import time
from datetime import datetime
import threading
from core.cognitive.hybrid_intelligence import HybridIntelligenceSystem
from core.cognitive.blockchain_memory import BlockchainMemorySystem
from core.ai.quantum_neural import QuantumNeuralNetwork

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis_supreme_2.0_secret_key'

# Enable CORS for all routes
CORS(app)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global Jarvis instances
jarvis_instances = {}
current_user_id = "default"

class JarvisWebInterface:
    """Web interface wrapper for Jarvis 2.0"""

    def __init__(self):
        self.hybrid_intelligence = None
        self.blockchain_memory = None
        self.quantum_network = None
        self.conversation_history = []
        self.is_initialized = False

    def initialize_jarvis(self):
        """Initialize all Jarvis components"""
        try:
            print("🚀 Initializing Jarvis 2.0 Web Interface...")

            # Initialize core components
            self.hybrid_intelligence = HybridIntelligenceSystem()
            self.blockchain_memory = BlockchainMemorySystem()
            self.quantum_network = QuantumNeuralNetwork()

            self.is_initialized = True
            print("✅ Jarvis 2.0 successfully initialized!")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize Jarvis: {e}")
            return False

    def process_message(self, message, user_id="default"):
        """Process user message and return response"""
        try:
            if not self.is_initialized:
                return "Jarvis is still initializing. Please wait..."

            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': message,
                'user_id': user_id
            })

            # Process with hybrid intelligence
            response = self.hybrid_intelligence.answer_question(message)

            # Store in blockchain memory
            memory_data = {
                'type': 'conversation',
                'content': f"User: {message}\nJarvis: {response}",
                'user_id': user_id,
                'timestamp': time.time()
            }

            self.blockchain_memory.add_memory(memory_data, confidence=0.9)

            # Mine pending memories if enough accumulated
            mined_block = self.blockchain_memory.mine_pending_memories()
            if mined_block:
                print(f"🧠 Mined new memory block: {mined_block.index}")

            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'jarvis': response,
                'user_id': user_id
            })

            return response

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            print(f"❌ Error processing message: {e}")
            return error_msg

    def get_system_status(self):
        """Get comprehensive system status"""
        return {
            'initialized': self.is_initialized,
            'memory_blocks': len(self.blockchain_memory.chain) if self.blockchain_memory else 0,
            'pending_memories': len(self.blockchain_memory.pending_memories) if self.blockchain_memory else 0,
            'conversation_count': len(self.conversation_history),
            'quantum_state': self.quantum_network.get_quantum_state() if self.quantum_network else None,
            'timestamp': datetime.now().isoformat()
        }

# Initialize Jarvis interface
jarvis_interface = JarvisWebInterface()

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        user_message = data['message']
        user_id = data.get('user_id', 'default')

        response = jarvis_interface.process_message(user_message, user_id)

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
        status = jarvis_interface.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history"""
    try:
        return jsonify({
            'conversations': jarvis_interface.conversation_history[-50:],  # Last 50 messages
            'count': len(jarvis_interface.conversation_history)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/memory/search', methods=['POST'])
def search_memory():
    """Search blockchain memory"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data['query']
        threshold = data.get('threshold', 0.7)

        if not jarvis_interface.blockchain_memory:
            return jsonify({'error': 'Memory system not initialized'}), 500

        results = jarvis_interface.blockchain_memory.search_memories(query, threshold)

        return jsonify({
            'results': [jarvis_interface.blockchain_memory.block_to_dict(block) for block in results],
            'count': len(results)
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# SocketIO events for real-time communication
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'message': 'Connected to Jarvis 2.0'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat messages"""
    try:
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')

        response = jarvis_interface.process_message(user_message, user_id)

        emit('jarvis_response', {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })

    except Exception as e:
        emit('error', {
            'error': str(e),
            'status': 'error'
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize Jarvis on startup
def init_jarvis():
    """Initialize Jarvis in a separate thread"""
    def init_worker():
        success = jarvis_interface.initialize_jarvis()
        if success:
            socketio.emit('system_ready', {'message': 'Jarvis 2.0 is ready!'})
        else:
            socketio.emit('system_error', {'message': 'Failed to initialize Jarvis'})

    thread = threading.Thread(target=init_worker)
    thread.daemon = True
    thread.start()

# Start Jarvis initialization when app starts
with app.app_context():
    init_jarvis()

if __name__ == '__main__':
    # For local development
    print("🌐 Starting Jarvis 2.0 Web Interface...")
    print("📍 Local URL: http://localhost:5000")
    print("🔗 API Endpoints:")
    print("   POST /api/chat - Send messages")
    print("   GET  /api/status - Get system status")
    print("   GET  /api/conversation - Get conversation history")
    print("   POST /api/memory/search - Search memory")

    # Run with SocketIO support
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
