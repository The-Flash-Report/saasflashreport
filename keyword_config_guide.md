# Keyword Configuration Guide (`keyword_config.json`)

This document outlines the structure and usage of the `keyword_config.json` file, which is used to define and manage keyword-specific content pages for the AI Flash Report website.

## File Structure

The `keyword_config.json` file is a JSON object with two main top-level keys:

1.  `keyword_pages`: A dictionary where each key is a unique identifier for a keyword page (e.g., `"openai-news"`), and the value is an object containing the configuration for that specific page.
2.  `settings`: A dictionary containing global settings that apply to the keyword filtering and page generation process.

```json
{
  "keyword_pages": {
    "page-identifier-1": { ... page configuration ... },
    "page-identifier-2": { ... page configuration ... }
  },
  "settings": {
    ... global settings ...
  }
}
```

## `keyword_pages` Configuration

Each entry within the `keyword_pages` object defines a specific content page. The key (e.g., `"openai-news"`) is used internally as an identifier.

### Page Configuration Fields:

*   `title` (String, Required): The main title of the keyword page, displayed on the page itself (e.g., `"OpenAI News"`).
*   `description` (String, Required): A brief description of the content on this page, often used for display purposes (e.g., `"Latest news and updates about OpenAI, GPT models, and ChatGPT"`).
*   `filename` (String, Required): The HTML filename for the generated page (e.g., `"openai-news.html"`).
*   `keywords` (Array of Strings, Required): A list of primary keywords to filter articles. An article is considered a match if its title contains *any* of these keywords (OR logic). Case sensitivity is controlled by the global `case_sensitive` setting.
*   `required_keywords` (Array of Strings, Optional): A list of keywords that *must* be present in an article's title for it to be included on this page, in addition to matching primary `keywords`. If this list is defined and an article does not match at least one `required_keyword`, it's excluded, even if it matches a primary keyword.
*   `negative_keywords` (Array of Strings, Optional): A list of keywords that, if found in an article's title, will cause the article to be excluded from this page, even if it matches primary or required keywords.
*   `max_articles` (Integer, Optional, Default: 50): The maximum number of articles to display on this page. Articles are typically sorted by relevance before this limit is applied.
*   `page_type` (String, Required): Specifies the type of page.
    *   `"automated"`: Articles are automatically filtered and populated based on the `keywords`, `negative_keywords`, and `required_keywords`.
    *   `"curated"`: Articles are manually specified in a corresponding JSON file located in the `curated_content/` directory (e.g., `curated_content/page-key.json`). The `keywords` field is ignored for this type.
*   `meta_title` (String, Optional): The content for the `<title>` HTML tag. If omitted, the `title` field might be used as a fallback.
*   `meta_description` (String, Optional): The content for the `<meta name="description">` HTML tag. If omitted, the `description` field might be used.
*   `content_max_age_days` (Integer, Optional): For "automated" pages, specifies the maximum age (in days) of articles to include. If an article has a parsable published date and is older than this, it's excluded. This allows specific topic pages to retain content longer. If omitted, a default behavior applies (e.g., relying on global fetch cutoffs like the current 2-day limit for RSS).

### Example Page Configuration:

```json
{
  "keyword_pages": {
    "chatgpt-updates": {
      "title": "ChatGPT Updates",
      "description": "Latest news and updates about ChatGPT.",
      "filename": "chatgpt-updates.html",
      "keywords": ["chatgpt", "gpt-4", "openai update"],
      "negative_keywords": ["rumor", "speculation"],
      "page_type": "automated",
      "content_max_age_days": 14
    },
    "ai-news-today": {
      "title": "AI News Today",
      "description": "Latest AI news and updates",
      "filename": "ai-news-today.html",
      "keywords": ["AI", "artificial intelligence"],
      "negative_keywords": [],
      "max_articles": 50,
      "page_type": "curated"
    }
  },
  "settings": {
    "content_freshness_days": 7,
    "enable_keyword_scoring": true,
    "duplicate_handling": "show_on_all_matching",
    "case_sensitive": false
  }
}
```

## `settings` Configuration

The `settings` object contains global parameters that affect how all keyword pages are processed.

### Global Settings Fields:

*   `content_freshness_days` (Integer, Required, Default: 7): Articles older than this number of days (from their publication date, if available) might be excluded or ranked lower. (Note: Exact implementation of freshness depends on `aggregator.py` logic).
*   `enable_keyword_scoring` (Boolean, Required, Default: true): If `true`, a relevance score is calculated for articles based on keyword matches, source, etc. This score is used for ranking.
*   `duplicate_handling` (String, Optional, Default: `"show_on_all_matching"`): Defines how to handle articles that might match criteria for multiple keyword pages.
    *   `"show_on_all_matching"`: The article will appear on every keyword page it qualifies for.
    *   (Future options might include `"show_on_best_match_only"` or a priority system).
*   `case_sensitive` (Boolean, Required, Default: false): If `false`, all keyword matching (primary, required, negative) is case-insensitive. If `true`, matching is case-sensitive.

### Example Settings Configuration:

```json
  "settings": {
    "content_freshness_days": 7,
    "enable_keyword_scoring": true,
    "duplicate_handling": "show_on_all_matching",
    "case_sensitive": false
  }
```

## Usage in `aggregator.py`

The `aggregator.py` script loads this configuration file at startup using the `load_keyword_config()` function. This function also performs basic schema validation.

The script then iterates through each page defined in `keyword_pages`, filters the aggregated content based on the specified keywords and rules, and generates the corresponding HTML files.

## Maintaining the Configuration

-   When adding a new keyword page, ensure all required fields are present for its configuration.
-   Choose a unique, descriptive identifier (key) for each new page.
-   Carefully define `keywords`, `required_keywords`, and `negative_keywords` to ensure accurate content filtering.
-   Update `meta_title` and `meta_description` for good SEO.
-   Review global `settings` if changes to overall filtering behavior are needed. 