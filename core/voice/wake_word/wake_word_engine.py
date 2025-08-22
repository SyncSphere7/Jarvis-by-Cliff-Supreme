"""
Wake Word Detection Engine for Jarvis 2.0
This module contains the implementation of the wake word detection engine.
"""

class WakeWordEngine:
    def __init__(self):
        import whisper
        self.model = whisper.load_model("tiny.en")

    def detect(self, audio):
        """
        Detects the wake word in the given audio.
        """
        text = self.model.transcribe(audio)["text"].lower()
        return any(trigger in text for trigger in ["jarvis", "hey jarvis"])
