# Content Replacement Checklist - AI → Niche Conversion

## Overview
This checklist documents systematic replacement of AI-specific content with niche-appropriate content for each Flash Report site.

## Files Requiring Content Replacement

### 1. Configuration Files
- [ ] **config.json** - Site branding (name, emoji, tagline, theme_color, domain)
- [ ] **keyword_config.json** - All keyword pages and categories  
- [ ] **netlify.toml** - Domain configuration
- [ ] **site.webmanifest** - PWA manifest (name, description, theme_color)

### 2. Template Files  
- [ ] **template.html** - Site title, meta tags, descriptions, navigation
- [ ] **archive_index_template.html** - Archive page titles and descriptions
- [ ] **sitemap_template.xml** - Update domain references
- [ ] **templates/template.html** - Main template file (if different)
- [ ] **templates/keyword_template.html** - Topic page template

### 3. Static Pages (Complete Rewrite Required)
- [ ] **about.html** - Complete niche-focused content rewrite
- [ ] **contact.html** - Update contact form text and descriptions  
- [ ] **contact-success.html** - Update success messaging
- [ ] **thank-you.html** - Update thank you messaging
- [ ] **robots.txt** - Update domain references

### 4. Build & Deployment Scripts
- [ ] **build.sh** - Update any AI-specific references
- [ ] **aggregator.py** - Categories, RSS feeds, NewsAPI keywords, content sources
- [ ] **generate_sitemap.py** - Domain configuration
- [ ] **validate_sitemap.py** - Domain references

### 5. GitHub Actions
- [ ] **.github/workflows/daily-update.yml** - Repository references, domain configs

### 6. Documentation
- [ ] **README.md** - Complete rewrite for niche
- [ ] Create niche-specific **PROJECT_SUMMARY.md**

## Search/Replace Patterns by Niche

### Health Flash Report 🧬
```
Find: "AI Flash Report" → Replace: "Health Flash Report"
Find: "AI news" → Replace: "health news"  
Find: "artificial intelligence" → Replace: "health technology"
Find: "AI" (context-dependent) → Replace: "health"
Find: "aiflashreport.com" → Replace: "healthflashreport.com"
Find: "#3B82F6" (blue) → Replace: "#10B981" (emerald)
Find: "⚡" → Replace: "🧬"
Find: "Latest AI News" → Replace: "Breakthrough Health at Breakthrough Speed"
```

### Tech Flash Report 🚀  
```
Find: "AI Flash Report" → Replace: "Tech Flash Report"
Find: "AI news" → Replace: "tech news"
Find: "artificial intelligence" → Replace: "technology startups"
Find: "aiflashreport.com" → Replace: "techflashreport.com"
Find: "#3B82F6" (blue) → Replace: "#8B5CF6" (violet)
Find: "⚡" → Replace: "🚀"
Find: "Latest AI News" → Replace: "Silicon Valley Speed, Global Reach"
```

### Fitness Flash Report 💪
```
Find: "AI Flash Report" → Replace: "Fitness Flash Report"
Find: "AI news" → Replace: "fitness news"
Find: "artificial intelligence" → Replace: "fitness science"
Find: "aiflashreport.com" → Replace: "fitnessflashreport.com"
Find: "#3B82F6" (blue) → Replace: "#EF4444" (red)
Find: "⚡" → Replace: "💪"
Find: "Latest AI News" → Replace: "Peak Performance, Peak Speed"
```

### Travel Flash Report ✈️
```
Find: "AI Flash Report" → Replace: "Travel Flash Report"
Find: "AI news" → Replace: "travel news"
Find: "artificial intelligence" → Replace: "travel industry"
Find: "aiflashreport.com" → Replace: "travelflashreport.com"
Find: "#3B82F6" (blue) → Replace: "#0EA5E9" (sky blue)
Find: "⚡" → Replace: "✈️"
Find: "Latest AI News" → Replace: "Adventures at Jet Speed"
```

### Startup Flash Report 🦄
```
Find: "AI Flash Report" → Replace: "Startup Flash Report"
Find: "AI news" → Replace: "startup news"
Find: "artificial intelligence" → Replace: "startup ecosystem"
Find: "aiflashreport.com" → Replace: "startupflashreport.com"
Find: "#3B82F6" (blue) → Replace: "#EC4899" (pink)
Find: "⚡" → Replace: "🦄"
Find: "Latest AI News" → Replace: "Unicorns at Rocket Speed"
```

