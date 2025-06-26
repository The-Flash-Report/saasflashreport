# SaaS Flash Report

## Project Overview

SaaS Flash Report is an automated news aggregation website that provides a daily roundup of the latest news and developments in the Software-as-a-Service industry. It sources articles from various RSS feeds, NewsAPI, Reddit, and Perplexity AI, categorizes them, and presents them in a clean, easy-to-read format focused on SaaS funding, enterprise software, product launches, and B2B technology trends.

The live site can be found at [saasflashreport.com](https://saasflashreport.com).

## Tech Stack

*   **Backend:** Python
    *   `requests`: For making HTTP requests to APIs and RSS feeds.
    *   `feedparser`: For parsing RSS/Atom feeds.
    *   `praw`: For interacting with the Reddit API.
    *   `jinja2`: For templating the HTML pages.
    *   `langdetect`: For detecting the language of articles and filtering out non-English content.
    *   Standard Python libraries: `os`, `datetime`, `json`, `re`.
*   **Frontend:** HTML, CSS (embedded in `template.html`)
*   **Data Sources:**
    *   NewsAPI
    *   Reddit API
    *   Perplexity AI API
    *   Various RSS Feeds (SaaS industry publications, software company blogs, etc.)
*   **Deployment & Automation:** GitHub Actions
*   **Analytics:** Plausible Analytics
*   **Lead Generation/Engagement:** ConvertBox

## Directory Structure

```
saasflashreport/
├── .github/
│   └── workflows/
│       └── daily-update.yml  # GitHub Actions workflow for daily SaaS updates
├── .cursor/
│   └── rules/
│       ├── git-workflow.mdc        # SOP for git usage
│       ├── project-brief.mdc       # Original project brief
│       └── seo-guidelines.mdc      # SEO best practices
├── archive/                    # Stores daily HTML archives
├── aggregator.py               # Main Python script for fetching, processing, and generating the site
├── template.html               # Jinja2 template for the HTML pages
├── requirements.txt            # Python dependencies
├── index.html                  # Main page of the website (generated)
├── archive_index_template.html # Jinja2 template for the archive index page
├── generate_sitemap.py         # Python script to generate sitemap.xml
├── sitemap.xml                 # Site map for SEO (generated)
├── about.html                  # Static about page
├── README.md                   # This file
└── test_perplexity.py          # Temporary script for testing Perplexity API
```

## Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/The-Flash-Report/saasflashreport.git
    cd saasflashreport
    ```

2.  **Set up a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    The `aggregator.py` script requires API keys for some of its data sources. These should be set as environment variables. Create a `.env` file in the `saasflashreport` directory (ensure this file is in your `.gitignore` and not committed) or set them directly in your shell:
    ```bash
    export NEWS_API_KEY="YOUR_NEWS_API_KEY"
    export PERPLEXITY_API_KEY="YOUR_PERPLEXITY_API_KEY"
    export REDDIT_CLIENT_ID="YOUR_REDDIT_CLIENT_ID"
    export REDDIT_CLIENT_SECRET="YOUR_REDDIT_CLIENT_SECRET"
    export REDDIT_USER_AGENT="YOUR_REDDIT_USER_AGENT" # e.g., "web:saasflashreport:v0.1 (by /u/yourusername)"
    ```
    *   If an API key is not set, the corresponding source will be skipped (a warning will be printed).

5.  **Run the aggregator script:**
    ```bash
    python3 aggregator.py
    ```
    This will:
    *   Fetch data from all configured SaaS industry sources.
    *   Process and categorize SaaS headlines.
    *   Generate/update `index.html`.
    *   Generate/update a daily archive file in the `archive/` directory.
    *   Update the `archive_index.html` page.

6.  **View the site:**
    Open `saasflashreport/index.html` in your web browser.

## Deployment Process

The site is automatically updated daily via a GitHub Actions workflow defined in `.github/workflows/daily-update.yml`.
This workflow:
1.  Checks out the `main` branch.
2.  Sets up Python and installs dependencies.
3.  Runs `aggregator.py` using API keys stored as GitHub Secrets.
    *   The script now includes **historical deduplication**. It maintains a `processed_urls.json` file (which should be in `.gitignore`) to track all URLs published in previous runs. This prevents the same article from reappearing on subsequent days.
4.  Runs `generate_sitemap.py`.
5.  Commits the generated `index.html`, archive files, `sitemap.xml`, and the updated `processed_urls.json` back to the `main` branch.
6.  Pushes the changes to GitHub, which (if configured) updates the live site.

Refer to `saasflashreport/.cursor/rules/git-workflow.mdc` for details on the Git workflow for manual changes.

## Contributing

Please refer to the `git-workflow.mdc` for contribution guidelines. Key points include:
*   Work on feature branches.
*   Ensure API keys are not committed.
*   Restore generated files (`index.html`, `archive/`, `sitemap.xml`, `processed_urls.json`) before committing if they were changed locally during testing. The GitHub Action is responsible for their final generation.

## Further Documentation

*   **Git Workflow:** `saasflashreport/.cursor/rules/git-workflow.mdc`
*   **Project Brief:** `saasflashreport/.cursor/rules/project-brief.mdc`
*   **SEO Guidelines:** `saasflashreport/.cursor/rules/seo-guidelines.mdc`

## Configuration

The aggregator can be configured through `config.json`. This file contains settings for site exclusions and content filtering:

```json
{
    "excluded_sites": [
        "pypi.org",
        "prtimes.jp",
        "thestar.com",
        "biztoc.com"
    ],
    "low_quality_url_patterns": [
        "/tag/",
        "/category/",
        "/author/",
        "/page/",
        "/feed/",
        "/rss/",
        "/amp/",
        "/mobile/",
        "/m/"
    ],
    "negative_keywords": [
        "ufo",
        "alien",
        "paranormal",
        "trump",
        "biden",
        "election",
        "politics",
        "gossip",
        "scandal",
        "crypto",
        "bitcoin",
        "blockchain",
        "casino",
        "gambling"
    ]
}
```

### Configuration Options

- `excluded_sites`: List of domains to completely exclude from aggregation
- `low_quality_url_patterns`: URL patterns that indicate low-quality content
- `negative_keywords`: Keywords that will cause an article to be skipped

To add or remove sites from the exclusion list, simply edit the `excluded_sites` array in `config.json`. The changes will take effect the next time the aggregator runs.

## SaaS Industry Focus

SaaS Flash Report specifically targets content related to:

- **SaaS Funding**: Venture capital rounds, Series A/B/C funding, IPOs, and SaaS company valuations
- **Enterprise Software**: B2B software launches, enterprise technology acquisitions, and corporate software trends
- **Product Launches**: New SaaS products, feature releases, platform integrations, and software innovations
- **SaaS Analytics**: Business intelligence tools, customer success insights, SaaS metrics research, and industry analysis
- **B2B Technology**: Business software developments, productivity tools, and enterprise technology trends
- **Software Industry**: SaaS company acquisitions, mergers, partnerships, and strategic initiatives

## Note on Deduplication Logic

The current deduplication logic prevents the same article URL from being published more than once across all days. However, if a story remains present in the news feeds for multiple days, it may appear on two consecutive days (e.g., on both May 24 and May 25) before being filtered out on subsequent days. This is because the deduplication is based on URLs already published in previous runs, and the update to the deduplication list happens after each day's publication.

If you want stricter deduplication (so a story never appears on two consecutive days), you would need to compare today's candidate URLs against both the historical set and the previous day's published URLs before publishing. This is not implemented by default, as it is common for news aggregators to allow stories to remain visible for more than one day if they are still current in the feeds. 