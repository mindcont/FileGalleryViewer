#!/usr/bin/env python3
"""Quick test to verify API routes are working"""

import requests
import sys

def test_routes():
    base_url = "http://localhost:9000"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test files endpoint
    try:
        response = requests.get(f"{base_url}/api/files")
        print(f"Files endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total_count', 0)} files")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Files endpoint failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_routes():
        print("All tests passed!")
    else:
        print("Some tests failed!")
        sys.exit(1)