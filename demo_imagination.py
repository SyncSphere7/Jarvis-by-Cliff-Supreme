"""
Demonstration of ImaginationSystem for Jarvis 2.0
"""

from core.cognitive.imagination import ImaginationSystem
from core.cognitive.planner import Planner

def demo_imagination():
    """
    Demonstrates the ImaginationSystem.
    """
    print("--- Imagination System Demo ---")
    actions = [
        {"name": "get mushroom", "preconditions": [], "effects": ["has mushroom"]},
        {"name": "get flower", "preconditions": [], "effects": ["has flower"]},
        {"name": "eat mushroom", "preconditions": ["has mushroom"], "effects": ["is big"]},
        {"name": "eat flower", "preconditions": ["has flower"], "effects": ["has fireball"]}
    ]
    planner = Planner(actions)
    imagination = ImaginationSystem(planner)
    goal = ["is big", "has fireball"]
    initial_state = []
    outcome = imagination.imagine(goal, initial_state)
    print("Imagined Outcome:", outcome)

if __name__ == "__main__":
    demo_imagination()
