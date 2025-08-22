"""
Demonstration of ConceptualBlending for Jarvis 2.0
"""

from core.cognitive.conceptual_blending import ConceptualBlending

def demo_conceptual_blending():
    """
    Demonstrates the ConceptualBlending.
    """
    print("--- Conceptual Blending Demo ---")
    blender = ConceptualBlending()
    concept1 = {"name": "car", "wheels": 4, "engine": "gasoline"}
    concept2 = {"name": "boat", "propeller": 1, "engine": "diesel"}
    blended_concept = blender.blend([concept1, concept2])
    print("Blended Concept:", blended_concept)

if __name__ == "__main__":
    demo_conceptual_blending()
