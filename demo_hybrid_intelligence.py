"""
Demonstration of the Hybrid Intelligence System for Jarvis 2.0
"""

from core.cognitive.hybrid_intelligence import HybridIntelligenceSystem

def demo_hybrid_intelligence():
    """
    Demonstrates the HybridIntelligenceSystem.
    """
    print("--- Hybrid Intelligence System Demo ---")
    hybrid_system = HybridIntelligenceSystem()

    # --- Demonstrate Reasoning ---
    print("\n--- Testing Reasoning Engine ---")
    goal = "has coffee"
    initial_state = ["has water", "has kettle", "has coffee beans", "has filter"]
    print(f"Goal: {goal}")
    print(f"Initial State: {initial_state}")
    hybrid_system.reason(goal, initial_state)
    
    # --- Demonstrate Advanced Reasoning ---
    print("\n--- Testing Advanced Reasoning Engine ---")
    input_data = "A B"
    print(f"Input data: '{input_data}'")
    inferred_facts = hybrid_system.advanced_reasoning_engine(input_data)
    print(f"Inferred facts: {inferred_facts}")

    # --- Demonstrate Learning ---
    print("\n--- Testing Learning Algorithm ---")
    # Dummy data for demonstration
    training_data = [[1, 0, 1, 0], [0, 1, 0, 1]]
    target_output = [1, 1, 1, 1]
    print("Training data and target output are for demonstration purposes.")
    hybrid_system.learn(training_data, target_output)
    print("Learning process complete.")

if __name__ == "__main__":
    demo_hybrid_intelligence()
