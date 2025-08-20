"""
Unit tests for task management system
"""

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock

from core.modules.productivity.task_manager import TaskManager, TaskSortBy, TaskFilter
from core.modules.productivity.reminder_system import ReminderSystem, ReminderType, ReminderPriority
from core.interfaces.base_module import Intent, IntentType
from core.interfaces.data_models import TaskStatus, TaskPriority
from core.security.data_encryption import DataEncryption
from core.security.privacy_manager import PrivacyManager, DataCategory, ConsentLevel
from core.security.secure_storage import SecureStorage

class TestTaskManager(unittest.TestCase):
    """Test cases for Task Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Set up security components
        self.encryption = DataEncryption()
        self.privacy_manager = PrivacyManager(self.encryption, self.temp_dir)
        self.secure_storage = SecureStorage(self.encryption, self.privacy_manager, self.temp_dir)
        
        # Create task manager
        self.task_manager = TaskManager(self.secure_storage)
        
        # Set up user with consent
        self.user_id = "test_user"
        self.privacy_manager.update_consent(
            user_id=self.user_id,
            category=DataCategory.PREFERENCES,
            consent_level=ConsentLevel.ENHANCED,
            purpose="Task management testing"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_task_manager_initialization(self):
        """Test task manager initialization"""
        self.assertEqual(self.task_manager.name, "task_manager")
        self.assertIn("create_task", self.task_manager.capabilities)
        self.assertIn("list_tasks", self.task_manager.capabilities)
    
    def test_can_handle_intent(self):
        """Test intent handling capability"""
        # Task management intent should be handled
        task_intent = Intent(
            action="create",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        self.assertTrue(self.task_manager.can_handle(task_intent))
        
        # Non-task intent should not be handled
        other_intent = Intent(
            action="play",
            intent_type=IntentType.ENTERTAINMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        self.assertFalse(self.task_manager.can_handle(other_intent))
    
    def test_create_task(self):
        """Test task creation"""
        intent = Intent(
            action="create",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={"original_text": "create task: Buy groceries"},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, {"user_id": self.user_id})
        
        self.assertTrue(response.success)
        self.assertIn("Buy groceries", response.message)
        self.assertIn("task_id", response.data)
        self.assertEqual(response.data["action"], "task_created")
    
    def test_list_tasks_empty(self):
        """Test listing tasks when none exist"""
        intent = Intent(
            action="list",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, {"user_id": self.user_id})
        
        self.assertTrue(response.success)
        self.assertIn("don't have any tasks", response.message)
        self.assertEqual(response.data["count"], 0)
    
    def test_create_and_list_tasks(self):
        """Test creating and then listing tasks"""
        # Create a task
        create_intent = Intent(
            action="create",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={"original_text": "create task: Test task"},
            timestamp=datetime.now()
        )
        
        create_response = self.task_manager.execute(create_intent, {"user_id": self.user_id})
        self.assertTrue(create_response.success)
        
        # List tasks
        list_intent = Intent(
            action="list",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        list_response = self.task_manager.execute(list_intent, {"user_id": self.user_id})
        
        self.assertTrue(list_response.success)
        self.assertEqual(list_response.data["count"], 1)
        self.assertIn("Test task", list_response.message)
    
    def test_complete_task(self):
        """Test completing a task"""
        # Create a task first
        create_intent = Intent(
            action="create",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={"original_text": "create task: Complete me"},
            timestamp=datetime.now()
        )
        
        self.task_manager.execute(create_intent, {"user_id": self.user_id})
        
        # Complete the task
        complete_intent = Intent(
            action="complete",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={"original_text": "complete Complete me"},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(complete_intent, {"user_id": self.user_id})
        
        self.assertTrue(response.success)
        self.assertIn("marked", response.message)
        self.assertIn("complete", response.message)
        self.assertEqual(response.data["action"], "task_completed")
    
    def test_task_statistics(self):
        """Test getting task statistics"""
        # Create some tasks
        tasks_to_create = [
            "Task 1",
            "Task 2", 
            "Task 3"
        ]
        
        for task_title in tasks_to_create:
            intent = Intent(
                action="create",
                intent_type=IntentType.TASK_MANAGEMENT,
                entities={},
                confidence=0.9,
                context={"original_text": f"create task: {task_title}"},
                timestamp=datetime.now()
            )
            self.task_manager.execute(intent, {"user_id": self.user_id})
        
        # Get statistics
        stats = self.task_manager.get_task_statistics(self.user_id)
        
        self.assertEqual(stats["total_tasks"], 3)
        self.assertEqual(stats["pending"], 3)
        self.assertEqual(stats["completed"], 0)
    
    def test_task_persistence(self):
        """Test that tasks are saved and loaded correctly"""
        # Create a task
        intent = Intent(
            action="create",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={"original_text": "create task: Persistent task"},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, {"user_id": self.user_id})
        self.assertTrue(response.success)
        
        # Create a new task manager instance (simulating restart)
        new_task_manager = TaskManager(self.secure_storage)
        
        # List tasks with new instance
        list_intent = Intent(
            action="list",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        list_response = new_task_manager.execute(list_intent, {"user_id": self.user_id})
        
        self.assertTrue(list_response.success)
        self.assertEqual(list_response.data["count"], 1)
        self.assertIn("Persistent task", list_response.message)

class TestReminderSystem(unittest.TestCase):
    """Test cases for Reminder System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notification_callback = Mock()
        self.reminder_system = ReminderSystem(self.notification_callback)
        self.user_id = "test_user"
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.reminder_system.stop()
    
    def test_reminder_system_initialization(self):
        """Test reminder system initialization"""
        self.assertIsNotNone(self.reminder_system)
        self.assertFalse(self.reminder_system.is_running)
    
    def test_create_reminder(self):
        """Test creating a reminder"""
        reminder_time = datetime.now() + timedelta(minutes=5)
        
        reminder_id = self.reminder_system.create_reminder(
            user_id=self.user_id,
            title="Test Reminder",
            message="This is a test reminder",
            reminder_time=reminder_time,
            reminder_type=ReminderType.CUSTOM,
            priority=ReminderPriority.MEDIUM
        )
        
        self.assertIsNotNone(reminder_id)
        self.assertIn(reminder_id, self.reminder_system.reminders)
        
        reminder = self.reminder_system.reminders[reminder_id]
        self.assertEqual(reminder.title, "Test Reminder")
        self.assertEqual(reminder.user_id, self.user_id)
    
    def test_get_user_reminders(self):
        """Test getting user reminders"""
        # Create multiple reminders
        reminder_time = datetime.now() + timedelta(minutes=5)
        
        for i in range(3):
            self.reminder_system.create_reminder(
                user_id=self.user_id,
                title=f"Reminder {i+1}",
                message=f"Test reminder {i+1}",
                reminder_time=reminder_time + timedelta(minutes=i),
                reminder_type=ReminderType.CUSTOM
            )
        
        reminders = self.reminder_system.get_user_reminders(self.user_id)
        
        self.assertEqual(len(reminders), 3)
        self.assertEqual(reminders[0].title, "Reminder 1")  # Should be sorted by time
    
    def test_upcoming_reminders(self):
        """Test getting upcoming reminders"""
        # Create reminders at different times
        now = datetime.now()
        
        # One in 30 minutes (should be included)
        self.reminder_system.create_reminder(
            user_id=self.user_id,
            title="Soon",
            message="Coming up soon",
            reminder_time=now + timedelta(minutes=30)
        )
        
        # One in 2 days (should not be included in 24h window)
        self.reminder_system.create_reminder(
            user_id=self.user_id,
            title="Later",
            message="Coming up later",
            reminder_time=now + timedelta(days=2)
        )
        
        upcoming = self.reminder_system.get_upcoming_reminders(self.user_id, hours_ahead=24)
        
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].title, "Soon")
    
    def test_cancel_reminder(self):
        """Test cancelling a reminder"""
        reminder_time = datetime.now() + timedelta(minutes=5)
        
        reminder_id = self.reminder_system.create_reminder(
            user_id=self.user_id,
            title="Cancel Me",
            message="This reminder will be cancelled",
            reminder_time=reminder_time
        )
        
        # Cancel the reminder
        success = self.reminder_system.cancel_reminder(reminder_id, self.user_id)
        
        self.assertTrue(success)
        self.assertNotIn(reminder_id, self.reminder_system.reminders)
    
    def test_snooze_reminder(self):
        """Test snoozing a reminder"""
        original_time = datetime.now() + timedelta(minutes=5)
        
        reminder_id = self.reminder_system.create_reminder(
            user_id=self.user_id,
            title="Snooze Me",
            message="This reminder will be snoozed",
            reminder_time=original_time
        )
        
        # Snooze for 10 minutes
        success = self.reminder_system.snooze_reminder(reminder_id, self.user_id, 10)
        
        self.assertTrue(success)
        
        reminder = self.reminder_system.reminders[reminder_id]
        self.assertGreater(reminder.reminder_time, original_time)
        self.assertFalse(reminder.is_sent)
    
    def test_task_reminder_creation(self):
        """Test creating task-specific reminders"""
        reminder_time = datetime.now() + timedelta(hours=1)
        
        reminder_id = self.reminder_system.create_task_reminder(
            user_id=self.user_id,
            task_title="Important Task",
            task_id="task_123",
            reminder_time=reminder_time
        )
        
        reminder = self.reminder_system.reminders[reminder_id]
        
        self.assertEqual(reminder.reminder_type, ReminderType.TASK)
        self.assertIn("Important Task", reminder.title)
        self.assertEqual(reminder.metadata["task_id"], "task_123")
    
    def test_break_reminder_creation(self):
        """Test creating break reminders"""
        reminder_id = self.reminder_system.create_break_reminder(
            user_id=self.user_id,
            break_type="water",
            interval_minutes=30
        )
        
        reminder = self.reminder_system.reminders[reminder_id]
        
        self.assertEqual(reminder.reminder_type, ReminderType.BREAK)
        self.assertTrue(reminder.is_recurring)
        self.assertIn("water", reminder.message.lower())
    
    def test_reminder_statistics(self):
        """Test getting reminder statistics"""
        # Create various types of reminders
        reminder_time = datetime.now() + timedelta(minutes=30)
        
        self.reminder_system.create_reminder(
            user_id=self.user_id,
            title="High Priority",
            message="Important reminder",
            reminder_time=reminder_time,
            priority=ReminderPriority.HIGH
        )
        
        self.reminder_system.create_task_reminder(
            user_id=self.user_id,
            task_title="Task Reminder",
            task_id="task_456",
            reminder_time=reminder_time
        )
        
        stats = self.reminder_system.get_reminder_statistics(self.user_id)
        
        self.assertEqual(stats["total_reminders"], 2)
        self.assertEqual(stats["active_reminders"], 2)
        self.assertIn("custom", stats["by_type"])
        self.assertIn("task", stats["by_type"])

if __name__ == '__main__':
    unittest.main(verbosity=1)