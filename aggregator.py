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
    """Filter articles for a specific keyword page based on its configuration."""
    filtered_articles = []
    case_sensitive = keyword_config.get('settings', {}).get('case_sensitive', False)
    
    # Get content_max_age_days from page_config, default to a large number if not specified
    # so that pages without this config are not aggressively filtered by date here.
    # The global RSS_CUTOFF_DAYS (2) in fetch_rss_entries will still apply for those.
    content_max_age_days = page_config.get('content_max_age_days') # Will be None if not set
    today = datetime.date.today()

    for i, article in enumerate(all_articles):
        title = article.get('title', '')
        
        # --- DATE FILTERING START ---
        if content_max_age_days is not None:
            article_date = article.get('published_date_obj') # This is a datetime.date object or None
            if article_date:
                age_delta = today - article_date
                if age_delta.days > content_max_age_days:
                    continue
        # --- DATE FILTERING END ---

        if not title:
            continue
        
        negative_keywords = page_config.get('negative_keywords', [])
        if negative_keywords and matches_keywords(title, negative_keywords, case_sensitive):
            continue
        
        required_keywords = page_config.get('required_keywords', [])
        if required_keywords and not matches_keywords(title, required_keywords, case_sensitive):
            continue
        
        keywords = page_config.get('keywords', [])
        if keywords and not matches_keywords(title, keywords, case_sensitive):
            continue
        
        relevance_score = calculate_keyword_relevance_score(article, page_config)
        
        if relevance_score > 0:
            article_copy = article.copy()
            article_copy['relevance_score'] = relevance_score
            filtered_articles.append(article_copy)

    # Sort by relevance score (highest first)
    filtered_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Limit to max articles
    max_articles = page_config.get('max_articles', 50)
    filtered_articles = filtered_articles[:max_articles]
    
    return filtered_articles

def generate_keyword_pages_data(all_articles):
    """Generate filtered data for all keyword pages."""
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
            # Decide if you want to stop or continue if directory creation fails
            # For now, we'll continue and individual file loads will fail gracefully

    for page_key, page_config in keyword_config['keyword_pages'].items():
        if page_config.get('page_type') == 'curated':
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
                        # Also ensure 'published_date_obj' is serializable if it somehow gets in here
                        # (though curated content isn't expected to have it by default)
                        for article in articles:
                            if 'rewritten_title' not in article and 'title' in article:
                                article['rewritten_title'] = rewrite_headline(article['title'])
                            if 'source' not in article: 
                                article['source'] = "Curated"
                            # If by chance a date object is here, ensure it's a string for saving
                            if 'published_date_obj' in article and isinstance(article['published_date_obj'], (datetime.date, datetime.datetime)):
                                article['published_date_str_for_curated'] = article['published_date_obj'].isoformat()

                        print(f"  - Loaded {len(articles)} articles from {curated_content_path}")
                except json.JSONDecodeError:
                    print(f"Warning: Error decoding JSON from {curated_content_path}. Skipping.")
                    articles = []
                except Exception as e:
                    print(f"Warning: Could not load curated content from {curated_content_path}: {e}. Skipping.")
                    articles = []
            else:
                print(f"Warning: Curated content file {curated_content_path} not found. Page will be empty.")
            
            # Even if articles list is empty, create the structure so an empty page can be generated
            keyword_pages_data[page_key] = {
                'config': page_config,
                'articles': articles # This will be the manually loaded articles or an empty list
            }
        else: # Automated page
            filtered_articles = filter_articles_for_keyword_page(all_articles, page_key, page_config)
            # Always add the page_key, even if articles are empty, so the template can render it
            keyword_pages_data[page_key] = {
                'config': page_config,
                'articles': filtered_articles # This will be an empty list if none were found
            }
    
    return keyword_pages_data

