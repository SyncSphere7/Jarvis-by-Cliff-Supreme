"""
Demonstration of GenerativeModels for Jarvis 2.0
"""

from core.cognitive.generative_models import GenerativeModels

def demo_generative_models():
    """
    Demonstrates the GenerativeModels.
    """
    print("--- Generative Models Demo ---")
    model = GenerativeModels(vocab_size=10, hidden_size=20)
    generated_text = model.generate(seed=0, length=10)
    print("Generated Text:", generated_text)

if __name__ == "__main__":
    demo_generative_models()
