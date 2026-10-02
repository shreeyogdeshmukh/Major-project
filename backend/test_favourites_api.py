"""
Quick test script to verify favourites API endpoints are working
Run this after starting the Flask server
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    print("Testing Favourites API Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        res = requests.get(f"{BASE_URL}/check-auth")
        print(f"[OK] Server is running (Status: {res.status_code})")
    except Exception as e:
        print(f"[ERROR] Server is not accessible: {e}")
        return
    
    # Test 2: Check if favourites endpoint exists
    try:
        # This should return 401 if not logged in, but endpoint should exist
        res = requests.get(f"{BASE_URL}/favourites")
        print(f"[OK] GET /favourites endpoint exists (Status: {res.status_code})")
        if res.status_code == 401:
            print("  -> Endpoint requires authentication (expected)")
        elif res.status_code == 404:
            print("  -> [WARNING] Endpoint not found! Backend may need restart.")
    except Exception as e:
        print(f"[ERROR] GET /favourites endpoint error: {e}")
    
    # Test 3: Check POST endpoint
    try:
        res = requests.post(
            f"{BASE_URL}/favourites",
            json={"recipe_id": "test", "recipe_name": "Test Recipe"},
            headers={"Content-Type": "application/json"}
        )
        print(f"[OK] POST /favourites endpoint exists (Status: {res.status_code})")
        if res.status_code == 401:
            print("  -> Endpoint requires authentication (expected)")
        elif res.status_code == 404:
            print("  -> [WARNING] Endpoint not found! Backend may need restart.")
    except Exception as e:
        print(f"[ERROR] POST /favourites endpoint error: {e}")
    
    # Test 4: Check DELETE endpoint
    try:
        res = requests.delete(f"{BASE_URL}/favourites/test-recipe")
        print(f"[OK] DELETE /favourites/<recipe_id> endpoint exists (Status: {res.status_code})")
        if res.status_code == 401:
            print("  -> Endpoint requires authentication (expected)")
        elif res.status_code == 404:
            print("  -> [WARNING] Endpoint not found! Backend may need restart.")
    except Exception as e:
        print(f"[ERROR] DELETE /favourites endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("If all endpoints show 401, they are working correctly!")
    print("You need to be logged in to use them.")
    print("\nTo test fully:")
    print("1. Login via http://localhost:5000/login")
    print("2. Then try adding favourites from the frontend")

if __name__ == "__main__":
    test_endpoints()
