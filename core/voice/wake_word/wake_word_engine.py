"""
Wake Word Detection Engine for Jarvis 2.0
This module contains the implementation of the wake word detection engine.
"""

from pocketsphinx import LiveSpeech

class WakeWordEngine:
    def __init__(self, wake_word):
        self.wake_word = wake_word
        self.speech = LiveSpeech(
            verbose=False,
            sampling_rate=16000,
            buffer_size=2048,
            no_search=False,
            full_utt=False,
            hmm='cmusphinx-en-us-5.2',
            lm=False,
            dic='cmudict.dict',
            kws_threshold=1e-20,
            keyphrase=wake_word
        )

    def detect(self):
        """
        Detects the wake word in the given audio.
        """
        for phrase in self.speech:
            if self.wake_word in str(phrase):
                return True
        return False
