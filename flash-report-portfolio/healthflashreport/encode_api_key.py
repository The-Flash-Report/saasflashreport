#!/usr/bin/env python3
"""
Helper script to base64 encode the Perplexity API key for GitHub Actions
"""

import base64
import sys
import os

def encode_api_key():
    """Encode the Perplexity API key to base64 for GitHub Actions"""
    
    print("🔑 Perplexity API Key Encoder for GitHub Actions")
    print("-" * 50)
    print("This script will encode your Perplexity API key to base64")
    print("to prevent GitHub Actions secret masking issues.")
    print()
    
    # Get API key from environment or user input
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("Enter your Perplexity API key (it will not be displayed):")
        try:
            import getpass
            api_key = getpass.getpass("API Key: ")
        except ImportError:
            print("⚠️  getpass not available, using regular input (key will be visible):")
            api_key = input("API Key: ")
    else:
        print("✅ Using API key from PERPLEXITY_API_KEY environment variable")
    
    if not api_key:
        print("❌ No API key provided!")
        sys.exit(1)
    
    # Validate API key format
    if not api_key.startswith('pplx-'):
        print("⚠️  Warning: API key doesn't start with 'pplx-'")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            sys.exit(1)
    
    # Encode to base64
    try:
        encoded_key = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
        print()
        print("✅ Successfully encoded API key!")
        print()
        print("📋 Add this to your GitHub repository secrets:")
        print(f"   Secret Name: PERPLEXITY_API_KEY_B64")
        print(f"   Secret Value: {encoded_key}")
        print()
        print("🔧 Steps to add the secret:")
        print("   1. Go to your GitHub repository")
        print("   2. Click Settings > Secrets and variables > Actions")
        print("   3. Click 'New repository secret'")
        print("   4. Name: PERPLEXITY_API_KEY_B64")
        print(f"   5. Value: {encoded_key}")
        print("   6. Click 'Add secret'")
        print()
        print("🧪 To test decoding:")
        
        # Test decoding
        decoded_test = base64.b64decode(encoded_key).decode('utf-8')
        if decoded_test == api_key:
            print("✅ Encoding/decoding test successful!")
        else:
            print("❌ Encoding/decoding test failed!")
            
    except Exception as e:
        print(f"❌ Error encoding API key: {e}")
        sys.exit(1)

if __name__ == "__main__":
    encode_api_key() 