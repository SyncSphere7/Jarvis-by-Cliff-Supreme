"""
Task management system for Jarvis AI Assistant
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

from core.interfaces.base_module import BaseModule, Intent, IntentType, ModuleResponse
from core.interfaces.data_models import Task, TaskStatus, TaskPriority
from core.security.secure_storage import SecureStorage
from core.security.privacy_manager import DataCategory

logger = logging.getLogger(__name__)

class TaskFilter(Enum):
    """Task filtering options"""
    ALL = "all"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    TODAY = "today"
    THIS_WEEK = "this_week"
    HIGH_PRIORITY = "high_priority"

class TaskManager(BaseModule):
    """Manages tasks, reminders, and productivity tracking"""
    
    def __init__(self, secure_storage: SecureStorage):
        super().__init__("task_manager")
        self.secure_storage = secure_storage
        self.capabilities = [
            "create_task", "list_tasks", "update_task", "delete_task",
            "set_reminder", "get_reminders", "mark_complete", "get_stats"
        ]
        
        # In-memory cache for active tasks
        self.task_cache: Dict[str, Dict[str, Task]] = {}  # user_id -> task_id -> Task
        
        logger.info("Task Manager initialized")
    
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        return intent.intent_type == IntentType.TASK_MANAGEMENT
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute task management commands"""
        try:
            user_id = context.get('user_id', 'default')
            action = intent.action.lower()
            
            # Load user tasks if not cached
            if user_id not in self.task_cache:
                self._load_user_tasks(user_id)
            
            if action in ['create', 'add', 'new']:
                return self._handle_create_task(intent, user_id)
            elif action in ['list', 'show', 'display']:
                return self._handle_list_tasks(intent, user_id)
            elif action in ['complete', 'finish', 'done']:
                return self._handle_complete_task(intent, user_id)
            elif action in ['stats', 'statistics', 'summary']:
                return self._handle_get_stats(intent, user_id)
            else:
                return ModuleResponse(
                    success=False,
                    message="I'm not sure what you want to do with tasks. Try 'create task', 'list tasks', or 'complete task'.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error executing task management command: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while managing your tasks.",
                data={"error": str(e)}
            )    

    def _handle_create_task(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle task creation"""
        try:
            # Extract task details from entities
            entities = intent.entities
            
            # Get task title from the command
            title = self._extract_task_title(intent.action, entities)
            if not title:
                return ModuleResponse(
                    success=False,
                    message="I need a task title. Try saying 'create task: buy groceries'",
                    data={}
                )
            
            # Extract due date if provided
            due_date = self._extract_due_date(entities)
            
            # Extract priority if provided
            priority = self._extract_priority(entities)
            
            # Create new task
            task = Task(
                id=str(uuid.uuid4()),
                title=title,
                description="",
                status=TaskStatus.PENDING,
                priority=priority,
                due_date=due_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=[]
            )
            
            # Save task
            success = self._save_task(user_id, task)
            
            if success:
                # Format response message
                message = f"Created task: {title}"
                if due_date:
                    message += f" (due {due_date.strftime('%Y-%m-%d')})"
                if priority != TaskPriority.MEDIUM:
                    message += f" with {priority.name.lower()} priority"
                
                return ModuleResponse(
                    success=True,
                    message=message,
                    data={"task": asdict(task)}
                )
            else:
                return ModuleResponse(
                    success=False,
                    message="I couldn't save the task. Please try again.",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while creating the task.",
                data={"error": str(e)}
            )
    
    def _handle_list_tasks(self, intent: Intent, user_id: str) -> ModuleResponse:
        """Handle listing tasks"""
        try:
            # Determine filter from entities
            task_filter = self._extract_task_filter(intent.entities)
            
            # Get filtered tasks
            tasks = self._get_filtered_tasks(user_id, task_filter)
            
            if not tasks:
                filter_msg = f" ({task_filter.value})" if task_filter != TaskFilter.ALL else ""
                return ModuleResponse(
                    success=True,
                    message=f"You have no tasks{filter_msg}.",
                    data={"tasks": [], "filter": task_filter.value}
                )
            
            # Sort tasks by priority and due date
            sorted_tasks = sel)           tr(e)}
 r": sata={"erro        d        tasks.",
eving your e retrierror whild an countereenessage="I   m              se,
ss=Falceuc   s        (
     onsen ModuleResp       reture}")
      tasks: {rror listingr(f"Eer.erroogg  l          e:
on as cept Excepti       ex
             )
      }
                     
 ilter.valueer": task_filt       "f           sks),
  rted_tasoen(ount": l         "c        sks],
   tated_task in sorr ) foct(taskasdi"tasks": [                    data={
            age,
    essage=mess     m   
        ess=True,cc          su
      onse(duleRespn Mo       retur       
   )
       k_filters, tassksorted_ta_task_list(formatlf._sage = se       mes     onse
mat resp   # For     
                ks(tasks)
f._sort_tas