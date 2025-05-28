## Relevant Files

- `aggregator.py` - Main aggregation script that needs modification for keyword filtering and page generation
- `keyword_config.json` - New configuration file for managing page definitions and keywords
- `keyword_template.html` - New Jinja2 template for keyword-filtered pages
- `template.html` - Existing template that may need navigation updates
- `generate_sitemap.py` - Needs updates to include keyword pages in sitemap
- `sitemap.xml` - Will be updated to include new keyword pages
- `config.json` - May need updates for keyword-specific filtering rules
- `openai-news.html` - Generated OpenAI-specific news page
- `google-ai-news.html` - Generated Google AI-specific news page
- `chatgpt-news.html` - Generated ChatGPT-specific news page
- `chatgpt-updates.html` - Generated ChatGPT updates page
- `machine-learning-news.html` - Generated machine learning news page
- `deep-learning-news.html` - Generated deep learning news page
- `ai-research-news.html` - Generated AI research news page
- `ai-news-today.html` - Generated daily curated highlights page
- `ai-breakthrough-news.html` - Generated breakthrough news page
- `ai-startup-news.html` - Generated startup news page
- `ai-industry-news.html` - Generated industry news page

### Notes

- All generated HTML pages will be created automatically by the modified aggregator.py script
- The keyword filtering system will integrate with existing RSS feeds, NewsAPI, Reddit, and Perplexity sources
- Templates will maintain consistency with existing site design and navigation
- SEO optimization will be built into the page generation process

## Tasks

- [ ] 1.0 Implement Core Keyword Filtering Infrastructure
  - [x] 1.1 Create keyword_config.json configuration file with page definitions
  - [x] 1.2 Add load_keyword_config() function to aggregator.py
  - [x] 1.3 Implement matches_keywords() function for text matching
  - [x] 1.4 Create calculate_keyword_relevance_score() function for article scoring
  - [x] 1.5 Implement filter_articles_for_keyword_page() function
  - [x] 1.6 Add generate_keyword_pages_data() function to process all pages
  - [x] 1.7 Add generate_keyword_page_files() function for HTML generation
  - [x] 1.8 Integrate keyword page generation into main() function
  - [ ] 1.9 Test keyword filtering with sample data
- [x] 2.0 Create Keyword Configuration System
  - [x] 2.1 Review `keyword_config.json` for completeness and correctness against the PRD.
  - [x] 2.2 Implement schema validation for `keyword_config.json` within `load_keyword_config()`.
  - [x] 2.3 Document the `keyword_config.json` format.
- [x] 3.0 Develop Keyword Page Template System
  - [x] 3.1 Create `keyword_template.html` (e.g., by duplicating/extending `template.html`).
  - [x] 3.2 Modify `keyword_template.html` to display keyword-specific content (title, description, articles) and use variables like `keyword_page_config`.
  - [x] 3.3 Ensure common elements (header, footer, navigation, contact form, prompt widget) are present and styled consistently.
  - [x] 3.4 Confirm `aggregator.py` uses `keyword_template.html` correctly.
- [x] 4.0 Implement Automated Company-Specific Pages
  - [x] 4.1 Verify `keyword_config.json` for "openai-news", "google-ai-news", "chatgpt-news", "chatgpt-updates" against PRD.
  - [x] 4.2 Confirm `aggregator.py` correctly processes automated company-specific page types.
  - [x] 4.3 Test generation of company-specific pages (openai-news.html, google-ai-news.html, etc.).
- [x] 5.0 Implement Topic-Specific Pages
  - [x] 5.1 Verify `keyword_config.json` for "machine-learning-news", "deep-learning-news", "ai-research-news" against PRD.
  - [x] 5.2 Confirm `aggregator.py` correctly processes automated topic-specific page types.
  - [x] 5.3 Test generation of topic-specific pages (machine-learning-news.html, etc.).
- [x] 6.0 Implement Curated Content Pages Framework
  - [x] 6.1 Clarify/confirm `page_type` for `ai-startup-news` & `ai-industry-news` (assume automated per config).
  - [x] 6.2 Review `aggregator.py` handling of `page_type: "curated"` (currently skips auto-filtering).
  - [x] 6.3 Design manual content structure for curated pages (e.g., `curated_content/[page_key].json`).
  - [x] 6.4 Modify `aggregator.py` to load and render content from these manual JSON files for "curated" pages.
  - [x] 6.5 Create placeholder `curated_content/ai-news-today.json` and `curated_content/ai-breakthrough-news.json`.
  - [x] 6.6 Test generation of `ai-news-today.html` and `ai-breakthrough-news.html` using placeholder manual content.
  - [x] 6.7 Fix content display on automated keyword pages (e.g., ensuring openai-news.html shows its own articles or 'no articles' message).
  - [x] 6.8 Ensure "Prompt of the Day" widget HTML and CSS are correctly implemented and appearing on keyword pages.
  - [x] 6.9 Ensure Newsletter Form HTML and CSS are correctly implemented and appearing on keyword pages.
- [x] 7.0 Integrate Navigation and SEO Enhancements
  - [x] 7.1 Add links to new keyword pages in the site's main navigation (e.g., under a "Categories" or "Topics" dropdown).
  - [x] 7.2 Update `generate_sitemap.py` to include all keyword pages in `sitemap.xml`.
  - [x] 7.3 Add relevant meta tags (description, keywords) to `keyword_template.html` using data from `keyword_config.json`.
- [ x ] 8.0 Implement category page on site navigation 
- [ ] 9.0 Testing, Optimization and Deployment
  - [x ] 9.1 Remove the text that appears above site logo 
- [x] 10. Update REPLICABLE_NEWS_AGGREGATOR_GUIDE.md to document changes
- [x] 11. Final QA and Deployment
  - [x] 11.1 Verify sitemap has new pages and SEO is correct
  - [x] 11.2 Test all keyword pages load correctly
  - [x] 11.3 Clean up any debug code or temporary files
  - [x] 11.4 Final aggregator run to ensure everything works