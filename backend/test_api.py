import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ Health check passed:", response.json())
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print("✗ Health check failed:", str(e))
        return False

def test_file_upload():
    try:
        # Look for PDF files in the current directory
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        
        if not pdf_files:
            print("✗ No PDF files found in current directory")
            print("Available files:", os.listdir('.'))
            return False
            
        test_file = pdf_files[0]  # Use the first PDF found
        print(f"Testing with file: {test_file}")
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/generate", files=files, timeout=60)
            
        if response.status_code == 200:
            data = response.json()
            print("✓ File upload and AI processing successful!")
            print(f"  - MCQs: {len(data.get('mcqs', []))} questions")
            print(f"  - Theory questions: {len(data.get('theory', []))} questions")
            print(f"  - Flashcards: {len(data.get('flashcards', []))} cards")
            print(f"  - Summary: {len(data.get('summary', ''))} characters")
            
            # Show sample content
            if data.get('mcqs'):
                print(f"\nSample MCQ: {data['mcqs'][0].get('question', 'N/A')[:100]}...")
            if data.get('theory'):
                print(f"Sample Theory: {data['theory'][0][:100]}..." if data['theory'] else "")
            if data.get('flashcards'):
                card = data['flashcards'][0]
                print(f"Sample Flashcard: {card.get('term', 'N/A')} -> {card.get('definition', 'N/A')[:50]}...")
            if data.get('summary'):
                print(f"Summary preview: {data['summary'][:100]}...")
                
            return True
        else:
            print(f"✗ File upload failed with status {response.status_code}: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out (this may be normal for AI processing)")
        return False
    except Exception as e:
        print("✗ File upload failed:", str(e))
        return False

def test_caching():
    """Test that the same file returns cached results faster"""
    try:
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if not pdf_files:
            return False
            
        test_file = pdf_files[0]
        print(f"\nTesting caching with {test_file}...")
        
        # First request
        import time
        start_time = time.time()
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            response1 = requests.post(f"{BASE_URL}/generate", files=files, timeout=60)
        first_duration = time.time() - start_time
        
        if response1.status_code == 200:
            # Second request (should be cached)
            start_time = time.time()
            with open(test_file, 'rb') as f:
                files = {'file': (test_file, f, 'application/pdf')}
                response2 = requests.post(f"{BASE_URL}/generate", files=files, timeout=60)
            second_duration = time.time() - start_time
            
            if response2.status_code == 200:
                print(f"Second request duration: {second_duration:.2f} seconds")
                print(f"First request duration: {first_duration:.2f} seconds")
                if second_duration < first_duration * 0.5:
                    print("✓ Caching is working - second request was much faster!")
                else:
                    print("⚠ Caching may not be working - similar response times")
                return True
            else:
                print(f"✗ Second request failed: {response2.status_code}")
                return False
        else:
            print(f"✗ First request failed: {response1.status_code}")
            return False
    except Exception as e:
        print("✗ Caching test failed:", str(e))
        return False

if __name__ == "__main__":
    print("🔍 Testing StudyAI Backend API...")
    print("=" * 50)
    
    # Test health
    health_ok = test_health()
    
    if health_ok:
        print("\n" + "=" * 50)
        # Test file upload
        upload_ok = test_file_upload()
        
        if upload_ok:
            print("\n" + "=" * 50)
            # Test caching
            test_caching()
    
    print("\n" + "=" * 50)
    print("Testing complete!")