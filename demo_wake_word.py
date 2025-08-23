"""
Demonstration of WakeWordEngine for Jarvis 2.0
"""

from core.voice.wake_word.wake_word_engine import WakeWordEngine

def demo_wake_word():
    """
    Demonstrates the WakeWordEngine.
    """
    print("--- Wake Word Engine Demo ---")
    engine = WakeWordEngine(wake_word="jarvis")
    engine.detect()

if __name__ == "__main__":
    demo_wake_word()