def generate_keyword_page_files(keyword_pages_data, env, prompt_of_the_day):
    """Generate HTML files for keyword pages."""
    print(f"Generating {len(keyword_pages_data)} keyword page files...")
    
    # Ensure the output directory exists
    # Output keyword pages to the root directory
    output_dir = "." 
    os.makedirs(output_dir, exist_ok=True)

    # The 'env' is passed in, so we don't need to re-initialize FileSystemLoader here.
    # We just need to ensure the globals are set correctly for this rendering context if they haven't been.
    # However, these globals are typically set on the env when it's first created in main().
    # For safety, let's ensure they are available if this function were ever called with a different env.
    env.globals['current_year'] = datetime.datetime.now().year
    env.globals['prompt_of_the_day'] = prompt_of_the_day
    env.globals['all_keyword_pages_config'] = keyword_config.get('keyword_pages', {})

    try:
        template = env.get_template("keyword_template.html") # This will now look in 'templates/keyword_template.html'
        print("Using keyword_template.html for keyword pages.")
    except jinja2_exceptions.TemplateNotFound:
        print("Error: keyword_template.html not found. Make sure it's in the templates directory.")
        return
    except Exception as e:
        print(f"Error loading keyword_template.html: {e}")
        return

    for page_key, data in keyword_pages_data.items():
        # if not data['articles'] and data['config'].get('page_type') == 'automated':
        #     print(f"  - Skipping generation of {page_key}.html as it's an automated page with no new articles.")
        #     continue

        # Ensure 'categories' is structured as expected by keyword_template.html
        # For keyword pages, articles are typically not further sub-categorized in the same way as the main page.
        # We'll put all articles under a single category, which is the page title itself.
        page_specific_categories = {data['config']['title']: data['articles']}
        
        # Determine canonical path
        # All keyword pages are at the root level, e.g., /openai-news.html
        canonical_path = f"/{page_key}.html"

        try:
            # Pass keyword_page_config for meta tags and specific content
            # Pass prompt_of_the_day for the prompt widget
            html_content = template.render(
                categories=page_specific_categories,
                page_title=data['config']['title'],
                page_description=data['config'].get('description', ''), # Use .get for safety
                update_time=datetime.datetime.now().strftime("%Y-%m-%d"), # Add update_time
                current_year=datetime.datetime.now().year, # Add current_year
                is_keyword_page=True, # Flag to indicate this is a keyword page
                keyword_page_config=data['config'], # Pass the full config for this page
                canonical_path=canonical_path,
                prompt_of_the_day=prompt_of_the_day, # Pass prompt data
                all_keyword_pages_config=keyword_config.get('keyword_pages', {}) # Added for navigation
            )
            with open(os.path.join(output_dir, f"{page_key}.html"), "w") as f:
                f.write(html_content)
            print(f"  - Successfully generated {page_key}.html")
        except Exception as e:
            print(f"Error generating page for {page_key}: {e}")
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
MAX_REDDIT_POSTS_PER_SUB = 2 # Keep the reduced number
REDDIT_TIME_FILTER = 'day' # Restore this constant

# Updated NewsAPI query to be more inclusive
NEWS_API_QUERY = '(artificial intelligence OR AI OR "machine learning" OR "deep learning" OR "neural network" OR "large language model" OR LLM OR GPT OR "generative AI") AND (technology OR business OR science OR research OR innovation)'
MAX_NEWS_API_ARTICLES = 100 # Number of articles to fetch from NewsAPI (Increased from 25)
MAX_HEADLINE_WORDS = 8

# Add these new constants
MAX_RSS_ENTRIES_PER_SOURCE = 3  # Limit RSS entries per source (Updated from 5 to 3)
RSS_CUTOFF_DAYS = 2  # Only include RSS entries from the last 2 days (Changed from 7)

