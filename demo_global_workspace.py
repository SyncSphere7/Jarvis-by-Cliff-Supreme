"""
Demonstration of GlobalWorkspace for Jarvis 2.0
"""

from core.cognitive.global_workspace import GlobalWorkspace

class KnowledgeSource:
    def __init__(self, name):
        self.name = name

    def contribute(self, blackboard):
        """
        Contributes to the solution on the blackboard.
        """
        if "problem" in blackboard and blackboard["problem"] == "solve world hunger":
            print(f"{self.name} is contributing to the solution")

def demo_global_workspace():
    """
    Demonstrates the GlobalWorkspace.
    """
    print("--- Global Workspace Demo ---")
    workspace = GlobalWorkspace()
    ks1 = KnowledgeSource("ks1")
    ks2 = KnowledgeSource("ks2")
    workspace.add_knowledge_source(ks1)
    workspace.add_knowledge_source(ks2)
    workspace.update_blackboard("problem", "solve world hunger")

if __name__ == "__main__":
    demo_global_workspace()
