"""
Semantic Memory for Jarvis 2.0
This module allows Jarvis to understand the meaning of words and concepts.
"""

import networkx as nx

class SemanticMemory:
    def __init__(self):
        self.graph = nx.Graph()

    def add_concept(self, concept, meaning):
        """
        Adds a concept to the memory.
        """
        self.graph.add_node(concept, meaning=meaning)

    def get_meaning(self, concept):
        """
        Returns the meaning of a concept.
        """
        return self.graph.nodes[concept]["meaning"]

    def add_relation(self, concept1, concept2, relation):
        """
        Adds a relation between two concepts.
        """
        self.graph.add_edge(concept1, concept2, relation=relation)

    def get_related_concepts(self, concept):
        """
        Returns all concepts from the memory that are related to the given concept.
        """
        return list(self.graph.neighbors(concept))
