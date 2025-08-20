#!/usr/bin/env python3
"""
Setup AI capabilities for Supreme Jarvis GUI
"""

import os
import subprocess
import sys

def setup_openai():
    """Setup OpenAI integration"""
    print("🤖 Setting up OpenAI integration...")
    
    try:
        import openai
        print("✅ OpenAI library already installed")
    except ImportError:
        print("📦 Installing OpenAI library...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openai"])
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 To enable OpenAI integration:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("3. Restart the backend")
    else:
        print("✅ OpenAI API key found!")
    
    return api_key is not None

def setup_ollama():
    """Setup Ollama for local AI"""
    print("\n🦙 Setting up Ollama (local AI)...")
    
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed!")
            
            # Check if we have any models
            models_result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if 'llama2' in models_result.stdout:
                print("✅ Llama2 model is available!")
                return True
            else:
                print("📥 Installing Llama2 model (this may take a while)...")
                subprocess.run(['ollama', 'pull', 'llama2'])
                return True
        else:
            print("❌ Ollama not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("\n📥 To install Ollama:")
        print("1. Visit: https://ollama.ai/")
        print("2. Download and install for your OS")
        print("3. Run: ollama pull llama2")
        return False

def main():
    print("🚀 SUPREME JARVIS AI SETUP")
    print("=" * 40)
    
    openai_ready = setup_openai()
    ollama_ready = setup_ollama()
    
    print("\n📊 SETUP SUMMARY:")
    print("=" * 40)
    print(f"OpenAI Integration: {'✅ Ready' if openai_ready else '⚠️  Needs API key'}")
    print(f"Local AI (Ollama): {'✅ Ready' if ollama_ready else '❌ Not available'}")
    
    if openai_ready or ollama_ready:
        print("\n🎉 AI capabilities are ready!")
        print("Restart the backend to enable natural conversations.")
    else:
        print("\n⚠️  No AI models available.")
        print("Supreme Jarvis will use intelligent fallback responses.")

if __name__ == "__main__":
    main()