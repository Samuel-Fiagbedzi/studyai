import requests

# Test the backend
url = 'http://localhost:8000/generate'
files = {'file': open('test.txt', 'rb')}

try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ File processed successfully!")
        print(f"MCQs: {len(data.get('mcq', []))}")
        print(f"Theory questions: {len(data.get('theory', []))}")
        print(f"Flashcards: {len(data.get('flashcards', []))}")
        print(f"Summary length: {len(data.get('summary', ''))}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Connection error: {e}")