#!/usr/bin/env python3
"""
RSS Feed Generator for SaaS Flash Report
Generates a comprehensive RSS 2.0 feed from the site's content data.
"""

import json
import os
import datetime
from xml.sax.saxutils import escape

def load_config():
    """Load site configuration from config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "site_name": "SaaS Flash Report",
            "domain": "saasflashreport.com",
            "tagline": "Software Intelligence, Business Speed",
            "meta_description": "Real-time SaaS intelligence for software executives, product managers, and B2B professionals."
        }

def load_content_data():
    """Load content from data/main_page_content.json and topic_archives"""
    all_stories = []
    
    # Load main page content (most recent)
    main_content_path = 'data/main_page_content.json'
    if os.path.exists(main_content_path):
        try:
            with open(main_content_path, 'r', encoding='utf-8') as f:
                main_content = json.load(f)
                
            # Flatten all categories into a single list
            for category, stories in main_content.items():
                for story in stories:
                    story['category'] = category
                    all_stories.append(story)
                    
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading main content: {e}")
    
    # If main content is empty, load from topic archives as fallback
    if not all_stories:
        topic_archives_dir = 'topic_archives'
        if os.path.exists(topic_archives_dir):
            for filename in os.listdir(topic_archives_dir):
                if filename.endswith('_stories.json'):
                    category = filename.replace('_stories.json', '').replace('-', ' ').title()
                    try:
                        with open(os.path.join(topic_archives_dir, filename), 'r', encoding='utf-8') as f:
                            stories = json.load(f)
                            # Take only the most recent 10 stories from each category
                            for story in stories[:10]:
                                story['category'] = category
                                all_stories.append(story)
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f"Error loading {filename}: {e}")
    
    # Sort by publication date (most recent first)
    all_stories.sort(key=lambda x: x.get('published_date_obj', ''), reverse=True)
    
    # Return only the most recent 50 stories for RSS feed
    return all_stories[:50]

def format_rfc822_date(date_string):
    """Convert date string to RFC822 format for RSS"""
    try:
        # Parse the date string (assumes YYYY-MM-DD format)
        date_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        # Convert to RFC822 format (e.g., "Mon, 01 Jul 2025 00:00:00 +0000")
        return date_obj.strftime('%a, %d %b %Y %H:%M:%S +0000')
    except (ValueError, TypeError):
        # Fallback to current date if parsing fails
        return datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

def generate_rss_feed():
    """Generate RSS 2.0 feed"""
    print("🔄 Generating RSS feed...")
    
    # Load configuration and content
    config = load_config()
    stories = load_content_data()
    
    if not stories:
        print("⚠️  No content found for RSS feed")
        return False
    
    # Build RSS feed URL
    base_url = f"https://{config['domain']}"
    rss_url = f"{base_url}/rss.xml"
    
    # Generate current date for feed metadata
    current_date = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Start building RSS XML
    rss_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss_content += '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
    rss_content += '  <channel>\n'
    
    # Channel metadata
    rss_content += f'    <title>{escape(config["site_name"])}</title>\n'
    rss_content += f'    <link>{base_url}</link>\n'
    rss_content += f'    <description>{escape(config["meta_description"])}</description>\n'
    rss_content += f'    <language>en-us</language>\n'
    rss_content += f'    <lastBuildDate>{current_date}</lastBuildDate>\n'
    rss_content += f'    <pubDate>{current_date}</pubDate>\n'
    rss_content += f'    <managingEditor>editor@{config["domain"]} ({config["site_name"]})</managingEditor>\n'
    rss_content += f'    <webMaster>webmaster@{config["domain"]} ({config["site_name"]})</webMaster>\n'
    rss_content += f'    <generator>SaaS Flash Report RSS Generator</generator>\n'
    rss_content += f'    <category>Technology/Software/SaaS</category>\n'
    rss_content += f'    <ttl>60</ttl>\n'  # Update every hour
    rss_content += f'    <atom:link href="{rss_url}" rel="self" type="application/rss+xml" />\n'
    
    # Add channel image
    rss_content += f'    <image>\n'
    rss_content += f'      <url>{base_url}/favicon.svg</url>\n'
    rss_content += f'      <title>{escape(config["site_name"])}</title>\n'
    rss_content += f'      <link>{base_url}</link>\n'
    rss_content += f'      <width>32</width>\n'
    rss_content += f'      <height>32</height>\n'
    rss_content += f'    </image>\n'
    
    # Add items
    for story in stories:
        title = story.get('rewritten_title') or story.get('title', 'Untitled')
        url = story.get('url', '')
        source = story.get('source', 'Unknown')
        category = story.get('category', 'SaaS News')
        pub_date = format_rfc822_date(story.get('published_date_obj'))
        
        # Create a unique GUID for each item
        guid = f"{config['domain']}-{abs(hash(url))}"
        
        # Create description
        description = f"Latest {category.lower()} news from {source}. "
        description += f"Read the full article at {source}."
        
        rss_content += f'    <item>\n'
        rss_content += f'      <title>{escape(title)}</title>\n'
        rss_content += f'      <link>{escape(url)}</link>\n'
        rss_content += f'      <description>{escape(description)}</description>\n'
        rss_content += f'      <category>{escape(category)}</category>\n'
        rss_content += f'      <source url="{escape(url)}">{escape(source)}</source>\n'
        rss_content += f'      <pubDate>{pub_date}</pubDate>\n'
        rss_content += f'      <guid isPermaLink="false">{guid}</guid>\n'
        rss_content += f'    </item>\n'
    
    # Close RSS
    rss_content += '  </channel>\n'
    rss_content += '</rss>'
    
    # Write RSS file
    try:
        with open('rss.xml', 'w', encoding='utf-8') as f:
            f.write(rss_content)
        
        print(f"✅ RSS feed generated successfully!")
        print(f"   📄 File: rss.xml")
        print(f"   📊 Items: {len(stories)} stories")
        print(f"   🔗 URL: {rss_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing RSS file: {e}")
        return False

def validate_rss_feed():
    """Basic validation of the generated RSS feed"""
    if not os.path.exists('rss.xml'):
        print("❌ RSS file not found")
        return False
    
    try:
        with open('rss.xml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic validation checks
        checks = [
            ('XML declaration', '<?xml version="1.0"' in content),
            ('RSS root element', '<rss version="2.0"' in content),
            ('Channel element', '<channel>' in content),
            ('Title element', '<title>' in content),
            ('Items present', '<item>' in content),
            ('Valid closing', '</rss>' in content)
        ]
        
        all_valid = True
        print("🔍 RSS Feed Validation:")
        for check_name, is_valid in checks:
            status = "✅" if is_valid else "❌"
            print(f"   {status} {check_name}")
            if not is_valid:
                all_valid = False
        
        if all_valid:
            print("🎉 RSS feed validation passed!")
        else:
            print("⚠️  RSS feed has validation issues")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error validating RSS feed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = generate_rss_feed()
        if success:
            validate_rss_feed()
        else:
            exit(1)
    except Exception as e:
        print(f"❌ RSS generation failed: {e}")
        exit(1) 