# Add major news sources to RSS feeds
RSS_FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Anthropic": "https://www.anthropic.com/rss/",  # Updated URL
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Meta AI": "https://ai.meta.com/blog/rss/",
    # Major news sources
    "The Economist": "https://www.economist.com/science-and-technology/rss.xml",
    "MIT Technology Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "Wired": "https://www.wired.com/tag/artificial-intelligence/feed/rss",
    "The Verge": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    # Existing RSS feeds
    "Import AI": "https://jack-clark.net/feed/",
    "Machine Learning Mastery": "https://machinelearningmastery.com/blog/feed/",
    "The Batch": "https://read.deeplearning.ai/the-batch/rss/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "Towards Data Science": "https://towardsdatascience.com/feed",
    "Synced Review": "https://syncedreview.com/feed/",
    "Analytics Vidhya": "https://www.analyticsvidhya.com/blog/feed/",
    "The Gradient": "https://thegradient.pub/rss/"
}

# Define categories based on the project brief
CATEGORIES = [
    'Trending Now',
    'AI Products',
    'Creator Economy',
    'Generative AI',
    'AI Business News',
    'AI Research & Methods',
    'AI in Practice',
    'AI Companies',
    'AI Ethics & Policy',
    'Weird'
]

# Define keywords for categorization (more aligned with the brief)
# NOTE: This is a simple keyword approach and may need refinement.
# Order matters: More specific categories should come first.
CATEGORY_KEYWORDS = {
    'AI Companies': ['openai', 'google', 'meta', 'anthropic', 'microsoft', 'nvidia', 'tesla', 'apple', 'amazon', 'ibm', 'baidu', 'deepmind', 'hugging face', 'stability ai'],
    'AI Products': ['launch', 'release', 'beta', 'model', 'api', 'platform', 'framework', 'library', 'tool', 'service', 'update', 'feature', 'gpu', 'chip', 'hardware'],
    'Creator Economy': ['art', 'music', 'video', 'image', 'generate', 'creative', 'creator', 'artist', 'design', 'diffusion', 'stable diffusion', 'midjourney', 'dall-e', 'sora', 'suno', 'udio'],
    'Generative AI': ['generator', 'generative', 'text-to-image', 'text-to-video', 'diffusion', 'gan', 'synthesis', 'synthetic', 'deepfake', 'style transfer'],
    'AI Business News': ['funding', 'business', 'investment', 'market', 'strategy', 'competition', 'partnership', 'acquisition', 'stock', 'earnings', 'startup', 'venture capital', 'ipo'],
    'AI Research & Methods': ['research', 'paper', 'study', 'breakthrough', 'arxiv', 'neurips', 'icml', 'cvpr', 'scientific', 'discovery', 'publish', 'journal', 'neural network', 'transformer', 'cnn', 'rnn', 'reinforcement learning', 'pytorch', 'tensorflow', 'jax', 'algorithm', 'architecture', 'training', 'inference'],
    'AI in Practice': ['healthcare', 'finance', 'automotive', 'retail', 'manufacturing', 'logistics', 'energy', 'legal', 'education', 'pharma', 'drug discovery', 'use case', 'implementation', 'deployment', 'solution'],
    'AI Ethics & Policy': ['ethics', 'bias', 'risk', 'safety', 'regulation', 'job', 'privacy', 'agi', 'alignment', 'doom', 'existential', 'responsible ai', 'fairness', 'policy', 'governance', 'transparency'],
    'Weird': ['strange', 'unusual', 'weird', 'odd', 'curious', 'bizarre', 'unexpected', 'surprising', 'funny', 'humor', 'meme'],
    'Trending Now': ['ai', 'artificial intelligence', 'gpt', 'llm'] # Catch-all / high-level terms
}

# Define keywords that strongly suggest a 'Trending Now' priority
TRENDING_KEYWORDS = ['exclusive', 'breaking', 'leak', 'major', 'significant']

# --- Helper Functions ---

def rewrite_headline(title, max_words=MAX_HEADLINE_WORDS):
    """Rewrites headline to be punchy: uppercase, limited words."""
    words = title.split()
    # Simple truncation
    rewritten = " ".join(words[:max_words])
    if len(words) > max_words:
        rewritten += "..."
    return rewritten.upper()

