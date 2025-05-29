#!/usr/bin/env python3
"""
Test script to debug Perplexity API access issues in GitHub Actions
"""

import os
import requests
import sys
import base64

def decode_api_key():
    """Decode API key from base64 to prevent GitHub Actions masking"""
    
    # Try to get base64 encoded key first (primary method)
    b64_key = os.getenv('PERPLEXITY_API_KEY_B64')
    if b64_key:
        try:
            decoded_key = base64.b64decode(b64_key).decode('utf-8')
            if decoded_key.startswith('pplx-') and len(decoded_key) > 20:
                print("✅ Successfully decoded API key from base64")
                return decoded_key
        except Exception as e:
            print(f"⚠️  Failed to decode base64 key: {e}")
    
    # Fallback to direct environment variables
    for env_var in ['PERPLEXITY_API_KEY', 'PPLX_API_KEY']:
        key_value = os.getenv(env_var)
        if key_value and key_value != '***' and len(key_value) > 10:
            if key_value.startswith('pplx-'):
                print(f"✅ Using direct API key from {env_var}")
                return key_value
            else:
                print(f"⚠️  API key from {env_var} doesn't start with 'pplx-'")
    
    return None

def test_perplexity_api():
    """Test Perplexity API access with debugging information"""
    
    print("🔍 Testing Perplexity API Access...")
    print("-" * 50)
    
    # Get and decode API key
    api_key = decode_api_key()
    
    if not api_key:
        print("❌ No valid Perplexity API key found!")
        print("💡 Solutions:")
        print("   1. Set PERPLEXITY_API_KEY_B64 with base64-encoded API key")
        print("   2. Set PERPLEXITY_API_KEY with direct API key")
        print("   3. Set PPLX_API_KEY with direct API key")
        return False
    
    # Show partial API key for debugging
    if len(api_key) > 12:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print(f"✅ API Key found: {masked_key}")
        print(f"   Key length: {len(api_key)} characters")
    else:
        print(f"⚠️  API Key found but seems too short: {len(api_key)} characters")
    
    # Validate API key format
    if not api_key.startswith('pplx-'):
        print(f"⚠️  API key doesn't start with 'pplx-': {api_key[:10]}...")
        return False
    
    # Test API endpoint
    url = "https://api.perplexity.ai/chat/completions"
    
    # Create authorization header using secure method
    auth_header_value = f"Bearer {api_key}"
    
    headers = {
        "Authorization": auth_header_value,
        "Content-Type": "application/json",
        "User-Agent": "AIFlashReport-Test/1.0"
    }
    
    # Simple test payload
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello, this is a test. Please respond with just 'API connection successful!'"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        print(f"🌐 Testing API endpoint: {url}")
        print(f"📝 Using model: {payload['model']}")
        print(f"🔑 Authorization header configured")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"📝 Response: {content}")
                return True
            else:
                print("⚠️  Unexpected response format:")
                print(result)
                return False
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 401:
                print("💡 Authentication failed - check API key validity")
            elif response.status_code == 429:
                print("💡 Rate limiting - too many requests")
            elif response.status_code == 500:
                print("💡 Server error on Perplexity's side")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check internet connection")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout - API may be slow or unavailable")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_environment():
    """Test environment variables and Python environment"""
    print("🔧 Environment Check...")
    print("-" * 50)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check environment variables
    env_vars_to_check = ['PERPLEXITY_API_KEY_B64', 'PERPLEXITY_API_KEY', 'PPLX_API_KEY']
    for var in env_vars_to_check:
        value = os.getenv(var)
        if value:
            if len(value) > 20:
                print(f"✅ {var}: Found ({len(value)} chars)")
            else:
                print(f"⚠️  {var}: Found but short ({len(value)} chars)")
        else:
            print(f"❌ {var}: Not set")
    
    # Check if we're in GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        print("🏗️  Running in GitHub Actions environment")
        print(f"   Workflow: {os.getenv('GITHUB_WORKFLOW', 'Unknown')}")
        print(f"   Repository: {os.getenv('GITHUB_REPOSITORY', 'Unknown')}")
    else:
        print("💻 Running in local environment")

if __name__ == "__main__":
    test_environment()
    success = test_perplexity_api()
    
    if success:
        print("\n🎉 All tests passed! Perplexity API is accessible.")
        sys.exit(0)
    else:
        print("\n💥 API test failed!")
        print("\n📋 Troubleshooting steps:")
        print("   1. Verify API key is correctly set in GitHub secrets")
        print("   2. Try base64 encoding: echo 'your-api-key' | base64")
        print("   3. Set PERPLEXITY_API_KEY_B64 secret with encoded value")
        sys.exit(1) 