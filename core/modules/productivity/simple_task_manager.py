"""
Simple Task Management System for Jarvis AI Assistant
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from core.interfaces.base_module import BaseModule, Intent, IntentType, ModuleResponse
from core.interfaces.data_models import Task, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)

class SimpleTaskManager(BaseModule):
    """Simple task manager with basic CRUD operations"""
    
    def __init__(self):
        super().__init__("simple_task_manager")
        self.capabilities = ["create_task", "list_tasks", "complete_task", "get_stats"]
        
        # Simple in-memory storage for demo
        self.tasks: Dict[str, Dict[str, Task]] = {}  # user_id -> task_id -> Task
        
        logger.info("Simple Task Manager initialized")
    
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        return intent.intent_type == IntentType.TASK_MANAGEMENT
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute task management commands"""
        try:
            user_id = context.get('user_id', 'default')
            action = intent.action.lower()
            
            if user_id not in self.tasks:
                self.tasks[user_id] = {}
            
            if any(word in action for word in ['create', 'add', 'new']):
                return self._create_task(intent, user_id)
            elif any(word in action for word in ['list', 'show', 'display']):
                return self._list_tasks(user_id)
            elif any(word in action for word in ['complete', 'finish', 'done']):
                return self._complete_task(intent, user_id)
            elif any(word in action for word in ['stats', 'statistics']):
                return self._get_stats(user_id)
            else:
                return ModuleResponse(
                    success=False,
                    message="I can help you create tasks, list tasks, complete tasks, or get statistics.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error in task management: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while managing your tasks.",
                data={"error": str(e)}
            )
    
    def _create_task(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Create a new task"""
        try:
            # Extract task title from the action
            title = self._extract_title(intent.action)
            
            if not title:
                return ModuleResponse(
                    success=False,
                    message="I need a task title. Try saying 'create task buy groceries'",
                    data={}
                )
            
            # Create new task
            task = Task(
                id=str(uuid.uuid4()),
                title=title,
                description="",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=[]
            )
            
            # Store task
            self.tasks[user_id][task.id] = task
            
            return ModuleResponse(
                success=True,
                message=f"Created task: {title}",
                data={"task": asdict(task)}
            )
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't create the task.",
                data={"error": str(e)}
            )
    
    def _list_tasks(self, user_id: str) -> ModuleResponse:
        """List all tasks for user"""
        try:
            user_tasks = list(self.tasks[user_id].values())
            
            if not user_tasks:
                return ModuleResponse(
                    success=True,
                    message="You have no tasks.",
                    data={"tasks": []}
                )
            
            # Sort by creation date
            user_tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            # Format message
            message = "Here are your tasks:\\n\\n"
            for i, task in enumerate(user_tasks[:10], 1):
                status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳"
                message += f"{i}. {status_emoji} {task.title}\\n"
            
            if len(user_tasks) > 10:
                message += f"\\n... and {len(user_tasks) - 10} more tasks"
            
            return ModuleResponse(
                success=True,
                message=message.strip(),
                data={
                    "tasks": [asdict(task) for task in user_tasks],
                    "count": len(user_tasks)
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't retrieve your tasks.",
                data={"error": str(e)}
            )
    
    def _complete_task(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Mark a task as complete"""
        try:
            # Extract task identifier
            task_title = self._extract_title(intent.action)
            
            if not task_title:
                return ModuleResponse(
                    success=False,
                    message="Which task would you like to complete?",
                    data={}
                )
            
            # Find matching task
            matching_task = None
            for task in self.tasks[user_id].values():
                if task_title.lower() in task.title.lower():
                    matching_task = task
                    break
            
            if not matching_task:
                return ModuleResponse(
                    success=False,
                    message=f"I couldn't find a task matching '{task_title}'.",
                    data={}
                )
            
            # Mark as complete
            matching_task.status = TaskStatus.COMPLETED
            matching_task.updated_at = datetime.now()
            
            return ModuleResponse(
                success=True,
                message=f"Marked '{matching_task.title}' as complete! 🎉",
                data={"task": asdict(matching_task)}
            )
            
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't complete the task.",
                data={"error": str(e)}
            )
    
    def _get_stats(self, user_id: str) -> ModuleResponse:
        """Get productivity statistics"""
        try:
            user_tasks = list(self.tasks[user_id].values())
            
            total = len(user_tasks)
            completed = len([t for t in user_tasks if t.status == TaskStatus.COMPLETED])
            pending = total - completed
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            message = f"""📊 Your productivity stats:
📋 Total tasks: {total}
✅ Completed: {completed}
⏳ Pending: {pending}
📈 Completion rate: {completion_rate:.1f}%"""
            
            return ModuleResponse(
                success=True,
                message=message,
                data={
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "pending_tasks": pending,
                    "completion_rate": completion_rate
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return ModuleResponse(
                success=False,
                message="I couldn't calculate your statistics.",
                data={"error": str(e)}
            )
    
    def _extract_title(self, action: str) -> Optional[str]:
        """Extract task title from action string"""
        import re
        
        # Remove common command words and extract the rest
        patterns = [
            r'create task:?\s*(.+)',
            r'add task:?\s*(.+)',
            r'new task:?\s*(.+)',
            r'complete task:?\s*(.+)',
            r'finish task:?\s*(.+)',
            r'done task:?\s*(.+)',
            r'complete:?\s*(.+)',
            r'finish:?\s*(.+)',
            r'done:?\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, action, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None