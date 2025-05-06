import requests
import feedparser
import os
import datetime
import praw # Added for Reddit API
from jinja2 import Environment, FileSystemLoader
import json # Added for Perplexity JSON handling
import re # Added for footer update regex
from langdetect import detect, LangDetectException # Added for language detection

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

# Updated Subreddits list but keep the ones the user wants
SUBREDDITS = [
    "artificial", "LargeLanguageModels", "LocalLLaMA", "singularity", "MachineLearning", # Original
    "chatgpt", "claudeai", "characterai", "openai", "artificialintelligence",
    "ai_agents", "StableDiffusion", "AIArt" # Added by user
]
MAX_REDDIT_POSTS_PER_SUB = 2 # Keep the reduced number
REDDIT_TIME_FILTER = 'day' # Restore this constant

NEWS_API_QUERY = 'ai OR "artificial intelligence" OR gpt OR llm OR "machine learning" OR openai OR anthropic OR claude OR sam altman OR google ai OR meta ai'
MAX_NEWS_API_ARTICLES = 100 # Number of articles to fetch from NewsAPI (Increased from 25)
MAX_HEADLINE_WORDS = 8

# Add these new constants
MAX_RSS_ENTRIES_PER_SOURCE = 3  # Limit RSS entries per source (Updated from 5 to 3)
RSS_CUTOFF_DAYS = 2  # Only include RSS entries from the last 2 days (Changed from 7)

RSS_FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Anthropic": "https://www.anthropic.com/rss/",  # Updated URL
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Meta AI": "https://ai.meta.com/blog/rss/",
    # New RSS feeds
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

# --- Data Fetching Functions ---

