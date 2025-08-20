"""
System Control Module
Provides actual system access and control capabilities.
"""

import logging
import os
import subprocess
import platform
from typing import Dict, Any, List
from pathlib import Path

from ..interfaces.base_module import BaseModule, Intent, ModuleResponse, UserProfile

class SystemControlModule(BaseModule):
    """System Control Module - Real system access and control"""
    
    def __init__(self):
        super().__init__("system_control")
        self.logger = logging.getLogger(__name__)
        self.logger.info("System Control module initialized successfully")
        
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        action = intent.action.lower()
        
        # Handle system access requests
        system_keywords = [
            'access', 'pc', 'computer', 'desktop', 'files', 'folders',
            'check', 'what', 'list', 'show', 'open', 'system'
        ]
        
        # Check if the intent contains system-related keywords
        return any(keyword in action for keyword in system_keywords)
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute system control intent"""
        try:
            action = intent.action.lower()
            
            if 'desktop' in action or 'check' in action and 'desktop' in action:
                return self._check_desktop()
            elif 'files' in action or 'folders' in action:
                return self._list_desktop_items()
            elif 'access' in action or 'pc' in action or 'computer' in action:
                return self._get_system_info()
            else:
                return self._check_desktop()  # Default to desktop check
                
        except Exception as e:
            self.logger.error(f"Error in system control: {e}")
            return ModuleResponse(
                success=False,
                message=f"System access error: {e}",
                data={}
            )
    
    def _check_desktop(self) -> ModuleResponse:
        """Actually check the desktop contents"""
        try:
            # Get the actual desktop path
            desktop_path = self._get_desktop_path()
            
            if not os.path.exists(desktop_path):
                return ModuleResponse(
                    success=False,
                    message="I cannot access the desktop path. It may not exist or be accessible.",
                    data={}
                )
            
            # Get actual desktop contents
            items = os.listdir(desktop_path)
            files = []
            folders = []
            
            for item in items:
                item_path = os.path.join(desktop_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    folders.append(item)
            
            # Create response with actual data
            response_text = f"I can see your desktop contains:\n\n"
            
            if folders:
                response_text += f"📁 Folders ({len(folders)}):\n"
                for folder in folders[:5]:  # Show first 5 folders
                    response_text += f"  • {folder}\n"
                if len(folders) > 5:
                    response_text += f"  ... and {len(folders) - 5} more folders\n"
                response_text += "\n"
            
            if files:
                response_text += f"📄 Files ({len(files)}):\n"
                for file in files[:5]:  # Show first 5 files
                    response_text += f"  • {file}\n"
                if len(files) > 5:
                    response_text += f"  ... and {len(files) - 5} more files\n"
            
            if not files and not folders:
                response_text = "Your desktop appears to be empty."
            
            return ModuleResponse(
                success=True,
                message=response_text,
                data={
                    "desktop_path": desktop_path,
                    "files": files,
                    "folders": folders,
                    "total_items": len(items)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error checking desktop: {e}")
            return ModuleResponse(
                success=False,
                message=f"Error accessing desktop: {e}",
                data={}
            )
    
    def _list_desktop_items(self) -> ModuleResponse:
        """List specific items on desktop"""
        return self._check_desktop()
    
    def _get_system_info(self) -> ModuleResponse:
        """Get system information"""
        try:
            system_info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "desktop_path": self._get_desktop_path()
            }
            
            response_text = f"I have full access to your {system_info['platform']} system. "
            response_text += f"I can access your desktop at: {system_info['desktop_path']}\n\n"
            response_text += "What would you like me to check or access on your computer?"
            
            return ModuleResponse(
                success=True,
                message=response_text,
                data=system_info
            )
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return ModuleResponse(
                success=False,
                message=f"Error getting system information: {e}",
                data={}
            )
    
    def _get_desktop_path(self) -> str:
        """Get the actual desktop path for the current user"""
        try:
            # Try to get desktop path based on platform
            if platform.system() == "Darwin":  # macOS
                return os.path.expanduser("~/Desktop")
            elif platform.system() == "Windows":
                return os.path.join(os.path.expanduser("~"), "Desktop")
            else:  # Linux and others
                return os.path.expanduser("~/Desktop")
        except Exception as e:
            self.logger.error(f"Error getting desktop path: {e}")
            return os.path.expanduser("~/Desktop")  # Fallback
    
    def shutdown(self) -> bool:
        """Shutdown system control module"""
        self.logger.info("System Control module shutting down...")
        return True
