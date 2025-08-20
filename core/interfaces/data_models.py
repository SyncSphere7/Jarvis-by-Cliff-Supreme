"""
Core data models for Jarvis
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class Task:
    """Task management data model"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

@dataclass
class SmartDevice:
    """Smart home device model"""
    device_id: str
    name: str
    device_type: str
    protocol: str  # zigbee, zwave, wifi
    capabilities: List[str]
    current_state: Dict[str, Any]
    is_online: bool = True

@dataclass
class HealthMetric:
    """Health and wellness data model"""
    metric_type: str  # steps, heart_rate, sleep, etc.
    value: float
    unit: str
    timestamp: datetime
    source: str  # fitbit, apple_watch, manual, etc.

@dataclass
class LearningSession:
    """Learning and education session"""
    session_id: str
    topic: str
    duration_minutes: int
    progress_percentage: float
    completed_at: datetime
    notes: str = ""

@dataclass
class MediaItem:
    """Entertainment media item"""
    item_id: str
    title: str
    media_type: str  # music, video, podcast, etc.
    source: str  # spotify, youtube, local, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommunicationMessage:
    """Communication message model"""
    message_id: str
    sender: str
    recipient: str
    content: str
    message_type: str  # email, sms, chat, etc.
    timestamp: datetime
    is_read: bool = False
    priority: int = 1

@dataclass
class Intent:
    """Intent recognition data model"""
    text: str
    intent_type: str
    entities: Dict[str, Any]
    confidence: float
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ModuleResponse:
    """Module response data model"""
    success: bool
    response: str
    confidence: float
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserProfile:
    """User profile data model"""
    user_id: str
    name: str
    preferences: Dict[str, Any]
    learning_history: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)