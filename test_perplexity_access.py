#!/usr/bin/env python3
"""
Test script to validate Perplexity API access for GitHub Actions workflow.
This script checks if the Perplexity API key is properly configured.
"""

import os
import sys
import base64

def test_perplexity_access():
    """Test Perplexity API key configuration."""
    print("🔍 Testing Perplexity API configuration...")
    
    # Check for different API key environment variables
    api_key = None
    api_key_source = None
    
    # Try to get API key from various environment variables
    if os.getenv('PERPLEXITY_API_KEY'):
        api_key = os.getenv('PERPLEXITY_API_KEY')
        api_key_source = 'PERPLEXITY_API_KEY'
    elif os.getenv('PPLX_API_KEY'):
        api_key = os.getenv('PPLX_API_KEY')
        api_key_source = 'PPLX_API_KEY'
    elif os.getenv('PERPLEXITY_API_KEY_B64'):
        try:
            # Try to decode base64 encoded key
            encoded_key = os.getenv('PERPLEXITY_API_KEY_B64')
            api_key = base64.b64decode(encoded_key).decode('utf-8')
            api_key_source = 'PERPLEXITY_API_KEY_B64 (decoded)'
        except Exception as e:
            print(f"❌ Failed to decode base64 API key: {e}")
            return False
    
    if not api_key:
        print("❌ No Perplexity API key found in environment variables")
        print("   Expected one of: PERPLEXITY_API_KEY, PPLX_API_KEY, PERPLEXITY_API_KEY_B64")
        return False
    
    # Validate API key format
    if not api_key.startswith('pplx-'):
        print(f"⚠️  API key from {api_key_source} doesn't start with 'pplx-'")
        print("   This might not be a valid Perplexity API key format")
        return False
    
    # Basic length check (Perplexity keys are typically around 56 characters)
    if len(api_key) < 40:
        print(f"⚠️  API key from {api_key_source} seems too short ({len(api_key)} characters)")
        print("   This might not be a valid Perplexity API key")
        return False
    
    print(f"✅ Perplexity API key found via {api_key_source}")
    print(f"   Key format: {api_key[:8]}...{api_key[-4:]} ({len(api_key)} characters)")
    print("✅ API key validation passed")
    
    return True

if __name__ == "__main__":
    try:
        success = test_perplexity_access()
        if success:
            print("🎉 Perplexity API configuration test completed successfully!")
            sys.exit(0)
        else:
            print("❌ Perplexity API configuration test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during API test: {e}")
        sys.exit(1) 