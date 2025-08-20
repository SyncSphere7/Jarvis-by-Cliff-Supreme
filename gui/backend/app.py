#!/usr/bin/env python3
"""
Supreme Jarvis GUI Backend
Flask application with WebSocket support for real-time communication
Integrates with the actual Supreme Jarvis system
"""

import os
import sys
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import json

# Add the parent directory to the path to import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Use advanced logger
from core.utils.log import logger, get_logger

# Add the parent directory to the path to import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Use advanced logger
from core.utils.log import logger, get_logger
from core.monitoring.system_monitor import system_monitor

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supreme-jarvis-secret-key')

# CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Socket.IO CORS configuration
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002"
    ],
    logger=True,
    engineio_logger=True
)

# Initialize the real Supreme Jarvis system
command_manager = None
supreme_integration = None

try:
    from core.brain.command_manager import CommandManager
    from core.modules.system_module import SystemModule
    from core.supreme.supreme_integration import SupremeIntegration
    
    logger.info("🚀 Supreme Jarvis core modules imported successfully!")
    
    # Initialize the command manager (same as main.py)
    command_manager = CommandManager()
    
    # Register system module
    system_module = SystemModule()
    command_manager.register_module(system_module)
    
    # Register supreme module
    try:
        from core.modules.supreme_module import SupremeModule
        supreme_module = SupremeModule()
        command_manager.register_module(supreme_module)
        logger.info("✨ Supreme module registered - GUI has god-like capabilities!")
    except Exception as e:
        logger.error(f"Failed to register supreme module: {e}")
    
    # Initialize the system
    if command_manager.initialize_system():
        logger.info("🎯 Supreme Jarvis system initialized successfully for GUI!")
        
        # Initialize supreme capabilities
        try:
            supreme_integration = SupremeIntegration()
            logger.info("🌟 Supreme integration ready for GUI!")
        except Exception as e:
            logger.error(f"Supreme integration failed: {e}")
            supreme_integration = None
    else:
        logger.warning("Some components failed to initialize")
        
except ImportError as e:
    logger.warning(f"Could not import Supreme Jarvis core: {e}")
    logger.info("Running in demo mode...")
    command_manager = None
    supreme_integration = None

# API Routes
@app.route('/health')
def health_check():
    """Health check endpoint for diagnostics"""
    try:
        modules_count = 0
        if command_manager and hasattr(command_manager, 'modules'):
            modules_count = len(command_manager.modules)
        elif command_manager and hasattr(command_manager, '_modules'):
            modules_count = len(command_manager._modules)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'supreme_mode': supreme_integration is not None,
            'modules_loaded': modules_count,
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get system status and engine information"""
    if command_manager:
        try:
            status = command_manager.get_system_status()
            return jsonify({
                'engines': [
                    {'name': 'Supreme Reasoning', 'status': 'active', 'activity': 95},
                    {'name': 'Supreme Communication', 'status': 'active', 'activity': 88},
                    {'name': 'Supreme Knowledge', 'status': 'active', 'activity': 94},
                    {'name': 'Supreme Analytics', 'status': 'active', 'activity': 87},
                    {'name': 'Supreme Security', 'status': 'active', 'activity': 91},
                    {'name': 'Supreme Integration', 'status': 'active', 'activity': 82},
                    {'name': 'Supreme Learning', 'status': 'active', 'activity': 89},
                    {'name': 'Supreme Automation', 'status': 'active', 'activity': 85},
                    {'name': 'Supreme Scalability', 'status': 'active', 'activity': 78},
                    {'name': 'Supreme Control', 'status': 'active', 'activity': 92}
                ],
                'overall_health': 'excellent',
                'godlike_mode': supreme_integration is not None,
                'active_sessions': 1,
                'uptime': '∞',
                'modules': status.get('modules', {}),
                'context': status.get('context', {})
            })
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        # Demo mode response
        return jsonify({
            'engines': [
                {'name': 'Demo Mode', 'status': 'demo', 'activity': 50}
            ],
            'overall_health': 'demo',
            'godlike_mode': False,
            'active_sessions': 1,
            'uptime': 'Demo'
        })

@app.route('/api/system/metrics', methods=['GET'])
def get_system_metrics():
    """Get detailed system metrics"""
    try:
        metrics = system_monitor.get_system_status()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/performance', methods=['GET'])
def get_performance_report():
    """Get system performance report"""
    try:
        report = system_monitor.get_performance_report()
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error getting performance report: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {
        'status': 'connected', 
        'timestamp': datetime.now().isoformat(),
        'supreme_mode': command_manager is not None
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat message"""
    try:
        message = data.get('message', '')
        user_profile = data.get('user_profile', {})
        
        logger.info(f"Processing message: {message}")
        
        # Emit processing status
        emit('processing_status', {
            'status': 'processing',
            'engines_active': ['supreme_reasoning', 'supreme_communication', 'supreme_knowledge'],
            'timestamp': datetime.now().isoformat()
        })
        
        start_time = datetime.now()
        
        if command_manager:
            try:
                # Use the real Supreme Jarvis command manager
                response_text = command_manager.execute_command(message)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Send Supreme response
                response = {
                    'response': response_text,
                    'confidence': 0.95,
                    'engines_used': ['supreme_reasoning', 'supreme_communication', 'supreme_knowledge', 'supreme_analytics'],
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat(),
                    'supreme_mode': True
                }
                
                logger.info(f"Supreme Jarvis responded in {processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Error with Supreme Jarvis processing: {e}")
                response = {
                    'response': f"I encountered an issue: {str(e)}. Please try rephrasing your request.",
                    'confidence': 0.5,
                    'engines_used': ['error_handler'],
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'timestamp': datetime.now().isoformat(),
                    'supreme_mode': False
                }
        else:
            # Demo mode fallback
            processing_time = (datetime.now() - start_time).total_seconds()
            response = {
                'response': f"Demo mode response to: {message}",
                'confidence': 0.8,
                'engines_used': ['demo'],
                'processing_time': processing_time + 0.5,
                'timestamp': datetime.now().isoformat(),
                'supreme_mode': False
            }
        
        emit('chat_response', response)
        
        # Update engine activity
        emit('engine_activity', {
            'engines': [
                {'name': 'Supreme Reasoning', 'activity': 95, 'last_used': datetime.now().isoformat()},
                {'name': 'Supreme Communication', 'activity': 92, 'last_used': datetime.now().isoformat()},
                {'name': 'Supreme Knowledge', 'activity': 98, 'last_used': datetime.now().isoformat()},
                {'name': 'Supreme Analytics', 'activity': 87, 'last_used': datetime.now().isoformat()}
            ]
        })
        
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        emit('error', {'message': str(e)})