def categorize_headline(title, url, source=None):
    """Attempts to categorize headline based on keywords or source, aligning with project brief categories."""
    title_lower = title.lower()

    # 1. Prioritize Company Blogs/Sources for 'AI Companies' Category
    # Expanded list based on common AI players
    company_sources_or_keywords = ['openai', 'google ai', 'meta ai', 'anthropic', 'microsoft research', 'nvidia blog', 'deepmind']
    if source and any(cs.lower() in source.lower() for cs in company_sources_or_keywords):
        # Check if title also mentions business terms, otherwise default to AI Companies
        business_kws = CATEGORY_KEYWORDS['AI Business News']
        if any(kw in title_lower for kw in business_kws):
            return 'AI Business News'
        return 'AI Companies'

    # 2. Check for specific company names in the title itself
    if any(company in title_lower for company in CATEGORY_KEYWORDS['AI Companies']):
         # Check if title also mentions business terms, otherwise default to AI Companies
        business_kws = CATEGORY_KEYWORDS['AI Business News']
        if any(kw in title_lower for kw in business_kws):
            return 'AI Business News'
        return 'AI Companies'

    # 3. Check for specific trending keywords first
    if any(kw in title_lower for kw in TRENDING_KEYWORDS):
        return 'Trending Now'

    # 4. Iterate through other categories based on keywords (order matters)
    for category, keywords in CATEGORY_KEYWORDS.items():
        # Skip AI Companies as it was handled above, skip Trending Now default
        if category in ['AI Companies', 'Trending Now']:
            continue
        if any(keyword in title_lower for keyword in keywords):
            return category

    # 5. Default category if no keywords match
    # Using 'Trending Now' as the catch-all for general AI news if nothing else fits
    return 'Trending Now'

