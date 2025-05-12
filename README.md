# AI Flash Report

## Project Overview

AI Flash Report is an automated news aggregation website that provides a daily roundup of the latest news and developments in the field of Artificial Intelligence. It sources articles from various RSS feeds, NewsAPI, Reddit, and Perplexity AI, categorizes them, and presents them in a clean, easy-to-read format. The site also features a "Prompt of the Day" to inspire AI users.

The live site can be found at [aiflashreport.com](https://aiflashreport.com).

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
    *   Various RSS Feeds (OpenAI, Google AI, Meta AI, etc.)
*   **Deployment & Automation:** GitHub Actions
*   **Analytics:** Plausible Analytics
*   **Lead Generation/Engagement:** ConvertBox

## Directory Structure

```
promptwire/
├── .github/
│   └── workflows/
│       └── daily-update.yml  # GitHub Actions workflow for daily updates
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
    git clone https://github.com/bryancollins99/prompt-wire.git
    cd prompt-wire
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
    The `aggregator.py` script requires API keys for some of its data sources. These should be set as environment variables. Create a `.env` file in the `promptwire` directory (ensure this file is in your `.gitignore` and not committed) or set them directly in your shell:
    ```bash
    export NEWS_API_KEY="YOUR_NEWS_API_KEY"
    export PERPLEXITY_API_KEY="YOUR_PERPLEXITY_API_KEY"
    export REDDIT_CLIENT_ID="YOUR_REDDIT_CLIENT_ID"
    export REDDIT_CLIENT_SECRET="YOUR_REDDIT_CLIENT_SECRET"
    export REDDIT_USER_AGENT="YOUR_REDDIT_USER_AGENT" # e.g., "web:promptwire:v0.1 (by /u/yourusername)"
    ```
    *   If an API key is not set, the corresponding source will be skipped (a warning will be printed).

5.  **Run the aggregator script:**
    ```bash
    python3 aggregator.py
    ```
    This will:
    *   Fetch data from all configured sources.
    *   Process and categorize headlines.
    *   Generate/update `index.html`.
    *   Generate/update a daily archive file in the `archive/` directory.
    *   Update the `archive_index.html` page.

6.  **View the site:**
    Open `promptwire/index.html` in your web browser.

## Deployment Process

The site is automatically updated daily via a GitHub Actions workflow defined in `.github/workflows/daily-update.yml`.
This workflow:
1.  Checks out the `main` branch.
2.  Sets up Python and installs dependencies.
3.  Runs `aggregator.py` using API keys stored as GitHub Secrets.
4.  Runs `generate_sitemap.py`.
5.  Commits the generated `index.html`, archive files, and `sitemap.xml` back to the `main` branch.
6.  Pushes the changes to GitHub, which (if configured) updates the live site.

Refer to `promptwire/.cursor/rules/git-workflow.mdc` for details on the Git workflow for manual changes.

## Contributing

Please refer to the `git-workflow.mdc` for contribution guidelines. Key points include:
*   Work on feature branches.
*   Ensure API keys are not committed.
*   Restore generated files (`index.html`, `archive/`) before committing if they were changed locally during testing. The GitHub Action is responsible for their final generation.

## Further Documentation

*   **Git Workflow:** `promptwire/.cursor/rules/git-workflow.mdc`
*   **Project Brief:** `promptwire/.cursor/rules/project-brief.mdc`
*   **SEO Guidelines:** `promptwire/.cursor/rules/seo-guidelines.mdc`

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
        "airport",
        "airline",
        "travel disruption",
        "trump",
        "biden",
        "election",
        "politics",
        "gossip",
        "scandal",
        "glen tullman",
        "fyodorov"
    ]
}
```

### Configuration Options

- `excluded_sites`: List of domains to completely exclude from aggregation
- `low_quality_url_patterns`: URL patterns that indicate low-quality content
- `negative_keywords`: Keywords that will cause an article to be skipped

To add or remove sites from the exclusion list, simply edit the `excluded_sites` array in `config.json`. The changes will take effect the next time the aggregator runs. 