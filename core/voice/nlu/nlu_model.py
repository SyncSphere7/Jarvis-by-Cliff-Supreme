"""
NLU Model for Jarvis 2.0
This module contains the implementation of the NLU model.
"""

from core.interfaces.base_module import IntentType

class NLUModel:
    def __init__(self):
        self.training_data = {}

    def train(self, training_data):
        """
        Trains the NLU model on the given training data.
        """
        # This is a very simplified version of a training algorithm.
        # A real implementation would be much more complex.
        for intent, utterances in training_data.items():
            for utterance in utterances:
                self.training_data[utterance] = intent

    def predict(self, text):
        """
        Predicts the intent of the given text.
        """
        # This is a very simplified version of a prediction algorithm.
        # A real implementation would be much more complex.
        intent = self.training_data.get(text)
        if intent:
            return {
                "action": text,
                "intent_type": intent,
                "entities": {},
                "confidence": 1.0,
            }
        else:
            return {
                "action": text,
                "intent_type": IntentType.SYSTEM,
                "entities": {},
                "confidence": 0.0,
            }
