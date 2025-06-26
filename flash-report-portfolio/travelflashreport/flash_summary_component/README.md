# 🔥 Flash Summary Component

A reusable component for converting Perplexity AI output to properly formatted HTML with clickable citations and sources. Built for AI news aggregation but adaptable to any content type.

## ✅ What it Solves

**Before:** Perplexity API returns markdown with broken citations
- Plain text citations `[1]`, `[2]` (not clickable)
- Source URLs as raw text (not clickable)
- Prompt instruction leakage in output
- Inconsistent formatting

**After:** Professional HTML with working functionality
- ✅ **Clickable Citations**: `[1]`, `[2]` link directly to sources
- ✅ **Clickable Sources**: URLs become proper hyperlinks  
- ✅ **Clean Output**: Removes prompt leakage automatically
- ✅ **Proper Styling**: Matches your site design
- ✅ **H2 Headlines**: Auto-detects and formats main headlines

## 🚀 Quick Start

### Installation
```python
# Copy the flash_summary_component/ directory to your project
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

# Basic usage
generator = FlashSummaryGenerator()
html_output = generator.convert_to_html(perplexity_content)
```

### Integration Example
```python
# Replace your existing Perplexity conversion function
def convert_perplexity_to_rich_html(content, source_headlines=None):
    """Convert Perplexity content to HTML using the flash summary component."""
    config = FlashSummaryConfig.for_ai_site()  # or .for_crypto_site()
    generator = FlashSummaryGenerator(config)
    return generator.convert_to_html(content)
```

## 🎯 Key Features

### Smart Citation Processing
- **Multiple formats**: Handles `[1]`, `[2]` and `[^1]`, `[^2]` citations
- **Auto-linking**: Converts citations to clickable links
- **Source extraction**: Finds and formats source URLs automatically

### Content Cleanup
- **Prompt leakage removal**: Strips "IMPORTANT:" and instruction text
- **Headline detection**: Finds and converts main headlines to H2
- **Markdown processing**: Converts **bold**, bullet points, links

### Flexible Styling
- **Configurable colors**: Easy brand customization
- **Multiple presets**: `.for_ai_site()`, `.for_crypto_site()`
- **No containers**: Clean output without extra borders/backgrounds

## 📋 Real-World Example

**Input (Perplexity API):**
```
**AI NEWS FLASH - May 30, 2025**

**Microsoft Announces Major AI Agent Updates**

- Microsoft has announced significant updates [3]
- Google I/O 2025 highlights business AI [4]

IMPORTANT: Include working links...
- [3] https://windowscentral.com/software-apps/...
- [4] https://aitoday.com/ai-models/...
```

**Output (HTML):**
```html
<div class="ai-flash-summary" style="...">
    <strong>AI NEWS FLASH - May 30, 2025</strong><br><br>
    <h2 style="...">Microsoft Announces Major AI Agent Updates</h2><br><br>
    • Microsoft has announced significant updates <a href="..." target="_blank">[3]</a><br>
    • Google I/O 2025 highlights business AI <a href="..." target="_blank">[4]</a><br><br>
    [3]: <a href="https://windowscentral.com/..." target="_blank">https://windowscentral.com/...</a><br>
    [4]: <a href="https://aitoday.com/..." target="_blank">https://aitoday.com/...</a><br>
</div>
```

## 🔧 Configuration Options

### Preset Configurations
```python
# AI News Site (red accents)
config = FlashSummaryConfig.for_ai_site()

# Crypto Site (gold accents) 
config = FlashSummaryConfig.for_crypto_site()

# Custom configuration
config = FlashSummaryConfig(
    link_color="#your-brand-color",
    background_color="transparent",  # No background
    remove_prompt_leakage=True
)
```

### Available Options
- `background_color`: Container background (default: transparent)
- `text_color`: Main text color (default: #333)
- `link_color`: Citation and link color (default: #dc3545)
- `font_family`: Typography (default: system fonts)
- `remove_prompt_leakage`: Clean up instructions (default: True)

## 🧪 Testing

### Real API Testing
```python
# Test with actual Perplexity API
python -m flash_summary_component.test_real_api

# Manual testing
python test_manual_flash.py
```

### Sample Output Files
- `real_perplexity_test_[timestamp].html` - Real API results
- `manual_flash_test.html` - Manual test results

## 📁 File Structure

```
flash_summary_component/
├── __init__.py          # Package exports
├── core.py              # Main FlashSummaryGenerator class
├── config.py            # Configuration and presets
├── test_component.py    # Basic component testing
├── test_real_api.py     # Real Perplexity API testing
└── README.md            # This documentation
```

## 🔄 Integration Steps

1. **Copy Component**: Add `flash_summary_component/` to your project
2. **Replace Function**: Update your Perplexity conversion function
3. **Test Locally**: Run tests to verify functionality
4. **Deploy**: Push to production (no API changes needed)

## 🌐 Multi-Project Usage

This component is designed for reuse across projects:

- **AI News Sites**: Use `.for_ai_site()` preset (red theme)
- **Crypto Projects**: Use `.for_crypto_site()` preset (gold theme)
- **Custom Sites**: Create your own config with brand colors

## 🔒 Security Notes

- API keys never stored in component
- Uses existing project's API key management
- No additional credentials required
- Safe for git commits (no secrets)

## 📊 Performance

- **Fast**: Simple regex-based processing
- **Lightweight**: No external dependencies beyond existing project
- **Reliable**: Handles malformed input gracefully
- **Scalable**: Works with any Perplexity output size

## 🐛 Troubleshooting

### Citations Not Clickable
- Check if Perplexity returned source URLs
- Verify citation format (`[1]`, `[2]` or `[^1]`, `[^2]`)

### Styling Issues
- Use browser dev tools to inspect output
- Verify config settings
- Check for CSS conflicts

### Headline Not H2
- Ensure headline follows "AI NEWS FLASH" line
- Check for bullet points before headline
- Verify content structure

## 📈 Roadmap

- [ ] Support for numbered lists
- [ ] Image citation handling
- [ ] Multi-language support
- [ ] RSS feed integration
- [ ] Custom citation formats

---

Built with ❤️ for better AI content presentation. Ready for production use. 