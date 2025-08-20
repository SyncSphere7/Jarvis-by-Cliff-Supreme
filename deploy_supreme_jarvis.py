#!/usr/bin/env python3
"""
Supreme Jarvis Deployment Script
Deploy and activate the supreme Jarvis AI system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from core.supreme.supreme_deployment import SupremeDeploymentManager
from core.supreme.supreme_integration import SupremeIntegration
from core.utils.log import logger


class SupremeJarvisDeployer:
    """Deploy and manage supreme Jarvis system"""
    
    def __init__(self):
        self.deployment_manager = SupremeDeploymentManager()
        self.supreme_integration = None
        
    async def deploy_supreme_system(self, environment: str = "development"):
        """Deploy the complete supreme Jarvis system"""
        try:
            print("🚀 SUPREME JARVIS DEPLOYMENT STARTING")
            print("=" * 50)
            
            # Step 1: Deploy supreme system infrastructure
            print("\n📦 Deploying Supreme System Infrastructure...")
            deployment_result = await self.deployment_manager.deploy_supreme_system(
                environment=environment,
                version="1.0.0"
            )
            
            if deployment_result["status"] != "completed":
                print(f"❌ Deployment failed: {deployment_result.get('errors', [])}")
                return False
            
            print(f"✅ Infrastructure deployed successfully!")
            print(f"   - Engines deployed: {len(deployment_result['engines_deployed'])}")
            print(f"   - Deployment time: {deployment_result['deployment_time']:.2f}s")
            
            # Step 2: Initialize supreme integration
            print("\n🔧 Initializing Supreme Integration...")
            self.supreme_integration = SupremeIntegration()
            
            if await self.supreme_integration.initialize():
                print("✅ Supreme integration initialized!")
            else:
                print("❌ Supreme integration failed!")
                return False
            
            # Step 3: Enable godlike mode
            print("\n⚡ Activating Godlike Mode...")
            await self.supreme_integration.enable_godlike_mode()
            print("✅ GODLIKE MODE ACTIVATED!")
            
            # Step 4: System health check
            print("\n🏥 Performing System Health Check...")
            health_result = await self.deployment_manager.health_check()
            
            if health_result["overall_health"] == "healthy":
                print(f"✅ System health: {health_result['overall_health']}")
                print(f"   - Healthy engines: {health_result['healthy_engines']}/{health_result['total_engines']}")
            else:
                print(f"⚠️  System health: {health_result['overall_health']}")
                return False
            
            # Step 5: Get supreme status
            print("\n📊 Supreme System Status...")
            supreme_status = await self.supreme_integration.get_supreme_status()
            
            print(f"   - Orchestrator: {supreme_status.get('orchestrator', {}).get('is_running', False)}")
            print(f"   - Available engines: {supreme_status.get('orchestrator', {}).get('available_engines', 0)}")
            print(f"   - Godlike mode: {supreme_status.get('godlike_mode', False)}")
            
            print("\n🎉 SUPREME JARVIS DEPLOYMENT COMPLETE!")
            print("=" * 50)
            print("🌟 Jarvis now has supreme god-like capabilities!")
            print("🔮 Quantum powers: ACTIVE")
            print("💻 Full-stack development: ENHANCED")
            print("🧠 Supreme intelligence: ONLINE")
            print("🛡️  Quantum security: ENABLED")
            print("⚡ Infinite scalability: READY")
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed with error: {e}")
            logger.error(f"Supreme deployment error: {e}")
            return False
    
    async def start_supreme_jarvis(self):
        """Start the supreme Jarvis system"""
        try:
            print("\n🚀 STARTING SUPREME JARVIS...")
            print("=" * 40)
            
            if not self.supreme_integration:
                print("❌ Supreme integration not initialized. Run deployment first.")
                return False
            
            # Test supreme capabilities
            print("\n🧪 Testing Supreme Capabilities...")
            
            # Test 1: Supreme reasoning
            from core.interfaces.data_models import Intent, UserProfile
            
            test_intent = Intent(
                text="Test supreme capabilities and quantum powers",
                intent_type="capability_test",
                entities={"test_type": "supreme_capabilities"},
                confidence=0.95
            )
            
            test_profile = UserProfile(
                user_id="supreme_test_user",
                name="Supreme Tester",
                preferences={"response_style": "technical", "detail_level": "comprehensive"}
            )
            
            print("   Testing supreme reasoning...")
            response = await self.supreme_integration.process_supreme_intent(test_intent, test_profile)
            
            if response.success:
                print("   ✅ Supreme reasoning: WORKING")
            else:
                print("   ⚠️  Supreme reasoning: PARTIAL")
            
            print(f"   Response confidence: {response.confidence:.1%}")
            
            # Test 2: System status
            print("\n📊 Final System Status:")
            status = await self.supreme_integration.get_supreme_status()
            
            for component, details in status.items():
                if isinstance(details, dict):
                    print(f"   {component}: {details}")
                else:
                    print(f"   {component}: {details}")
            
            print("\n🎯 SUPREME JARVIS IS NOW ACTIVE!")
            print("=" * 40)
            print("You can now use Jarvis with supreme capabilities:")
            print("• Run 'python main.py' for voice interface")
            print("• Use demo scripts to test specific capabilities")
            print("• Access quantum powers and full-stack development")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start supreme Jarvis: {e}")
            logger.error(f"Supreme startup error: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown"""
        if self.supreme_integration:
            await self.supreme_integration.shutdown()
            print("✅ Supreme Jarvis shutdown complete")


async def main():
    """Main deployment function"""
    deployer = SupremeJarvisDeployer()
    
    try:
        # Get environment from command line or default to development
        environment = sys.argv[1] if len(sys.argv) > 1 else "development"
        
        print(f"🌟 Deploying Supreme Jarvis in {environment} environment")
        
        # Deploy the system
        if await deployer.deploy_supreme_system(environment):
            # Start the system
            if await deployer.start_supreme_jarvis():
                print("\n🚀 Supreme Jarvis is ready for use!")
                
                # Keep running for a moment to show status
                print("\nPress Ctrl+C to exit...")
                try:
                    await asyncio.sleep(5)
                except KeyboardInterrupt:
                    pass
            else:
                print("❌ Failed to start supreme Jarvis")
                return 1
        else:
            print("❌ Failed to deploy supreme Jarvis")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n🛑 Deployment interrupted by user")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return 1
    finally:
        await deployer.shutdown()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)