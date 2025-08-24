"""
Jarvis 2.0 - Supabase Integration
Using Supabase for PostgreSQL database and real-time features
"""

import os
from supabase import create_client, Client
from typing import Dict, Any, List
import json
from datetime import datetime

class SupabaseManager:
    """Manages Supabase database integration for Jarvis"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            print("⚠️  Supabase credentials not found")
            print("   Please set SUPABASE_URL and SUPABASE_ANON_KEY")
            self.client = None
        else:
            self.client = create_client(self.supabase_url, self.supabase_key)

    def store_conversation(self, user_id: str, message: str, response: str,
                          sentiment: float = 0.0, confidence: float = 1.0) -> bool:
        """Store conversation in Supabase"""
        if not self.client:
            return False

        try:
            data = {
                'user_id': user_id,
                'message': message,
                'response': response,
                'sentiment': sentiment,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'session_id': f"session_{user_id}_{int(datetime.now().timestamp())}"
            }

            result = self.client.table('conversations').insert(data).execute()
            return len(result.data) > 0

        except Exception as e:
            print(f"❌ Supabase error: {e}")
            return False

    def store_memory_block(self, user_id: str, block_data: Dict[str, Any]) -> bool:
        """Store blockchain memory block in Supabase"""
        if not self.client:
            return False

        try:
            # Convert complex data to JSON strings
            memory_data = {
                'user_id': user_id,
                'block_index': block_data.get('index', 0),
                'previous_hash': block_data.get('previous_hash', ''),
                'current_hash': block_data.get('hash', ''),
                'nonce': block_data.get('nonce', 0),
                'memory_type': block_data.get('data', {}).get('type', 'unknown'),
                'content': json.dumps(block_data.get('data', {})),
                'confidence_score': block_data.get('confidence_score', 1.0),
                'emotional_context': json.dumps(block_data.get('emotional_context', {})),
                'signature': block_data.get('signature', ''),
                'timestamp': datetime.now().isoformat()
            }

            result = self.client.table('blockchain_memory').insert(memory_data).execute()
            return len(result.data) > 0

        except Exception as e:
            print(f"❌ Supabase memory storage error: {e}")
            return False

    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve conversation history"""
        if not self.client:
            return []

        try:
            result = self.client.table('conversations')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()

            return result.data

        except Exception as e:
            print(f"❌ Supabase query error: {e}")
            return []

    def search_memories(self, query: str, user_id: str = None) -> List[Dict]:
        """Search memory blocks using Supabase full-text search"""
        if not self.client:
            return []

        try:
            # Use Supabase's built-in text search
            search_filter = {'content': f"ilike.*{query}*"}
            if user_id:
                search_filter['user_id'] = f"eq.{user_id}"

            result = self.client.table('blockchain_memory')\
                .select('*')\
                .match(search_filter)\
                .execute()

            return result.data

        except Exception as e:
            print(f"❌ Supabase search error: {e}")
            return []

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics from Supabase"""
        if not self.client:
            return {}

        try:
            # Get conversation count
            conv_result = self.client.table('conversations').select('id', count='exact').execute()
            conversation_count = conv_result.count

            # Get memory block count
            mem_result = self.client.table('blockchain_memory').select('id', count='exact').execute()
            memory_count = mem_result.count

            # Get recent activity
            recent = self.client.table('conversations')\
                .select('timestamp')\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()

            last_activity = recent.data[0]['timestamp'] if recent.data else None

            return {
                'total_conversations': conversation_count,
                'total_memory_blocks': memory_count,
                'last_activity': last_activity,
                'status': 'connected'
            }

        except Exception as e:
            print(f"❌ Supabase stats error: {e}")
            return {'status': 'error', 'error': str(e)}

    def initialize_tables(self):
        """Initialize required tables in Supabase"""
        if not self.client:
            return False

        try:
            # Note: In a real implementation, you'd create these tables
            # through the Supabase dashboard or migration scripts

            print("📊 Supabase tables should be created in your dashboard:")
            print("   1. conversations")
            print("   2. blockchain_memory")
            print("   3. system_metrics")
            print("   4. api_keys")

            return True

        except Exception as e:
            print(f"❌ Supabase initialization error: {e}")
            return False

# Global Supabase manager instance
supabase_manager = SupabaseManager()

def get_supabase_client():
    """Get the Supabase client instance"""
    return supabase_manager.client

def store_conversation_supabase(user_id: str, message: str, response: str,
                               sentiment: float = 0.0, confidence: float = 1.0):
    """Helper function to store conversation"""
    return supabase_manager.store_conversation(user_id, message, response, sentiment, confidence)

def store_memory_supabase(user_id: str, block_data: Dict[str, Any]):
    """Helper function to store memory block"""
    return supabase_manager.store_memory_block(user_id, block_data)

def get_conversation_history_supabase(user_id: str, limit: int = 50):
    """Helper function to get conversation history"""
    return supabase_manager.get_conversation_history(user_id, limit)

def search_memories_supabase(query: str, user_id: str = None):
    """Helper function to search memories"""
    return supabase_manager.search_memories(query, user_id)

def get_system_stats_supabase():
    """Helper function to get system stats"""
    return supabase_manager.get_system_stats()