def get_prompt_of_the_day():
    """Generates a structured placeholder prompt of the day."""
    # In a real scenario, this could be fetched from a database, generated by an AI, or curated
    prompts = [
        {
            "title": "Generate Viral Video Hooks",
            "text": "Create 5 short, punchy video hooks (under 10 seconds each) designed to go viral on TikTok/Reels, promoting a fictional new AI-powered tool that instantly summarizes complex research papers.",
            "platforms": ["ChatGPT", "Claude", "Gemini", "Perplexity"] # Added Perplexity
        },
        {
            "title": "Futuristic Cityscape Image Concept",
            "text": "Describe the visual elements for an image depicting a futuristic cityscape where organic architecture blends seamlessly with advanced technology. Focus on contrasting textures (bioluminescent flora vs. sleek metal) and the overall mood (utopian tranquility vs. underlying tension).",
            "platforms": ["Midjourney", "Stable Diffusion", "DALL-E"]
        },
        {
            "title": "AI Develops Humor Story Idea",
            "text": "Outline a short story (3-5 key plot points) about a domestic service robot that unexpectedly develops a sarcastic sense of humor after a software update glitch. Explore the owner's reaction and the potential complications.",
            "platforms": ["ChatGPT", "Claude", "Character.ai", "Perplexity"] # Added Perplexity
        },
        {
            "title": "Sustainable AI Startup Logo Concept",
            "text": "Generate 3 distinct logo concepts for a startup called 'EcoMind AI' that focuses on energy-efficient artificial intelligence. Each concept should visually represent both 'ecology' and 'intelligence' in a minimalist style.",
            "platforms": ["Ideogram", "Midjourney", "LogoAI"]
        },
        {
            "title": "AI Lo-Fi Track Composition Task",
            "text": "Compose a prompt for an AI music generator to create a 1-minute lo-fi hip-hop track suitable for focused work. Specify desired instrumentation (e.g., mellow piano chords, soft synth pads, subtle vinyl crackle), tempo (e.g., 70-80 BPM), and overall mood (e.g., calm, nostalgic, slightly melancholic).",
            "platforms": ["Suno", "Udio", "AIVA"]
        }
    ]
    # Simple rotation based on day of the year
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return prompts[day_of_year % len(prompts)]

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
    """Fetches and processes articles from NewsAPI with enhanced logging."""
    
    # Log if the API key is missing right at the start
    if not NEWS_API_KEY:
        print("LOG: NEWS_API_KEY is not set. Skipping NewsAPI fetch.")
        return []

    print(f"LOG: NEWS_API_KEY is present (partially masked): {NEWS_API_KEY[:4]}...{NEWS_API_KEY[-4:]}")

    headlines = []
    base_url = "https://newsapi.org/v2/everything"
    params = {
        'q': NEWS_API_QUERY,
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt', # Get latest articles first
        'pageSize': MAX_NEWS_API_ARTICLES,
        'domains': 'economist.com,nytimes.com,wsj.com,ft.com,technologyreview.com,wired.com,theverge.com,techcrunch.com,reuters.com,bloomberg.com' # Added major news domains
    }

    # Construct the full URL for logging (mask API key)
    log_params = params.copy()
    log_params['apiKey'] = '***MASKED***'
    request_url = base_url + '?' + requests.compat.urlencode(log_params)
    print(f"LOG: Attempting to fetch from NewsAPI URL: {request_url}")

    try:
        response = requests.get(base_url, params=params, timeout=15) # Added timeout
        
        # Log status code immediately
        print(f"LOG: NewsAPI response status code: {response.status_code}")
        
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        articles = data.get('articles', [])
        total_articles_received = len(articles)
        print(f"LOG: Successfully received {total_articles_received} articles from NewsAPI before internal filtering.")

        # Updated keywords for internal filtering - more inclusive
        title_keywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'gpt', 'llm', 'openai', 'anthropic', 'google', 'meta', 'microsoft', 'nvidia', 'intelligence', 'technology', 'research', 'innovation']
        print(f"LOG: Internal title filter keywords: {title_keywords}")

        articles_kept = 0
        for i, article in enumerate(articles):
            title = article.get('title', 'No Title') # Get title early
            title_lower = title.lower()
            url = article.get('url', '#')
            source_name = article.get('source', {}).get('name', 'Unknown Source') # Get source name if available

            # Check for excluded sites
            if any(excluded_site in url.lower() for excluded_site in EXCLUDED_SITES):
                print(f"LOG: Skipping article {i+1}/{total_articles_received}: URL '{url}' is from excluded site.")
                continue

            # Check for low-quality URL patterns
            if any(pattern in url.lower() for pattern in LOW_QUALITY_URL_PATTERNS):
                print(f"LOG: Skipping article {i+1}/{total_articles_received}: URL '{url}' matches low-quality pattern.")
                continue

            # New: Check for negative keywords first
            if any(neg_keyword in title_lower for neg_keyword in NEGATIVE_KEYWORDS):
                print(f"LOG: Skipping article {i+1}/{total_articles_received}: Title '{title}' contains negative keyword.")
                continue # Skip this article

            # Check for positive keywords (existing check)
            if not any(kw in title_lower for kw in title_keywords):
                 print(f"LOG: Skipping article {i+1}/{total_articles_received}: Title '{title}' missing required positive keywords.")
                 continue # Skip this article

            # Check for potentially problematic non-English characters sometimes returned
            try:
                article_title = article.get('title', 'No Title')
                # Attempt to encode/decode to catch potential issues early
                article_title.encode('utf-8').decode('utf-8') 
                
                # Add language detection
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
                    'source': f'NewsAPI ({source_name})', # Include original source name
                    'published_date_obj': parse_publish_date(article.get('publishedAt'))
                }
                headlines.append(headline_data)
                articles_kept += 1
                # Print the kept headline
                print(f"LOG: Kept NewsAPI Headline: {headline_data['title']} ({headline_data['url']})") 
            except UnicodeEncodeError as ue_error:
                print(f"LOG: Skipping article {i+1}/{total_articles_received} due to encoding error in title: {ue_error}")
                continue

        print(f"LOG: Kept {articles_kept} articles from NewsAPI after internal filtering.")

    except requests.exceptions.Timeout:
        print("ERROR: Request to NewsAPI timed out.")
    except requests.exceptions.HTTPError as http_err:
        print(f"ERROR: HTTP error occurred with NewsAPI: {http_err}")
        # Try to get more details from the response body if available
        try:
            error_details = response.json()
            print(f"ERROR Details: {json.dumps(error_details, indent=2)}")
        except json.JSONDecodeError:
            print(f"ERROR Details: Could not parse error response body. Raw text: {response.text}")
        except Exception as e:
             print(f"ERROR: Could not extract error details: {e}. Raw text: {response.text}")
    except requests.exceptions.RequestException as e:
        # Catch other request-related errors (DNS, connection, etc.)
        print(f"ERROR: Error during NewsAPI request: {e}")
    except json.JSONDecodeError as json_err:
        print(f"ERROR: Could not decode JSON response from NewsAPI: {json_err}")
        print(f"Raw response text: {response.text}")
    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"ERROR: An unexpected error occurred processing NewsAPI data: {e}")
        # Include traceback for unexpected errors
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

