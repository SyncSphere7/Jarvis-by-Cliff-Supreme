"""
Demonstration of QuantumNeuralNetwork for Jarvis 2.0
"""

from core.ai.quantum_neural import QuantumNeuralNetwork

def demo_quantum():
    """
    Demonstrates the QuantumNeuralNetwork.
    """
    print("--- Quantum Neural Network Demo ---")
    qnn = QuantumNeuralNetwork(num_qubits=2, num_parameters=4)
    
    # Create some dummy data and a label
    data = [0.5, 0.8]
    label = 0.7
    
    print(f"Training Quantum Neural Network with data: {data} and label: {label}")
    trained_parameters = qnn.train(data, label)
    print(f"Trained parameters: {trained_parameters}")

if __name__ == "__main__":
    demo_quantum()
