"""
Episodic Memory for Jarvis 2.0
This module allows Jarvis to remember past events and experiences.
"""

import networkx as nx

class EpisodicMemory:
    def __init__(self):
        self.graph = nx.Graph()

    def add_episode(self, episode):
        """
        Adds an episode to the memory.
        """
        self.graph.add_node(episode)
        for other_episode in self.graph.nodes():
            if self.are_related(episode, other_episode):
                self.graph.add_edge(episode, other_episode)

    def get_related_episodes(self, episode):
        """
        Returns all episodes related to the given episode.
        """
        return list(self.graph.neighbors(episode))

    def are_related(self, episode1, episode2):
        """
        Checks if two episodes are related.
        """
        # This is a placeholder for a more advanced relatedness metric.
        # A real implementation would be much more complex.
        keywords = ["park", "dog"]
        return any(keyword in episode1 and keyword in episode2 for keyword in keywords)