def fetch_perplexity_results(max_results=10):
    """Fetches and processes search results from Perplexity API."""
    if not PERPLEXITY_API_KEY:
        return []

    headlines = []
    url = "https://api.perplexity.ai/chat/completions"
    
    # Simplify payload
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI news aggregator. Find recent top news articles about AI. Format your response strictly as a JSON array where each object has a 'title' and a 'url' key. Do not include any introductory text, explanations, or markdown formatting outside of the JSON itself. For example: [{\"title\": \"Example Title\", \"url\": \"https://example.com\"}]"
            },
            {
                "role": "user",
                # Simplified user message, reinforcing JSON output
                "content": f"Top recent news about: {NEWS_API_QUERY}. Respond only with the JSON array of articles."
            }
        ]
        # Completely removed response_format key
    }
    
    # Ensure the key is treated as a string
    api_key_str = str(PERPLEXITY_API_KEY) 
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + api_key_str # Use the explicitly converted string
    }

    try:
        # DEBUG: Print the header before sending (key will be masked in logs)
        print(f"DEBUG: Sending Perplexity Header: {headers.get('Authorization')}") 
        
        print("Fetching from Perplexity API...")
        response = requests.post(url, json=payload, headers=headers)
        
        # Try to parse JSON, but if it fails, print the raw text
        try:
            data = response.json()
        except json.JSONDecodeError as jd_error:
            print(f"Error: Could not decode JSON directly from Perplexity response. Status Code: {response.status_code}")
            print(f"Raw Perplexity response text: {response.text}")
            # If JSON decoding fails, we can't proceed with the expected data structure.
            # We should raise for status to catch underlying HTTP errors, or return if it's a 2xx but not JSON.
            response.raise_for_status() 
            return headlines # Return empty or previously gathered headlines

        response.raise_for_status()  # Raise an exception for bad status codes if JSON parsing was okay
        
        # Attempt to parse the content if the response is structured as expected
        if 'choices' in data and data['choices']:
             message_content = data['choices'][0]['message']['content']
             try:
                 # Try parsing the JSON string within the content
                 extracted_data = json.loads(message_content)
                 # Assuming the extracted_data is a list of {'title': '...', 'url': '...'}
                 if isinstance(extracted_data, list):
                     count = 0
                     for item in extracted_data:
                         if 'title' in item and 'url' in item:
                             headlines.append({
                                 'title': item['title'],
                                 'url': item['url'],
                                 'source': 'Perplexity',
                                 'published_date_obj': parse_publish_date(datetime.datetime.now())
                             })
                             count += 1
                     print(f"Successfully extracted {count} headlines from Perplexity.")
                 elif isinstance(extracted_data, dict) and 'headlines' in extracted_data and isinstance(extracted_data['headlines'], list):
                      # Alternative structure check: {'headlines': [...]}
                      count = 0
                      for item in extracted_data['headlines']:
                         if 'title' in item and 'url' in item:
                             headlines.append({
                                 'title': item['title'],
                                 'url': item['url'],
                                 'source': 'Perplexity',
                                 'published_date_obj': parse_publish_date(datetime.datetime.now())
                             })
                             count += 1
                      print(f"Successfully extracted {count} headlines from Perplexity (nested structure).")
                 else:
                     print("Perplexity response content (after parsing message_content) was not the expected list or dict of headlines.")
                     print(f"Parsed message content from Perplexity: {extracted_data}") # Log what was parsed
                     
             except json.JSONDecodeError:
                 print(f"Error: Could not decode JSON from Perplexity message content.")
                 print(f"Raw message content from Perplexity: {message_content}") # Print the message_content that failed to parse
             except Exception as e:
                print(f"Error processing Perplexity response content: {e}")
        else:
            print("Perplexity API response did not contain expected 'choices'.")
            print(f"Full Perplexity response data: {data}") # Log the data if choices are missing


    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Perplexity API: {e}")
        # Check if response object exists before accessing it
        if 'response' in locals() and response is not None:
             try:
                 print(f"Response status code: {response.status_code}")
                 # Try to print the full response text for more detailed errors
                 print(f"Response text from RequestException: {response.text}") 
             except Exception as print_e:
                 print(f"Error printing response details: {print_e}")
    except Exception as e:
        print(f"An unexpected error occurred processing Perplexity API data: {e}")

    return headlines

