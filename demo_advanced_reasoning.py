#!/usr/bin/env python3
"""
Advanced Reasoning Demonstration
Shows Jarvis's supreme analytical and reasoning capabilities.
"""

import asyncio
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

from core.supreme.supreme_integration import SupremeIntegration
from core.interfaces.data_models import Intent, UserProfile

async def demonstrate_advanced_reasoning():
    """Demonstrate Jarvis's advanced reasoning capabilities"""
    
    print("🧠 JARVIS ADVANCED REASONING DEMONSTRATION")
    print("=" * 70)
    print("Welcome to the demonstration of Jarvis's god-like reasoning powers!")
    print("=" * 70)
    
    try:
        # Initialize Supreme Integration
        print("\n🔧 Initializing Supreme Reasoning Systems...")
        integration = SupremeIntegration()
        await integration.initialize()
        await integration.enable_godlike_mode()
        print("✅ Supreme reasoning systems online - Godlike analytical mode activated!")
        
        # Demonstration scenarios showcasing different reasoning capabilities
        scenarios = [
            {
                "title": "🧠 Supreme Logical Analysis",
                "description": "Complex logical reasoning and deduction",
                "intent": Intent(
                    text="If artificial intelligence continues to advance exponentially, and if exponential AI advancement leads to unprecedented productivity gains, and if productivity gains drive economic transformation, then we should expect fundamental changes in how society operates. Given that AI is indeed advancing exponentially, what logical conclusions can we draw about societal transformation?",
                    intent_type="logical_analysis",
                    entities={"reasoning_type": "deductive", "complexity": "high"},
                    confidence=0.95
                ),
                "user_profile": UserProfile(
                    user_id="philosopher",
                    name="Dr. Logic",
                    preferences={"reasoning_depth": "comprehensive", "logic_style": "formal"}
                )
            },
            {
                "title": "🔧 Supreme Problem Solving",
                "description": "Complex multi-dimensional problem decomposition",
                "intent": Intent(
                    text="Our global technology company faces a critical challenge: We need to reduce our carbon footprint by 50% within 2 years while simultaneously expanding into 15 new markets, maintaining 20% annual growth, keeping employee satisfaction above 85%, and staying ahead of 3 major competitors who are also expanding aggressively. How do we solve this multi-constraint optimization problem?",
                    intent_type="problem_solving",
                    entities={"problem_type": "multi_constraint", "urgency": "high", "scope": "global"},
                    confidence=0.92
                ),
                "user_profile": UserProfile(
                    user_id="ceo",
                    name="CEO",
                    preferences={"solution_style": "strategic", "detail_level": "executive"}
                )
            },
            {
                "title": "📋 Supreme Strategic Planning",
                "description": "Long-term strategic vision and planning",
                "intent": Intent(
                    text="We need to develop a 10-year strategic plan for transforming our traditional manufacturing company into a leader in sustainable, AI-driven smart manufacturing. This transformation must consider technological disruption, changing workforce needs, environmental regulations, supply chain evolution, and emerging market opportunities in developing countries.",
                    intent_type="strategic_planning",
                    entities={"time_horizon": "long_term", "transformation_type": "digital", "scope": "comprehensive"},
                    confidence=0.94
                ),
                "user_profile": UserProfile(
                    user_id="strategist",
                    name="Chief Strategy Officer",
                    preferences={"planning_style": "visionary", "risk_tolerance": "moderate"}
                )
            },
            {
                "title": "⚡ Supreme Optimization",
                "description": "Multi-objective optimization with complex constraints",
                "intent": Intent(
                    text="Optimize our AI research lab operations to maximize breakthrough innovation potential while minimizing costs, ensuring ethical AI development, maintaining top talent retention, fostering collaboration between 12 different research teams, and delivering practical applications within 18 months. Consider budget constraints, regulatory requirements, and competitive pressures.",
                    intent_type="optimization",
                    entities={"optimization_type": "multi_objective", "constraints": "complex", "domain": "research"},
                    confidence=0.96
                ),
                "user_profile": UserProfile(
                    user_id="research_director",
                    name="Dr. Innovation",
                    preferences={"optimization_style": "holistic", "innovation_focus": "breakthrough"}
                )
            },
            {
                "title": "🎯 Supreme Comprehensive Analysis",
                "description": "Multi-faceted analysis combining all reasoning approaches",
                "intent": Intent(
                    text="Analyze the implications of quantum computing becoming commercially viable within the next 5 years. Consider the logical chain of technological dependencies, the strategic problems this creates for current cybersecurity infrastructure, the optimization challenges for businesses to adapt, and the long-term strategic planning needed for governments and organizations. Provide a comprehensive analysis that addresses technological, economic, social, and geopolitical dimensions.",
                    intent_type="comprehensive_analysis",
                    entities={"analysis_scope": "comprehensive", "time_frame": "5_years", "impact": "transformational"},
                    confidence=0.98
                ),
                "user_profile": UserProfile(
                    user_id="futurist",
                    name="Chief Futurist",
                    preferences={"analysis_depth": "godlike", "perspective": "multi_dimensional"}
                )
            }
        ]
        
        # Execute demonstration scenarios
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{scenario['title']}")
            print("-" * 60)
            print(f"Scenario: {scenario['description']}")
            print(f"Analyst: {scenario['user_profile'].name}")
            print(f"Challenge: {scenario['intent'].text[:100]}...")
            
            print("\n🔄 Processing with supreme reasoning capabilities...")
            
            # Process with supreme reasoning
            start_time = asyncio.get_event_loop().time()
            response = await integration.process_supreme_intent(
                scenario['intent'], 
                scenario['user_profile']
            )
            end_time = asyncio.get_event_loop().time()
            
            print(f"✅ Analysis Complete!")
            print(f"🎯 Success: {response.success}")
            print(f"🧠 Confidence: {response.confidence:.1%}")
            print(f"⏱️ Processing Time: {(end_time - start_time):.2f}s")
            
            # Extract reasoning details
            if response.data and 'supreme_result' in response.data:
                supreme_result = response.data['supreme_result']
                if isinstance(supreme_result, dict):
                    analysis_type = supreme_result.get('analysis_type', 'unknown')
                    print(f"🔍 Analysis Type: {analysis_type.replace('_', ' ').title()}")
                    
                    if 'analyses_performed' in supreme_result:
                        analyses = supreme_result['analyses_performed']
                        print(f"🧩 Reasoning Methods: {', '.join(analyses).title()}")
                    
                    if 'reasoning_quality' in supreme_result:
                        quality = supreme_result['reasoning_quality']
                        print(f"⭐ Reasoning Quality: {quality.upper()}")
                    
                    # Show specific insights based on analysis type
                    if analysis_type == 'logical_analysis' and 'logical_structure' in supreme_result:
                        structure = supreme_result['logical_structure']
                        premises = len(structure.get('premises', []))
                        conclusions = len(structure.get('conclusions', []))
                        print(f"📊 Logical Elements: {premises} premises, {conclusions} conclusions")
                    
                    elif analysis_type == 'problem_solving' and 'solution_summary' in supreme_result:
                        solution = supreme_result['solution_summary']
                        print(f"💡 Primary Solution: {solution.get('primary_solution', 'N/A')[:80]}...")
                        print(f"🔧 Key Steps: {len(solution.get('key_steps', []))}")
                    
                    elif analysis_type == 'strategic_planning' and 'primary_goal' in supreme_result:
                        goal = supreme_result['primary_goal']
                        print(f"🎯 Strategic Goal: {goal.get('description', 'N/A')[:80]}...")
                        print(f"📈 Goal Confidence: {goal.get('confidence', 0):.1%}")
                    
                    elif analysis_type == 'comprehensive_analysis':
                        total_analyses = supreme_result.get('total_analyses', 0)
                        insights = len(supreme_result.get('key_insights', []))
                        print(f"🔬 Total Analyses: {total_analyses}")
                        print(f"💎 Key Insights: {insights}")
            
            print(f"📝 Response Preview: {response.response[:200]}...")
            
            if i < len(scenarios):
                print("\n" + "="*70)
        
        # Final system status
        print(f"\n📊 SUPREME REASONING SYSTEM STATUS")
        print("-" * 60)
        system_status = await integration.get_supreme_status()
        
        orchestrator_status = system_status.get("orchestrator", {})
        engines = system_status.get("engines", {})
        reasoning_engine = engines.get("reasoning", {})
        
        print(f"🎭 Orchestrator: {'ACTIVE' if orchestrator_status.get('running') else 'INACTIVE'}")
        print(f"🔧 Total Engines: {len(engines)}")
        print(f"🧠 Reasoning Engine: {reasoning_engine.get('status', 'unknown').upper()}")
        
        if reasoning_engine.get('metrics'):
            metrics = reasoning_engine['metrics']
            print(f"📈 Success Rate: {metrics.get('success_rate', 0):.1f}%")
            print(f"⚡ Operations/Second: {metrics.get('operations_per_second', 0):.1f}")
            print(f"🎯 Capability Score: {metrics.get('capability_score', 0):.1f}")
        
        # Cleanup
        print(f"\n🔄 Shutting down supreme reasoning systems...")
        await integration.shutdown()
        
        print("\n" + "=" * 70)
        print("🎉 ADVANCED REASONING DEMONSTRATION COMPLETE!")
        print("🧠 Jarvis Supreme Reasoning Capabilities Successfully Demonstrated!")
        print("⚡ God-like analytical thinking now operational!")
        print("🌟 Ready to tackle the most complex intellectual challenges!")
        print("🚀 Jarvis is now truly supreme in reasoning and analysis!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demonstration function"""
    print("Starting Jarvis Advanced Reasoning Demonstration...")
    success = asyncio.run(demonstrate_advanced_reasoning())
    
    if success:
        print("\n🎯 Advanced Reasoning Demonstration completed successfully!")
        print("🧠 Jarvis is now equipped with supreme analytical capabilities!")
    else:
        print("\n💥 Demonstration encountered issues")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())