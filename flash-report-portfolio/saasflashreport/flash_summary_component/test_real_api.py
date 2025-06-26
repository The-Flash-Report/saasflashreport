"""
Real Perplexity API Test for Flash Summary Component

Uses your actual Perplexity API key to generate real content and test the component.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the flash summary component
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

# Import Perplexity functions from aggregator.py
sys.path.append('..')
try:
    from aggregator import call_perplexity_api_with_retry, decode_perplexity_api_key
except ImportError:
    print("Error: Could not import Perplexity functions from aggregator.py")
    print("Make sure this script is run from the flash_summary_component directory")
    sys.exit(1)

def test_real_perplexity_api():
    """Test the flash summary component with real Perplexity API content."""
    
    print("🌐 Testing Flash Summary Component with REAL Perplexity API")
    print("=" * 60)
    
    # Check API key
    api_key = decode_perplexity_api_key()
    if not api_key:
        print("❌ No Perplexity API key found!")
        print("Make sure PERPLEXITY_API_KEY is set in your .env file")
        return None
    
    print(f"✅ Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Create the prompt for today's AI news
    today_prompt = """
Generate a concise AI news flash summary for today with the most significant AI developments. 

Include citations [1], [2], etc. in the text and provide the corresponding URLs at the bottom.

Format:
AI NEWS FLASH - [Today's Date]

[Compelling headline about most significant AI development]

- [3-4 bullet points with key AI news, each with citations]

Flash Insight: [Brief analysis paragraph]

Sources:
- [1] [URL]
- [2] [URL]
etc.

Focus on: AI breakthroughs, company announcements, product launches, research findings.
"""
    
    print("\n🚀 Calling Perplexity API...")
    print(f"Prompt preview: {today_prompt[:100]}...")
    
    # Call the real API
    raw_content = call_perplexity_api_with_retry(today_prompt)
    
    if not raw_content:
        print("❌ Failed to get content from Perplexity API")
        return None
        
    print("\n📄 Raw Perplexity Response:")
    print("-" * 40)
    print(raw_content)
    print("-" * 40)
    
    # Test the flash summary component
    print("\n🔥 Testing Flash Summary Component...")
    config = FlashSummaryConfig.for_ai_site()
    generator = FlashSummaryGenerator(config)
    
    # Convert to HTML
    html_result = generator.convert_to_html(raw_content)
    
    print("\n✅ Component Conversion Complete!")
    print("\n🎨 Final HTML Output:")
    print("-" * 40)
    print(html_result)
    print("-" * 40)
    
    # Save both raw and processed content
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Save raw content
    raw_filename = f"real_perplexity_raw_{timestamp}.txt"
    with open(raw_filename, 'w', encoding='utf-8') as f:
        f.write(raw_content)
    
    # Save HTML result
    html_filename = f"real_perplexity_test_{timestamp}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real Perplexity API Test - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Real Perplexity API Test</h1>
        <div class="timestamp">Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</div>
        <p><strong>Testing flash summary component with LIVE Perplexity API content:</strong></p>
        {html_result}
        
        <hr style="margin: 40px 0; border: 1px solid #eee;">
        <details>
            <summary><strong>Raw Perplexity Response</strong> (click to expand)</summary>
            <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto;">{raw_content}</pre>
        </details>
    </div>
</body>
</html>
        """)
    
    print(f"\n💾 Saved files:")
    print(f"   📄 Raw content: {raw_filename}")
    print(f"   🌐 HTML test: {html_filename}")
    print(f"\n🔍 Open {html_filename} in your browser to see the result!")
    
    return {
        'raw_content': raw_content,
        'html_result': html_result,
        'html_file': html_filename
    }

if __name__ == "__main__":
    test_real_perplexity_api() 