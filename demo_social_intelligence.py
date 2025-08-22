"""
Demonstration of SocialIntelligenceSystem for Jarvis 2.0
"""

from core.cognitive.social.social_intelligence import SocialIntelligenceSystem

def demo_social_intelligence():
    """
    Demonstrates the SocialIntelligenceSystem.
    """
    print("--- Social Intelligence System Demo ---")
    social_system = SocialIntelligenceSystem(vocab_size=256, hidden_size=100, num_classes=3)
    social_cue = social_system.understand_social_cues("hello")
    print("Social Cue:", social_cue)
    user_profile = {"name": "John"}
    social_system.build_rapport(user_profile)

if __name__ == "__main__":
    demo_social_intelligence()
