#!/usr/bin/env python3
import os
import datetime
from jinja2 import Environment, FileSystemLoader

def generate_sitemap():
    """Generate a dynamic sitemap.xml file with current date and archive entries"""
    print("Generating sitemap.xml...")
    
    # Get current date in ISO format for lastmod dates
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Get all archive files
    archive_dir = 'archive'
    archive_files = []
    archive_dates = []
    
    if os.path.exists(archive_dir):
        files = [f for f in os.listdir(archive_dir) if f.endswith('.html') and f != 'index.html']
        # Sort files by date (newest first)
        files.sort(reverse=True)
        archive_files = files
        
        # Extract dates from filenames (assuming YYYY-MM-DD.html format)
        for f in files:
            date_str = f.replace('.html', '')
            archive_dates.append(date_str)
    
    # Setup Jinja2 template environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('sitemap.xml.j2')
    
    # Render the sitemap template
    output = template.render(
        current_date=current_date,
        archive_files=archive_files,
        archive_dates=archive_dates
    )
    
    # Write the sitemap file
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Generated sitemap.xml with {len(archive_files)} archive entries")

if __name__ == "__main__":
    generate_sitemap() 