### SaaS Flash Report ⚙️
```
Find: "AI Flash Report" → Replace: "SaaS Flash Report"
Find: "AI news" → Replace: "SaaS news"
Find: "artificial intelligence" → Replace: "B2B software"
Find: "aiflashreport.com" → Replace: "saasflashreport.com"
Find: "#3B82F6" (blue) → Replace: "#6366F1" (indigo)
Find: "⚡" → Replace: "⚙️"
Find: "Latest AI News" → Replace: "Software Success at Software Speed"
```

## Content Source Configuration

### RSS Feeds (Replace AI sources with niche sources)
- Update `aggregator.py` RSS feed URLs
- Test all feeds for accessibility and content quality
- Minimum 25 working feeds per niche

### NewsAPI Keywords (Replace AI keywords)
- Update NewsAPI search terms in `aggregator.py`
- Configure niche-specific source filtering
- Test keyword effectiveness

### Reddit Sources (Replace AI subreddits)  
- Update Reddit subreddit list in `aggregator.py`
- Verify subreddit activity and relevance
- Configure appropriate content filtering

## Flash Summary Component Configuration

### Perplexity Prompt Customization
- [ ] Update prompt in `flash_summary_component/core.py`
- [ ] Test with niche-specific content
- [ ] Verify citation functionality works
- [ ] Update component styling for niche theme

### Niche-Specific Prompts

#### Health Flash Report Prompt:
```
Create a daily health/longevity news summary with this format:
**HEADLINE:** [Compelling headline about the biggest health breakthrough today]
**TOP 3 STORIES:**
1. [Story 1 with 2-sentence analysis of practical implications]
2. [Story 2 with 2-sentence analysis]  
3. [Story 3 with 2-sentence analysis]
**FLASH INSIGHT:** [3-sentence commentary on longevity/optimization trends]
Focus on: Longevity research, biohacking studies, health tech devices, medical breakthroughs, nutrition science, performance optimization. Prioritize actionable insights for health optimization enthusiasts.
```

#### Tech Flash Report Prompt:
```
Create a daily tech news summary with this format:
**HEADLINE:** [Compelling headline about the biggest tech story today]
**TOP 3 STORIES:**
1. [Story 1 with 2-sentence analysis of market implications]
2. [Story 2 with 2-sentence analysis]
3. [Story 3 with 2-sentence analysis]  
**FLASH INSIGHT:** [3-sentence commentary on tech trends/disruption]
Focus on: Startup funding, product launches, enterprise software, developer tools, big tech moves, IPOs, acquisitions. Prioritize insights for tech professionals and investors.
```

## SEO Metadata Updates

### Meta Tags (All Templates)
- [ ] Update title tags with niche keywords
- [ ] Update meta descriptions with niche focus
- [ ] Update OpenGraph tags
- [ ] Update Twitter Card tags
- [ ] Update Schema.org structured data

### Domain References
- [ ] Update canonical URLs
- [ ] Update sitemap references  
- [ ] Update analytics domains
- [ ] Update social media links

## Validation Checklist

### Before Declaring Complete:
- [ ] All AI references replaced with niche terms
- [ ] Color scheme updated throughout
- [ ] Flash Summary Component configured and tested
- [ ] All RSS feeds validated and working
- [ ] Content categories appropriate for niche
- [ ] Analytics tracking configured
- [ ] Navigation and links working
- [ ] Mobile responsive design maintained
- [ ] SEO metadata optimized for niche

## Quality Assurance Process

### Testing Protocol:
1. **Content Testing** - Run aggregator and verify niche content collection
2. **Flash Summary Testing** - Generate summary with real data  
3. **Template Testing** - Verify all templates render correctly
4. **Link Testing** - Check all navigation and external links
5. **Mobile Testing** - Verify responsive design works
6. **SEO Testing** - Validate meta tags and structured data

This checklist ensures systematic and complete conversion from AI Flash Report to any niche-specific Flash Report site. 