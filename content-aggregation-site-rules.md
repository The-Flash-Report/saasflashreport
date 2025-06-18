# Content Aggregation Site Rules & Best Practices

## 🎯 Core Principles

### 1. Quality Over Quantity
- Prioritize authoritative sources over high-volume, low-quality feeds
- Limit Reddit posts to max 30% of total content
- Test ALL RSS feeds before implementation
- Remove broken or low-quality sources immediately

### 2. Source Diversification Strategy
Target Source Mix:
- 60-70%: Authoritative RSS feeds (research institutions, major companies)
- 20-25%: Curated news APIs (NewsAPI with category filtering)
- 10-15%: Social sources (Reddit, with strict limits)
- 5%: AI-generated summaries (Perplexity, Claude, etc.)

## 📡 RSS Feed Selection Guidelines

### Tier 1 Sources (Primary - 15-20 feeds)
- Research institutions (MIT, Stanford, Berkeley)
- Major tech companies (Google Research, OpenAI, Microsoft Research)
- Established tech publications (MIT Technology Review, Wired, TechCrunch)
- Industry-specific authoritative sources

### Feed Validation Process
1. Test each RSS URL with a simple script
2. Verify recent posts (within last 7 days)
3. Check language detection (English only)
4. Validate content quality (no spam, relevant titles)
5. Monitor feed reliability over 1-2 weeks

## 🔧 Technical Implementation Rules

### Content Processing Pipeline
1. Fetch → RSS feeds, News APIs, Social sources
2. Filter → Language detection, date filtering, deduplication
3. Categorize → Smart keyword-based categorization
4. Enhance → AI summaries, rewritten headlines
5. Paginate → 20 items per page maximum
6. Archive → Historical data for analytics

### API Integration Standards
- NewsAPI: Use category filters (technology, science) over broad queries
- AI APIs: Implement retry logic and fallback content
- Rate Limiting: Respect all API limits with proper delays
- Error Handling: Graceful degradation when APIs fail

## 🚀 Deployment & Maintenance

### Local Development Workflow
1. Test aggregator with python3 aggregator.py
2. Preview locally with python3 -m http.server 8000
3. Verify all pages load correctly
4. Check RSS feed status before committing

### Git Workflow for Content Sites
# Standard workflow
git add .
git commit -m "feat: [brief description] - [key changes] - [impact]"
git push origin main

# For content conflicts (generated files)
git reset --hard HEAD  # If conflicts with generated content
git push origin main --force  # When local content is authoritative

## 🛠️ Project Git Workflow Rule

- **Always pull the latest version from GitHub before making any changes.**
  - The site updates automatically once per day when the script runs, so your local copy may be out of date.
  - Run: `git pull origin main` before starting any new work.
- Make your changes locally.
- Test your changes locally (run the script and preview the site).
- Before pushing, make sure your branch is up to date with `main`.
- Commit with a clear message describing your change.
- Push to GitHub: `git push origin main` (or your branch if using feature branches).
- The deployment will be triggered automatically after pushing to GitHub.

## ⚠️ Common Pitfalls to Avoid

### Content Issues
- ❌ Relying too heavily on Reddit (>30% content)
- ❌ Not testing RSS feeds before deployment
- ❌ Accepting broken or low-quality feeds
- ❌ Over-categorization (too many categories)
- ❌ Poor mobile experience

### Technical Issues
- ❌ No error handling for failed API calls
- ❌ Hard-coding API keys in source code
- ❌ No rate limiting on external APIs
- ❌ Poor date handling causing crashes
- ❌ No backup content when APIs fail

## 📈 Success Metrics

### Launch Criteria (First 30 Days)
- [ ] 15+ working RSS feeds from tier 1 sources
- [ ] <5% broken links across all content
- [ ] Daily fresh content (minimum 50 articles)
- [ ] Mobile page load <3 seconds
- [ ] All topic pages properly categorized

### Growth Metrics (30-90 Days)
- [ ] User engagement >2 minutes average
- [ ] <40% bounce rate
- [ ] 95%+ RSS feed uptime
- [ ] Search traffic growth >20% monthly
- [ ] Social shares increasing

**Remember**: The goal is sustainable, high-quality content aggregation that serves users better than any single source could alone.
