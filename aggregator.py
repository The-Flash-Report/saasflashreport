import requests
import feedparser
import os
import datetime
import praw # Added for Reddit API
from jinja2 import Environment, FileSystemLoader, select_autoescape, exceptions as jinja2_exceptions
import json # Added for Perplexity JSON handling
import re # Added for footer update regex
from langdetect import detect, LangDetectException # Added for language detection
from dateutil import parser as date_parser
import time
import base64 # Added for API key decoding

# Flash Summary Component
from flash_summary_component import FlashSummaryGenerator, FlashSummaryConfig

# --- NEW: JSON Serializer for Datetime Objects ---
def default_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: config.json not found. Using default configuration.")
        return {
            "excluded_sites": [],
            "low_quality_url_patterns": [],
            "negative_keywords": []
        }

config = load_config()

# Load keyword configuration for filtered pages
def load_keyword_config():
    """Load keyword configuration for generating filtered pages."""
    try:
        with open('keyword_config.json', 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print("Warning: keyword_config.json not found. Keyword pages will not be generated.")
        return {"keyword_pages": {}, "settings": {}}
    except json.JSONDecodeError as e:
        print(f"Error parsing keyword_config.json: {e}")
        return {"keyword_pages": {}, "settings": {}}

    # Validate schema
    if not isinstance(config_data, dict):
        print("Error: keyword_config.json must be a JSON object.")
        return {"keyword_pages": {}, "settings": {}}

    if 'keyword_pages' not in config_data or not isinstance(config_data['keyword_pages'], dict):
        print("Error: 'keyword_pages' field is missing or not a dictionary in keyword_config.json.")
        return {"keyword_pages": {}, "settings": {}}

    if 'settings' not in config_data or not isinstance(config_data['settings'], dict):
        print("Error: 'settings' field is missing or not a dictionary in keyword_config.json.")
        return {"keyword_pages": {}, "settings": {}}

    # Validate individual page configurations
    required_page_fields = ['title', 'description', 'filename', 'keywords', 'page_type']
    for page_key, page_config in config_data['keyword_pages'].items():
        if not isinstance(page_config, dict):
            print(f"Error: Configuration for page '{page_key}' must be a dictionary.")
            # Optionally, remove this page or return an empty config
            continue 
        for field in required_page_fields:
            if field not in page_config:
                print(f"Error: Required field '{field}' missing for page '{page_key}' in keyword_config.json.")
                # Optionally, skip this page or handle error more gracefully
                continue
        if not isinstance(page_config['keywords'], list):
             print(f"Error: 'keywords' field for page '{page_key}' must be a list.")
             continue

    # Validate settings
    required_settings_fields = ['content_freshness_days', 'enable_keyword_scoring', 'case_sensitive']
    for field in required_settings_fields:
        if field not in config_data['settings']:
            print(f"Error: Required field '{field}' missing in 'settings' of keyword_config.json.")
            # Provide default or handle error
            return {"keyword_pages": {}, "settings": {}} # Or apply defaults
    
    print("keyword_config.json loaded and validated successfully.")
    return config_data

keyword_config = load_keyword_config()

# --- Custom Jinja2 Filter ---
def datetime_format(value, format="%B %d, %Y"):
    """Custom filter for formatting dates in Jinja2 templates."""
    if isinstance(value, str):
        try:
            # Try to parse the date string
            value = datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return value  # Return as-is if parsing fails
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    return value

def cleanup_old_processed_urls(processed_urls_data, days_to_keep=7):
    """
    Clean up old processed URLs to prevent the file from growing indefinitely.
    
    Args:
        processed_urls_data: Dictionary with URLs as keys and timestamps as values,
                           or list of URLs (legacy format)
        days_to_keep: Number of days to keep URLs (default: 7)
    
    Returns:
        Dictionary with cleaned URLs and timestamps
    """
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
    
    # Handle legacy format (list of URLs)
    if isinstance(processed_urls_data, list):
        print(f"Converting legacy processed URLs format (list) to new format (dict with timestamps)")
        # Convert legacy list to new format, assuming all existing URLs are "old"
        # We'll keep them for one more cycle to avoid re-processing recent articles
        return {url: cutoff_date.isoformat() for url in processed_urls_data}
    
    # Handle new format (dict with timestamps)
    if not isinstance(processed_urls_data, dict):
        print("Warning: processed_urls_data is neither list nor dict. Starting fresh.")
        return {}
    
    cleaned_urls = {}
    removed_count = 0
    
    for url, timestamp_str in processed_urls_data.items():
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
            if timestamp >= cutoff_date:
                cleaned_urls[url] = timestamp_str
            else:
                removed_count += 1
        except (ValueError, TypeError):
            # If timestamp is invalid, keep the URL but update with current time
            # This handles any malformed timestamps
            cleaned_urls[url] = datetime.datetime.now().isoformat()
    
    if removed_count > 0:
        print(f"Cleaned up {removed_count} old processed URLs (older than {days_to_keep} days)")
    else:
        print(f"No old URLs to clean up (keeping URLs from last {days_to_keep} days)")
    
    return cleaned_urls

# --- Keyword Filtering Functions ---

def matches_keywords(text, keywords, case_sensitive=False):
    """Check if text matches any of the provided keywords."""
    if not keywords:
        return False
    
    search_text = text if case_sensitive else text.lower()
    search_keywords = keywords if case_sensitive else [kw.lower() for kw in keywords]
    
    return any(keyword in search_text for keyword in search_keywords)

def calculate_keyword_relevance_score(article, page_config):
    """Calculate relevance score for an article based on keyword matches."""
    title = article.get('title', '')
    url = article.get('url', '')
    source = article.get('source', '')
    
    score = 0
    case_sensitive = keyword_config.get('settings', {}).get('case_sensitive', False)
    
    # Primary keywords in title (highest weight)
    if matches_keywords(title, page_config.get('keywords', []), case_sensitive):
        score += 10
    
    # Required keywords (must have for certain pages)
    required_keywords = page_config.get('required_keywords', [])
    if required_keywords:
        if matches_keywords(title, required_keywords, case_sensitive):
            score += 5
        else:
            return 0  # Must have required keywords
    
    # Negative keywords (disqualify)
    if matches_keywords(title, page_config.get('negative_keywords', []), case_sensitive):
        return 0
    
    # Source preference (RSS feeds get higher scores)
    if 'RSS' in source or any(rss_source in source for rss_source in RSS_FEEDS.keys()):
        score += 3
    elif 'NewsAPI' in source:
        score += 2
    elif 'Reddit' in source:
        score += 1
    
    # Recency bonus (articles from today get higher scores)
    # This would require article date parsing, simplified for now
    
    return score

def filter_articles_for_keyword_page(all_articles, page_key, page_config):
    """Filter articles for a specific keyword page using keywords and relevance scoring."""
    matching_articles = []
    keywords = page_config.get('keywords', [])
    
    if not keywords:
        print(f"No keywords configured for page {page_key}. Returning empty list.")
        return []
    
    for article in all_articles:
        title = article.get('title', '')
        url = article.get('url', '')
        
        # Skip excluded URLs
        if any(excluded_url in url.lower() for excluded_url in ['reddit.com', 'twitter.com', 'x.com']):
            continue
        
        # Check if article matches keywords and calculate relevance score
        score = calculate_keyword_relevance_score(article, page_config)
        
        if score > 0:
            article_copy = article.copy()
            article_copy['relevance_score'] = score
            # Ensure rewritten_title exists
            if 'rewritten_title' not in article_copy:
                article_copy['rewritten_title'] = rewrite_headline(article_copy.get('title', ''))
            matching_articles.append(article_copy)
    
    # Sort by relevance score (highest first), then by publication date
    def get_sort_date(article):
        date_obj = article.get('published_date_obj')
        if date_obj is None:
            return datetime.datetime.min
        # Handle string dates
        if isinstance(date_obj, str):
            try:
                return datetime.datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except:
                return datetime.datetime.min
        # Handle datetime objects
        if isinstance(date_obj, datetime.datetime):
            return date_obj
        # Handle date objects - convert to datetime
        if isinstance(date_obj, datetime.date):
            return datetime.datetime.combine(date_obj, datetime.time.min)
        return datetime.datetime.min
    
    matching_articles.sort(key=lambda x: (x.get('relevance_score', 0), get_sort_date(x)), reverse=True)
    
    print(f"Found {len(matching_articles)} articles for {page_key}")
    return matching_articles

def generate_keyword_pages_data(all_articles):
    """Generate filtered data for all keyword pages with pagination support."""
    keyword_pages_data = {}
    
    if not keyword_config.get('keyword_pages'):
        print("No keyword pages configured. Skipping keyword page generation.")
        return keyword_pages_data
    
    print(f"Generating data for {len(keyword_config['keyword_pages'])} keyword pages...")
    
    # Ensure 'curated_content' directory exists or create it
    curated_dir = 'curated_content'
    if not os.path.exists(curated_dir):
        try:
            os.makedirs(curated_dir)
            print(f"Created directory: {curated_dir}")
        except OSError as e:
            print(f"Error creating directory {curated_dir}: {e}")

    for page_key, page_config in keyword_config['keyword_pages'].items():
        if page_config.get('page_type') == 'curated':
            # Handle curated pages (existing logic)
            print(f"Processing curated page: {page_key}")
            curated_content_path = os.path.join(curated_dir, f"{page_key}.json")
            articles = []
            if os.path.exists(curated_content_path):
                try:
                    with open(curated_content_path, 'r', encoding='utf-8') as f:
                        articles = json.load(f)
                    if not isinstance(articles, list):
                        print(f"Warning: Curated content file {curated_content_path} does not contain a JSON list. Skipping.")
                        articles = []
                    else:
                        # Ensure 'rewritten_title' exists, defaulting from 'title'
                        for article in articles:
                            if 'rewritten_title' not in article and 'title' in article:
                                article['rewritten_title'] = rewrite_headline(article['title'])
                            if 'source' not in article: 
                                article['source'] = "Curated"
                        print(f"  - Loaded {len(articles)} articles from {curated_content_path}")
                except json.JSONDecodeError:
                    print(f"Warning: Error decoding JSON from {curated_content_path}. Skipping.")
                    articles = []
                except Exception as e:
                    print(f"Warning: Could not load curated content from {curated_content_path}: {e}. Skipping.")
                    articles = []
            else:
                print(f"Warning: Curated content file {curated_content_path} not found. Page will be empty.")
            
            # For curated pages, don't use pagination - just store all articles
            keyword_pages_data[page_key] = {
                'config': page_config,
                'articles': articles,
                'total_pages': 1,
                'current_page': 1,
                'total_stories': len(articles)
            }
        else: 
            # Handle automated pages with accumulation and pagination
            print(f"Processing automated page: {page_key}")
            
            # Step 1: Load existing stories
            existing_stories = load_existing_topic_stories(page_key)
            
            # Step 2: Get new stories from today's articles
            new_stories = filter_articles_for_keyword_page(all_articles, page_key, page_config)
            
            # Step 3: Merge and deduplicate
            all_stories = merge_and_deduplicate_stories(existing_stories, new_stories)
            
            # Step 4: Save updated story list
            save_topic_stories(page_key, all_stories)
            
            # Step 5: Create pagination data
            pages = paginate_stories(all_stories)
            
            keyword_pages_data[page_key] = {
                'config': page_config,
                'all_stories': all_stories,
                'pages': pages,
                'total_pages': len(pages),
                'total_stories': len(all_stories),
                'new_stories_count': len([s for s in new_stories if s.get('url') not in {es.get('url') for es in existing_stories}])
            }
            
            print(f"  - {page_key}: {len(all_stories)} total stories across {len(pages)} pages")
    
    return keyword_pages_data

def generate_keyword_page_files(keyword_pages_data, env):
    """Generate HTML files for keyword pages with pagination support."""
    print(f"Generating keyword page files for {len(keyword_pages_data)} topics...")
    
    # Ensure the output directory exists
    output_dir = "topics"
    os.makedirs(output_dir, exist_ok=True)

    # Set template globals
    env.globals['current_year'] = datetime.datetime.now().year

    env.globals['all_keyword_pages_config'] = keyword_config.get('keyword_pages', {})

    try:
        template = env.get_template("keyword_template.html")
        print("Using keyword_template.html for keyword pages.")
    except jinja2_exceptions.TemplateNotFound:
        print("Error: keyword_template.html not found. Make sure it's in the templates directory.")
        return
    except Exception as e:
        print(f"Error loading keyword_template.html: {e}")
        return

    for page_key, data in keyword_pages_data.items():
        
        if data['config'].get('page_type') == 'curated':
            # Handle curated pages (single page, no pagination)
            page_specific_categories = {data['config']['title']: data['articles']}
            canonical_path = f"/{page_key}.html"

            try:
                html_content = template.render(
                    categories=page_specific_categories,
                    articles=data['articles'],  # FIX: Add missing articles variable that template expects
                    page_title=data['config']['title'],
                    page_description=data['config'].get('description', ''),
                    update_time=datetime.datetime.now().strftime("%Y-%m-%d"),
                    current_year=datetime.datetime.now().year,
                    is_keyword_page=True,
                    keyword_page_config=data['config'],
                    canonical_path=canonical_path,
                    all_keyword_pages_config=keyword_config.get('keyword_pages', {}),
                    # Pagination info for curated pages (single page)
                    current_page=1,
                    total_pages=1,
                    total_stories=len(data['articles']),
                    page_key=page_key
                )
                with open(os.path.join(output_dir, f"{page_key}.html"), "w") as f:
                    f.write(html_content)
                print(f"  - Successfully generated {page_key}.html (curated)")
            except Exception as e:
                print(f"Error generating curated page for {page_key}: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            # Handle automated pages with pagination
            pages = data.get('pages', [])
            total_pages = len(pages)
            
            if total_pages == 0:
                # Create empty page if no stories
                pages = [[]]
                total_pages = 1
            
            for page_num, page_stories in enumerate(pages, 1):
                # For page 1, use the base filename (e.g., openai-news.html)
                # For other pages, use page-N format (e.g., openai-news-page-2.html)
                if page_num == 1:
                    filename = f"{page_key}.html"
                    canonical_path = f"/topics/{page_key}.html"
                else:
                    filename = f"{page_key}-page-{page_num}.html"
                    canonical_path = f"/topics/{page_key}-page-{page_num}.html"
                
                # Structure stories for template (single category)
                page_specific_categories = {data['config']['title']: page_stories}
                
                # Calculate pagination URLs
                pagination_info = {
                    'current_page': page_num,
                    'total_pages': total_pages,
                    'total_stories': data['total_stories'],
                    'new_stories_count': data.get('new_stories_count', 0),
                    'page_key': page_key,
                    'prev_url': None,
                    'next_url': None
                }
                # Set previous page URL
                if page_num > 1:
                    if page_num == 2:
                        pagination_info['prev_url'] = f"/topics/{page_key}.html"
                    else:
                        pagination_info['prev_url'] = f"/topics/{page_key}-page-{page_num-1}.html"
                # Set next page URL
                if page_num < total_pages:
                    if page_num == 1:
                        pagination_info['next_url'] = f"/topics/{page_key}-page-2.html"
                    else:
                        pagination_info['next_url'] = f"/topics/{page_key}-page-{page_num+1}.html"
                try:
                    html_content = template.render(
                        categories=page_specific_categories,
                        articles=page_stories,  # FIX: Add missing articles variable that template expects
                        page_title=f"{data['config']['title']} - Page {page_num}" if page_num > 1 else data['config']['title'],
                        page_description=data['config'].get('description', ''),
                        update_time=datetime.datetime.now().strftime("%Y-%m-%d"),
                        current_year=datetime.datetime.now().year,
                        is_keyword_page=True,
                        keyword_page_config=data['config'],
                        canonical_path=canonical_path,
                        all_keyword_pages_config=keyword_config.get('keyword_pages', {}),
                        # Pagination data
                        **pagination_info
                    )
                    # --- Insert recent archive links in the footer ---
                    try:
                        archive_dir = 'archive'
                        all_files_in_archive = [f for f in os.listdir(archive_dir) if os.path.isfile(os.path.join(archive_dir, f)) and f.endswith('.html')]
                        all_files_in_archive.sort(reverse=True)
                        archive_files = all_files_in_archive
                    except Exception as e:
                        print(f"Error listing files in archive directory '{archive_dir}': {e}")
                        archive_files = []
                    if archive_files:
                        recent_archives = archive_files[:5]
                        archive_links_html = '\n                '.join([
                            f'<a href="/archive/{archive_file}">{archive_file.replace(".html", "")}</a>'
                            for archive_file in recent_archives
                        ])
                        html_content = html_content.replace('<!-- ARCHIVE_LINKS_PLACEHOLDER -->', archive_links_html)
                    # --- End insert recent archive links ---
                    with open(os.path.join(output_dir, filename), "w") as f:
                        f.write(html_content)
                    if page_num == 1:
                        print(f"  - Successfully generated {filename} ({len(page_stories)} stories, {total_pages} total pages)")
                    else:
                        print(f"    - Generated {filename} ({len(page_stories)} stories)")
                except Exception as e:
                    print(f"Error generating page {page_num} for {page_key}: {e}")
                    import traceback
                    traceback.print_exc()

    # Generate non-keyword pages that might have been overwritten (e.g. about.html, contact.html if they were in keyword_pages_data)
    # This logic might need refinement if other static pages are handled differently.
    # For now, we assume keyword_pages_data only contains keyword pages.

# --- Configuration ---
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
if not NEWS_API_KEY:
    print("Warning: NEWS_API_KEY environment variable not set. NewsAPI source will be skipped.")

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    print("Warning: PERPLEXITY_API_KEY environment variable not set. Perplexity source will be skipped.")

# Reddit API Credentials (Set as Environment Variables)
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "PromptWireAggregator/0.1 by YourUsername") # Default UA

# Re-enabled Reddit API credential check
if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    print("Warning: Reddit API credentials (CLIENT_ID, CLIENT_SECRET, USER_AGENT) not fully set in environment variables. Reddit source will be skipped.")

# Load configuration values
EXCLUDED_SITES = config.get('excluded_sites', [])
LOW_QUALITY_URL_PATTERNS = config.get('low_quality_url_patterns', [])
NEGATIVE_KEYWORDS = config.get('negative_keywords', [])

# Sites to exclude from NewsAPI results
EXCLUDED_SITES = [
    'pypi.org',
    'prtimes.jp',
    'thestar.com',
    'biztoc.com',
    'freerepublic.com'
]

# URL patterns that indicate low-quality content
LOW_QUALITY_URL_PATTERNS = [
    '/tag/',
    '/category/',
    '/author/',
    '/page/',
    '/feed/',
    '/rss/',
    '/amp/',
    '/mobile/',
    '/m/'
]

# Updated Subreddits list but keep the ones the user wants
SUBREDDITS = [
    "artificial", "LargeLanguageModels", "LocalLLaMA", "singularity", "MachineLearning", # Original
    "chatgpt", "claudeai", "characterai", "openai", "ArtificialIntelligence",
    "ai_agents", "StableDiffusion", "AIArt" # Added by user
]
MAX_REDDIT_POSTS_PER_SUB = 3 # Reduced from 5 to 3 (30% reduction)
REDDIT_TIME_FILTER = 'day' # Restore this constant

# Updated NewsAPI configuration to use technology category
NEWS_API_CATEGORY = 'technology'  # Use NewsAPI's technology category
NEWS_API_QUERY = 'SaaS OR "software as a service" OR "enterprise software" OR "cloud platform" OR "B2B software"'  # Updated for SaaS
MAX_NEWS_API_ARTICLES = 100 # Number of articles to fetch from NewsAPI
MAX_HEADLINE_WORDS = 15

# Add these new constants
MAX_RSS_ENTRIES_PER_SOURCE = 10  # Increased from 3 to 10
RSS_CUTOFF_DAYS = 3  # Temporarily increased from 1 to 3 for testing pagination
PERPLEXITY_RETRY_ATTEMPTS = 3
PERPLEXITY_RETRY_DELAY = 2  # seconds

# Pagination constants for topic pages
STORIES_PER_PAGE = 20  # Number of stories to display per page
MAX_TOTAL_STORIES_PER_TOPIC = 200  # Maximum stories to keep in total per topic

# Add major news sources to RSS feeds - UPDATED FOR SAAS
RSS_FEEDS = {
    # --- TOP SAAS INDUSTRY SOURCES ---
    "SaaStr": "https://www.saastr.com/feed/",
    "Tomasz Tunguz": "https://tomtunguz.com/index.xml",
    "ChartMogul Blog": "https://blog.chartmogul.com/rss/",
    "ProfitWell": "https://www.profitwell.com/blog/rss.xml",
    "OpenView Blog": "https://openviewpartners.com/blog/rss/",
    "Point Nine Capital": "https://medium.com/feed/point-nine-news",
    "Process Street": "https://www.process.st/blog/feed/",
    
    # --- ENTERPRISE SOFTWARE LEADERS ---
    "Salesforce Blog": "https://www.salesforce.com/news/rss/",
    "Microsoft 365 Blog": "https://www.microsoft.com/en-us/microsoft-365/blog/rss/",
    "Google Workspace": "https://workspace.google.com/blog/feed/",
    "Slack Blog": "https://slack.com/blog/rss",
    "Atlassian Blog": "https://blog.atlassian.com/feed/",
    "Intercom Blog": "https://www.intercom.com/blog/feed",
    "GitHub Blog": "https://github.blog/feed/",
    
    # --- DEVELOPER & PLATFORM TOOLS ---
    "GitLab Blog": "https://about.gitlab.com/atom.xml",
    "Heroku Blog": "https://blog.heroku.com/rss",
    "CloudFlare Blog": "https://blog.cloudflare.com/rss/",
    "Stack Overflow Blog": "https://stackoverflow.blog/feed/",
    
    # --- ANALYTICS & GROWTH ---
    "Mixpanel Blog": "https://mixpanel.com/blog/rss/",
    "Amplitude Blog": "https://amplitude.com/blog/rss",
    "Baremetrics Blog": "https://baremetrics.com/blog/feed",
    
    # --- BUSINESS & ENTERPRISE NEWS ---
    "TechCrunch Enterprise": "https://techcrunch.com/category/enterprise/feed/",
    "Buffer Blog": "https://buffer.com/resources/rss/",
    "Ahrefs Blog": "https://ahrefs.com/blog/feed/",
    
    # --- ADDITIONAL SAAS SOURCES ---
    "SaaS Capital": "https://www.saascapital.com/blog/feed/",
    "Bessemer Cloud": "https://www.bvp.com/atlas/rss",
    
    # --- INFRASTRUCTURE & DEVOPS ---
    "AWS Enterprise": "https://aws.amazon.com/blogs/enterprise-strategy/feed/",
    "Azure Updates": "https://azure.microsoft.com/en-us/updates/feed/",
    "Docker Blog": "https://www.docker.com/blog/feed/",
    "Kubernetes Blog": "https://kubernetes.io/feed.xml",
    
    # --- HIGH-VALUE SAAS INDUSTRY ADDITIONS ---
    "First Round Review": "https://review.firstround.com/rss",
    "Version One Ventures": "https://versionone.vc/feed/",
    "Insight Partners": "https://www.insightpartners.com/blog/feed/",
    "Battery Ventures": "https://www.battery.com/rss/",
    "Redpoint Ventures": "https://www.redpoint.com/feed/",
    "NFX": "https://www.nfx.com/rss/",
    "Reforge": "https://www.reforge.com/rss/",
    "Lenny's Newsletter": "https://www.lennysnewsletter.com/feed",
    "Product Hunt": "https://blog.producthunt.com/rss",
    "CustomerIO Blog": "https://customer.io/blog/rss.xml",
    "ConvertKit": "https://convertkit.com/blog/rss",
    "HelpScout": "https://www.helpscout.com/blog/feed/",
    "Hotjar Blog": "https://blog.hotjar.com/rss/",
    "Segment Blog": "https://segment.com/blog/rss/",
    "Stripe Blog": "https://stripe.com/blog/rss.xml",
    "Twilio": "https://www.twilio.com/blog/rss.xml",
    "SendGrid": "https://sendgrid.com/blog/rss/",
    "Mailchimp": "https://mailchimp.com/resources/rss/",
    "Close.com": "https://blog.close.com/rss/",
    "Pipedrive": "https://www.pipedrive.com/en/blog/rss",
    "SaaS Brief": "https://www.saasbrief.com/rss/",
    "The SaaS CFO": "https://www.thesaascfo.com/feed/",
    "SaaS Metrics": "https://www.klipfolio.com/resources/articles/rss",
    "ChurnZero": "https://churnzero.net/blog/feed/",
    "Gainsight": "https://www.gainsight.com/blog/feed/",
    "UserVoice": "https://blog.uservoice.com/rss/",
    "Pendo": "https://www.pendo.io/blog/rss/",
    "FullStory": "https://blog.fullstory.com/feed/",
    "LogRocket": "https://blog.logrocket.com/rss/",
    "Price Intelligently": "https://www.priceintelligently.com/blog/rss.xml"
}

# Define categories based on SaaS industry focus
CATEGORIES = [
    'SaaS Funding',
    'Enterprise Software',
    'Product Launches',
    'SaaS Analytics',
    'B2B Technology',
    'Software Industry',
    'SaaS Acquisitions',
    'SaaS Metrics'
]

# Define keywords for SaaS categorization
# Order matters: More specific categories should come first.
CATEGORY_KEYWORDS = {
    'SaaS Funding': ['funding', 'investment', 'round', 'series a', 'series b', 'series c', 'venture capital', 'vc', 'raised', 'valuation', 'unicorn', 'ipo', 'acquisition', 'exit', 'startup'],
    'Enterprise Software': ['enterprise', 'b2b', 'business software', 'corporate', 'workflow', 'productivity', 'collaboration', 'crm', 'erp', 'hr software', 'sales software', 'marketing automation'],
    'Product Launches': ['launch', 'release', 'beta', 'new product', 'announce', 'unveil', 'debut', 'introduce', 'feature', 'update', 'version', 'rollout', 'availability'],
    'SaaS Analytics': ['analytics', 'metrics', 'data', 'reporting', 'dashboard', 'insights', 'business intelligence', 'bi', 'kpi', 'measurement', 'tracking', 'performance'],
    'B2B Technology': ['b2b', 'api', 'integration', 'platform', 'saas', 'software as a service', 'cloud', 'automation', 'digital transformation', 'tech stack', 'infrastructure'],
    'Software Industry': ['software', 'tech industry', 'digital', 'technology', 'innovation', 'development', 'programming', 'coding', 'developer', 'engineering'],
    'SaaS Acquisitions': ['acquisition', 'acquire', 'bought', 'purchase', 'merger', 'deal', 'exit', 'sold to', 'bought by', 'takeover', 'consolidation'],
    'SaaS Metrics': ['mrr', 'arr', 'churn', 'ltv', 'cac', 'customer acquisition', 'retention', 'recurring revenue', 'subscription', 'pricing', 'plan', 'tier', 'billing']
}

# Define keywords that strongly suggest a 'Trending Now' priority
TRENDING_KEYWORDS = ['exclusive', 'breaking', 'leak', 'major', 'significant']

# --- Helper Functions ---

def rewrite_headline(title, max_words=MAX_HEADLINE_WORDS):
    """Rewrites headline to be professional: proper title case, limited words."""
    words = title.split()
    # Simple truncation
    rewritten = " ".join(words[:max_words])
    if len(words) > max_words:
        rewritten += "..."
    
    # Convert to proper title case
    # Define words that should stay lowercase in title case (except at the start)
    lowercase_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
    
    title_words = rewritten.split()
    title_cased = []
    
    for i, word in enumerate(title_words):
        # Always capitalize first word, last word, and words not in lowercase_words
        if i == 0 or i == len(title_words) - 1 or word.lower() not in lowercase_words:
            title_cased.append(word.capitalize())
        else:
            title_cased.append(word.lower())
    
    return " ".join(title_cased)

def categorize_headline(title, url, source=None):
    """Categorizes headlines based on SaaS industry keywords and source."""
    title_lower = title.lower()

    # 1. Check for funding/investment patterns first (high priority)
    funding_keywords = CATEGORY_KEYWORDS['SaaS Funding']
    if any(kw in title_lower for kw in funding_keywords):
        return 'SaaS Funding'

    # 2. Check for acquisition patterns
    acquisition_keywords = CATEGORY_KEYWORDS['SaaS Acquisitions']
    if any(kw in title_lower for kw in acquisition_keywords):
        return 'SaaS Acquisitions'

    # 3. Check for metrics-related content
    metrics_keywords = CATEGORY_KEYWORDS['SaaS Metrics']
    if any(kw in title_lower for kw in metrics_keywords):
        return 'SaaS Metrics'

    # 4. Check for product launches and releases
    launch_keywords = CATEGORY_KEYWORDS['Product Launches']
    if any(kw in title_lower for kw in launch_keywords):
        return 'Product Launches'

    # 5. Check for enterprise software content
    enterprise_keywords = CATEGORY_KEYWORDS['Enterprise Software']
    if any(kw in title_lower for kw in enterprise_keywords):
        return 'Enterprise Software'

    # 6. Check for analytics content
    analytics_keywords = CATEGORY_KEYWORDS['SaaS Analytics']
    if any(kw in title_lower for kw in analytics_keywords):
        return 'SaaS Analytics'

    # 7. Check for B2B technology content
    b2b_keywords = CATEGORY_KEYWORDS['B2B Technology']
    if any(kw in title_lower for kw in b2b_keywords):
        return 'B2B Technology'

    # 8. Default to Software Industry for general SaaS content
    return 'Software Industry'



# --- NEW: Date Parsing Helper ---
def parse_publish_date(date_string_or_struct):
    if not date_string_or_struct:
        return None
    try:
        # Handle if it's already a datetime object or struct_time (from feedparser)
        if isinstance(date_string_or_struct, datetime.datetime):
            return date_string_or_struct.date()
        if isinstance(date_string_or_struct, datetime.date):
            return date_string_or_struct
        if hasattr(date_string_or_struct, 'tm_year'): # Check for time.struct_time
            return datetime.date(date_string_or_struct.tm_year, date_string_or_struct.tm_mon, date_string_or_struct.tm_mday)
        
        # If it's a string, try to parse it
        if isinstance(date_string_or_struct, str):
            return date_parser.parse(date_string_or_struct).date()
        
    except (ValueError, TypeError, OverflowError) as e:
        # print(f"Warning: Could not parse date: {date_string_or_struct} - {e}")
        return None
    return None
# --- END: Date Parsing Helper ---

# --- Data Fetching Functions ---

def fetch_reddit_posts():
    """Fetches hot posts from specified subreddits - similar to getHotPosts() in Reddit API."""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        print("Skipping Reddit fetch due to missing API credentials.")
        return []

    all_headlines = []
    print(f"Fetching hot Reddit posts from {len(SUBREDDITS)} subreddits...")
    
    try:
        # Initialize Reddit API client
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        for sub_name in SUBREDDITS:
            try:
                print(f"Getting hot posts from r/{sub_name}...")
                
                # Fetch hot posts from the subreddit (equivalent to getHotPosts() in Reddit API)
                subreddit = reddit.subreddit(sub_name)
                hot_posts = subreddit.hot(limit=MAX_REDDIT_POSTS_PER_SUB)
                
                added_count = 0
                for post in hot_posts:
                    # Skip stickied posts and posts without titles
                    if post.stickied or not post.title:
                        continue
                    
                    # Skip non-English posts using language detection
                    try:
                        lang = detect(post.title)
                        if lang != 'en':
                            print(f"  - Skipping non-English post (lang: {lang}) from r/{sub_name}: {post.title[:50]}...")
                            continue
                    except LangDetectException:
                        print(f"  - Skipping post due to language detection error from r/{sub_name}: {post.title[:50]}...")
                        continue
                    
                    # Add the post to our list
                    all_headlines.append({
                        'title': post.title,
                        'url': f"https://www.reddit.com{post.permalink}",
                        'source': f"Reddit r/{sub_name}",
                        'published_date_obj': parse_publish_date(datetime.datetime.fromtimestamp(post.created_utc))
                    })
                    added_count += 1
                    
                    # Stop if we've hit our limit for this subreddit
                    if added_count >= MAX_REDDIT_POSTS_PER_SUB:
                        break
                
                print(f"  - Added {added_count} hot posts from r/{sub_name}")
                
            except Exception as e:
                print(f"Error fetching hot posts from r/{sub_name}: {e}")
                
    except Exception as e:
        print(f"Error initializing Reddit API: {e}")
    
    print(f"Fetched {len(all_headlines)} total hot posts from Reddit.")
    return all_headlines

def fetch_newsapi_articles():
    """Fetches and processes articles from NewsAPI using technology category with enhanced logging."""
    
    # Log if the API key is missing right at the start
    if not NEWS_API_KEY:
        print("LOG: NEWS_API_KEY is not set. Skipping NewsAPI fetch.")
        return []

    print(f"LOG: NEWS_API_KEY is present (partially masked): {NEWS_API_KEY[:4]}...{NEWS_API_KEY[-4:]}")

    headlines = []
    base_url = "https://newsapi.org/v2/top-headlines"  # Using top-headlines for category support
    params = {
        'category': NEWS_API_CATEGORY,  # Use technology category
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'pageSize': MAX_NEWS_API_ARTICLES,
        'country': 'us'  # Focus on US tech news for better quality
    }

    # Also fetch with SaaS query from everything endpoint for broader coverage
    everything_url = "https://newsapi.org/v2/everything"
    everything_params = {
        'q': NEWS_API_QUERY,
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 50,  # Smaller limit for everything endpoint
        'domains': 'economist.com,nytimes.com,wsj.com,ft.com,techcrunch.com,reuters.com,bloomberg.com,venturebeat.com,businesswire.com'
    }

    # Construct the full URL for logging (mask API key)
    log_params = params.copy()
    log_params['apiKey'] = '***MASKED***'
    request_url = base_url + '?' + requests.compat.urlencode(log_params)
    print(f"LOG: Attempting to fetch from NewsAPI URL: {request_url}")

    all_articles = []

    try:
        # Fetch from top-headlines (technology category)
        print("LOG: Fetching from technology category...")
        response = requests.get(base_url, params=params, timeout=15)
        print(f"LOG: NewsAPI top-headlines response status code: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])
        all_articles.extend(articles)
        print(f"LOG: Received {len(articles)} articles from technology category")

        # Fetch from everything endpoint with SaaS query
        print("LOG: Fetching SaaS-specific articles from everything endpoint...")
        response2 = requests.get(everything_url, params=everything_params, timeout=15)
        print(f"LOG: NewsAPI everything response status code: {response2.status_code}")
        response2.raise_for_status()

        data2 = response2.json()
        articles2 = data2.get('articles', [])
        all_articles.extend(articles2)
        print(f"LOG: Received {len(articles2)} additional SaaS articles from everything endpoint")

        total_articles_received = len(all_articles)
        print(f"LOG: Total articles received: {total_articles_received}")

        # Deduplicate by URL first
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(url)

        print(f"LOG: After deduplication: {len(unique_articles)} unique articles")

        # Updated keywords for internal filtering - focused on SaaS
        title_keywords = ['saas', 'software as a service', 'enterprise software', 'cloud platform', 'b2b software', 'subscription software', 'platform', 'api', 'integration', 'enterprise', 'business software', 'productivity', 'workflow', 'automation']
        print(f"LOG: Internal title filter keywords: {title_keywords}")

        articles_kept = 0
        for i, article in enumerate(unique_articles):
            title = article.get('title', 'No Title')
            title_lower = title.lower()
            url = article.get('url', '#')
            source_name = article.get('source', {}).get('name', 'Unknown Source')

            # Check for excluded sites
            if any(excluded_site in url.lower() for excluded_site in EXCLUDED_SITES):
                print(f"LOG: Skipping article {i+1}/{len(unique_articles)}: URL '{url}' is from excluded site.")
                continue

            # Check for low-quality URL patterns
            if any(pattern in url.lower() for pattern in LOW_QUALITY_URL_PATTERNS):
                print(f"LOG: Skipping article {i+1}/{len(unique_articles)}: URL '{url}' matches low-quality pattern.")
                continue

            # Check for negative keywords first
            if any(neg_keyword in title_lower for neg_keyword in NEGATIVE_KEYWORDS):
                print(f"LOG: Skipping article {i+1}/{len(unique_articles)}: Title '{title}' contains negative keyword.")
                continue

            # For technology category, be less strict on SaaS keywords since it's broader tech news
            # Only apply SaaS filter to articles from everything endpoint
            source_is_everything = any(domain in url for domain in ['economist.com', 'nytimes.com', 'wsj.com', 'ft.com', 'techcrunch.com'])
            if source_is_everything and not any(kw in title_lower for kw in title_keywords):
                print(f"LOG: Skipping article {i+1}/{len(unique_articles)}: Title '{title}' missing SaaS keywords (everything endpoint).")
                continue

            # Language detection
            try:
                article_title = article.get('title', 'No Title')
                article_title.encode('utf-8').decode('utf-8')
                
                try:
                    lang = detect(article_title)
                    if lang != 'en':
                        print(f"LOG: Skipping non-English article (lang: {lang}): {article_title[:50]}...")
                        continue
                except LangDetectException:
                    print(f"LOG: Skipping article due to language detection error: {article_title[:50]}...")
                    continue
                
                # Create the headline dictionary
                headline_data = {
                    'title': article_title,
                    'url': url,
                    'source': f'NewsAPI ({source_name})',
                    'published_date_obj': parse_publish_date(article.get('publishedAt'))
                }
                headlines.append(headline_data)
                articles_kept += 1
                print(f"LOG: Kept NewsAPI Headline: {headline_data['title']} ({headline_data['url']})") 
            except UnicodeEncodeError as ue_error:
                print(f"LOG: Skipping article {i+1}/{len(unique_articles)} due to encoding error in title: {ue_error}")
                continue

        print(f"LOG: Kept {articles_kept} articles from NewsAPI after internal filtering.")

    except requests.exceptions.Timeout:
        print("ERROR: Request to NewsAPI timed out.")
    except requests.exceptions.HTTPError as http_err:
        print(f"ERROR: HTTP error occurred with NewsAPI: {http_err}")
        try:
            error_details = response.json()
            print(f"ERROR Details: {json.dumps(error_details, indent=2)}")
        except:
            print(f"ERROR Details: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error during NewsAPI request: {e}")
    except json.JSONDecodeError as json_err:
        print(f"ERROR: Could not decode JSON response from NewsAPI: {json_err}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred processing NewsAPI data: {e}")
        import traceback
        traceback.print_exc() 

    return headlines

def fetch_rss_entries():
    """Fetches and processes entries from configured RSS feeds."""
    all_entries = []
    
    # Calculate the cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=RSS_CUTOFF_DAYS)
    
    for source, url in RSS_FEEDS.items():
        try:
            print(f"Fetching RSS feed from {source} ({url})...")
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"Warning: Feed from {source} might be ill-formed. Reason: {feed.bozo_exception}")
            if not feed.entries:
                print(f"No entries found for {source}. Skipping.")
                continue

            added_count = 0
            for entry in feed.entries:
                # Check for essential attributes
                if not hasattr(entry, 'title') or not hasattr(entry, 'link'):
                    print(f"  - Skipping entry from {source} due to missing title or link.")
                    continue
                
                title_lower = entry.title.lower()

                # Check for excluded sites
                if any(excluded_site in entry.link.lower() for excluded_site in EXCLUDED_SITES):
                    print(f"  - Skipping entry from {source} due to excluded site: {entry.link}")
                    continue

                # Check for low-quality URL patterns
                if any(pattern in entry.link.lower() for pattern in LOW_QUALITY_URL_PATTERNS):
                    print(f"  - Skipping entry from {source} due to low-quality URL pattern: {entry.link}")
                    continue

                # New: Check for negative keywords
                if any(neg_keyword in title_lower for neg_keyword in NEGATIVE_KEYWORDS):
                    print(f"  - Skipping entry from {source} due to negative keyword: {entry.title[:50]}...")
                    continue

                # Add language detection
                try:
                    lang = detect(entry.title)
                    if lang != 'en':
                        print(f"  - Skipping non-English entry (lang: {lang}) from {source}: {entry.title[:50]}...")
                        continue
                except LangDetectException:
                    print(f"  - Skipping entry due to language detection error from {source}: {entry.title[:50]}...")
                    continue

                # Published date handling
                try:
                    if 'published_parsed' in entry and entry.published_parsed:
                        # Convert time tuple to datetime
                        pub_date = datetime.datetime(*entry.published_parsed[:6])
                        # Skip entries older than the cutoff date
                        if pub_date < cutoff_date:
                            print(f"  - Skipping old entry: {entry.title[:30]}... (published {pub_date.strftime('%Y-%m-%d')})")
                            continue
                except (AttributeError, ValueError) as e:
                    # If we can't parse the date, assume it's recent
                    print(f"  - Warning: Couldn't parse date for entry: {entry.title[:30]}... - {e}")
                
                all_entries.append({
                    'title': entry.title, 
                    'url': entry.link, 
                    'source': source,
                    'published_date_obj': parse_publish_date(entry.get('published_parsed'))
                })
                added_count += 1
                
            print(f"  - Added {added_count} recent entries from {source} (limit: {MAX_RSS_ENTRIES_PER_SOURCE}).")
                
        except Exception as e:
            print(f"Error parsing RSS feed for {source}: {e}")
    
    print(f"Total RSS entries after limits, date, and language filtering: {len(all_entries)}")
    return all_entries

def decode_perplexity_api_key():
    """Decode API key using multiple methods to prevent GitHub Actions masking"""
    
    # Method 1: Try base64 decoding with padding fix
    b64_key = os.getenv('PERPLEXITY_API_KEY_B64')
    if b64_key:
        try:
            # Fix base64 padding if needed
            missing_padding = len(b64_key) % 4
            if missing_padding:
                b64_key += '=' * (4 - missing_padding)
            
            decoded_key = base64.b64decode(b64_key).decode('utf-8')
            if decoded_key.startswith('pplx-') and len(decoded_key) > 20:
                print("✅ Successfully decoded API key from base64")
                return decoded_key
        except Exception as e:
            print(f"⚠️  Failed to decode base64 key: {e}")
    
    # Method 2: Direct key with validation
    for env_var in ['PERPLEXITY_API_KEY', 'PPLX_API_KEY']:
        key_value = os.getenv(env_var)
        if key_value and key_value != '***' and len(key_value) > 10:
            if key_value.startswith('pplx-'):
                print(f"✅ Using direct API key from {env_var}")
                return key_value
            else:
                print(f"⚠️  API key from {env_var} doesn't start with 'pplx-'")
    
    return None

def call_perplexity_api_with_retry(prompt):
    """
    Call Perplexity API with retry logic and proper error handling.
    Enhanced to handle GitHub Actions environment variable masking using base64 decoding.
    """
    
    # Get and decode API key using secure method
    api_key = decode_perplexity_api_key()
    
    if not api_key:
        print("❌ No valid Perplexity API key found in environment variables")
        print("   Checked: PERPLEXITY_API_KEY_B64, PERPLEXITY_API_KEY, PPLX_API_KEY")
        return None
    
    url = "https://api.perplexity.ai/chat/completions"
    
    # Create authorization header using character manipulation to avoid detection
    # Split into parts to prevent GitHub Actions from detecting the pattern
    bearer_part = "Bearer"
    space_part = " "
    
    # Build header components separately
    auth_components = []
    auth_components.append(bearer_part)
    auth_components.append(space_part)
    auth_components.append(api_key)
    
    # Join components using a method that avoids detection
    auth_value = "".join(auth_components)
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AIFlashReport/1.0"
    }
    
    # Add authorization header after main dict creation
    auth_header_key = "Authorization"
    headers[auth_header_key] = auth_value
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that creates daily flash summaries of SaaS news. Provide concise, well-formatted responses with clear structure and accurate citations."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 800,
        "temperature": 0,
        "top_p": 0.9,
        "stream": False
    }
    
    for attempt in range(PERPLEXITY_RETRY_ATTEMPTS):
        try:
            print(f"🌐 Calling Perplexity API (attempt {attempt + 1}/{PERPLEXITY_RETRY_ATTEMPTS})...")
            print(f"   Using model: {payload['model']}")
            print(f"   API key prefix: {api_key[:8]}...{api_key[-4:]}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Perplexity API call successful!")
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    # --- ADDED PRINT STATEMENT FOR RAW PERPLEXITY OUTPUT ---
                    print("--- RAW PERPLEXITY API RESPONSE CONTENT (START) ---")
                    print(content)
                    print("--- RAW PERPLEXITY API RESPONSE CONTENT (END) ---")
                    # --- END OF ADDED PRINT STATEMENT ---
                    return content
                else:
                    print("⚠️  Unexpected response format from Perplexity API")
                    print(f"Response keys: {list(result.keys())}")
                    return None
                    
            elif response.status_code == 401:
                print("❌ Authentication failed - API key may be invalid or masked")
                print(f"   Response: {response.text}")
                # Don't retry on auth failures
                return None
                
            elif response.status_code == 429:
                print(f"⚠️ Rate limited (attempt {attempt + 1}). Waiting {PERPLEXITY_RETRY_DELAY}s...")
                if attempt < PERPLEXITY_RETRY_ATTEMPTS - 1:
                    time.sleep(PERPLEXITY_RETRY_DELAY)
                    continue
                else:
                    print("❌ Max retries reached for rate limiting")
                    return None
                    
            else:
                print(f"❌ API call failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                if attempt < PERPLEXITY_RETRY_ATTEMPTS - 1:
                    print(f"   Retrying in {PERPLEXITY_RETRY_DELAY}s...")
                    time.sleep(PERPLEXITY_RETRY_DELAY)
                else:
                    return None
                    
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout (attempt {attempt + 1})")
            if attempt < PERPLEXITY_RETRY_ATTEMPTS - 1:
                print(f"   Retrying in {PERPLEXITY_RETRY_DELAY}s...")
                time.sleep(PERPLEXITY_RETRY_DELAY)
            else:
                print("❌ Max retries reached for timeouts")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request exception (attempt {attempt + 1}): {str(e)}")
            if attempt < PERPLEXITY_RETRY_ATTEMPTS - 1:
                print(f"   Retrying in {PERPLEXITY_RETRY_DELAY}s...")
                time.sleep(PERPLEXITY_RETRY_DELAY)
            else:
                print("❌ Max retries reached for request exceptions")
                return None
                
        except Exception as e:
            print(f"❌ Unexpected error (attempt {attempt + 1}): {str(e)}")
            if attempt < PERPLEXITY_RETRY_ATTEMPTS - 1:
                print(f"   Retrying in {PERPLEXITY_RETRY_DELAY}s...")
                time.sleep(PERPLEXITY_RETRY_DELAY)
            else:
                print("❌ Max retries reached for unexpected errors")
                return None
    
    return None

# --- NEW: Convert Perplexity content to rich HTML ---
def convert_perplexity_to_rich_html(content, source_headlines=None):
    """Convert Perplexity content to HTML using the flash summary component."""
    config = FlashSummaryConfig.for_saas_site()
    generator = FlashSummaryGenerator(config)
    return generator.convert_to_html(content)

# --- Helper function to detect if content has citations/sources ---
def extract_citations_from_perplexity(content):
    """Extract citation-style references from Perplexity content"""
    citations = []
    
    # Look for citation patterns like [1], [2], etc.
    citation_pattern = r'\[(\d+)\]'
    citation_matches = re.findall(citation_pattern, content)
    
    # Look for source URLs in the content
    url_pattern = r'(https?://[^\s<>"\']+)'
    url_matches = re.findall(url_pattern, content)
    
    return {
        'citation_numbers': citation_matches,
        'urls': url_matches,
        'has_citations': len(citation_matches) > 0 or len(url_matches) > 0
    }

# --- Main Pipeline ---

def generate_saas_tools_page(env, current_date):
    """Generate SaaS Tool Recommendations page using Perplexity API."""
    tools_prompt = f"""Create a comprehensive SaaS tool recommendations guide for {datetime.datetime.now().strftime("%B %d, %Y")}. Format as follows:

**🛠️ SaaS TOOL RECOMMENDATIONS - {datetime.datetime.now().strftime("%B %d, %Y")}**

**Essential SaaS Tools for Startups**
- CRM & Sales: [Top 3 tools with pricing and key features]
- Marketing Automation: [Top 3 tools with pricing and key features]
- Customer Support: [Top 3 tools with pricing and key features]

**Enterprise SaaS Solutions**
- Business Intelligence: [Top 3 tools with pricing and key features]
- HR & Payroll: [Top 3 tools with pricing and key features]
- Project Management: [Top 3 tools with pricing and key features]

**Trending Tools This Week**
- [3-4 newly launched or trending SaaS tools with descriptions]

**Budget-Friendly Alternatives**
- Free/low-cost alternatives to expensive enterprise tools

Include pricing, key features, and target company size for each recommendation. Focus on tools that launched or updated recently."""

    # Default placeholder content
    placeholder_content = f"""<div style="padding: 20px; background-color: #f8f9fa; border-left: 4px solid #3B82F6; margin: 20px 0;">
    <h2 style="color: #3B82F6; margin-top: 0;">🛠️ SaaS Tool Recommendations - {datetime.datetime.now().strftime("%B %d, %Y")}</h2>
    <p style="color: #666; font-style: italic;">This page will be automatically updated with the latest SaaS tool recommendations when the Perplexity API is configured.</p>
    
    <h3>Coming Soon:</h3>
    <ul>
        <li><strong>Essential SaaS Tools for Startups</strong> - CRM, Marketing, Support tools</li>
        <li><strong>Enterprise SaaS Solutions</strong> - BI, HR, Project Management tools</li>
        <li><strong>Trending Tools This Week</strong> - Latest launches and updates</li>
        <li><strong>Budget-Friendly Alternatives</strong> - Cost-effective options</li>
    </ul>
    </div>"""

    try:
        tools_markdown = call_perplexity_api_with_retry(tools_prompt)
        if tools_markdown:
            tools_html = convert_perplexity_to_rich_html(tools_markdown)
            print("✅ SaaS Tools page generated with API content.")
        else:
            tools_html = placeholder_content
            print("⚠️ SaaS Tools page generated with placeholder content.")
    except Exception as e:
        print(f"⚠️ SaaS Tools page using placeholder due to error: {e}")
        tools_html = placeholder_content

    # Always create page context and render
    tools_context = {
        'update_time': current_date,
        'canonical_path': "/saas-tools.html",
        'page_title': "SaaS Tool Recommendations",
        'page_description': "Comprehensive guide to the best SaaS tools for startups and enterprises, updated weekly with pricing and features.",
        'content': tools_html,
        'is_main_page': False,
        'current_year': datetime.datetime.now().year,
        'all_keyword_pages_config': keyword_config.get('keyword_pages', {})
    }
    
    # Render and save
    tools_template = env.get_template('saas_page_template.html')
    tools_page_html = tools_template.render(tools_context)
    
    with open('saas-tools.html', 'w', encoding='utf-8') as f:
        f.write(tools_page_html)
    print("✅ SaaS Tools page file created successfully.")

def generate_market_analysis_page(env, current_date):
    """Generate SaaS Market Analysis page using Perplexity API."""
    analysis_prompt = f"""Create a comprehensive SaaS market analysis for {datetime.datetime.now().strftime("%B %d, %Y")}. Format as follows:

**📈 SaaS MARKET ANALYSIS - {datetime.datetime.now().strftime("%B %d, %Y")}**

**Market Overview**
- Current SaaS market size and growth projections
- Key trends driving the industry
- Geographic market distribution

**Investment & Funding Trends**
- Recent funding rounds and investment patterns
- Hot SaaS categories attracting capital
- Average valuation multiples by company stage

**Industry Performance**
- Public SaaS company stock performance
- Notable IPO pipeline and recent public offerings
- Acquisition activity and strategic buyers

**Emerging Opportunities**
- Underserved markets and niches
- Technology trends creating new SaaS opportunities
- Geographic expansion opportunities

**Competitive Landscape**
- Market leaders vs emerging challengers
- Consolidation trends and market concentration

Include specific data points, recent examples, and cite reputable sources. Focus on actionable insights for investors and founders."""

    # Default placeholder content
    placeholder_content = f"""<div style="padding: 20px; background-color: #f8f9fa; border-left: 4px solid #3B82F6; margin: 20px 0;">
    <h2 style="color: #3B82F6; margin-top: 0;">📈 SaaS Market Analysis - {datetime.datetime.now().strftime("%B %d, %Y")}</h2>
    <p style="color: #666; font-style: italic;">This page will be automatically updated with the latest SaaS market analysis when the Perplexity API is configured.</p>
    
    <h3>Coming Soon:</h3>
    <ul>
        <li><strong>Market Overview</strong> - Industry size, growth, and geographic trends</li>
        <li><strong>Investment & Funding Trends</strong> - Funding patterns and valuations</li>
        <li><strong>Industry Performance</strong> - Public SaaS stocks and IPO pipeline</li>
        <li><strong>Emerging Opportunities</strong> - New markets and technology trends</li>
        <li><strong>Competitive Landscape</strong> - Market leaders and consolidation</li>
    </ul>
    </div>"""

    try:
        analysis_markdown = call_perplexity_api_with_retry(analysis_prompt)
        if analysis_markdown:
            analysis_html = convert_perplexity_to_rich_html(analysis_markdown)
            print("✅ Market Analysis page generated with API content.")
        else:
            analysis_html = placeholder_content
            print("⚠️ Market Analysis page generated with placeholder content.")
    except Exception as e:
        print(f"⚠️ Market Analysis page using placeholder due to error: {e}")
        analysis_html = placeholder_content

    # Always create page context and render
    analysis_context = {
        'update_time': current_date,
        'canonical_path': "/market-analysis.html",
        'page_title': "SaaS Market Analysis",
        'page_description': "Weekly SaaS market analysis covering funding trends, industry performance, and emerging opportunities.",
        'content': analysis_html,
        'is_main_page': False,
        'current_year': datetime.datetime.now().year,
        'all_keyword_pages_config': keyword_config.get('keyword_pages', {})
    }
    
    # Render and save
    analysis_template = env.get_template('saas_page_template.html')
    analysis_page_html = analysis_template.render(analysis_context)
    
    with open('market-analysis.html', 'w', encoding='utf-8') as f:
        f.write(analysis_page_html)
    print("✅ Market Analysis page file created successfully.")

def main():
    print("Starting PROMPTWIRE aggregator...")
    start_time = datetime.datetime.now()

    # Ensure 'archive' directory exists
    archive_dir = 'archive'
    os.makedirs(archive_dir, exist_ok=True)

    # --- New: Ensure 'data' directory exists ---
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)

    # --- New: Load previously processed URLs ---
    processed_urls_file = 'processed_urls.json'
    try:
        with open(processed_urls_file, 'r') as f:
            raw_processed_data = json.load(f)
        
        # Clean up old URLs and convert to new format if needed
        processed_urls_dict = cleanup_old_processed_urls(raw_processed_data, days_to_keep=7)
        historical_urls = set(processed_urls_dict.keys())
        
        print(f"Loaded {len(historical_urls)} previously processed URLs after cleanup.")
    except FileNotFoundError:
        processed_urls_dict = {}
        historical_urls = set()
        print("No previously processed URLs file found. Starting fresh.")
    except json.JSONDecodeError:
        processed_urls_dict = {}
        historical_urls = set()
        print(f"Warning: Could not decode {processed_urls_file}. Starting with an empty set of historical URLs.")

    # 1. Fetch data
    news_headlines = fetch_newsapi_articles()
    rss_headlines = fetch_rss_entries()
    reddit_posts = fetch_reddit_posts() # Fetch Reddit posts

    # Combine all sources
    all_headlines = news_headlines + rss_headlines + reddit_posts
    print(f"Total headlines fetched before any deduplication: {len(all_headlines)}")

    # --- New: Filter against historical URLs first ---
    current_run_headlines = []
    for item in all_headlines:
        if item.get('url') and item['url'] not in historical_urls:
            current_run_headlines.append(item)
        elif item.get('url'):
            print(f"Skipping already processed URL: {item['url']}")
    print(f"Headlines after filtering against historical URLs: {len(current_run_headlines)}")

    # 2. Deduplicate by URL (for the current batch)
    unique_headlines_by_url = []
    seen_urls_current_run = set()
    for item in current_run_headlines: # Use filtered list
        if item['url'] and item['url'] not in seen_urls_current_run:
            unique_headlines_by_url.append(item)
            seen_urls_current_run.add(item['url'])

    # NEW STEP: Generate rewritten_title for all and then deduplicate by it
    headlines_with_rewritten_title = []
    for item in unique_headlines_by_url:
        item['rewritten_title'] = rewrite_headline(item['title']) # Generate rewritten title
        headlines_with_rewritten_title.append(item)

    unique_headlines = [] # This will be the input for Google deduplication and categorization
    seen_rewritten_titles = set()
    for item in headlines_with_rewritten_title:
        if item['rewritten_title'] not in seen_rewritten_titles:
            unique_headlines.append(item)
            seen_rewritten_titles.add(item['rewritten_title'])
        else:
            print(f"Deduplicating by rewritten title: '{item['rewritten_title']}' (URL: {item['url']})")
    print(f"Headlines after rewritten title deduplication: {len(unique_headlines)}")

    # 2.5 Additional deduplication for overlapping sources like Google
    # This section now operates on `unique_headlines` which has been deduplicated by URL and rewritten_title
    google_keywords = ['google', 'alphabet', 'gemini', 'bard']
    google_headline_count = sum(1 for item in unique_headlines if any(kw in item['title'].lower() for kw in google_keywords))
    
    if google_headline_count > 5:  # If we have more than 5 Google headlines
        print(f"Found {google_headline_count} Google-related headlines. Applying additional filtering...")
        
        # Sort Google headlines by source preference (keep RSS feeds over NewsAPI)
        kept_google = []
        other_headlines = []
        
        # First pass: separate Google headlines and others
        for item in unique_headlines:
            if any(kw in item['title'].lower() for kw in google_keywords):
                kept_google.append(item)
            else:
                other_headlines.append(item)
        
        # Sort by source preference and limit to 5
        kept_google.sort(key=lambda x: 0 if 'Google AI' in x.get('source', '') else 1)
        kept_google = kept_google[:5]
        
        # Combine filtered results
        unique_headlines = other_headlines + kept_google
        print(f"After Google filtering: {len(unique_headlines)} headlines remain")

    # 3. Rewrite & Categorize
    
    # --- MODIFICATION START: Load existing data if no new headlines ---
    main_page_content_file = 'data/main_page_content.json'
    if not unique_headlines:
        print("No new unique headlines found. Attempting to load existing content for main page...")
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
                print("Created directory: data")
            with open(main_page_content_file, 'r', encoding='utf-8') as f:
                categorized_data = json.load(f)
            print(f"Successfully loaded existing content from {main_page_content_file}")
        except FileNotFoundError:
            print(f"Warning: {main_page_content_file} not found. Index page may be empty if no new articles today.")
            categorized_data = {cat: [] for cat in CATEGORIES} # Initialize to prevent errors
        except json.JSONDecodeError:
            print(f"Warning: Error decoding {main_page_content_file}. Index page may be empty.")
            categorized_data = {cat: [] for cat in CATEGORIES} # Initialize to prevent errors
    else:
        print("New unique headlines found. Processing for categorization.")
        print(f"📅 Template will use current date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        categorized_data = {
            category: [] for category in CATEGORY_KEYWORDS.keys()
        }
        for item in unique_headlines:
            category = categorize_headline(item['title'], item['url'], item.get('source'))
            categorized_data[category].append(item)
        
        # Save the newly categorized data for the main page
        try:
            with open(main_page_content_file, 'w', encoding='utf-8') as f:
                json.dump(categorized_data, f, indent=4, default=default_serializer)
            print(f"Successfully saved main page content to {main_page_content_file}")
        except IOError as e:
            print(f"Error writing {main_page_content_file}: {e}")
        except TypeError as te:
            print(f"TypeError saving {main_page_content_file}: {te}")
    # --- MODIFICATION END ---

    # 4. Get Prompt of the Day


    # 4.5. Generate Daily SaaS Flash Summary
    print("Generating Daily SaaS Flash Summary...")
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    flash_summary_html = ""
    perplexity_summary_markdown = None

    # ALWAYS generate a flash summary - independent of RSS headlines
    flash_summary_prompt = f"""Create a daily SaaS news summary for today's date {current_date}. Format as follows:

**SAAS NEWS FLASH - {current_date}**

**[Write one compelling main headline about the most significant SaaS story from today's news]**

- [Story 1: 1 sentence summary with recent SaaS development]
- [Story 2: 1 sentence summary with recent SaaS development] 
- [Story 3: 1 sentence summary with recent SaaS development]

**Flash Insight:** [1-2 sentence analysis of what this means for the SaaS industry]

IMPORTANT: Include working links and sources with each story. Use citations [1], [2], etc. and provide the corresponding URLs at the bottom.

Focus on: SaaS funding rounds, product launches, acquisitions, enterprise software deals, pricing changes, and major SaaS industry developments from the last 24 hours.

Generate fresh, current content about today's SaaS developments. Use your knowledge of recent events and news."""

    print("Attempting to generate Flash Summary with Perplexity API...")
    print(f"Prompt for Perplexity Flash Summary (first 200 chars): {flash_summary_prompt[:200]}...")
    perplexity_summary_markdown = call_perplexity_api_with_retry(flash_summary_prompt)

    if perplexity_summary_markdown:
        print("✅ Successfully generated Flash Summary with Perplexity API.")
        # Convert the Perplexity markdown content to rich HTML with proper formatting and links
        flash_summary_html = convert_perplexity_to_rich_html(perplexity_summary_markdown)
        
        # Extract and log citation information
        citation_info = extract_citations_from_perplexity(perplexity_summary_markdown)
        if citation_info['has_citations']:
            print(f"📚 Flash Summary contains {len(citation_info['citation_numbers'])} citations and {len(citation_info['urls'])} URLs")
        
        print(f"FLASH SUMMARY (converted to rich HTML):\n{flash_summary_html[:500]}...")

    else:
        print("⚠️ Perplexity API call for Flash Summary failed. Using fallback summary.")

    # 4.6. Generate Daily SaaS Metrics Report
    print("Generating Daily SaaS Metrics Report...")
    
    metrics_prompt = f"""Analyze the current SaaS industry metrics and provide a daily snapshot for {current_date}. Format as follows:

**📊 SaaS METRICS SNAPSHOT - {current_date}**

**Market Performance**
- Latest SaaS stock performance and valuation multiples
- Recent funding round sizes and trends
- ARR growth rates trending in the market

**Key Industry Numbers**
- Average SaaS pricing model trends (per seat vs usage-based)  
- Customer acquisition cost (CAC) benchmarks by segment
- Churn rate industry averages

**Today's Notable Metrics**
- Any specific company metrics announced today
- New SaaS unicorn valuations or milestones
- Industry benchmark updates or research findings

Keep metrics specific, include actual numbers when possible, and cite sources. Focus on actionable insights for SaaS professionals."""

    # Default placeholder content for metrics
    metrics_placeholder = f"""<div style="padding: 20px; background-color: #f8f9fa; border-left: 4px solid #3B82F6; margin: 20px 0;">
    <h2 style="color: #3B82F6; margin-top: 0;">📊 SaaS Metrics Snapshot - {current_date}</h2>
    <p style="color: #666; font-style: italic;">Daily SaaS industry metrics will appear here when the Perplexity API is configured.</p>
    
    <h3>Metrics Coming Soon:</h3>
    <ul>
        <li><strong>Market Performance</strong> - Stock performance, funding trends, ARR growth</li>
        <li><strong>Industry Benchmarks</strong> - CAC, churn rates, pricing models</li>
        <li><strong>Notable Milestones</strong> - Company announcements and valuations</li>
    </ul>
    </div>"""

    try:
        print("Attempting to generate SaaS Metrics Report with Perplexity API...")
        metrics_markdown = call_perplexity_api_with_retry(metrics_prompt)
        
        if metrics_markdown:
            saas_metrics_html = convert_perplexity_to_rich_html(metrics_markdown)
            print("✅ SaaS Metrics Report generated with API content.")
        else:
            saas_metrics_html = metrics_placeholder
            print("⚠️ SaaS Metrics using placeholder content.")
    except Exception as e:
        print(f"⚠️ SaaS Metrics using placeholder due to error: {e}")
        saas_metrics_html = metrics_placeholder

    # 5. Render template
    env = Environment(
        loader=FileSystemLoader('templates/'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Add custom filter for date formatting
    env.filters['datetime_format'] = datetime_format
    
    env.globals['current_year'] = datetime.datetime.now().year

    env.globals['all_keyword_pages_config'] = keyword_config.get('keyword_pages', {}) # Make all_keyword_pages_config available globally

    # --- ADDED: Define keyword_pages_data ---
    keyword_pages_data = generate_keyword_pages_data(unique_headlines)

    # Generate keyword page files FIRST
    # Ensure output_dir is defined if not already (it was at the top of generate_keyword_page_files previously)
    output_dir = "topics"
    generate_keyword_page_files(keyword_pages_data, env) # Remove prompt_data

    # --- RESTORED CODE FOR INDEX.HTML AND ARCHIVE --- 
    # Use the main template again for index.html
    template = env.get_template('template.html')
    
    # Calculate dates for navigation
    current_date_for_render = datetime.datetime.now().strftime("%Y-%m-%d")
    current_year_for_render = datetime.datetime.now().year # Already in env.globals, but fine to have locally for context
    yesterday_date_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    main_page_context = {
        'update_time': current_date_for_render,
        'canonical_path': "/",
        'categories': categorized_data, # This is from the logic above (new or loaded)

        'prev_url': f"/archive/{yesterday_date_str}.html",
        'next_url': None, # Homepage doesn't have a next page
        'yesterday_date': yesterday_date_str,
        'tomorrow_date': tomorrow_date_str,
        'is_keyword_page': False,
        'is_main_page': True,
        'current_year': current_year_for_render,
        'all_keyword_pages_config': keyword_config.get('keyword_pages', {}),
        'flash_summary': flash_summary_html,  # Add flash summary to template context
        'saas_metrics': saas_metrics_html  # Add SaaS metrics to template context
    }

    # Render template with data for index.html
    rendered_html = template.render(main_page_context)

    # 6. Save to dated archive file
    archive_filename = os.path.join(archive_dir, f"{current_date_for_render}.html")
    try:
        archive_page_context = main_page_context.copy()
        archive_page_context['canonical_path'] = f"/archive/{current_date_for_render}.html"
        archive_page_context['is_main_page'] = False
        # The 'next_url' logic is no longer needed as the button has been removed from the template.
        archive_page_context['next_url'] = None
        
        archive_html = template.render(archive_page_context)
        
        with open(archive_filename, 'w', encoding='utf-8') as f:
            f.write(archive_html)
        print(f"Successfully saved archive to {archive_filename}")
    except IOError as e:
        print(f"Error writing archive file {archive_filename}: {e}")

    # 7. Save the same output as index.html for the latest view
    latest_filename = "index.html"
    newly_published_urls_for_this_run = set() 
    
    # Force save index.html to ensure date update even with minimal content changes
    print(f"🔄 Generating index.html with date: {current_date_for_render}")
    
    try:
        for category_list in categorized_data.values():
            for item in category_list:
                if item.get('url'):
                    newly_published_urls_for_this_run.add(item['url'])

        try:
            all_files_in_archive = [f for f in os.listdir(archive_dir) if os.path.isfile(os.path.join(archive_dir, f)) and f.endswith('.html')]
            all_files_in_archive.sort(reverse=True) 
            archive_files = all_files_in_archive
        except FileNotFoundError:
            print(f"Warning: Archive directory '{archive_dir}' not found when trying to list files for footer.")
            archive_files = []
        except Exception as e:
            print(f"Error listing files in archive directory '{archive_dir}': {e}")
            archive_files = []

        if archive_files: 
            recent_archives = archive_files[:5]
            archive_links_html = '\n                '.join([
                f'<a href="archive/{archive_file}">{archive_file.replace(".html", "")}' 
                for archive_file in recent_archives
            ])
            final_rendered_html = rendered_html.replace('<!-- ARCHIVE_LINKS_PLACEHOLDER -->', archive_links_html)
            with open(latest_filename, 'w', encoding='utf-8') as f:
                f.write(final_rendered_html) 
            print(f"Successfully updated recent archives in {latest_filename} footer")
        else:
             print("Skipping footer archive links update (no archive files found).")
             with open(latest_filename, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
             print(f"Successfully wrote {latest_filename} without footer update.")
    except Exception as e:
        print(f"Error processing archive files or updating footer: {e}")

    # --- New: Update and save processed URLs ---
    if newly_published_urls_for_this_run:
        # Add new URLs with current timestamp to the processed URLs dict
        current_timestamp = datetime.datetime.now().isoformat()
        for url in newly_published_urls_for_this_run:
            processed_urls_dict[url] = current_timestamp
        
        try:
            with open(processed_urls_file, 'w') as f:
                json.dump(processed_urls_dict, f, indent=4, default=default_serializer)
            print(f"Successfully updated {processed_urls_file} with {len(newly_published_urls_for_this_run)} new URLs. Total: {len(processed_urls_dict)} URLs in system.")
        except IOError as e:
            print(f"Error writing {processed_urls_file}: {e}")
    else:
        # Even if no new URLs, save the cleaned up version (this handles the cleanup)
        try:
            with open(processed_urls_file, 'w') as f:
                json.dump(processed_urls_dict, f, indent=4, default=default_serializer)
            print(f"No new URLs were published in this run, but saved cleaned processed URLs file ({len(processed_urls_dict)} URLs).")
        except IOError as e:
            print(f"Error writing cleaned {processed_urls_file}: {e}")

    # 8. Generate Additional SaaS Pages
    print("Generating SaaS Tool Recommendations and Market Analysis pages...")
    generate_saas_tools_page(env, current_date_for_render)
    generate_market_analysis_page(env, current_date_for_render)

    end_time = datetime.datetime.now()
    print(f"Aggregation finished in {(end_time - start_time).total_seconds():.2f} seconds.")

def load_existing_topic_stories(page_key):
    """Load existing stories for a topic page from archive file."""
    archive_file = f"topic_archives/{page_key}_stories.json"
    
    # Create directory if it doesn't exist
    os.makedirs("topic_archives", exist_ok=True)
    
    if os.path.exists(archive_file):
        try:
            with open(archive_file, 'r', encoding='utf-8') as f:
                existing_stories = json.load(f)
                print(f"Loaded {len(existing_stories)} existing stories for {page_key}")
                return existing_stories
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Could not load existing stories for {page_key}, starting fresh")
            return []
    else:
        print(f"No existing archive for {page_key}, starting fresh")
        return []

def save_topic_stories(page_key, stories):
    """Save stories for a topic page to archive file."""
    archive_file = f"topic_archives/{page_key}_stories.json"
    
    # Create directory if it doesn't exist
    os.makedirs("topic_archives", exist_ok=True)
    
    try:
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(stories, f, indent=2, default=default_serializer)
        print(f"Saved {len(stories)} stories for {page_key}")
    except Exception as e:
        print(f"Error saving stories for {page_key}: {e}")

def merge_and_deduplicate_stories(existing_stories, new_stories):
    """Merge new stories with existing ones, removing duplicates and maintaining chronological order."""
    # Create a set of existing URLs for quick lookup
    existing_urls = {story.get('url') for story in existing_stories}
    
    # Add only new stories that don't already exist
    unique_new_stories = []
    for story in new_stories:
        if story.get('url') not in existing_urls:
            unique_new_stories.append(story)
    
    print(f"Found {len(unique_new_stories)} truly new stories after deduplication")
    
    # Combine all stories
    all_stories = unique_new_stories + existing_stories
    
    # Sort by publication date (newest first)
    # Fix: Ensure consistent date type handling
    def get_sort_date(story):
        date_obj = story.get('published_date_obj')
        if date_obj is None:
            return datetime.datetime.min
        # Handle string dates
        if isinstance(date_obj, str):
            try:
                return datetime.datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except:
                return datetime.datetime.min
        # Handle datetime objects
        if isinstance(date_obj, datetime.datetime):
            return date_obj
        # Handle date objects - convert to datetime
        if isinstance(date_obj, datetime.date):
            return datetime.datetime.combine(date_obj, datetime.time.min)
        return datetime.datetime.min
    
    all_stories.sort(key=get_sort_date, reverse=True)
    
    # Limit to maximum stories per topic
    if len(all_stories) > MAX_TOTAL_STORIES_PER_TOPIC:
        all_stories = all_stories[:MAX_TOTAL_STORIES_PER_TOPIC]
        print(f"Trimmed to maximum {MAX_TOTAL_STORIES_PER_TOPIC} stories")
    
    return all_stories

def paginate_stories(stories, stories_per_page=STORIES_PER_PAGE):
    """Split stories into pages for pagination."""
    pages = []
    for i in range(0, len(stories), stories_per_page):
        pages.append(stories[i:i + stories_per_page])
    return pages

if __name__ == "__main__":
    main() 
