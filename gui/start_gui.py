#!/usr/bin/env python3
"""
Simple Supreme Jarvis GUI Starter
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("🚀 SUPREME JARVIS GUI")
    print("=" * 40)
    print("Starting your user-friendly interface...")
    print("=" * 40)

def start_backend():
    """Start the backend server"""
    print("🔧 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir)
        
        print("✅ Backend started on http://localhost:5000")
        return process
    except Exception as e:
        print(f"❌ Backend failed: {e}")
        return None

def main():
    print_banner()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Wait for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    print("\n🎉 SUPREME JARVIS GUI BACKEND IS READY!")
    print("=" * 50)
    print("🔧 Backend API: http://localhost:5000")
    print("🌐 Health Check: http://localhost:5000/api/health")
    print("=" * 50)
    print("\n📝 NEXT STEPS:")
    print("1. Open a new terminal")
    print("2. Run: cd gui/frontend && npm run dev")
    print("3. Open http://localhost:3000 in your browser")
    print("\nPress Ctrl+C to stop the backend server")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🔄 Shutting down...")
        backend_process.terminate()
        print("✅ Backend stopped")

if __name__ == "__main__":
    main()