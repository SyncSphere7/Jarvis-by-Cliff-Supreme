"""
Demonstration of LifelongLearningSystem for Jarvis 2.0
"""

import numpy as np
from core.cognitive.lifelong_learning import LifelongLearningSystem

def demo_lifelong_learning():
    """
    Demonstrates the LifelongLearningSystem.
    """
    print("--- Lifelong Learning System Demo ---")
    lls = LifelongLearningSystem(input_size=10, hidden_sizes=[20, 10], output_size=5)
    new_data = np.random.rand(10, 1)
    target_output = np.random.rand(5, 1)
    lls.learn(new_data, target_output)
    print("Lifelong learning system has learned from new data")

if __name__ == "__main__":
    demo_lifelong_learning()
