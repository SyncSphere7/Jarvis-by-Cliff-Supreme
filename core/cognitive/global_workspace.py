"""
Global Workspace Theory for Jarvis 2.0
This module implements the Global Workspace Theory, which suggests that consciousness arises from a global workspace where different brain regions can share information and compete for attention.
"""

class GlobalWorkspace:
    def __init__(self):
        self.workspace = []
        self.subscribers = []

    def subscribe(self, subscriber):
        """
        Subscribes a cognitive module to the global workspace.
        """
        self.subscribers.append(subscriber)

    def broadcast(self, item):
        """
        Broadcasts an item to all subscribed cognitive modules.
        """
        for subscriber in self.subscribers:
            subscriber.receive(item)

    def add_to_workspace(self, item):
        """
        Adds an item to the global workspace and broadcasts it to all subscribers.
        """
        self.workspace.append(item)
        self.broadcast(item)

    def get_workspace_contents(self):
        """
        Returns the contents of the global workspace.
        """
        return self.workspace

    def clear_workspace(self):
        """
        Clears the global workspace.
        """
        self.workspace = []
