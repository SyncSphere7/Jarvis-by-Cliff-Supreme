"""
Demonstration of the Text-to-Speech (TTS) functionality for Jarvis 2.0
"""

from core.voice.voice_response_generator import VoiceResponseGenerator, PersonalityTrait
from core.interfaces.voice_interface import VoiceResponse

def demo_tts():
    """
    Demonstrates the TTS functionality.
    """
    print("--- Text-to-Speech (TTS) Demo ---")
    
    # Initialize the voice response generator with a professional personality
    response_generator = VoiceResponseGenerator(personality=PersonalityTrait.PROFESSIONAL)
    
    # Create a simple voice response
    response = VoiceResponse(
        text="Hello, this is a test of the text-to-speech functionality.",
        emotion="friendly",
        priority=1
    )
    
    # Speak the response
    print("Speaking response...")
    response_generator.speak_response(response)
    print("Response spoken.")

if __name__ == "__main__":
    demo_tts()
