#!/usr/bin/env python3
"""
Test script for the document metadata extraction endpoint
"""
import requests
import os
from pathlib import Path

def test_endpoint():
    """Test the document metadata extraction endpoint"""
    url = "http://localhost:5000/extract-metadata"
    
    # Test with a simple text file
    test_content = """This is a test document.
    
It contains multiple paragraphs and some structured content.

Key points:
- Document processing
- Metadata extraction  
- Prompt generation

This document has 3 sections and demonstrates the API functionality."""
    
    # Create a temporary test file
    test_file_path = Path("test_document.txt")
    test_file_path.write_text(test_content)
    
    try:
        # Test the endpoint
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint test successful!")
            print(f"Document type: {data['metadata']['document_type']}")
            print(f"File size: {data['metadata']['file_size']} bytes")
            print(f"Text preview: {data['metadata']['text_preview'][:100]}...")
            print(f"\nPrompt context:\n{data['prompt_context']}")
        else:
            print(f"❌ Test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()

if __name__ == "__main__":
    test_endpoint()