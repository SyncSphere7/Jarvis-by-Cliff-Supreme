"""
Demonstration of EpisodicMemory for Jarvis 2.0
"""

from core.cognitive.episodic_memory import EpisodicMemory

def demo_episodic_memory():
    """
    Demonstrates the EpisodicMemory.
    """
    print("--- Episodic Memory Demo ---")
    memory = EpisodicMemory()
    memory.add_episode("I ate a delicious pizza")
    memory.add_episode("I went to the park")
    memory.add_episode("I saw a dog at the park")
    related_episodes = memory.get_related_episodes("I went to the park")
    print("Related Episodes:", related_episodes)

if __name__ == "__main__":
    demo_episodic_memory()
