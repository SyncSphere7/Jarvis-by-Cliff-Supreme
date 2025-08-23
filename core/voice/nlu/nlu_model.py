"""
NLU Model for Jarvis 2.0
This module contains the implementation of the NLU model.
"""

from transformers import pipeline
from core.interfaces.base_module import IntentType

class NLUModel:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def predict(self, text):
        """
        Predicts the intent of the given text.
        """
        candidate_labels = [e.value for e in IntentType]
        result = self.classifier(text, candidate_labels)
        return {
            "action": text,
            "intent_type": IntentType(result["labels"][0]),
            "entities": {},
            "confidence": result["scores"][0],
        }
