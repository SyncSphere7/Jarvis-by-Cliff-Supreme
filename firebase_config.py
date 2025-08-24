"""
Jarvis 2.0 - Firebase Integration
Using Firebase for backend services, database, and hosting
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from typing import Dict, Any, List
import json
from datetime import datetime
import uuid

class FirebaseManager:
    """Manages Firebase integration for Jarvis"""

    def __init__(self):
        self.firebase_config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID")
        }

        self.db = None
        self.auth = None
        self.bucket = None
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # For server-side (Python)
            if not firebase_admin._apps:
                cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': os.getenv("FIREBASE_PROJECT_ID")
                    })

                    # Initialize services
                    self.db = firestore.client()
                    self.auth = auth
                    self.bucket = storage.bucket()

                    print("✅ Firebase initialized successfully")
                else:
                    print("⚠️  Firebase service account key not found")
                    print("   Please set FIREBASE_SERVICE_ACCOUNT_KEY environment variable")
            else:
                self.db = firestore.client()
                self.auth = auth
                self.bucket = storage.bucket()

        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")

    def store_conversation(self, user_id: str, message: str, response: str,
                          sentiment: float = 0.0, confidence: float = 1.0) -> bool:
        """Store conversation in Firestore"""
        if not self.db:
            return False

        try:
            conversation_ref = self.db.collection('conversations').document()

            conversation_data = {
                'user_id': user_id,
                'message': message,
                'response': response,
                'sentiment': sentiment,
                'confidence': confidence,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'session_id': f"session_{user_id}_{int(datetime.now().timestamp())}"
            }

            conversation_ref.set(conversation_data)
            return True

        except Exception as e:
            print(f"❌ Firebase conversation storage error: {e}")
            return False

    def store_memory_block(self, user_id: str, block_data: Dict[str, Any]) -> bool:
        """Store blockchain memory block in Firestore"""
        if not self.db:
            return False

        try:
            memory_ref = self.db.collection('blockchain_memory').document()

            memory_data = {
                'user_id': user_id,
                'block_index': block_data.get('index', 0),
                'previous_hash': block_data.get('previous_hash', ''),
                'current_hash': block_data.get('hash', ''),
                'nonce': block_data.get('nonce', 0),
                'memory_type': block_data.get('data', {}).get('type', 'unknown'),
                'content': json.dumps(block_data.get('data', {})),
                'confidence_score': block_data.get('confidence_score', 1.0),
                'emotional_context': block_data.get('emotional_context', {}),
                'signature': block_data.get('signature', ''),
                'timestamp': firestore.SERVER_TIMESTAMP
            }

            memory_ref.set(memory_data)
            return True

        except Exception as e:
            print(f"❌ Firebase memory storage error: {e}")
            return False

    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve conversation history from Firestore"""
        if not self.db:
            return []

        try:
            conversations_ref = self.db.collection('conversations')\
                .where('user_id', '==', user_id)\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(limit)

            docs = conversations_ref.stream()

            conversations = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                conversations.append(data)

            return conversations

        except Exception as e:
            print(f"❌ Firebase conversation query error: {e}")
            return []

    def search_memories(self, query: str, user_id: str = None) -> List[Dict]:
        """Search memory blocks using Firestore queries"""
        if not self.db:
            return []

        try:
            memories_ref = self.db.collection('blockchain_memory')

            # Build query
            if user_id:
                query_ref = memories_ref.where('user_id', '==', user_id)
            else:
                query_ref = memories_ref

            # Note: Firestore doesn't have built-in full-text search like Supabase
            # For production, you'd want to use Algolia or similar
            docs = query_ref.stream()

            results = []
            query_lower = query.lower()

            for doc in docs:
                data = doc.to_dict()
                content = data.get('content', '').lower()

                if query_lower in content:
                    data['id'] = doc.id
                    results.append(data)

            return results

        except Exception as e:
            print(f"❌ Firebase memory search error: {e}")
            return []

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics from Firestore"""
        if not self.db:
            return {}

        try:
            # Get conversation count
            conversations_ref = self.db.collection('conversations')
            conversation_count = len(list(conversations_ref.stream()))

            # Get memory block count
            memories_ref = self.db.collection('blockchain_memory')
            memory_count = len(list(memories_ref.stream()))

            return {
                'total_conversations': conversation_count,
                'total_memory_blocks': memory_count,
                'status': 'connected'
            }

        except Exception as e:
            print(f"❌ Firebase stats error: {e}")
            return {'status': 'error', 'error': str(e)}

    def create_user(self, email: str, password: str, display_name: str = None) -> Dict[str, Any]:
        """Create a new user in Firebase Auth"""
        if not self.auth:
            return {'success': False, 'error': 'Firebase Auth not initialized'}

        try:
            user = self.auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )

            return {
                'success': True,
                'user_id': user.uid,
                'email': user.email
            }

        except Exception as e:
            print(f"❌ Firebase user creation error: {e}")
            return {'success': False, 'error': str(e)}

    def upload_file(self, file_path: str, destination: str) -> str:
        """Upload file to Firebase Storage"""
        if not self.bucket:
            return ""

        try:
            blob = self.bucket.blob(destination)
            blob.upload_from_filename(file_path)

            # Make the file publicly accessible
            blob.make_public()

            return blob.public_url

        except Exception as e:
            print(f"❌ Firebase file upload error: {e}")
            return ""

    def get_firebase_config(self) -> Dict[str, Any]:
        """Get Firebase client configuration for frontend"""
        return self.firebase_config

# Global Firebase manager instance
firebase_manager = FirebaseManager()

def get_firestore_client():
    """Get the Firestore client instance"""
    return firebase_manager.db

def store_conversation_firebase(user_id: str, message: str, response: str,
                               sentiment: float = 0.0, confidence: float = 1.0):
    """Helper function to store conversation"""
    return firebase_manager.store_conversation(user_id, message, response, sentiment, confidence)

def store_memory_firebase(user_id: str, block_data: Dict[str, Any]):
    """Helper function to store memory block"""
    return firebase_manager.store_memory_block(user_id, block_data)

def get_conversation_history_firebase(user_id: str, limit: int = 50):
    """Helper function to get conversation history"""
    return firebase_manager.get_conversation_history(user_id, limit)

def search_memories_firebase(query: str, user_id: str = None):
    """Helper function to search memories"""
    return firebase_manager.search_memories(query, user_id)

def get_system_stats_firebase():
    """Helper function to get system stats"""
    return firebase_manager.get_system_stats()

def get_firebase_config():
    """Helper function to get Firebase config"""
    return firebase_manager.get_firebase_config()
