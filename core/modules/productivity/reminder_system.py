"""
Reminder and notification system for Jarvis AI Assistant
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class ReminderType(Enum):
    """Types of reminders"""
    TASK = "task"
    APPOINTMENT = "appointment"
    MEDICATION = "medication"
    BREAK = "break"
    CUSTOM = "custom"

class ReminderPriority(Enum):
    """Reminder priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class Reminder:
    """Reminder data structure"""
    id: str
    title: str
    message: str
    reminder_time: datetime
    reminder_type: ReminderType
    priority: ReminderPriority
    user_id: str
    is_sent: bool = False
    is_acknowledged: bool = False
    created_at: datetime = None
    repeat_interval: Optional[str] = None  # daily, weekly, monthly
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class ReminderSystem:
    """Manages reminders and notifications"""
    
    def __init__(self, notification_callback: Optional[Callable] = None):
        self.notification_callback = notification_callback
        self.reminders: Dict[str, Reminder] = {}
        self.active_reminders: Dict[str, List[str]] = {}  # user_id -> reminder_ids
        
        # Background processing
        self.is_running = False
        self.reminder_thread = None
        self.check_interval = 30  # seconds
        
        logger.info("Reminder System initialized")
    
    def start(self):
        """Start the reminder system background processing"""
        if self.is_running:
            return
        
        self.is_running = True
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        
        logger.info("Reminder system started")
    
    def stop(self):
        """Stop the reminder system"""
        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=5)
        
        logger.info("Reminder system stopped")
    
    def create_reminder(self, 
                       user_id: str,
                       title: str,
                       message: str,
                       reminder_time: datetime,
                       reminder_type: ReminderType = ReminderType.CUSTOM,
                       priority: ReminderPriority = ReminderPriority.MEDIUM,
                       repeat_interval: Optional[str] = None) -> str:
        """
        Create a new reminder
        
        Args:
            user_id: User identifier
            title: Reminder title
            message: Reminder message
            reminder_time: When to trigger the reminder
            reminder_type: Type of reminder
            priority: Priority level
            repeat_interval: Repeat pattern (daily, weekly, monthly)
            
        Returns:
            Reminder ID
        """
        try:
            reminder_id = str(uuid.uuid4())
            
            reminder = Reminder(
                id=reminder_id,
                title=title,
                message=message,
                reminder_time=reminder_time,
                reminder_type=reminder_type,
                priority=priority,
                user_id=user_id,
                repeat_interval=repeat_interval
            )
            
            # Store reminder
            self.reminders[reminder_id] = reminder
            
            # Add to user's active reminders
            if user_id not in self.active_reminders:
                self.active_reminders[user_id] = []
            self.active_reminders[user_id].append(reminder_id)
            
            logger.info(f"Created reminder '{title}' for user {user_id} at {reminder_time}")
            return reminder_id
            
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return ""
    
    def get_user_reminders(self, 
                          user_id: str, 
                          include_sent: bool = False,
                          upcoming_hours: Optional[int] = None) -> List[Reminder]:
        """
        Get reminders for a user
        
        Args:
            user_id: User identifier
            include_sent: Include already sent reminders
            upcoming_hours: Only include reminders in next N hours
            
        Returns:
            List of reminders
        """
        try:
            if user_id not in self.active_reminders:
                return []
            
            user_reminder_ids = self.active_reminders[user_id]
            reminders = []
            
            current_time = datetime.now()
            cutoff_time = None
            if upcoming_hours:
                cutoff_time = current_time + timedelta(hours=upcoming_hours)
            
            for reminder_id in user_reminder_ids:
                if reminder_id in self.reminders:
                    reminder = self.reminders[reminder_id]
                    
                    # Filter by sent status
                    if not include_sent and reminder.is_sent:
                        continue
                    
                    # Filter by time window
                    if cutoff_time and reminder.reminder_time > cutoff_time:
                        continue
                    
                    reminders.append(reminder)
            
            # Sort by reminder time
            reminders.sort(key=lambda r: r.reminder_time)
            return reminders
            
        except Exception as e:
            logger.error(f"Error getting user reminders: {e}")
            return []
    
    def acknowledge_reminder(self, reminder_id: str) -> bool:
        """Mark a reminder as acknowledged"""
        try:
            if reminder_id in self.reminders:
                self.reminders[reminder_id].is_acknowledged = True
                logger.info(f"Reminder {reminder_id} acknowledged")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging reminder: {e}")
            return False
    
    def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel a reminder"""
        try:
            if reminder_id in self.reminders:
                reminder = self.reminders[reminder_id]
                user_id = reminder.user_id
                
                # Remove from reminders
                del self.reminders[reminder_id]
                
                # Remove from user's active reminders
                if user_id in self.active_reminders:
                    if reminder_id in self.active_reminders[user_id]:
                        self.active_reminders[user_id].remove(reminder_id)
                
                logger.info(f"Cancelled reminder {reminder_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling reminder: {e}")
            return False
    
    def snooze_reminder(self, reminder_id: str, snooze_minutes: int = 10) -> bool:
        """Snooze a reminder for specified minutes"""
        try:
            if reminder_id in self.reminders:
                reminder = self.reminders[reminder_id]
                reminder.reminder_time = datetime.now() + timedelta(minutes=snooze_minutes)
                reminder.is_sent = False
                reminder.is_acknowledged = False
                
                logger.info(f"Snoozed reminder {reminder_id} for {snooze_minutes} minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error snoozing reminder: {e}")
            return False
    
    def _reminder_loop(self):
        """Background loop to check and send reminders"""
        while self.is_running:
            try:
                self._check_and_send_reminders()
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in reminder loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_and_send_reminders(self):
        """Check for due reminders and send notifications"""
        current_time = datetime.now()
        
        for reminder_id, reminder in list(self.reminders.items()):
            if (not reminder.is_sent and 
                not reminder.is_acknowledged and 
                reminder.reminder_time <= current_time):
                
                # Send reminder
                self._send_reminder(reminder)
                
                # Handle repeating reminders
                if reminder.repeat_interval:
                    self._schedule_repeat_reminder(reminder)
                else:
                    # Mark as sent for one-time reminders
                    reminder.is_sent = True
    
    def _send_reminder(self, reminder: Reminder):
        """Send a reminder notification"""
        try:
            logger.info(f"Sending reminder: {reminder.title} to user {reminder.user_id}")
            
            # Call notification callback if provided
            if self.notification_callback:
                try:
                    self.notification_callback(reminder)
                except Exception as e:
                    logger.error(f"Error in notification callback: {e}")
            
            # Default notification (print to console)
            priority_emoji = {
                ReminderPriority.LOW: "🔵",
                ReminderPriority.MEDIUM: "🟡", 
                ReminderPriority.HIGH: "🟠",
                ReminderPriority.URGENT: "🔴"
            }
            
            emoji = priority_emoji.get(reminder.priority, "⏰")
            print(f"{emoji} REMINDER: {reminder.title}")
            print(f"   {reminder.message}")
            
            reminder.is_sent = True
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def _schedule_repeat_reminder(self, reminder: Reminder):
        """Schedule the next occurrence of a repeating reminder"""
        try:
            if reminder.repeat_interval == "daily":
                next_time = reminder.reminder_time + timedelta(days=1)
            elif reminder.repeat_interval == "weekly":
                next_time = reminder.reminder_time + timedelta(weeks=1)
            elif reminder.repeat_interval == "monthly":
                # Approximate monthly repeat (30 days)
                next_time = reminder.reminder_time + timedelta(days=30)
            else:
                return
            
            # Create new reminder for next occurrence
            new_reminder_id = self.create_reminder(
                user_id=reminder.user_id,
                title=reminder.title,
                message=reminder.message,
                reminder_time=next_time,
                reminder_type=reminder.reminder_type,
                priority=reminder.priority,
                repeat_interval=reminder.repeat_interval
            )
            
            logger.info(f"Scheduled repeat reminder {new_reminder_id} for {next_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling repeat reminder: {e}")
    
    def get_reminder_stats(self, user_id: str) -> Dict[str, int]:
        """Get reminder statistics for a user"""
        try:
            if user_id not in self.active_reminders:
                return {
                    'total_reminders': 0,
                    'pending_reminders': 0,
                    'sent_reminders': 0,
                    'acknowledged_reminders': 0
                }
            
            user_reminder_ids = self.active_reminders[user_id]
            total = len(user_reminder_ids)
            pending = 0
            sent = 0
            acknowledged = 0
            
            for reminder_id in user_reminder_ids:
                if reminder_id in self.reminders:
                    reminder = self.reminders[reminder_id]
                    
                    if reminder.is_acknowledged:
                        acknowledged += 1
                    elif reminder.is_sent:
                        sent += 1
                    else:
                        pending += 1
            
            return {
                'total_reminders': total,
                'pending_reminders': pending,
                'sent_reminders': sent,
                'acknowledged_reminders': acknowledged
            }
            
        except Exception as e:
            logger.error(f"Error getting reminder stats: {e}")
            return {}
    
    def cleanup_old_reminders(self, days_old: int = 7) -> int:
        """Clean up old acknowledged reminders"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_old)
            removed_count = 0
            
            for reminder_id in list(self.reminders.keys()):
                reminder = self.reminders[reminder_id]
                
                if (reminder.is_acknowledged and 
                    reminder.reminder_time < cutoff_time):
                    
                    # Remove from reminders
                    del self.reminders[reminder_id]
                    
                    # Remove from user's active reminders
                    user_id = reminder.user_id
                    if (user_id in self.active_reminders and 
                        reminder_id in self.active_reminders[user_id]):
                        self.active_reminders[user_id].remove(reminder_id)
                    
                    removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old reminders")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up reminders: {e}")
            return 0