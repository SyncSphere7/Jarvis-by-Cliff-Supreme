"""
Jarvis 2.0 - Database Configuration & Models
PostgreSQL with SQLAlchemy ORM for blockchain memory and user data
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import json
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

class EncryptedField(db.Text):
    """Custom field for encrypted data storage"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._encryption_key = self._generate_key()

    def _generate_key(self):
        """Generate encryption key from environment"""
        password = os.environ.get('ENCRYPTION_KEY', 'jarvis_default_key').encode()
        salt = b'jarvis_salt_2024'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def process_bind_param(self, value, dialect):
        """Encrypt data before storing"""
        if value is None:
            return None

        f = Fernet(self._encryption_key)
        encrypted_data = f.encrypt(str(value).encode())
        return encrypted_data.decode()

    def process_result_value(self, value, dialect):
        """Decrypt data when retrieving"""
        if value is None:
            return None

        f = Fernet(self._encryption_key)
        decrypted_data = f.decrypt(value.encode())
        return decrypted_data.decode()

# Database Models
class User(db.Model):
    """User account management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')

    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    memories = db.relationship('BlockchainMemory', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Conversation(db.Model):
    """Chat conversation history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_sentiment = db.Column(db.Float, default=0.0)  # -1 to 1
    jarvis_confidence = db.Column(db.Float, default=1.0)

    # AI processing metadata
    reasoning_strategy = db.Column(db.String(50))
    processing_time = db.Column(db.Float)  # seconds
    memory_blocks_used = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Conversation {self.id} - {self.timestamp}>'

class BlockchainMemory(db.Model):
    """Persistent storage for blockchain memory blocks"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    block_index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    previous_hash = db.Column(db.String(64), nullable=False)
    current_hash = db.Column(db.String(64), nullable=False)
    nonce = db.Column(db.Integer, default=0)

    # Memory content
    memory_type = db.Column(db.String(50), nullable=False)  # conversation, learning, etc.
    content = db.Column(EncryptedField, nullable=False)
    confidence_score = db.Column(db.Float, default=1.0)

    # Emotional and contextual data
    emotional_context = db.Column(db.JSON, default={})
    embedding_vector = db.Column(db.Text)  # Serialized numpy array

    # Blockchain validation
    signature = db.Column(db.Text)
    validation_status = db.Column(db.String(20), default='valid')  # valid, invalid, pending
    validated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<BlockchainMemory {self.block_index} - {self.memory_type}>'

class AIModel(db.Model):
    """AI model configurations and versions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # quantum, hybrid, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Model parameters
    parameters = db.Column(db.JSON, default={})
    performance_metrics = db.Column(db.JSON, default={})

    # Quantum-specific
    num_qubits = db.Column(db.Integer, default=8)
    coherence_time = db.Column(db.Float, default=0.95)

    def __repr__(self):
        return f'<AIModel {self.name} v{self.version}>'

class SystemMetrics(db.Model):
    """System performance and usage metrics"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, api_calls, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='count')

    # Context
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_id = db.Column(db.String(100))

    def __repr__(self):
        return f'<SystemMetrics {self.metric_type}: {self.value} {self.unit}>'

class APIKey(db.Model):
    """External API key management"""
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), nullable=False)  # google, openai, etc.
    api_key_encrypted = db.Column(EncryptedField, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)

    def __repr__(self):
        return f'<APIKey {self.service_name}>'

# Database initialization functions
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@jarvis.local',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

# Utility functions
def get_memory_stats():
    """Get comprehensive memory statistics"""
    total_memories = BlockchainMemory.query.count()
    valid_memories = BlockchainMemory.query.filter_by(validation_status='valid').count()
    avg_confidence = db.session.query(db.func.avg(BlockchainMemory.confidence_score)).scalar() or 0

    return {
        'total_blocks': total_memories,
        'valid_blocks': valid_memories,
        'invalid_blocks': total_memories - valid_memories,
        'average_confidence': round(avg_confidence, 3),
        'memory_types': get_memory_type_distribution()
    }

def get_memory_type_distribution():
    """Get distribution of memory types"""
    from sqlalchemy import func
    result = db.session.query(
        BlockchainMemory.memory_type,
        func.count(BlockchainMemory.id)
    ).group_by(BlockchainMemory.memory_type).all()

    return {memory_type: count for memory_type, count in result}

def get_conversation_stats():
    """Get conversation statistics"""
    total_conversations = Conversation.query.count()
    avg_sentiment = db.session.query(db.func.avg(Conversation.user_sentiment)).scalar() or 0
    avg_confidence = db.session.query(db.func.avg(Conversation.jarvis_confidence)).scalar() or 0

    return {
        'total_conversations': total_conversations,
        'average_sentiment': round(avg_sentiment, 3),
        'average_confidence': round(avg_confidence, 3)
    }

def cleanup_old_data(days=30):
    """Clean up old conversation data"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Delete old conversations (keep blockchain memories)
    old_conversations = Conversation.query.filter(
        Conversation.timestamp < cutoff_date
    ).delete()

    db.session.commit()
    return old_conversations

def backup_memory_blocks():
    """Backup all memory blocks to JSON"""
    memories = BlockchainMemory.query.all()
    backup_data = []

    for memory in memories:
        backup_data.append({
            'id': memory.id,
            'block_index': memory.block_index,
            'timestamp': memory.timestamp.isoformat(),
            'previous_hash': memory.previous_hash,
            'current_hash': memory.current_hash,
            'nonce': memory.nonce,
            'memory_type': memory.memory_type,
            'content': memory.content,
            'confidence_score': memory.confidence_score,
            'emotional_context': memory.emotional_context,
            'signature': memory.signature,
            'validation_status': memory.validation_status
        })

    return backup_data
