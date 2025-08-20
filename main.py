from core.utils.log import logger, get_logger
from core.brain.command_manager import CommandManager
from core.modules.time import get_time
from core.modules.system_module import SystemModule
from core.supreme.supreme_integration import SupremeIntegration
from core.monitoring.system_monitor import system_monitor
from jarvis_voice import JarvisVoice
import asyncio

class Jarvis:
    def __init__(self):
        self.command_manager = CommandManager()
        self.supreme_integration = None
        self.system_monitor = system_monitor
        self.register_modules()
        self.register_legacy_commands()
        self.voice = JarvisVoice(self.command_manager)

    def register_modules(self):
        """Register new modular components"""
        # Register system module for basic commands
        system_module = SystemModule()
        self.command_manager.register_module(system_module)
        
        # Register system control module for actual system access
        try:
            from core.modules.system_control_module import SystemControlModule
            system_control_module = SystemControlModule()
            self.command_manager.register_module(system_control_module)
            logger.info("System Control module registered - Jarvis can now access your computer!")
        except Exception as e:
            logger.error(f"Failed to register system control module: {e}")
        
        # Register supreme module for god-like capabilities
        try:
            from core.modules.supreme_module import SupremeModule
            supreme_module = SupremeModule()
            self.command_manager.register_module(supreme_module)
            logger.info("Supreme module registered - Jarvis now has god-like capabilities!")
        except Exception as e:
            logger.error(f"Failed to register supreme module: {e}")
        
        # Register other modules
        try:
            from core.modules.weather_module import WeatherModule
            from core.modules.news_module import NewsModule
            from core.modules.calculator_module import CalculatorModule
            for module_class in [WeatherModule, NewsModule, CalculatorModule]:
                try:
                    module = module_class()
                    self.command_manager.register_module(module)
                except Exception as e:
                    logger.error(f"Failed to register {module_class.__name__}: {e}")
        except Exception as e:
            logger.error(f"Failed to register other modules: {e}")
        
        logger.info("Modules registered successfully")

    def register_legacy_commands(self):
        """Register legacy commands for backward compatibility"""
        self.command_manager.register_command(["time", "what time is it"], get_time)
        logger.info("Legacy commands registered")

    async def initialize_supreme_capabilities(self):
        """Initialize supreme capabilities"""
        try:
            logger.info("Initializing Supreme Capabilities...")
            self.supreme_integration = SupremeIntegration()
            if await self.supreme_integration.initialize():
                # Enable godlike mode for maximum power
                await self.supreme_integration.enable_godlike_mode()
                logger.info("🚀 SUPREME CAPABILITIES ACTIVATED - Jarvis is now all-powerful!")
                return True
            else:
                logger.error("Failed to initialize supreme capabilities")
                return False
        except Exception as e:
            logger.error(f"Error initializing supreme capabilities: {e}")
            return False

    def run(self):
        logger.info("Jarvis is starting...")
        
        # Start system monitoring
        try:
            asyncio.run(self.system_monitor.start_monitoring(30))  # Monitor every 30 seconds
            logger.info("System monitoring started")
        except Exception as e:
            logger.error(f"Failed to start system monitoring: {e}")
        
        # Initialize the modular system
        if self.command_manager.initialize_system():
            logger.info("Jarvis system initialized successfully")
        else:
            logger.warning("Some components failed to initialize")
        
        # Initialize supreme capabilities
        try:
            supreme_success = asyncio.run(self.initialize_supreme_capabilities())
            if supreme_success:
                logger.info("✨ Jarvis Supreme Mode: ACTIVATED")
            else:
                logger.warning("Running in standard mode - supreme capabilities unavailable")
        except Exception as e:
            logger.error(f"Supreme initialization failed: {e}")
            logger.info("Continuing in standard mode...")
        
        # Start voice interface
        self.voice.start()

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Jarvis is shutting down...")
        
        # Stop system monitoring
        try:
            asyncio.run(self.system_monitor.stop_monitoring())
            logger.info("System monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping system monitoring: {e}")
        
        # Shutdown supreme capabilities
        if self.supreme_integration:
            try:
                asyncio.run(self.supreme_integration.shutdown())
                logger.info("Supreme capabilities shutdown complete")
            except Exception as e:
                logger.error(f"Error shutting down supreme capabilities: {e}")
        
        self.command_manager.shutdown()
        logger.info("Jarvis shutdown complete")

if __name__ == "__main__":
    jarvis = Jarvis()
    try:
        jarvis.run()
    except KeyboardInterrupt:
        jarvis.shutdown()