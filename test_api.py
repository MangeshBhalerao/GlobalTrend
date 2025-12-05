"""
Sample requests to test the GlobalTrend Weather API.
Run this after starting the server with: python main.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_api():
    """Test all API endpoints."""
    
    print("🌤️  Testing GlobalTrend Weather API")
    
    # 1. Health Check
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    # 2. Current Weather by City
    response = requests.get(f"{BASE_URL}/weather/current/London")
    print_response("Current Weather - London", response)
    
    # 3. Current Weather by ID
    response = requests.get(f"{BASE_URL}/weather/current/id/2643743")  # London ID
    print_response("Current Weather by ID - London", response)
    
    # 4. 5-Day Forecast
    response = requests.get(f"{BASE_URL}/weather/forecast/Paris?cnt=8")
    print_response("Forecast - Paris (24 hours)", response)
    
    # 5. Filtered Forecast - Rain only
    response = requests.get(
        f"{BASE_URL}/weather/forecast/London/filter",
        params={"weather_condition": "Clear", "cnt": 16}
    )
    print_response("Filtered Forecast - Clear Weather in London", response)
    
    # 6. Filtered Forecast - Temperature range
    response = requests.get(
        f"{BASE_URL}/weather/forecast/Tokyo/filter",
        params={"min_temp": 15, "max_temp": 25, "cnt": 20}
    )
    print_response("Filtered Forecast - Tokyo (15-25°C)", response)
    
    # 7. Clear expired cache
    response = requests.delete(f"{BASE_URL}/weather/cache/clear-expired")
    print_response("Clear Expired Cache", response)
    
    print("\n" + "="*60)
    print("  ✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
