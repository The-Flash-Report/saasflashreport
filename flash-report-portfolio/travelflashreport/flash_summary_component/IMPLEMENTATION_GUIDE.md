# Flash Summary Component - Implementation Guide

## 📋 Quick Implementation Checklist

Use this checklist to integrate the Flash Summary Component into any new project:

### ✅ Pre-Implementation
- [ ] **Project Assessment**: Confirm you have Perplexity API integration
- [ ] **API Key Access**: Verify Perplexity API key is available
- [ ] **Python Version**: Ensure Python 3.6+ is installed
- [ ] **Dependencies**: Check for existing `re` and `typing` modules (standard library)

### ✅ Component Setup
- [ ] **Copy Component**: Copy entire `flash_summary_component/` directory to your project root
- [ ] **Test Import**: Verify you can import the component: `from flash_summary_component import FlashSummaryGenerator`
- [ ] **Choose Configuration**: Select `.for_ai_site()`, `.for_crypto_site()`, or create custom config

### ✅ Integration Steps
- [ ] **Locate Conversion Function**: Find your existing Perplexity → HTML conversion code
- [ ] **Replace Function**: Update to use Flash Summary Component (see code example below)
- [ ] **Test Locally**: Run with sample Perplexity output to verify functionality
- [ ] **Validate Citations**: Ensure citations become clickable links
- [ ] **Check Styling**: Verify output matches your site design

### ✅ Testing & Validation
- [ ] **Real API Test**: Test with actual Perplexity API calls
- [ ] **Edge Cases**: Test with empty content, malformed input, missing citations
- [ ] **Cross-Browser**: Verify links work in Chrome, Firefox, Safari
- [ ] **Mobile Testing**: Check responsive behavior on mobile devices
- [ ] **Performance**: Measure processing time for typical content size

### ✅ Deployment
- [ ] **Remove Test Files**: Delete any test HTML files before deployment
- [ ] **Verify API Keys**: Ensure production API keys are configured
- [ ] **Deploy to Staging**: Test in staging environment first
- [ ] **Monitor Production**: Watch for errors after production deployment
- [ ] **Validate Live Citations**: Click test citations on live site

## 🔧 Code Integration Examples

### Basic Integration (Replace Existing Function)

**Before:**
```python
def convert_perplexity_to_rich_html(content, source_headlines=None):
    # Old, complex conversion logic with bugs
    html_content = content.replace('\n', '<br>')
    # ... 50+ lines of brittle formatting code
    return html_content
```

**After:**
```python
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

def convert_perplexity_to_rich_html(content, source_headlines=None):
    """Convert Perplexity content to HTML using the flash summary component."""
    config = FlashSummaryConfig.for_ai_site()  # Choose appropriate preset
    generator = FlashSummaryGenerator(config)
    return generator.convert_to_html(content)
```

### Custom Configuration Example

```python
# Custom styling for your brand
config = FlashSummaryConfig(
    link_color="#your-brand-color",      # Your brand's primary color
    text_color="#333",                   # Dark gray text
    background_color="transparent",      # No background container
    font_family="'Your Font', sans-serif",
    remove_prompt_leakage=True,          # Clean up AI instructions
    add_sources_header=False             # No "Sources:" header
)

generator = FlashSummaryGenerator(config)
html = generator.convert_to_html(perplexity_response)
```

### Framework-Specific Examples

#### Flask Integration
```python
from flask import Flask
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

app = Flask(__name__)
generator = FlashSummaryGenerator(FlashSummaryConfig.for_ai_site())

@app.route('/api/summary')
def generate_summary():
    perplexity_response = call_perplexity_api(request.args.get('query'))
    html_summary = generator.convert_to_html(perplexity_response)
    return {'html': html_summary}
```

#### Django Integration
```python
# views.py
from django.shortcuts import render
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

def summary_view(request):
    generator = FlashSummaryGenerator(FlashSummaryConfig.for_ai_site())
    perplexity_response = get_perplexity_data()
    summary_html = generator.convert_to_html(perplexity_response)
    return render(request, 'summary.html', {'summary': summary_html})
```

## 🎨 Configuration Presets

### Available Presets

#### AI News Sites
```python
config = FlashSummaryConfig.for_ai_site()
# Red accents (#dc3545), clean styling, tech-focused
```

#### Crypto Projects  
```python
config = FlashSummaryConfig.for_crypto_site()
# Gold accents (#f39c12), finance-focused styling
```

#### Custom Brands
```python
config = FlashSummaryConfig(
    link_color="#your-color",
    background_color="transparent",  # Recommended: no background
    text_color="#333",               # Standard dark text
    border_left="none",              # Remove left border
    padding="0",                     # Remove container padding
)
```

## 🧪 Testing Strategies

### 1. Component Testing
```python
# Create test file: test_integration.py
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

def test_basic_functionality():
    generator = FlashSummaryGenerator()
    
    # Test with sample content
    test_content = """
    **AI NEWS FLASH - May 30, 2025**
    
    **Test Headline**
    
    - First point with citation [1]
    - Second point with citation [2]
    
    [1]: https://example.com/source1
    [2]: https://example.com/source2
    """
    
    result = generator.convert_to_html(test_content)
    
    # Verify expected elements
    assert '<h2' in result              # Headline converted
    assert 'href=' in result            # Citations are links
    assert '[1]</a>' in result          # Citation format correct
    assert 'example.com' in result      # Sources included
    
    print("✅ Basic functionality test passed!")

if __name__ == "__main__":
    test_basic_functionality()
```

