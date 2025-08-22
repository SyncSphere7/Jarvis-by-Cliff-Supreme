"""
Emotion Intelligence System for Jarvis 2.0
This module allows Jarvis to understand and express emotions.
"""

class EmotionIntelligenceSystem:
    def __init__(self):
        self.emotions = {
            "happy": ["happy", "joyful", "excited"],
            "sad": ["sad", "unhappy", "depressed"],
            "angry": ["angry", "mad", "furious"],
        }

    def detect_emotion(self, text):
        """
        Detects the emotion of the given text.
        """
        for emotion, keywords in self.emotions.items():
            for keyword in keywords:
                if keyword in text:
                    return emotion
        return "neutral"

    def express_emotion(self, emotion):
        """
        Expresses the given emotion.
        """
        # For the purpose of this demonstration, we will just print the emotion to the console
        print(f"Jarvis is feeling {emotion}")
