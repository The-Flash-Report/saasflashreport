#!/usr/bin/env python3
"""
Manual test to force a fresh Perplexity API call and demonstrate the working flash summary component.
"""

import os
import sys
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import aggregator functions
from aggregator import call_perplexity_api_with_retry, convert_perplexity_to_rich_html

# Check if API key is available
if not os.environ.get('PERPLEXITY_API_KEY'):
    print("❌ Error: PERPLEXITY_API_KEY environment variable not set.")
    print("💡 Please add it to your .env file:")
    print("   echo 'PERPLEXITY_API_KEY=your-api-key-here' >> .env")
    sys.exit(1)

def test_manual_flash_summary():
    """Test the integrated flash summary component with a fresh Perplexity call."""
    
    print("🔥 Testing Flash Summary Component Integration...")
    
    # Create a test prompt for current AI news
    prompt = """Write a brief AI News Flash summary for today (May 30, 2025). Include:

1. A compelling headline about current AI developments
2. 3-4 bullet points covering recent AI trends, company news, or breakthroughs
3. A brief "Flash Insight" observation
4. Include some [1], [2], [3] style citations with sources

Focus on realistic, current AI industry topics like OpenAI updates, Google AI developments, enterprise AI adoption, or AI research breakthroughs."""

    try:
        # Call Perplexity API
        print("📡 Calling Perplexity API...")
        perplexity_response = call_perplexity_api_with_retry(prompt)
        
        if perplexity_response:
            print("✅ Perplexity API call successful!")
            print(f"Raw response length: {len(perplexity_response)} characters")
            
            # Convert using our integrated flash summary component
            print("🔄 Converting with Flash Summary Component...")
            converted_html = convert_perplexity_to_rich_html(perplexity_response)
            
            # Generate timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to test file
            with open('manual_flash_test.html', 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual Flash Summary Test</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        h1 {{ color: #dc3545; }}
    </style>
</head>
<body>
    <h1>🔥 Manual Flash Summary Test</h1>
    <p><strong>Generated:</strong> {timestamp}</p>
    
    <h2>Raw Perplexity Response:</h2>
    <pre style="background: #f8f9fa; padding: 20px; border-radius: 8px; overflow-x: auto;">{perplexity_response}</pre>
    
    <h2>Converted HTML (Flash Summary Component):</h2>
    <div style="border: 2px solid #dc3545; border-radius: 8px; padding: 20px;">
        {converted_html}
    </div>
</body>
</html>""")
            
            print("✅ Manual test completed!")
            print("📁 View results: http://localhost:8001/manual_flash_test.html")
            
        else:
            print("❌ Perplexity API call failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_manual_flash_summary() 