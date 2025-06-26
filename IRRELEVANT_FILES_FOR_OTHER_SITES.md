# Files Not Relevant for Other Niche Sites

This document lists files in the AI Flash Report project that are AI-specific and should not be copied when building other niche sites.

## AI-Specific Content Files (Do Not Copy)
- `index.html` - Contains AI-specific content, use as template only
- `about.html` - AI-focused about page, needs complete rewrite per niche
- `ai-news-today.html` - AI-specific curated page
- `processed_urls.json` - AI site's processed URLs, each site needs its own
- `sitemap.xml` - AI site specific, each site generates its own
- `data/main_page_content.json` - AI content data, each site needs its own
- `data/main_page_content.json.backup` - AI content backup

## AI-Specific Configuration (Template Only, Modify Content)
- `config.json` - Copy structure, replace with niche-specific settings
- `keyword_config.json` - Copy structure, replace with niche keywords
- `aggregator.py` - Copy and modify categories, RSS feeds, keywords for each niche

## Generated/Archive Directories (Site-Specific)
- `archive/` - Daily archives for AI site only
- `topics/` - AI-specific topic pages
- `topic_archives/` - AI topic archives
- `curated_content/` - AI curated content

## Testing/Development Files (Not for Production Sites)
- `test_manual_flash.py` - Development testing script
- `test_perplexity.py` - API testing script  
- `test_perplexity_access.py` - API validation script
- `flash-summary-qa.html` - QA testing page
- `real_perplexity_raw_20250530_212943.txt` - Test data
- `integration_example.py` - Example code
- `quick_encode.py` - Utility script
- `encode_api_key.py` - Key encoding utility
- `fix_api_key.py` - Key fixing utility
- `update_rss.py` - Empty utility file
- `update_template.py` - Template update utility

## Documentation (AI Project Specific)
- `PROJECT_SUMMARY.md` - AI Flash Report project summary
- `README.md` - AI site specific README
- `TODO.md` - AI site todos
- `seo-strategy.md` - AI site SEO strategy
- `content-aggregation-site-rules.md` - AI site rules

## Universal Files (Copy These)
- `template.html` - Universal template (modify AI references)
- `archive_index_template.html` - Archive template
- `sitemap_template.xml` - Sitemap template
- `contact.html` - Contact form (modify AI references)
- `contact-success.html` - Contact success page (modify AI references)
- `thank-you.html` - Thank you page (modify AI references)
- `requirements.txt` - Python dependencies
- `generate_sitemap.py` - Sitemap generator
- `validate_sitemap.py` - Sitemap validator
- `build.sh` - Build script (modify for niche)
- `netlify.toml` - Deployment config
- `robots.txt` - SEO robots file
- `site.webmanifest` - PWA manifest (modify for niche)
- `favicon.ico` - Replace with niche-specific favicon
- `favicon.svg` - Replace with niche-specific favicon
- `.gitignore` - Git ignore rules
- `flash_summary_component/` - Flash Summary Component (universal)

## GitHub Actions
- `.github/workflows/` - Copy workflow, modify for niche-specific repos

## Template Process for New Sites

### Step 1: Copy Universal Files
Copy the "Universal Files" listed above to new site folder.

### Step 2: Modify Content References
Systematically replace all AI references with niche-specific content in:
- Templates (template.html, contact.html, etc.)
- Configuration files (config.json, keyword_config.json) 
- Scripts (aggregator.py categories and RSS feeds)
- Static pages (about.html content rewrite)

### Step 3: Create Niche-Specific Content
- Write new about.html for the niche
- Update site.webmanifest with niche branding
- Create niche-specific favicon files
- Update README.md for the niche
- Modify build.sh for niche requirements

### Step 4: Do NOT Copy
- Any generated content files (index.html, archives, processed_urls.json)
- AI-specific documentation or test files
- Site-specific data files

This ensures each new site starts clean with universal templates but niche-specific content and configuration. 