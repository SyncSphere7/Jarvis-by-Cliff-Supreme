"""
Demonstration of the Speaker Identification functionality for Jarvis 2.0
"""

import numpy as np
from core.voice.enhanced_voice_processor import EnhancedVoiceProcessor
from python_speech_features import mfcc

def demo_speaker_identification():
    """
    Demonstrates the Speaker Identification functionality.
    """
    print("--- Speaker Identification Demo ---")
    
    # Initialize the voice processor
    voice_processor = EnhancedVoiceProcessor()
    
    # --- Enroll a new speaker ---
    print("\n--- Enrolling a new speaker: Alice ---")
    # Create a dummy audio sample for Alice
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    alice_audio = 0.5 * np.sin(2 * np.pi * 220 * t) # A3 note
    
    # Extract MFCC features and add to speaker profiles
    alice_mfcc = mfcc(alice_audio, sample_rate)
    voice_processor.speaker_profiles["alice"] = alice_mfcc
    print("Alice enrolled.")

    # --- Identify a known speaker ---
    print("\n--- Identifying a known speaker: Alice ---")
    identified_speaker = voice_processor.identify_speaker(alice_audio)
    print(f"Identified speaker: {identified_speaker}")

    # --- Identify an unknown speaker ---
    print("\n--- Identifying an unknown speaker ---")
    # Create a dummy audio sample for an unknown speaker
    unknown_audio = 0.5 * np.sin(2 * np.pi * 440 * t) # A4 note
    identified_speaker = voice_processor.identify_speaker(unknown_audio)
    print(f"Identified speaker: {identified_speaker}")

if __name__ == "__main__":
    demo_speaker_identification()
