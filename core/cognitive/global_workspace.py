"""
Global Workspace Theory for Jarvis 2.0
This module implements the Global Workspace Theory, which suggests that consciousness arises from a global workspace where different brain regions can share information and compete for attention.
"""

class GlobalWorkspace:
    def __init__(self):
        self.blackboard = {}
        self.knowledge_sources = []

    def add_knowledge_source(self, knowledge_source):
        """
        Adds a knowledge source to the global workspace.
        """
        self.knowledge_sources.append(knowledge_source)

    def update_blackboard(self, key, value):
        """
        Updates the blackboard with new information.
        """
        self.blackboard[key] = value
        self.trigger_knowledge_sources()

    def get_blackboard_contents(self):
        """
        Returns the contents of the blackboard.
        """
        return self.blackboard

    def trigger_knowledge_sources(self):
        """
        Triggers all knowledge sources to see if they can contribute to the solution.
        """
        for knowledge_source in self.knowledge_sources:
            knowledge_source.contribute(self.blackboard)