# --- Main Pipeline ---

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
    perplexity_results = fetch_perplexity_results() # Fetch Perplexity results

    # Combine all sources
    all_headlines = news_headlines + rss_headlines + reddit_posts + perplexity_results
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
    prompt_data = get_prompt_of_the_day()

    # 5. Render template
    env = Environment(
        loader=FileSystemLoader('templates/'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Add custom filter for date formatting
    env.filters['datetime_format'] = datetime_format
    
    env.globals['current_year'] = datetime.datetime.now().year
    env.globals['prompt_of_the_day'] = prompt_data.get('prompt_of_the_day') # Corrected: was a tuple
    env.globals['all_keyword_pages_config'] = keyword_config.get('keyword_pages', {}) # Make all_keyword_pages_config available globally

    # --- ADDED: Define keyword_pages_data ---
    keyword_pages_data = generate_keyword_pages_data(unique_headlines)

    # Generate keyword page files FIRST
    # Ensure output_dir is defined if not already (it was at the top of generate_keyword_page_files previously)
    output_dir = "."
    generate_keyword_page_files(keyword_pages_data, env, prompt_data) # Pass prompt_data directly

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
        'prompt_of_the_day': prompt_data, # Pass the full prompt_data object
        # 'category_descriptions': prompt_data.get('category_descriptions', {}), # This was in prompt_data, not separate
        'yesterday_date': yesterday_date_str,
        'tomorrow_date': tomorrow_date_str,
        'is_keyword_page': False,
        'is_main_page': True,
        'current_year': current_year_for_render,
        'all_keyword_pages_config': keyword_config.get('keyword_pages', {}) 
    }

    # Render template with data for index.html
    rendered_html = template.render(main_page_context)

    # 6. Save to dated archive file
    archive_filename = os.path.join(archive_dir, f"{current_date_for_render}.html")
    try:
        archive_page_context = main_page_context.copy()
        archive_page_context['canonical_path'] = f"/archive/{current_date_for_render}.html"
        archive_page_context['is_main_page'] = False
        
        archive_html = template.render(archive_page_context)
        
        with open(archive_filename, 'w', encoding='utf-8') as f:
            f.write(archive_html)
        print(f"Successfully saved archive to {archive_filename}")
    except IOError as e:
        print(f"Error writing archive file {archive_filename}: {e}")

    # 7. Save the same output as index.html for the latest view
    latest_filename = "index.html"
    newly_published_urls_for_this_run = set() 
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

    end_time = datetime.datetime.now()
    print(f"Aggregation finished in {(end_time - start_time).total_seconds():.2f} seconds.")

if __name__ == "__main__":
    main() 
