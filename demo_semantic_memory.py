"""
Demonstration of SemanticMemory for Jarvis 2.0
"""

from core.cognitive.semantic_memory import SemanticMemory

def demo_semantic_memory():
    """
    Demonstrates the SemanticMemory.
    """
    print("--- Semantic Memory Demo ---")
    memory = SemanticMemory()
    memory.add_concept("cat", "a small domesticated carnivorous mammal with soft fur")
    memory.add_concept("dog", "a domesticated carnivorous mammal that typically has a long snout")
    memory.add_relation("cat", "dog", "is_a")
    related_concepts = memory.get_related_concepts("cat")
    print("Related Concepts:", related_concepts)

if __name__ == "__main__":
    demo_semantic_memory()
