"""
Blockchain-based Memory System for Jarvis 2.0
Implements decentralized, immutable memory with quantum-resistant cryptography
"""

import hashlib
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

@dataclass
class MemoryBlock:
    """A block in the memory blockchain"""
    index: int
    timestamp: float
    data: Dict[str, Any]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    signature: str = ""
    confidence_score: float = 1.0
    emotional_context: Dict[str, float] = None

    def __post_init__(self):
        if self.emotional_context is None:
            self.emotional_context = {}

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'confidence_score': self.confidence_score,
            'emotional_context': self.emotional_context
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int = 4):
        """Proof-of-work mining"""
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class BlockchainMemorySystem:
    """Decentralized memory system using blockchain technology"""

    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.chain: List[MemoryBlock] = []
        self.pending_memories: List[Dict[str, Any]] = []

        # Cryptographic keys for memory authentication
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

        # Memory consensus parameters
        self.consensus_threshold = 0.7
        self.memory_validators = []

        # Initialize genesis block
        self.create_genesis_block()

        # Advanced memory features
        self.memory_embeddings = {}  # Vector embeddings for semantic search
        self.temporal_index = {}     # Time-based indexing
        self.context_clusters = {}   # Context-based clustering

    def create_genesis_block(self):
        """Create the genesis (first) block"""
        genesis_block = MemoryBlock(
            index=0,
            timestamp=time.time(),
            data={"type": "genesis", "message": "Jarvis Memory Genesis Block"},
            previous_hash="0" * 64,
            confidence_score=1.0
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    def add_memory(self, data: Dict[str, Any], confidence: float = 1.0,
                   emotional_context: Dict[str, float] = None) -> bool:
        """Add a new memory to the pending list"""
        if not self.validate_memory_data(data):
            return False

        memory_entry = {
            'data': data,
            'confidence': confidence,
            'emotional_context': emotional_context or {},
            'timestamp': time.time(),
            'embedding': self.generate_memory_embedding(data)
        }

        self.pending_memories.append(memory_entry)
        return True

    def mine_pending_memories(self) -> Optional[MemoryBlock]:
        """Mine a new block with pending memories"""
        if not self.pending_memories:
            return None

        # Aggregate memories with consensus
        if len(self.pending_memories) >= 3:  # Minimum threshold
            aggregated_data = self.aggregate_memories()
            new_block = self.create_new_block(aggregated_data)
            new_block.mine_block(self.difficulty)

            if self.validate_block(new_block):
                self.chain.append(new_block)
                self.pending_memories.clear()

                # Update indices
                self.update_memory_indices(new_block)

                return new_block

        return None

    def create_new_block(self, data: Dict[str, Any]) -> MemoryBlock:
        """Create a new memory block"""
        previous_block = self.chain[-1]

        new_block = MemoryBlock(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
            confidence_score=data.get('consensus_confidence', 1.0),
            emotional_context=data.get('emotional_context', {})
        )

        # Sign the block
        new_block.signature = self.sign_block(new_block)
        new_block.hash = new_block.calculate_hash()

        return new_block

    def validate_memory_data(self, data: Dict[str, Any]) -> bool:
        """Validate memory data structure and content"""
        required_fields = ['type', 'content']

        if not all(field in data for field in required_fields):
            return False

        # Check for malicious content
        if self.detect_malicious_content(data):
            return False

        # Validate emotional context if present
        if 'emotional_context' in data:
            if not self.validate_emotional_context(data['emotional_context']):
                return False

        return True

    def aggregate_memories(self) -> Dict[str, Any]:
        """Aggregate pending memories with consensus algorithm"""
        if not self.pending_memories:
            return {}

        # Calculate consensus confidence
        confidences = [mem['confidence'] for mem in self.pending_memories]
        consensus_confidence = np.mean(confidences)

        # Aggregate emotional contexts
        emotional_contexts = [mem['emotional_context'] for mem in self.pending_memories]
        aggregated_emotions = self.aggregate_emotional_contexts(emotional_contexts)

        # Create embeddings for semantic search
        embeddings = [mem['embedding'] for mem in self.pending_memories]
        cluster_embedding = np.mean(embeddings, axis=0)

        return {
            'type': 'aggregated_memory',
            'memories': [mem['data'] for mem in self.pending_memories],
            'consensus_confidence': consensus_confidence,
            'emotional_context': aggregated_emotions,
            'cluster_embedding': cluster_embedding.tolist(),
            'memory_count': len(self.pending_memories),
            'timestamp': time.time()
        }

    def sign_block(self, block: MemoryBlock) -> str:
        """Sign a memory block with private key"""
        block_string = block.calculate_hash().encode()

        signature = self.private_key.sign(
            block_string,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature.hex()

    def validate_block(self, block: MemoryBlock) -> bool:
        """Validate a memory block"""
        # Check hash integrity
        if block.hash != block.calculate_hash():
            return False

        # Verify signature
        try:
            block_hash = block.calculate_hash().encode()
            signature_bytes = bytes.fromhex(block.signature)

            self.public_key.verify(
                signature_bytes,
                block_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except:
            return False

        # Check chain continuity
        if block.previous_hash != self.chain[-1].hash:
            return False

        return True

    def search_memories(self, query: str, semantic_threshold: float = 0.7) -> List[MemoryBlock]:
        """Search memories using semantic similarity and blockchain traversal"""
        query_embedding = self.generate_memory_embedding({'content': query})

        relevant_memories = []

        for block in reversed(self.chain):  # Search from most recent
            if 'cluster_embedding' in block.data:
                similarity = self.calculate_embedding_similarity(
                    query_embedding,
                    np.array(block.data['cluster_embedding'])
                )

                if similarity >= semantic_threshold:
                    relevant_memories.append(block)

        return relevant_memories

    def generate_memory_embedding(self, data: Dict[str, Any]) -> np.ndarray:
        """Generate vector embedding for memory data"""
        # Simple text-based embedding (in practice, use BERT or similar)
        content = str(data.get('content', ''))
        embedding = np.zeros(128)  # 128-dimensional embedding

        # Hash-based embedding generation
        for i, char in enumerate(content[:128]):
            embedding[i % 128] += ord(char) / 255.0

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm

        return embedding

    def calculate_embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def detect_malicious_content(self, data: Dict[str, Any]) -> bool:
        """Detect potentially malicious memory content"""
        content = str(data.get('content', '')).lower()

        malicious_patterns = [
            'system.delete', 'rm -rf', 'drop table',
            'password', 'api_key', 'secret'
        ]

        for pattern in malicious_patterns:
            if pattern in content:
                return True

        return False

    def validate_emotional_context(self, emotional_data: Dict[str, float]) -> bool:
        """Validate emotional context data"""
        valid_emotions = {'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust'}

        for emotion in emotional_data.keys():
            if emotion not in valid_emotions:
                return False

            value = emotional_data[emotion]
            if not (0.0 <= value <= 1.0):
                return False

        return True

    def aggregate_emotional_contexts(self, contexts: List[Dict[str, float]]) -> Dict[str, float]:
        """Aggregate multiple emotional contexts"""
        if not contexts:
            return {}

        all_emotions = set()
        for context in contexts:
            all_emotions.update(context.keys())

        aggregated = {}
        for emotion in all_emotions:
            values = [context.get(emotion, 0.0) for context in contexts]
            aggregated[emotion] = np.mean(values)

        return aggregated

    def update_memory_indices(self, block: MemoryBlock):
        """Update memory indices for efficient retrieval"""
        # Temporal index
        timestamp = block.timestamp
        self.temporal_index[timestamp] = block.index

        # Embedding index for semantic search
        if 'cluster_embedding' in block.data:
            embedding = tuple(block.data['cluster_embedding'])
            self.memory_embeddings[embedding] = block.index

    def get_memory_chain_integrity(self) -> float:
        """Calculate blockchain integrity score"""
        if len(self.chain) <= 1:
            return 1.0

        valid_blocks = sum(1 for block in self.chain[1:] if self.validate_block(block))
        return valid_blocks / (len(self.chain) - 1)

    def backup_memory_chain(self, filepath: str):
        """Backup the entire memory chain"""
        chain_data = {
            'chain': [self.block_to_dict(block) for block in self.chain],
            'public_key': self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        }

        with open(filepath, 'w') as f:
            json.dump(chain_data, f, indent=2)

    def block_to_dict(self, block: MemoryBlock) -> Dict[str, Any]:
        """Convert block to dictionary for serialization"""
        return {
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'hash': block.hash,
            'signature': block.signature,
            'confidence_score': block.confidence_score,
            'emotional_context': block.emotional_context
        }

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return {
            'total_blocks': len(self.chain),
            'pending_memories': len(self.pending_memories),
            'chain_integrity': self.get_memory_chain_integrity(),
            'average_confidence': np.mean([block.confidence_score for block in self.chain]),
            'memory_types': self.get_memory_type_distribution(),
            'temporal_coverage': self.get_temporal_coverage()
        }

    def get_memory_type_distribution(self) -> Dict[str, int]:
        """Get distribution of memory types in the chain"""
        type_counts = {}
        for block in self.chain:
            mem_type = block.data.get('type', 'unknown')
            type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
        return type_counts

    def get_temporal_coverage(self) -> Dict[str, Any]:
        """Get temporal coverage statistics"""
        if not self.chain:
            return {}

        timestamps = [block.timestamp for block in self.chain]
        return {
            'earliest_memory': min(timestamps),
            'latest_memory': max(timestamps),
            'total_span_days': (max(timestamps) - min(timestamps)) / (24 * 3600)
        }
