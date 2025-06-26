"""
Test Flash Summary Component

Tests the component with real Perplexity output to ensure it works correctly.
"""

from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

# Real Perplexity output from the live site (with issues)
SAMPLE_PERPLEXITY_OUTPUT = """
AI NEWS FLASH - May 30, 2025

Google and Microsoft Commit $80 Billion to AI Data Centers, While Anthropic Raises Antitrust Concerns

- Google I/O 2025 Transforms Business AI Landscape: Google is delivering measurable ROI through reasoning AI, enterprise security, and autonomous workflow capabilities. The new AI Mode shopping experience integrates agentic assistants for autonomous customer decisions, and Google Meet's speech translation maintains voice tone in real-time. Project Mariner automates routine digital tasks, and the Google-NVIDIA partnership enables on-premises deployment for healthcare and financial institutions [1].

- Microsoft's $80 Billion AI Vision Takes Shape: Microsoft is positioning itself as an AI-first company with ambitious plans, including the evolution of Copilot and the introduction of autonomous agents. The company has committed $80 billion to AI data centers throughout 2025 and is expanding its OpenAI partnership with collaborations including Mistral AI. CEO Satya Nadella emphasizes that AI's scaling power surpasses previous technological advances, promising to increase value and reduce waste in knowledge work [1].

- Anthropic Cautions DOJ's Antitrust Move Against Google: Anthropic has raised concerns that the Department of Justice's antitrust move against Google might hinder AI investment. This move could impact the development and deployment of AI technologies, potentially affecting the entire industry [2].

Flash Insight: The significant investments by Google and Microsoft in AI data centers highlight the growing importance of AI in business operations, while Anthropic's cautionary statement underscores the regulatory challenges that AI companies face, potentially influencing future AI development strategies. These developments underscore the dynamic and competitive landscape of the AI industry.

IMPORTANT: Include working links and sources with each story. Use citations [1], [2], etc. and provide the corresponding URLs at the bottom.

Sources:
- [1] https://aitoday.com/ai-models/big-ai-news-from-anthropic-google-microsoft-deepseek/
- [2] https://opentools.ai/news/openai-eyes-a-chromium-future-a-game-changing-browser-bid/antitrust
"""

def test_component():
    """Test the flash summary component with real Perplexity output."""
    
    print("🧪 Testing Flash Summary Component")
    print("=" * 50)
    
    # Initialize component
    config = FlashSummaryConfig.for_ai_site()
    generator = FlashSummaryGenerator(config)
    
    # Convert the sample content
    result_html = generator.convert_to_html(SAMPLE_PERPLEXITY_OUTPUT)
    
    # Print the result
    print("✅ Conversion Complete!")
    print("\n📄 Generated HTML:")
    print("-" * 30)
    print(result_html)
    print("-" * 30)
    
    # Save to file for testing
    with open('test_flash_summary_output.html', 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flash Summary Component Test</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Flash Summary Component Test</h1>
        <p><strong>Testing with real Perplexity output:</strong></p>
        {result_html}
    </div>
</body>
</html>
        """)
    
    print("\n💾 Saved test output to: test_flash_summary_output.html")
    print("🌐 Open this file in a browser to see the result!")
    
    return result_html

if __name__ == "__main__":
    test_component() 