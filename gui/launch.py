#!/usr/bin/env python3
"""
Supreme Jarvis GUI Launcher
Launches both frontend and backend servers
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

def print_banner():
    print("🚀 SUPREME JARVIS GUI LAUNCHER")
    print("=" * 50)
    print("Starting user-friendly web interface...")
    print("=" * 50)

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Install backend dependencies
    backend_dir = Path(__file__).parent / "backend"
    if (backend_dir / "requirements.txt").exists():
        print("Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(backend_dir / "requirements.txt")
        ], cwd=backend_dir)
    
    # Install frontend dependencies
    frontend_dir = Path(__file__).parent / "frontend"
    if (frontend_dir / "package.json").exists():
        print("Installing Node.js dependencies...")
        if subprocess.run(["npm", "--version"], capture_output=True).returncode == 0:
            subprocess.run(["npm", "install"], cwd=frontend_dir)
        else:
            print("⚠️  npm not found. Please install Node.js and npm first.")
            print("Visit: https://nodejs.org/")
            return False
    
    return True

def start_backend():
    """Start the Flask backend server"""
    print("🔧 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Start Flask app
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir)
        
        print("✅ Backend server started on http://localhost:5000")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        # Start Vite dev server
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir)
        
        print("✅ Frontend server started on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_server(url, timeout=30):
    """Wait for server to be ready"""
    import requests
    
    for _ in range(timeout):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def open_browser():
    """Open the web browser to the GUI"""
    import webbrowser
    
    print("🌐 Opening web browser...")
    webbrowser.open("http://localhost:3000")

def main():
    print_banner()
    
    # Check if we're in the right directory
    if not (Path(__file__).parent / "frontend" / "package.json").exists():
        print("❌ Frontend not found. Please run this script from the gui directory.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    print("\n🚀 Launching Supreme Jarvis GUI...")
    print("-" * 30)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    # Wait for servers to be ready
    print("\n⏳ Waiting for servers to be ready...")
    
    # Wait for backend
    if wait_for_server("http://localhost:5000/api/health"):
        print("✅ Backend is ready!")
    else:
        print("⚠️  Backend may not be fully ready")
    
    # Wait a moment for frontend
    time.sleep(5)
    
    print("\n🎉 SUPREME JARVIS GUI IS READY!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend:  http://localhost:5000")
    print("=" * 50)
    print("Press Ctrl+C to stop all servers")
    
    # Open browser
    open_browser()
    
    # Handle shutdown
    def signal_handler(sig, frame):
        print("\n\n🔄 Shutting down Supreme Jarvis GUI...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Shutdown complete!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Wait for processes
    try:
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()

if __name__ == "__main__":
    main()