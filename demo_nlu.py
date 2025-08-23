"""
Demonstration of NLUModel for Jarvis 2.0
"""

from core.voice.nlu.nlu_model import NLUModel

def demo_nlu():
    """
    Demonstrates the NLUModel.
    """
    print("--- NLU Model Demo ---")
    nlu = NLUModel()
    prediction = nlu.predict("turn on the lights")
    print("Prediction:", prediction)

if __name__ == "__main__":
    demo_nlu()
