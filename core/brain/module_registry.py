"""
Module registry for managing all Jarvis modules
"""

import logging
from typing import Dict, List, Optional, Any
from core.interfaces.base_module import BaseModule, Intent, ModuleResponse

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """Registry for managing and routing to modules"""
    
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self.module_capabilities: Dict[str, List[str]] = {}
        self.initialized = False
    
    def register_module(self, module: BaseModule) -> bool:
        """Register a new module"""
        try:
            if module.name in self.modules:
                logger.warning(f"Module {module.name} already registered, replacing...")
            
            self.modules[module.name] = module
            self.module_capabilities[module.name] = module.get_capabilities()
            
            logger.info(f"Registered module: {module.name} with capabilities: {module.get_capabilities()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register module {module.name}: {e}")
            return False
    
    def unregister_module(self, module_name: str) -> bool:
        """Unregister a module"""
        if module_name in self.modules:
            try:
                self.modules[module_name].shutdown()
                del self.modules[module_name]
                del self.module_capabilities[module_name]
                logger.info(f"Unregistered module: {module_name}")
                return True
            except Exception as e:
                logger.error(f"Error unregistering module {module_name}: {e}")
                return False
        return False
    
    def initialize_all_modules(self) -> bool:
        """Initialize all registered modules"""
        success_count = 0
        total_modules = len(self.modules)
        
        for name, module in self.modules.items():
            try:
                if module.initialize():
                    success_count += 1
                    logger.info(f"Successfully initialized module: {name}")
                else:
                    logger.error(f"Failed to initialize module: {name}")
            except Exception as e:
                logger.error(f"Exception initializing module {name}: {e}")
        
        self.initialized = success_count == total_modules
        logger.info(f"Module initialization complete: {success_count}/{total_modules} successful")
        return self.initialized
    
    def find_capable_modules(self, intent: Intent) -> List[BaseModule]:
        """Find modules that can handle the given intent"""
        capable_modules = []
        
        for module in self.modules.values():
            if module.is_enabled and module.can_handle(intent):
                if module.validate_ethical_compliance(intent):
                    capable_modules.append(module)
                else:
                    logger.warning(f"Module {module.name} rejected intent due to ethical concerns")
        
        return capable_modules
    
    def execute_intent(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute intent using the best available module"""
        try:
            # Find all modules that can handle this intent
            capable_modules = []
            for module in self.modules.values():
                if module.can_handle(intent):
                    capable_modules.append(module)
            
            if not capable_modules:
                # No module can handle this intent
                return ModuleResponse(
                    success=False,
                    message="I'm not sure how to help with that request.",
                    data={"error": "no_capable_module"}
                )
            
            # Prioritize modules based on type
            if len(capable_modules) > 1:
                # Supreme module takes priority for general conversation
                supreme_module = next((m for m in capable_modules if m.name == "supreme"), None)
                if supreme_module:
                    selected_module = supreme_module
                else:
                    # System control module for system operations
                    system_control_module = next((m for m in capable_modules if m.name == "system_control"), None)
                    if system_control_module:
                        selected_module = system_control_module
                    else:
                        # Default to first capable module
                        selected_module = capable_modules[0]
            else:
                selected_module = capable_modules[0]
            
            logger.info(f"Using {selected_module.name} module for: {intent.action}")
            return selected_module.execute(intent, context)
            
        except Exception as e:
            logger.error(f"Error executing intent: {e}")
            return ModuleResponse(
                success=False,
                message="I encountered an error while processing your request.",
                data={"error": str(e)}
            )
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered modules"""
        return self.module_capabilities.copy()
    
    def get_module_status(self) -> Dict[str, Dict]:
        """Get status of all modules"""
        status = {}
        for name, module in self.modules.items():
            status[name] = {
                "enabled": module.is_enabled,
                "capabilities": module.get_capabilities(),
                "initialized": self.initialized
            }
        return status
    
    def shutdown_all_modules(self) -> bool:
        """Shutdown all modules"""
        success_count = 0
        for name, module in self.modules.items():
            try:
                if module.shutdown():
                    success_count += 1
                    logger.info(f"Successfully shutdown module: {name}")
                else:
                    logger.error(f"Failed to shutdown module: {name}")
            except Exception as e:
                logger.error(f"Exception shutting down module {name}: {e}")
        
        return success_count == len(self.modules)