### 2. Real API Testing
```python
# Create test file: test_real_api.py
import os
from your_project import call_perplexity_api  # Your existing function
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

def test_real_perplexity_integration():
    # Ensure API key is available
    if not os.environ.get('PERPLEXITY_API_KEY'):
        print("❌ Set PERPLEXITY_API_KEY environment variable first")
        return
    
    # Call real Perplexity API
    test_prompt = "Write a brief summary about recent AI developments with citations."
    perplexity_response = call_perplexity_api(test_prompt)
    
    # Convert using component
    generator = FlashSummaryGenerator(FlashSummaryConfig.for_ai_site())
    html_result = generator.convert_to_html(perplexity_response)
    
    # Save result for manual inspection
    with open('test_real_output.html', 'w') as f:
        f.write(f'''
        <!DOCTYPE html>
        <html><head><title>Test</title></head>
        <body>{html_result}</body></html>
        ''')
    
    print("✅ Real API test completed! Check test_real_output.html")

if __name__ == "__main__":
    test_real_perplexity_integration()
```

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

#### Citations Not Clickable
**Problem**: Citation numbers appear as plain text  
**Cause**: Perplexity didn't return source URLs  
**Solution**: 
- Check raw Perplexity response for URL patterns
- Verify your prompt asks for sources/citations
- Test with different Perplexity models

#### Styling Conflicts
**Problem**: Component styling conflicts with site CSS  
**Solution**:
```python
# Use transparent background and minimal styling
config = FlashSummaryConfig(
    background_color="transparent",
    padding="0",
    margin="0",
    border_left="none"
)
```

#### Headlines Not Converting
**Problem**: Main headline stays as plain text  
**Cause**: Component can't detect headline structure  
**Solution**:
- Ensure headline comes after "AI NEWS FLASH" line
- Check for bullet points appearing before headline
- Verify headline isn't wrapped in multiple ** markers

#### Performance Issues
**Problem**: Slow processing of large content  
**Solution**:
- Check content size (component handles <10KB efficiently)
- Profile with `time.time()` measurements
- Consider splitting very large content

### Debug Mode
```python
# Enable verbose processing for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

generator = FlashSummaryGenerator(config)
result = generator.convert_to_html(content)

# Check intermediate steps
print("Citations found:", generator._last_citations)  # Debug info
```

## 📦 Project Templates

### New Project Setup
```bash
# 1. Create new project directory
mkdir my-ai-news-site
cd my-ai-news-site

# 2. Copy Flash Summary Component
cp -r /path/to/flash_summary_component ./

# 3. Create basic structure
mkdir templates static
touch app.py requirements.txt

# 4. Install dependencies
pip install flask requests python-dotenv

# 5. Create .env file
echo "PERPLEXITY_API_KEY=your-key-here" > .env
```

### Minimal App Template
```python
# app.py
import os
from flask import Flask, render_template_string
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig
import requests

app = Flask(__name__)

# Configure Flash Summary Component
config = FlashSummaryConfig.for_ai_site()  # or .for_crypto_site()
generator = FlashSummaryGenerator(config)

def call_perplexity_api(prompt):
    # Your Perplexity API integration here
    # Return the response content
    pass

@app.route('/')
def home():
    # Generate fresh summary
    prompt = "Create an AI news summary for today with citations"
    perplexity_response = call_perplexity_api(prompt)
    summary_html = generator.convert_to_html(perplexity_response)
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI News Summary</title>
        <style>
            body { font-family: -apple-system, sans-serif; margin: 40px; }
            .summary { max-width: 800px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div class="summary">
            {{ summary_html|safe }}
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, summary_html=summary_html)

if __name__ == '__main__':
    app.run(debug=True)
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] **Remove Test Files**: Delete `test_*.html`, debug scripts
- [ ] **Environment Variables**: Verify API keys in production environment
- [ ] **Dependencies**: Ensure component is included in deployment package
- [ ] **Configuration**: Set appropriate config for production (`.for_ai_site()` etc.)

### Production Validation
- [ ] **Test Live Citations**: Click citation links on production site
- [ ] **Monitor Errors**: Check logs for component-related errors
- [ ] **Performance**: Monitor page load times after integration
- [ ] **Mobile Testing**: Verify mobile responsiveness in production

### Post-Deployment
- [ ] **User Feedback**: Monitor for citation/formatting issues
- [ ] **Analytics**: Track citation click rates if possible
- [ ] **Updates**: Plan for component updates and maintenance

## 📈 Success Metrics

Track these metrics to measure integration success:

### Technical Metrics
- **Integration Time**: Should be < 30 minutes
- **Error Rate**: < 0.1% of conversions should fail
- **Performance**: < 100ms processing time per summary

### User Experience Metrics
- **Citation Clicks**: > 5% of readers click citations
- **Source Access**: > 95% of citation links work correctly
- **Mobile Usage**: Component renders on all screen sizes

### Maintenance Metrics
- **Bug Reports**: < 1 formatting issue per month
- **Code Maintenance**: No custom formatting code to maintain
- **Update Time**: Component updates deploy in < 5 minutes

---

**🎉 Ready to implement?** Start with the Quick Implementation Checklist above and refer back to specific sections as needed. The component is designed to "just work" with minimal configuration! 