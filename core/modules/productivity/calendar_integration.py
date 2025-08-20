"""
Calendar integration for Jarvis AI Assistant
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from core.interfaces.base_module import BaseModule, Intent, IntentType, ModuleResponse
from core.modules.productivity.reminder_system import ReminderSystem, ReminderType, ReminderPriority

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of calendar events"""
    MEETING = "meeting"
    APPOINTMENT = "appointment"
    REMINDER = "reminder"
    TASK_DEADLINE = "task_deadline"
    PERSONAL = "personal"

@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    event_type: EventType
    user_id: str
    location: Optional[str] = None
    attendees: List[str] = None
    is_all_day: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.attendees is None:
            self.attendees = []

class CalendarIntegration(BaseModule):
    """Simple calendar integration with basic scheduling"""
    
    def __init__(self, reminder_system: ReminderSystem):
        super().__init__("calendar_integration")
        self.reminder_system = reminder_system
        self.capabilities = [
            "schedule_event", "list_events", "cancel_event", 
            "check_availability", "get_schedule"
        ]
        
        # Simple in-memory storage for demo
        self.events: Dict[str, Dict[str, CalendarEvent]] = {}  # user_id -> event_id -> Event
        
        logger.info("Calendar Integration initialized")
    
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        # For now, we'll handle calendar-related task management
        return (intent.intent_type == IntentType.TASK_MANAGEMENT and 
                any(word in intent.action.lower() for word in ['schedule', 'calendar', 'meeting', 'appointment']))
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute calendar commands"""
        try:
            user_id = context.get('user_id', 'default')
            action = intent.action.lower()
            
            if user_id not in self.events:
                self.events[user_id] = {}
            
            if any(word in action for word in ['schedule', 'create', 'add']):
                return self._schedule_event(intent, user_id)
            elif any(word in action for word in ['list', 'show', 'calendar']):
                return self._list_events(user_id)
            elif any(word in action for word in ['cancel', 'delete', 'remove']):
                return self._cancel_event(intent, user_id)
            elif any(word in action for word in ['available', 'free', 'busy']):
                return self._check_availability(intent, user_id)
            else:
                return ModuleResponse(
                    success=False,
                    message="I can help you schedule events, list your calendar, or check availability.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error in calendar integration: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while managing your calendar.",
                data={"error": str(e)}
            )
    
    def _schedule_event(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Schedule a new calendar event"""
        try:
            # Extract event details
            title = self._extract_event_title(intent.action)
            if not title:
                return ModuleResponse(
                    success=False,
                    message="I need an event title. Try saying 'schedule meeting: team standup'",
                    data={}
                )
            
            # Extract time information
            start_time, end_time = self._extract_event_times(intent.entities)
            if not start_time:
                # Default to 1 hour from now
                start_time = datetime.now() + timedelta(hours=1)
                end_time = start_time + timedelta(hours=1)
            
            # Determine event type
            event_type = self._determine_event_type(title, intent.action)
            
            # Check for conflicts
            conflicts = self._check_conflicts(user_id, start_time, end_time)
            if conflicts:
                conflict_titles = [event.title for event in conflicts]
                return ModuleResponse(
                    success=False,
                    message=f"Time conflict detected with: {', '.join(conflict_titles)}. Please choose a different time.",
                    data={"conflicts": [asdict(event) for event in conflicts]}
                )
            
            # Create event
            event = CalendarEvent(
                id=str(uuid.uuid4()),
                title=title,
                description="",
                start_time=start_time,
                end_time=end_time,
                event_type=event_type,
                user_id=user_id
            )
            
            # Store event
            self.events[user_id][event.id] = event
            
            # Create reminder 15 minutes before
            reminder_time = start_time - timedelta(minutes=15)
            if reminder_time > datetime.now():
                self.reminder_system.create_reminder(
                    user_id=user_id,
                    title=f"Upcoming: {title}",
                    message=f"Your {event_type.value} '{title}' starts in 15 minutes",
                    reminder_time=reminder_time,
                    reminder_type=ReminderType.APPOINTMENT,
                    priority=ReminderPriority.MEDIUM
                )
            
            return ModuleResponse(
                success=True,
                message=f"Scheduled '{title}' for {start_time.strftime('%Y-%m-%d at %I:%M %p')}",
                data={"event": asdict(event)}
            )
            
        except Exception as e:
            logger.error(f"Error scheduling event: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't schedule the event.",
                data={"error": str(e)}
            )
    
    def _list_events(self, user_id: str, days_ahead: int = 7) -> ModuleResponse:
        """List upcoming events"""
        try:
            user_events = list(self.events[user_id].values())
            
            # Filter to upcoming events
            current_time = datetime.now()
            end_time = current_time + timedelta(days=days_ahead)
            
            upcoming_events = [
                event for event in user_events
                if current_time <= event.start_time <= end_time
            ]
            
            if not upcoming_events:
                return ModuleResponse(
                    success=True,
                    message=f"You have no events scheduled for the next {days_ahead} days.",
                    data={"events": []}
                )
            
            # Sort by start time
            upcoming_events.sort(key=lambda e: e.start_time)
            
            # Format message
            message = f"Here are your upcoming events:\\n\\n"
            for i, event in enumerate(upcoming_events[:10], 1):
                start_str = event.start_time.strftime('%m/%d at %I:%M %p')
                message += f"{i}. {event.title} - {start_str}\\n"
            
            if len(upcoming_events) > 10:
                message += f"\\n... and {len(upcoming_events) - 10} more events"
            
            return ModuleResponse(
                success=True,
                message=message.strip(),
                data={
                    "events": [asdict(event) for event in upcoming_events],
                    "count": len(upcoming_events)
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't retrieve your calendar events.",
                data={"error": str(e)}
            )
    
    def _cancel_event(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Cancel a calendar event"""
        try:
            event_title = self._extract_event_title(intent.action)
            if not event_title:
                return ModuleResponse(
                    success=False,
                    message="Which event would you like to cancel?",
                    data={}
                )
            
            # Find matching event
            matching_event = None
            for event in self.events[user_id].values():
                if event_title.lower() in event.title.lower():
                    matching_event = event
                    break
            
            if not matching_event:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't find an event matching '{event_title}'.",
                    data={}
                )
            
            # Remove event
            del self.events[user_id][matching_event.id]
            
            return ModuleResponse(
                success=True,
                message=f"Cancelled '{matching_event.title}'",
                data={"cancelled_event": asdict(matching_event)}
            )
            
        except Exception as e:
            logger.error(f"Error cancelling event: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't cancel the event.",
                data={"error": str(e)}
            )
    
    def _check_availability(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Check availability for a time period"""
        try:
            # For now, just check if there are any events today
            today = datetime.now().date()
            today_events = [
                event for event in self.events[user_id].values()
                if event.start_time.date() == today
            ]
            
            if not today_events:
                return ModuleResponse(
                    success=True,
                    message="You're free today! No events scheduled.",
                    data={"available": True, "events_today": 0}
                )
            else:
                return ModuleResponse(
                    success=True,
                    message=f"You have {len(today_events)} event(s) scheduled today.",
                    data={
                        "available": False, 
                        "events_today": len(today_events),
                        "events": [asdict(event) for event in today_events]
                    }
                )
                
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't check your availability.",
                data={"error": str(e)}
            )
    
    def _extract_event_title(self, action: str) -> Optional[str]:
        """Extract event title from action"""
        import re
        
        patterns = [
            r'schedule:?\s*(.+)',
            r'create event:?\s*(.+)',
            r'add event:?\s*(.+)',
            r'meeting:?\s*(.+)',
            r'appointment:?\s*(.+)',
            r'cancel:?\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, action, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_event_times(self, entities: Dict[str, Any]) -> tuple:
        """Extract start and end times from entities"""
        # Simplified time extraction - could be enhanced
        start_time = None
        end_time = None
        
        # Look for time entities
        if 'time' in entities:
            # Use first time as start time
            start_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)  # Default 2 PM
            end_time = start_time + timedelta(hours=1)  # 1 hour duration
        
        return start_time, end_time
    
    def _determine_event_type(self, title: str, action: str) -> EventType:
        """Determine event type from title and action"""
        title_lower = title.lower()
        action_lower = action.lower()
        
        if any(word in title_lower or word in action_lower for word in ['meeting', 'standup', 'call']):
            return EventType.MEETING
        elif any(word in title_lower or word in action_lower for word in ['appointment', 'doctor', 'dentist']):
            return EventType.APPOINTMENT
        elif any(word in title_lower or word in action_lower for word in ['reminder', 'remind']):
            return EventType.REMINDER
        else:
            return EventType.PERSONAL
    
    def _check_conflicts(self, user_id: str, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        for event in self.events[user_id].values():
            # Check if times overlap
            if (start_time < event.end_time and end_time > event.start_time):
                conflicts.append(event)
        
        return conflicts
    
    def get_calendar_stats(self, user_id: str) -> Dict[str, Any]:
        """Get calendar statistics"""
        try:
            if user_id not in self.events:
                return {
                    'total_events': 0,
                    'events_today': 0,
                    'events_this_week': 0,
                    'upcoming_events': 0
                }
            
            user_events = list(self.events[user_id].values())
            current_time = datetime.now()
            today = current_time.date()
            week_end = current_time + timedelta(days=7)
            
            total_events = len(user_events)
            events_today = len([e for e in user_events if e.start_time.date() == today])
            events_this_week = len([e for e in user_events if current_time <= e.start_time <= week_end])
            upcoming_events = len([e for e in user_events if e.start_time > current_time])
            
            return {
                'total_events': total_events,
                'events_today': events_today,
                'events_this_week': events_this_week,
                'upcoming_events': upcoming_events
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar stats: {e}")
            return {}