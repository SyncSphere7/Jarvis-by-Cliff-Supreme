"""
Unit tests for task management system
"""

import unittest
from datetime import datetime

from core.modules.productivity.simple_task_manager import SimpleTaskManager
from core.interfaces.base_module import Intent, IntentType
from core.interfaces.data_models import TaskStatus

class TestSimpleTaskManager(unittest.TestCase):
    """Test cases for Simple Task Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.task_manager = SimpleTaskManager()
        self.user_id = "test_user"
        self.context = {"user_id": self.user_id}
    
    def test_initialization(self):
        """Test task manager initialization"""
        self.assertEqual(self.task_manager.name, "simple_task_manager")
        self.assertIn("create_task", self.task_manager.capabilities)
        self.assertIn("list_tasks", self.task_manager.capabilities)
        self.assertIsInstance(self.task_manager.tasks, dict)
    
    def test_can_handle_task_management_intent(self):
        """Test that module can handle task management intents"""
        intent = Intent(
            action="create task",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        self.assertTrue(self.task_manager.can_handle(intent))
    
    def test_cannot_handle_other_intents(self):
        """Test that module rejects non-task intents"""
        intent = Intent(
            action="play music",
            intent_type=IntentType.ENTERTAINMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        self.assertFalse(self.task_manager.can_handle(intent))
    
    def test_create_task_success(self):
        """Test successful task creation"""
        intent = Intent(
            action="create task buy groceries",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Created task: buy groceries", response.message)
        self.assertIn("task", response.data)
        
        # Verify task was stored
        self.assertIn(self.user_id, self.task_manager.tasks)
        self.assertEqual(len(self.task_manager.tasks[self.user_id]), 1)
        
        task = list(self.task_manager.tasks[self.user_id].values())[0]
        self.assertEqual(task.title, "buy groceries")
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_create_task_without_title(self):
        """Test task creation without title fails gracefully"""
        intent = Intent(
            action="create task",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertFalse(response.success)
        self.assertIn("need a task title", response.message)
    
    def test_list_tasks_empty(self):
        """Test listing tasks when none exist"""
        intent = Intent(
            action="list tasks",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertEqual(response.message, "You have no tasks.")
        self.assertEqual(response.data["tasks"], [])
    
    def test_list_tasks_with_tasks(self):
        """Test listing tasks when tasks exist"""
        # Create some tasks first
        self._create_test_task("buy milk")
        self._create_test_task("walk the dog")
        
        intent = Intent(
            action="list tasks",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Here are your tasks", response.message)
        self.assertIn("buy milk", response.message)
        self.assertIn("walk the dog", response.message)
        self.assertEqual(len(response.data["tasks"]), 2)
        self.assertEqual(response.data["count"], 2)
    
    def test_complete_task_success(self):
        """Test successful task completion"""
        # Create a task first
        self._create_test_task("finish project")
        
        intent = Intent(
            action="complete finish project",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Marked 'finish project' as complete", response.message)
        
        # Verify task status changed
        task = list(self.task_manager.tasks[self.user_id].values())[0]
        self.assertEqual(task.status, TaskStatus.COMPLETED)
    
    def test_complete_task_not_found(self):
        """Test completing non-existent task"""
        intent = Intent(
            action="complete nonexistent task",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertFalse(response.success)
        self.assertIn("couldn't find a task", response.message)
    
    def test_get_stats_empty(self):
        """Test getting statistics with no tasks"""
        intent = Intent(
            action="stats",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Total tasks: 0", response.message)
        self.assertEqual(response.data["total_tasks"], 0)
        self.assertEqual(response.data["completion_rate"], 0)
    
    def test_get_stats_with_tasks(self):
        """Test getting statistics with mixed task statuses"""
        # Create and complete some tasks
        self._create_test_task("task 1")
        self._create_test_task("task 2")
        self._create_test_task("task 3")
        
        # Complete one task
        task_id = list(self.task_manager.tasks[self.user_id].keys())[0]
        self.task_manager.tasks[self.user_id][task_id].status = TaskStatus.COMPLETED
        
        intent = Intent(
            action="statistics",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertTrue(response.success)
        self.assertIn("Total tasks: 3", response.message)
        self.assertIn("Completed: 1", response.message)
        self.assertIn("Pending: 2", response.message)
        self.assertEqual(response.data["total_tasks"], 3)
        self.assertEqual(response.data["completed_tasks"], 1)
        self.assertEqual(response.data["pending_tasks"], 2)
        self.assertAlmostEqual(response.data["completion_rate"], 33.3, places=1)
    
    def test_unknown_action(self):
        """Test handling of unknown actions"""
        intent = Intent(
            action="unknown action",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        
        self.assertFalse(response.success)
        self.assertIn("I can help you create tasks", response.message)
    
    def test_title_extraction(self):
        """Test task title extraction from various formats"""
        test_cases = [
            ("create task: buy milk", "buy milk"),
            ("add task walk the dog", "walk the dog"),
            ("new task finish homework", "finish homework"),
            ("complete buy groceries", "buy groceries"),
            ("finish project work", "project work"),
            ("done with laundry", "with laundry")
        ]
        
        for action, expected_title in test_cases:
            extracted_title = self.task_manager._extract_title(action)
            self.assertEqual(extracted_title, expected_title, 
                           f"Failed to extract '{expected_title}' from '{action}'")
    
    def test_multiple_users(self):
        """Test that tasks are isolated between users"""
        user1_context = {"user_id": "user1"}
        user2_context = {"user_id": "user2"}
        
        # Create task for user1
        intent1 = Intent(
            action="create task user1 task",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response1 = self.task_manager.execute(intent1, user1_context)
        self.assertTrue(response1.success)
        
        # Create task for user2
        intent2 = Intent(
            action="create task user2 task",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response2 = self.task_manager.execute(intent2, user2_context)
        self.assertTrue(response2.success)
        
        # Verify tasks are separate
        self.assertEqual(len(self.task_manager.tasks["user1"]), 1)
        self.assertEqual(len(self.task_manager.tasks["user2"]), 1)
        
        user1_task = list(self.task_manager.tasks["user1"].values())[0]
        user2_task = list(self.task_manager.tasks["user2"].values())[0]
        
        self.assertEqual(user1_task.title, "user1 task")
        self.assertEqual(user2_task.title, "user2 task")
    
    def _create_test_task(self, title: str):
        """Helper method to create a test task"""
        intent = Intent(
            action=f"create task {title}",
            intent_type=IntentType.TASK_MANAGEMENT,
            entities={},
            confidence=0.9,
            context={},
            timestamp=datetime.now()
        )
        
        response = self.task_manager.execute(intent, self.context)
        self.assertTrue(response.success)

if __name__ == '__main__':
    unittest.main(verbosity=1)