#!/usr/bin/env python3
"""
Test Supreme Jarvis GUI Backend
"""

import requests
import json
import time

def test_backend():
    print("🧪 Testing Supreme Jarvis GUI Backend...")
    
    # Wait for backend to start
    time.sleep(2)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test system status
        print("\nTesting system status...")
        response = requests.get('http://localhost:5001/api/system/status', timeout=5)
        print(f"System status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Engines: {len(data.get('engines', []))}")
            print(f"Health: {data.get('overall_health')}")
        
        # Test chat endpoint
        print("\nTesting chat endpoint...")
        chat_data = {
            'message': 'Hello Supreme Jarvis!',
            'user_profile': {
                'user_id': 'test_user',
                'name': 'Test User'
            }
        }
        response = requests.post(
            'http://localhost:5001/api/chat',
            json=chat_data,
            timeout=10
        )
        print(f"Chat response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', 'No response')[:100]}...")
        
        print("\n✅ Backend tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 5001?")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_backend()