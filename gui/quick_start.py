#!/usr/bin/env python3
"""
Quick Start for Supreme Jarvis GUI
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 SUPREME JARVIS GUI - QUICK START")
    print("=" * 50)
    
    # Check if we're in the right directory
    gui_dir = Path(__file__).parent
    backend_dir = gui_dir / "backend"
    frontend_dir = gui_dir / "frontend"
    
    if not backend_dir.exists() or not frontend_dir.exists():
        print("❌ GUI directories not found")
        return
    
    print("🔧 Starting Supreme Jarvis GUI Backend...")
    
    # Start backend in the background
    try:
        backend_process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for it to start
        time.sleep(2)
        
        # Check if it's still running
        if backend_process.poll() is None:
            print("✅ Backend server started successfully!")
            print("🌐 Backend running on: http://localhost:5000")
        else:
            stdout, stderr = backend_process.communicate()
            print("❌ Backend failed to start:")
            print(stderr.decode())
            return
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return
    
    print("\n📋 NEXT STEPS TO COMPLETE SETUP:")
    print("=" * 50)
    print("1. Open a NEW terminal window")
    print("2. Navigate to the frontend directory:")
    print(f"   cd {frontend_dir}")
    print("3. Start the frontend server:")
    print("   npm run dev")
    print("4. Open your browser to: http://localhost:3000")
    print("=" * 50)
    
    print("\n🎯 YOUR SUPREME JARVIS GUI WILL HAVE:")
    print("• Modern chat interface with Supreme Jarvis")
    print("• Real-time engine monitoring dashboard")
    print("• Quick action buttons and templates")
    print("• File upload and project integration")
    print("• Export and sharing capabilities")
    
    print(f"\n🔧 Backend is running (PID: {backend_process.pid})")
    print("Press Ctrl+C to stop the backend server")
    
    try:
        # Keep the backend running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🔄 Stopping backend server...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("✅ Backend stopped")

if __name__ == "__main__":
    main()