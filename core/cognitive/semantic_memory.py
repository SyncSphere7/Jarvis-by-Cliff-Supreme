"""
Semantic Memory for Jarvis 2.0
This module allows Jarvis to understand the meaning of words and concepts.
"""

class SemanticMemory:
    def __init__(self):
        self.memory = {}

    def add_concept(self, concept, meaning):
        """
        Adds a concept to the memory.
        """
        self.memory[concept] = meaning

    def get_meaning(self, concept):
        """
        Returns the meaning of a concept.
        """
        return self.memory.get(concept)

    def get_related_concepts(self, concept):
        """
        Returns all concepts from the memory that are related to the given concept.
        """
        related_concepts = []
        for key, value in self.memory.items():
            if concept in value:
                related_concepts.append(key)
        return related_concepts
