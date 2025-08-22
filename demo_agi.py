"""
Demonstration of AGI capabilities for Jarvis 2.0
"""

from core.cognitive.hybrid_intelligence import HybridIntelligenceSystem

def demo_goal_oriented_reasoning():
    """
    Demonstrates the goal-oriented reasoning process.
    """
    print("--- Goal-Oriented Reasoning Demo ---")
    actions = [
        {"name": "call pizza place", "preconditions": ["has phone"], "effects": ["called pizza place"]},
        {"name": "order pizza", "preconditions": ["called pizza place"], "effects": ["pizza ordered"]},
        {"name": "pay for pizza", "preconditions": ["pizza ordered"], "effects": ["pizza paid for"]},
        {"name": "eat pizza", "preconditions": ["pizza paid for"], "effects": ["pizza eaten"]}
    ]
    jarvis = HybridIntelligenceSystem()
    jarvis.planner.actions = actions
    initial_state = ["has phone"]
    goal = ["pizza eaten"]
    jarvis.reason(goal, initial_state)
    print("Goal Completed:", goal)

if __name__ == "__main__":
    demo_goal_oriented_reasoning()