def fetch_reddit_posts():
    """Fetches recent posts from specified subreddits."""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        print("Skipping Reddit fetch due to missing API credentials.")
        return []

    all_headlines = []
    print(f"Fetching Reddit posts from {len(SUBREDDITS)} subreddits...")
    
    try:
        # Initialize Reddit API client
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        for sub_name in SUBREDDITS:
            try:
                print(f"Getting posts from r/{sub_name}...")
                
                # Fetch hot posts from the subreddit
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
                        'source': f"Reddit r/{sub_name}"
                    })
                    added_count += 1
                    
                    # Stop if we've hit our limit for this subreddit
                    if added_count >= MAX_REDDIT_POSTS_PER_SUB:
                        break
                
                print(f"  - Added {added_count} posts from r/{sub_name}")
                
            except Exception as e:
                print(f"Error fetching posts from r/{sub_name}: {e}")
                
    except Exception as e:
        print(f"Error initializing Reddit API: {e}")
    
    print(f"Fetched {len(all_headlines)} total posts from Reddit.")
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
        'pageSize': MAX_NEWS_API_ARTICLES
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

        # Define the keywords for internal filtering
        title_keywords = ['ai', 'gpt', 'llm', 'prompt', 'claude', 'openai', 'anthropic', 'google', 'meta', 'tool']
        print(f"LOG: Internal title filter keywords: {title_keywords}")

        articles_kept = 0
        for i, article in enumerate(articles):
            title_lower = article.get('title', '').lower()
            url = article.get('url', '#')
            source_name = article.get('source', {}).get('name', 'Unknown Source') # Get source name if available

            # Check for keywords
            if not any(kw in title_lower for kw in title_keywords):
                 print(f"LOG: Skipping article {i+1}/{total_articles_received}: Title '{article.get('title', 'N/A')}' missing required keywords.")
                 continue # Skip this article

            # Check for potentially problematic non-English characters sometimes returned
            try:
                article_title = article.get('title', 'No Title')
                # Attempt to encode/decode to catch potential issues early
                article_title.encode('utf-8').decode('utf-8') 
                
                # Create the headline dictionary
                headline_data = {
                    'title': article_title,
                    'url': url,
                    'source': f'NewsAPI ({source_name})' # Include original source name
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
                print(f"No entries found for {source}.")
                continue

            print(f"Successfully fetched {len(feed.entries)} entries from {source}.")
            
            # Apply source-specific limits
            source_limit = MAX_RSS_ENTRIES_PER_SOURCE
            
            # Special handling for Google AI - limit to only 1 entry
            if source == "Google AI":
                source_limit = 1
                print(f"  - Note: Applying stricter limit (1) for Google AI feed")
                
            entry_count = 0
            for entry in feed.entries:
                # Stop if we've reached the limit for this source
                if entry_count >= source_limit:
                    break
                    
                title = entry.get('title', 'No Title')
                link = entry.get('link', '#')

                # Language detection
                try:
                    if title and title != 'No Title':
                        lang = detect(title)
                        if lang != 'en':
                            print(f"  - Skipping non-English entry (lang: {lang}): {title[:50]}...")
                            continue
                    else: # If title is empty or 'No Title', skip it.
                        print(f"  - Skipping entry with no valid title from {source}.")
                        continue
                except LangDetectException:
                    # If language detection fails (e.g., title is too short, ambiguous, or not text)
                    # We can choose to skip it or allow it. For now, let's skip to be safe.
                    print(f"  - Skipping entry due to language detection error (possibly too short/ambiguous): {title[:50]}...")
                    continue
                
                # Try to get the published date
                try:
                    if 'published_parsed' in entry and entry.published_parsed:
                        # Convert time tuple to datetime
                        pub_date = datetime.datetime(*entry.published_parsed[:6])
                        # Skip entries older than the cutoff date
                        if pub_date < cutoff_date:
                            print(f"  - Skipping old entry: {title[:30]}... (published {pub_date.strftime('%Y-%m-%d')})")
                            continue
                except (AttributeError, ValueError) as e:
                    # If we can't parse the date, assume it's recent
                    print(f"  - Warning: Couldn't parse date for entry: {title[:30]}... - {e}")
                
                all_entries.append({'title': title, 'url': link, 'source': source})
                entry_count += 1
                
            print(f"  - Added {entry_count} recent entries from {source} (limit: {source_limit}).")
                
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
                "content": "You are an AI news aggregator. Find recent top news articles about AI."
            },
            {
                "role": "user",
                # Simplified user message
                "content": f"Top recent news about: {NEWS_API_QUERY}"
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
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
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
                                 'source': 'Perplexity'
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
                                 'source': 'Perplexity'
                             })
                             count += 1
                      print(f"Successfully extracted {count} headlines from Perplexity (nested structure).")
                 else:
                     print("Perplexity response content was not the expected list of headlines.")
                     # Optionally, print the raw content for debugging:
                     # print(f"Raw content from Perplexity: {message_content}")
                     
             except json.JSONDecodeError:
                 print(f"Error: Could not decode JSON from Perplexity response content.")
                 # print(f"Raw content from Perplexity: {message_content}")
             except Exception as e:
                print(f"Error processing Perplexity response content: {e}")
        else:
            print("Perplexity API response did not contain expected choices.")
            # print(f"Full Perplexity response: {data}")


    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Perplexity API: {e}")
        # Check if response object exists before accessing it
        if 'response' in locals() and response is not None:
             try:
                 print(f"Response status code: {response.status_code}")
                 # Try to print the full response text for more detailed errors
                 print(f"Response text: {response.text}") 
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

    # 1. Fetch data
    news_headlines = fetch_newsapi_articles()
    rss_headlines = fetch_rss_entries()
    reddit_posts = fetch_reddit_posts() # Fetch Reddit posts
    perplexity_results = fetch_perplexity_results() # Fetch Perplexity results

    # Combine all sources
    all_headlines = news_headlines + rss_headlines + reddit_posts + perplexity_results
    print(f"Total headlines fetched before deduplication: {len(all_headlines)}")

    # 2. Deduplicate by URL
    unique_headlines_by_url = []
    seen_urls = set()
    for item in all_headlines:
        if item['url'] and item['url'] not in seen_urls:
            unique_headlines_by_url.append(item)
            seen_urls.add(item['url'])
        elif not item['url']:
             print(f"Warning: Headline '{item['title'][:50]}...' has no URL, skipping.")
    print(f"Headlines after URL deduplication: {len(unique_headlines_by_url)}")

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
    categorized_data = {cat: [] for cat in CATEGORIES}
    for item in unique_headlines: # This `unique_headlines` is now the result of all deduplication steps
        # item['rewritten_title'] is already generated
        category = categorize_headline(item['title'], item['url'], item.get('source'))
        if category in categorized_data:
            categorized_data[category].append(item)
        else:
            print(f"Warning: Categorization resulted in unknown category '{category}' for title: {item['title']}")
            if 'Trending Now' in categorized_data:
                 categorized_data['Trending Now'].append(item)

    # 4. Get Prompt of the Day
    prompt_data = get_prompt_of_the_day()

    # 5. Render template
    env = Environment(loader=FileSystemLoader('.'))
    
    # Add custom filter for date formatting
    def datetime_format(value, format="%B %d, %Y"):
        """Format a date string YYYY-MM-DD as Month DD, YYYY"""
        try:
            date_obj = datetime.datetime.strptime(value, "%Y-%m-%d")
            return date_obj.strftime(format)
        except (ValueError, TypeError):
            return value
    
    env.filters['datetime_format'] = datetime_format
    
    # Use the main template again
    template = env.get_template('template.html')
    
    # Calculate dates for navigation
    yesterday_date_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # Render template with data
    rendered_html = template.render(
        update_time=datetime.datetime.now().strftime("%Y-%m-%d"),
        canonical_path="/",
        categories=categorized_data,
        prompt_of_the_day=prompt_data,
        yesterday_date=yesterday_date_str,
        tomorrow_date=tomorrow_date_str
    )

    # 6. Save to dated archive file
    archive_filename = os.path.join(archive_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.html")
    try:
        # For the archive page, render with its own canonical path
        archive_html = template.render(
            update_time=datetime.datetime.now().strftime("%Y-%m-%d"),
            canonical_path=f"/archive/{datetime.datetime.now().strftime('%Y-%m-%d')}.html",  # Archive-specific canonical path
            categories=categorized_data,
            prompt_of_the_day=prompt_data,
            yesterday_date=yesterday_date_str,
            tomorrow_date=tomorrow_date_str
        )
        
        with open(archive_filename, 'w', encoding='utf-8') as f:
            f.write(archive_html)
        print(f"Successfully saved archive to {archive_filename}")
    except IOError as e:
        print(f"Error writing archive file {archive_filename}: {e}")

    # 7. Save the same output as index.html for the latest view
    latest_filename = "index.html"
    try:
        with open(latest_filename, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"Successfully updated {latest_filename}")
    except IOError as e:
        print(f"Error writing latest file {latest_filename}: {e}")
    
    # 8. Fill in any missing dates in the archive
    try:
        # Get existing archive files
        existing_archives = [f.replace('.html', '') for f in os.listdir(archive_dir) 
                            if f.endswith('.html') and f != 'index.html']
        
        if existing_archives:
            # Get the earliest and latest dates
            date_format = "%Y-%m-%d"
            archive_dates = [datetime.datetime.strptime(date, date_format) for date in existing_archives]
            earliest_date = min(archive_dates)
            latest_date = max(archive_dates)
            
            # Check for missing dates in between
            print("Checking for missing dates in the archive...")
            current_date = earliest_date
            missing_dates = []
            
            while current_date <= latest_date:
                date_str = current_date.strftime(date_format)
                if date_str not in existing_archives:
                    missing_dates.append(date_str)
                current_date += datetime.timedelta(days=1)
            
            if missing_dates:
                print(f"Found {len(missing_dates)} missing dates: {', '.join(missing_dates)}")
                
                # Create the missing archive files
                for missing_date in missing_dates:
                    # Create a basic archive for the missing date with a note
                    missing_date_obj = datetime.datetime.strptime(missing_date, date_format)
                    formatted_date = missing_date_obj.strftime("%B %d, %Y")
                    
                    # Prepare template data for the missing date
                    missing_prompt = get_prompt_of_the_day()  # Get a prompt for the day
                    missing_categories = {'Trending Now': [
                        {'url': '#', 'rewritten_title': 'NO DATA AVAILABLE FOR THIS DATE'},
                        {'url': '#', 'rewritten_title': 'ARCHIVE PLACEHOLDER - AUTOMATICALLY GENERATED'}
                    ]}
                    
                    # Render the template
                    missing_html = template.render(
                        categories=missing_categories,
                        prompt_of_the_day=missing_prompt,
                        update_time=missing_date
                    )
                    
                    # Save the missing date file
                    missing_filename = os.path.join(archive_dir, f"{missing_date}.html")
                    with open(missing_filename, 'w', encoding='utf-8') as f:
                        f.write(missing_html)
                    print(f"Created placeholder archive for {missing_date}")
            else:
                print("No missing dates found in the archive.")
    except Exception as e:
        print(f"Error checking for missing dates: {e}")
    
    # 9. Update the archive index page
    print("Updating archive index page...")
    try:
        # Get all archive files
        archive_files = sorted([f for f in os.listdir(archive_dir) if f.endswith('.html') and f != 'index.html'], reverse=True)
        
        # Create archive index template data
        archive_list = []
        for archive_file in archive_files:
            date_str = archive_file.replace('.html', '')
            # Format the date for display (YYYY-MM-DD to Month DD, YYYY)
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%B %d, %Y")
            except ValueError:
                formatted_date = date_str
            archive_list.append({"filename": archive_file, "display_date": formatted_date})
        
        # Render archive index template
        archive_index_template = env.get_template('archive_index_template.html')
        archive_index_html = archive_index_template.render(archive_list=archive_list)
        
        # Save archive index
        with open(os.path.join(archive_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(archive_index_html)
        print("Successfully updated archive index")
        
        # --- Start Replacement Block ---
        # Get the 5 most recent archive files (assuming archive_files is available)
        if 'archive_files' in locals() and archive_files:
            recent_archives = archive_files[:5]
            
            # Create the HTML for recent archive links
            archive_links_html = '\n                '.join([
                f'<a href="archive/{archive_file}">{archive_file.replace(".html", "")}' 
                for archive_file in recent_archives
            ])
            
            # Replace ONLY the placeholder in the already rendered HTML
            # 'rendered_html' holds the result from template.render() before it's first written
            final_rendered_html = rendered_html.replace('<!-- ARCHIVE_LINKS_PLACEHOLDER -->', archive_links_html)

            # Save the final version with replaced links to index.html
            try:
                with open(latest_filename, 'w', encoding='utf-8') as f:
                    f.write(final_rendered_html) # Write the final version
                print(f"Successfully updated recent archives in {latest_filename} footer")
            except IOError as e:
                print(f"Error writing updated {latest_filename} file: {e}")
        else:
             print("Skipping footer archive links update (no archive files found).")
             # If no archives, write the original rendered_html anyway
             try:
                with open(latest_filename, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                print(f"Successfully wrote {latest_filename} without footer update.")
             except IOError as e:
                print(f"Error writing {latest_filename} file: {e}")
        # --- End Replacement Block ---
            
    except Exception as e:
        print(f"Error processing archive files or updating footer: {e}")

    end_time = datetime.datetime.now()
    print(f"Aggregation finished in {(end_time - start_time).total_seconds():.2f} seconds.")

if __name__ == "__main__":
    main() 
