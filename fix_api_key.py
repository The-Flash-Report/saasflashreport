#!/usr/bin/env python3
"""
Generate properly encoded base64 API key for GitHub Actions
"""

import base64
import os

# Get your actual API key (replace this with your real key)
# You can also set it as an environment variable: export PERPLEXITY_API_KEY="your-key-here"
api_key = os.getenv('PERPLEXITY_API_KEY')

if not api_key:
    print("❌ Please set your API key:")
    print("   export PERPLEXITY_API_KEY='your-actual-api-key-here'")
    print("   python3 fix_api_key.py")
    exit(1)

if not api_key.startswith('pplx-'):
    print(f"⚠️  Warning: API key doesn't start with 'pplx-': {api_key[:10]}...")

# Encode to base64 (ensure no newlines)
encoded = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')

print("🔑 Perplexity API Key Base64 Encoder")
print("-" * 50)
print(f"✅ Original key length: {len(api_key)} characters")
print(f"✅ Encoded key length: {len(encoded)} characters")
print(f"✅ Encoded key: {encoded}")
print()
print("📋 Next steps:")
print("1. Go to your GitHub repository settings")
print("2. Navigate to Secrets and variables > Actions")
print("3. Add a new repository secret:")
print("   Name: PERPLEXITY_API_KEY_B64")
print(f"   Value: {encoded}")
print("4. Keep your existing PERPLEXITY_API_KEY secret as backup")
print("5. Re-run the workflow")

# Test decoding to verify it works
try:
    decoded = base64.b64decode(encoded).decode('utf-8')
    if decoded == api_key:
        print("\n✅ Encoding/decoding test passed!")
    else:
        print("\n❌ Encoding/decoding test failed!")
except Exception as e:
    print(f"\n❌ Encoding test failed: {e}") 