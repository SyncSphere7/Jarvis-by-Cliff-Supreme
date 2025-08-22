"""
Demonstration of EmotionIntelligenceSystem for Jarvis 2.0
"""

from core.cognitive.emotion.emotion_intelligence import EmotionIntelligenceSystem

def demo_emotion_intelligence():
    """
    Demonstrates the EmotionIntelligenceSystem.
    """
    print("--- Emotion Intelligence System Demo ---")
    emotion_system = EmotionIntelligenceSystem(vocab_size=256, hidden_size=100, num_classes=3)
    emotion = emotion_system.detect_emotion("I am so happy")
    emotion_system.express_emotion(emotion)

if __name__ == "__main__":
    demo_emotion_intelligence()
