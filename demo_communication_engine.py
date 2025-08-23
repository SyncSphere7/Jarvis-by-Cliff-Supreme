"""
Demonstration of the Communication Engine for Jarvis 2.0
"""

import asyncio
from core.supreme.engines.communication_engine import SupremeCommunicationEngine
from core.supreme.supreme_config import SupremeConfig

async def demo_communication_engine():
    """
    Demonstrates the Communication Engine.
    """
    print("--- Communication Engine Demo ---")
    
    # Initialize the communication engine
    config = SupremeConfig()
    engine = SupremeCommunicationEngine("communication", config)
    await engine.initialize()
    
    # --- Test Language Detection ---
    print("\n--- Testing Language Detection ---")
    text_to_detect = "Bonjour, comment ça va?"
    print(f"Detecting language for: '{text_to_detect}'")
    detection_result = await engine.communicator.translator.detect_language(text_to_detect)
    print(f"Detected language: {detection_result}")

    # --- Test Translation ---
    print("\n--- Testing Translation ---")
    text_to_translate = "Hello, how are you?"
    target_language = "es"
    print(f"Translating '{text_to_translate}' to '{target_language}'")
    translation_result = await engine.communicator.translator.translate(text_to_translate, target_language)
    print(f"Translation: {translation_result}")

if __name__ == "__main__":
    asyncio.run(demo_communication_engine())
