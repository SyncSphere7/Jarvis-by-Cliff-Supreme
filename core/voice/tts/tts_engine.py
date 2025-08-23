"""
TTS Engine for Jarvis 2.0
This module contains the implementation of the TTS engine.
"""

from gtts import gTTS
import os

class TTSEngine:
    def __init__(self):
        pass

    def say(self, text):
        """
        Speaks the given text.
        """
        tts = gTTS(text=text, lang='en')
        tts.save("speech.mp3")
        os.system("mpg321 speech.mp3")
