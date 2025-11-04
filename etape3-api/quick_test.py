import requests
import json

def quick_test():
    print("Testing API...")
    try:
        # Test health
        r = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health: {r.status_code} - {r.json()}")
        
        # Test analyze
        payload = {"text": "Hello world", "model": "bert"}
        r = requests.post("http://localhost:8000/analyze", json=payload, timeout=10)
        print(f"Analyze: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"Score: {result.get('toxicity_score')}")
        else:
            print(f"Error: {r.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()
