#!/usr/bin/env python3
"""
Supreme Jarvis Demonstration
Shows the supreme capabilities in action.
"""

import asyncio
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

from core.supreme.supreme_integration import SupremeIntegration
from core.modules.supreme_module import SupremeModule
from core.interfaces.data_models import Intent, UserProfile
from core.interfaces.base_module import Intent as BaseIntent, IntentType

async def demonstrate_supreme_capabilities():
    """Demonstrate Jarvis supreme capabilities"""
    
    print("🚀 JARVIS SUPREME CAPABILITIES DEMONSTRATION")
    print("=" * 60)
    print("Welcome to the demonstration of Jarvis's god-like powers!")
    print("=" * 60)
    
    try:
        # Initialize Supreme Integration
        print("\n🔧 Initializing Supreme Systems...")
        integration = SupremeIntegration()
        await integration.initialize()
        await integration.enable_godlike_mode()
        print("✅ Supreme systems online - Godlike mode activated!")
        
        # Initialize Supreme Module
        print("\n🧩 Initializing Supreme Module...")
        supreme_module = SupremeModule()
        supreme_module.initialize()
        print("✅ Supreme module ready for commands!")
        
        # Demonstration scenarios
        scenarios = [
            {
                "title": "🧠 Supreme Analysis",
                "description": "Analyzing complex business problem",
                "intent": Intent(
                    text="Analyze the complex market dynamics and provide strategic recommendations for global expansion",
                    intent_type="supreme_analyze",
                    entities={"domain": "business", "complexity": "high", "scope": "global"},
                    confidence=0.95
                ),
                "user_profile": UserProfile(
                    user_id="ceo_user",
                    name="CEO",
                    preferences={"analysis_depth": "comprehensive", "format": "executive_summary"}
                )
            },
            {
                "title": "🔍 Supreme Knowledge",
                "description": "Researching cutting-edge technology",
                "intent": Intent(
                    text="Research the latest developments in quantum computing and AI integration",
                    intent_type="supreme_research",
                    entities={"field": "quantum_computing", "focus": "AI_integration"},
                    confidence=0.92
                ),
                "user_profile": UserProfile(
                    user_id="researcher",
                    name="Dr. Researcher",
                    preferences={"detail_level": "expert", "sources": "academic"}
                )
            },
            {
                "title": "⚡ Supreme Optimization",
                "description": "Optimizing system performance",
                "intent": Intent(
                    text="Optimize all system resources for maximum performance and efficiency",
                    intent_type="supreme_optimize",
                    entities={"target": "system_performance", "goal": "maximum_efficiency"},
                    confidence=0.98
                ),
                "user_profile": UserProfile(
                    user_id="admin",
                    name="System Administrator",
                    preferences={"optimization_level": "aggressive", "monitoring": "real_time"}
                )
            }
        ]
        
        # Execute demonstration scenarios
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{scenario['title']}")
            print("-" * 40)
            print(f"Scenario: {scenario['description']}")
            print(f"User: {scenario['user_profile'].name}")
            print(f"Request: {scenario['intent'].text}")
            
            print("\n🔄 Processing with supreme capabilities...")
            
            # Process with supreme integration
            response = await integration.process_supreme_intent(
                scenario['intent'], 
                scenario['user_profile']
            )
            
            print(f"✅ Success: {response.success}")
            print(f"🎯 Confidence: {response.confidence:.2%}")
            print(f"⏱️ Execution Time: {response.data.get('execution_time', 0):.3f}s")
            print(f"📝 Response Preview: {response.response[:150]}...")
            
            if i < len(scenarios):
                print("\n" + "="*60)
        
        # Test Supreme Module Commands
        print(f"\n🎮 TESTING SUPREME MODULE COMMANDS")
        print("-" * 40)
        
        # Test status command
        status_intent = BaseIntent(
            action="supreme status",
            intent_type=IntentType.SYSTEM,
            entities={},
            confidence=1.0,
            context={},
            timestamp=datetime.now(),
            user_id="demo_user"
        )
        
        print("📊 Requesting supreme status...")
        status_response = supreme_module.execute(status_intent, {"user_name": "Demo User"})
        print(f"✅ Status Retrieved: {status_response.success}")
        if status_response.success:
            print("📋 Status Report:")
            # Print first few lines of status
            status_lines = status_response.message.split('\n')[:8]
            for line in status_lines:
                print(f"   {line}")
        
        # Test help command
        help_intent = BaseIntent(
            action="supreme help",
            intent_type=IntentType.SYSTEM,
            entities={},
            confidence=1.0,
            context={},
            timestamp=datetime.now(),
            user_id="demo_user"
        )
        
        print("\n❓ Requesting supreme help...")
        help_response = supreme_module.execute(help_intent, {"user_name": "Demo User"})
        print(f"✅ Help Retrieved: {help_response.success}")
        if help_response.success:
            print("📖 Help Preview:")
            help_lines = help_response.message.split('\n')[:10]
            for line in help_lines:
                print(f"   {line}")
        
        # Final system status
        print(f"\n📈 FINAL SYSTEM STATUS")
        print("-" * 40)
        system_status = await integration.get_supreme_status()
        
        orchestrator_status = system_status.get("orchestrator", {})
        engines = system_status.get("engines", {})
        
        print(f"🎭 Orchestrator Running: {orchestrator_status.get('running', False)}")
        print(f"🔧 Total Engines: {len(engines)}")
        print(f"⚡ Active Engines: {len([e for e in engines.values() if e.get('status') == 'ready'])}")
        print(f"📊 Queue Size: {orchestrator_status.get('queue_size', 0)}")
        print(f"🧠 Supreme Mode: {orchestrator_status.get('supreme_mode', 'Unknown')}")
        
        # Cleanup
        print(f"\n🔄 Shutting down supreme systems...")
        supreme_module.shutdown()
        await integration.shutdown()
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRATION COMPLETE!")
        print("✨ Jarvis Supreme Capabilities Successfully Demonstrated!")
        print("🚀 All systems operating at GODLIKE capacity!")
        print("🌟 Ready for real-world supreme operations!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demonstration function"""
    print("Starting Jarvis Supreme Capabilities Demonstration...")
    success = asyncio.run(demonstrate_supreme_capabilities())
    
    if success:
        print("\n🎯 Demonstration completed successfully!")
        print("🚀 Jarvis is ready for supreme operations!")
    else:
        print("\n💥 Demonstration encountered issues")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())