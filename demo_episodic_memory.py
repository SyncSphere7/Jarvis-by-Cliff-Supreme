"""
Demonstration of EpisodicMemory for Jarvis 2.0
"""

from core.cognitive.episodic_memory import EpisodicMemory

def demo_episodic_memory():
    """
    Demonstrates the EpisodicMemory.
    """
    print("--- Episodic Memory Demo ---")
    memory = EpisodicMemory(similarity_threshold=0.6)  # Lower threshold for broader matches in demo

    print("Adding episodes to memory...")
    memory.add_episode("I ate a delicious pizza for dinner.")
    memory.add_episode("Yesterday, I went for a walk in the park.")
    memory.add_episode("I saw a cute dog playing fetch in the park.")
    memory.add_episode("I enjoy Italian food, especially pasta.")
    memory.add_episode("My favorite outdoor activity is hiking.")
    memory.add_episode("I'm thinking of getting a pet, maybe a puppy.")

    print("\n--- Testing Relatedness ---")
    
    episode_to_test = "I went for a stroll in the gardens."
    print(f"Finding episodes related to: '{episode_to_test}'")
    related_episodes = memory.get_related_episodes(episode_to_test)
    print("Related Episodes:", related_episodes)

    episode_to_test_2 = "I love animals."
    print(f"\nFinding episodes related to: '{episode_to_test_2}'")
    related_episodes_2 = memory.get_related_episodes(episode_to_test_2)
    print("Related Episodes:", related_episodes_2)

    episode_to_test_3 = "What kind of food should I have?"
    print(f"\nFinding episodes related to: '{episode_to_test_3}'")
    related_episodes_3 = memory.get_related_episodes(episode_to_test_3)
    print("Related Episodes:", related_episodes_3)

if __name__ == "__main__":
    demo_episodic_memory()
