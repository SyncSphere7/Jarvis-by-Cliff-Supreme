"""
Episodic Memory for Jarvis 2.0
This module allows Jarvis to remember past events and experiences.
"""

class EpisodicMemory:
    def __init__(self):
        self.memory = []

    def add_episode(self, episode):
        """
        Adds an episode to the memory.
        """
        self.memory.append(episode)

    def get_episode(self, index):
        """
        Returns an episode from the memory.
        """
        return self.memory[index]

    def get_all_episodes(self):
        """
        Returns all episodes from the memory.
        """
        return self.memory

    def get_episodes_by_keyword(self, keyword):
        """
        Returns all episodes from the memory that contain the given keyword.
        """
        return [episode for episode in self.memory if keyword in episode]