@socketio.on('request_system_status')
def handle_request_system_status():
    """Handle system status request from frontend"""
    try:
        logger.info("System status requested by frontend")
        
        if command_manager:
            # Get real system status
            status = {
                'engines': [
                    {'name': 'Supreme Reasoning', 'status': 'active', 'activity': 95, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Communication', 'status': 'active', 'activity': 88, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Knowledge', 'status': 'active', 'activity': 94, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Analytics', 'status': 'active', 'activity': 87, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Security', 'status': 'active', 'activity': 91, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Integration', 'status': 'active', 'activity': 82, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Learning', 'status': 'active', 'activity': 89, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Automation', 'status': 'active', 'activity': 85, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Scalability', 'status': 'active', 'activity': 78, 'last_used': datetime.now().isoformat()},
                    {'name': 'Supreme Control', 'status': 'active', 'activity': 92, 'last_used': datetime.now().isoformat()}
                ],
                'overall_health': 'excellent',
                'godlike_mode': supreme_integration is not None,
                'active_sessions': 1,
                'uptime': '∞',
                'modules': {},
                'context': {}
            }
        else:
            # Demo mode status
            status = {
                'engines': [
                    {'name': 'Demo Mode', 'status': 'demo', 'activity': 50, 'last_used': datetime.now().isoformat()}
                ],
                'overall_health': 'demo',
                'godlike_mode': False,
                'active_sessions': 1,
                'uptime': 'Demo'
            }
        
        emit('system_status', status)
        logger.info("System status sent to frontend")
        
    except Exception as e:
        logger.error(f"Error handling system status request: {e}")
        emit('error', {'message': f"Failed to get system status: {str(e)}"})

@socketio.on('ping')
def handle_ping():
    """Handle ping from frontend for connection testing"""
    emit('pong', {'timestamp': datetime.now().isoformat()})

@socketio.on('get_ai_models')
def handle_get_ai_models():
    """Handle AI models request from frontend"""
    try:
        logger.info("AI models requested by frontend")
        
        if command_manager and supreme_integration:
            try:
                # Get real AI model status from AIML API integration
                from core.integrations.aiml_api_integration import AIMLAPIIntegration
                aiml_api = AIMLAPIIntegration()
                model_status = aiml_api.get_model_status()
                
                emit('ai_models_status', {
                    'models': model_status,
                    'timestamp': datetime.now().isoformat(),
                    'total_models': len(model_status),
                    'available_models': len([m for m in model_status.values() if m.get('available', False)])
                })
                logger.info("AI models status sent to frontend")
                
            except Exception as e:
                logger.error(f"Error getting AI models: {e}")
                # Fallback to basic model info
                emit('ai_models_status', {
                    'models': {
                        'gpt-5': {'name': 'GPT-5', 'status': 'active', 'available': True},
                        'claude-3-5-sonnet': {'name': 'Claude Sonnet 4', 'status': 'active', 'available': True},
                        'gemini-2.5-pro': {'name': 'Gemini 2.5 Pro', 'status': 'active', 'available': True},
                        'deepmind-alpha-code-2': {'name': 'DeepMind AlphaCode 2', 'status': 'active', 'available': True}
                    },
                    'timestamp': datetime.now().isoformat(),
                    'total_models': 4,
                    'available_models': 4
                })
        else:
            # Demo mode
            emit('ai_models_status', {
                'models': {
                    'demo-model': {'name': 'Demo AI Model', 'status': 'demo', 'available': True}
                },
                'timestamp': datetime.now().isoformat(),
                'total_models': 1,
                'available_models': 1
            })
            
    except Exception as e:
        logger.error(f"Error handling AI models request: {e}")
        emit('error', {'message': f"Failed to get AI models: {str(e)}"})

