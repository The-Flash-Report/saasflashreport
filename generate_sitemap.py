#!/usr/bin/env python3
import os
import datetime
from jinja2 import Environment, FileSystemLoader
import json # Added to load keyword_config.json

# Function to load keyword_config.json (similar to aggregator.py)
def load_keyword_config():
    """Load keyword configuration for sitemap generation."""
    try:
        with open('keyword_config.json', 'r') as f:
            config_data = json.load(f)
            print("keyword_config.json loaded successfully for sitemap.")
            return config_data.get('keyword_pages', {}) # Return only the pages part
    except FileNotFoundError:
        print("Warning: keyword_config.json not found. Keyword pages will not be added to sitemap.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing keyword_config.json for sitemap: {e}")
        return {}

def generate_sitemap():
    """Generate a dynamic sitemap.xml file with current date, archive, and keyword page entries"""
    print("Generating sitemap.xml...")
    
    # Get current date in ISO format for lastmod dates
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Get all archive files
    archive_dir = 'archive'
    archive_files = []
    # archive_dates = [] # Not directly used by sitemap_template.xml, can be removed if not needed elsewhere
    
    if os.path.exists(archive_dir):
        files = [f for f in os.listdir(archive_dir) if f.endswith('.html') and f != 'index.html']
        # Sort files by date (newest first)
        files.sort(reverse=True)
        archive_files = files
        
        # archive_dates list generation removed as it's not used in the sitemap context directly
    
    # Load keyword pages configuration
    keyword_pages = load_keyword_config()

    # Setup Jinja2 template environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('sitemap_template.xml')
    
    # Render the sitemap template
    output = template.render(
        current_date=current_date,
        archive_files=archive_files,
        keyword_pages=keyword_pages # Pass keyword pages to the template
    )
    
    # Write the sitemap file
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Generated sitemap.xml with {len(archive_files)} archive entries and {len(keyword_pages)} keyword page entries")

if __name__ == "__main__":
    generate_sitemap() 