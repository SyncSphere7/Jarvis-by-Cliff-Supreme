"""
Demonstration of ConsciousnessMetric for Jarvis 2.0
"""

import numpy as np
from core.cognitive.consciousness_metric import ConsciousnessMetric

def demo_consciousness_metric():
    """
    Demonstrates the ConsciousnessMetric.
    """
    print("--- Consciousness Metric Demo ---")
    transition_matrix = np.random.rand(10, 10)
    consciousness_metric = ConsciousnessMetric(transition_matrix)
    phi = consciousness_metric.calculate_phi()
    print("Phi:", phi)

if __name__ == "__main__":
    demo_consciousness_metric()