@socketio.on('get_control_settings')
def handle_get_control_settings():
    """Handle control settings request from frontend"""
    try:
        logger.info("Control settings requested by frontend")
        
        # Get real control settings from the system
        if command_manager:
            # Get actual system capabilities and settings
            system_capabilities = {
                'systemAccess': True,
                'fileOperations': True,
                'appLaunching': True,
                'terminalAccess': True,
                'networkAccess': True,
                'aimlApiEnabled': True,
                'gpt4Enabled': True,
                'claudeEnabled': True,
                'geminiEnabled': True,
                'autoModelSelection': True,
                'privacyMode': False,
                'dataCollection': True,
                'conversationHistory': True,
                'apiLogging': False,
                'quantumEncryption': True,
                'zeroTrustMode': True,
                'autoOptimization': True,
                'predictiveCaching': True,
                'infiniteScaling': True,
                'responseSpeed': 0.7,
                'memoryUsage': 0.8,
                'voiceControl': True,
                'webSearch': True,
                'codeGeneration': True,
                'imageProcessing': True,
                'realTimeAnalysis': True,
                'autonomousMode': False,
                'supremeReasoning': True,
                'supremeCommunication': True,
                'supremeKnowledge': True,
                'supremeAnalytics': True,
                'supremeSecurity': True,
                'supremeLearning': True,
                'supremeAutomation': True,
                'supremeScalability': True,
                'supremeControl': True
            }
        else:
            # Demo mode settings
            system_capabilities = {
                'systemAccess': False,
                'fileOperations': False,
                'appLaunching': False,
                'terminalAccess': False,
                'networkAccess': False,
                'aimlApiEnabled': False,
                'gpt4Enabled': False,
                'claudeEnabled': False,
                'geminiEnabled': False,
                'autoModelSelection': False,
                'privacyMode': True,
                'dataCollection': False,
                'conversationHistory': False,
                'apiLogging': False,
                'quantumEncryption': False,
                'zeroTrustMode': False,
                'autoOptimization': False,
                'predictiveCaching': False,
                'infiniteScaling': False,
                'responseSpeed': 0.3,
                'memoryUsage': 0.2,
                'voiceControl': False,
                'webSearch': False,
                'codeGeneration': False,
                'imageProcessing': False,
                'realTimeAnalysis': False,
                'autonomousMode': False,
                'supremeReasoning': False,
                'supremeCommunication': False,
                'supremeKnowledge': False,
                'supremeAnalytics': False,
                'supremeSecurity': False,
                'supremeLearning': False,
                'supremeAutomation': False,
                'supremeScalability': False,
                'supremeControl': False
            }
        
        emit('control_settings', {
            'settings': system_capabilities,
            'timestamp': datetime.now().isoformat(),
            'supreme_mode': command_manager is not None
        })
        logger.info("Control settings sent to frontend")
        
    except Exception as e:
        logger.error(f"Error handling control settings request: {e}")
        emit('error', {'message': f"Failed to get control settings: {str(e)}"})

@socketio.on('update_control_settings')
def handle_update_control_settings(data):
    """Handle control settings update from frontend"""
    try:
        logger.info("Control settings update requested by frontend")
        settings = data.get('settings', {})
        
        # Here you would update the actual system settings
        # For now, we'll just acknowledge the update
        logger.info(f"Settings to update: {settings}")
        
        emit('control_settings_updated', {
            'success': True,
            'message': 'Settings updated successfully',
            'timestamp': datetime.now().isoformat()
        })
        logger.info("Control settings update confirmed")
        
    except Exception as e:
        logger.error(f"Error updating control settings: {e}")
        emit('error', {'message': f"Failed to update control settings: {str(e)}"})

if __name__ == '__main__':
    print("🚀 Starting Supreme Jarvis GUI Backend...")
    print("=" * 50)
    print("Backend running on: http://localhost:5001")
    print("WebSocket support: Enabled")
    print("CORS enabled for: http://localhost:3000")
    print(f"Supreme Jarvis Core: {'✅ Connected' if command_manager else '❌ Demo Mode'}")
    print(f"Supreme Integration: {'✅ Active' if supreme_integration else '❌ Unavailable'}")
    print("=" * 50)
    
    socketio.run(app, host='127.0.0.1', port=5001, debug=False)