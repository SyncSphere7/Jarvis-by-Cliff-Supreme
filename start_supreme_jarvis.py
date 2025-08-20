#!/usr/bin/env python3
"""
Supreme Jarvis Startup Script
Quick start script for supreme Jarvis with all capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from main import Jarvis
from core.utils.log import logger


async def start_supreme_jarvis():
    """Start Jarvis with supreme capabilities"""
    print("🌟 SUPREME JARVIS STARTUP")
    print("=" * 30)
    
    try:
        # Create Jarvis instance
        jarvis = Jarvis()
        
        # Initialize supreme capabilities
        print("🔧 Initializing supreme capabilities...")
        if await jarvis.initialize_supreme_capabilities():
            print("✅ Supreme capabilities: ACTIVE")
            print("🔮 Quantum powers: ENABLED")
            print("💻 Full-stack development: ENHANCED")
            print("🧠 Supreme intelligence: ONLINE")
            
            # Show system status
            if jarvis.supreme_integration:
                status = await jarvis.supreme_integration.get_supreme_status()
                print(f"\n📊 System Status:")
                print(f"   Godlike mode: {status.get('godlike_mode', False)}")
                print(f"   Available engines: {status.get('orchestrator', {}).get('available_engines', 0)}")
                print(f"   System health: {status.get('system_health', 'unknown')}")
            
            print("\n🎯 SUPREME JARVIS IS READY!")
            print("=" * 30)
            print("Starting voice interface...")
            
            # Start the main Jarvis system
            jarvis.run()
            
        else:
            print("❌ Failed to initialize supreme capabilities")
            print("🔄 Starting in standard mode...")
            jarvis.run()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Supreme Jarvis shutdown requested")
        if 'jarvis' in locals():
            jarvis.shutdown()
    except Exception as e:
        print(f"❌ Error starting Supreme Jarvis: {e}")
        logger.error(f"Supreme startup error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    print("🚀 Welcome to Supreme Jarvis!")
    print("Initializing supreme AI capabilities...")
    
    exit_code = asyncio.run(start_supreme_jarvis())
    sys.exit(exit_code)