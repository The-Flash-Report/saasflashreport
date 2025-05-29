#!/usr/bin/env python3
"""
Test script to debug Perplexity API access issues in GitHub Actions
"""

import os
import requests
import sys

def test_perplexity_api():
    """Test Perplexity API access with debugging information"""
    
    print("🔍 Testing Perplexity API Access...")
    print("-" * 50)
    
    # Check if API key is set
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY environment variable is not set!")
        print("💡 This indicates the GitHub Actions secret is not properly configured.")
        print("   Please add PERPLEXITY_API_KEY to repository secrets in GitHub.")
        return False
    
    # Show partial API key for debugging (first 8 and last 4 characters)
    if len(api_key) > 12:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print(f"✅ API Key found: {masked_key}")
        print(f"   Key length: {len(api_key)} characters")
    else:
        print(f"⚠️  API Key found but seems too short: {len(api_key)} characters")
    
    # Test API endpoint
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
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
            
            # Check for common error patterns
            if response.status_code == 401:
                print("💡 This suggests an authentication problem - API key may be invalid")
            elif response.status_code == 429:
                print("💡 This suggests rate limiting - too many requests")
            elif response.status_code == 500:
                print("💡 This suggests a server error on Perplexity's side")
            
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
        print("✅ GitHub Actions workflow can proceed with Perplexity integration.")
        sys.exit(0)
    else:
        print("\n💥 API test failed!")
        print("❌ The aggregator script will fall back to generating AI summaries")
        print("   from existing articles instead of using Perplexity.")
        print("\n🔧 To fix this issue:")
        print("   1. Go to your GitHub repository settings")
        print("   2. Navigate to Secrets and variables → Actions") 
        print("   3. Add PERPLEXITY_API_KEY as a repository secret")
        print("   4. Re-run this workflow")
        sys.exit(1) 