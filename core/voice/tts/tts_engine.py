"""
TTS Engine for Jarvis 2.0
This module contains the implementation of the TTS engine.
"""

class TTSEngine:
    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()

    def say(self, text):
        """
        Speaks the given text.
        """
        self.engine.say(text)
        self.engine.runAndWait()
