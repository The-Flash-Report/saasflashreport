#!/usr/bin/env python3
import base64
import os

# Get API key from environment
api_key = os.getenv('PERPLEXITY_API_KEY')
if api_key:
    encoded = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
    print(f"PERPLEXITY_API_KEY_B64: {encoded}")
else:
    print("Please set PERPLEXITY_API_KEY environment variable first")
    print("Example: export PERPLEXITY_API_KEY='your-key-here'") 