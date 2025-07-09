#!/usr/bin/env python3
import os
import datetime
from jinja2 import Environment, FileSystemLoader
import glob

def generate_sitemap():
    """Generate a comprehensive sitemap.xml file with all pages and proper prioritization"""
    print("Generating comprehensive sitemap.xml...")
    
    # Get current date in ISO format for lastmod dates
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Base URL - update this to match your domain
    base_url = "https://saasflashreport.com"
    
    urls = []
    
    # Main page (highest priority)
    urls.append({
        'url': f"{base_url}/",
        'lastmod': current_date,
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    # Static pages (high priority)
    static_pages = ['about.html', 'contact.html', 'contact-success.html', 'thank-you.html']
    for page in static_pages:
        if os.path.exists(page):
            urls.append({
                'url': f"{base_url}/{page}",
                'lastmod': current_date,
                'changefreq': 'weekly',
                'priority': '0.8'
            })
    
    # RSS Feed (high priority)
    if os.path.exists('rss.xml'):
        urls.append({
            'url': f"{base_url}/rss.xml",
            'lastmod': current_date,
            'changefreq': 'daily',
            'priority': '0.9'
        })
    
    # Archive index (high priority)
    if os.path.exists('archive/index.html'):
        urls.append({
            'url': f"{base_url}/archive/",
            'lastmod': current_date,
            'changefreq': 'daily',
            'priority': '0.8'
        })
    
    # Archive entries (medium priority)
    archive_files = glob.glob('archive/*.html')
    for archive_file in sorted(archive_files, reverse=True):
        if not archive_file.endswith('index.html'):
            filename = os.path.basename(archive_file)
            # Extract date from filename for lastmod
            date_str = filename.replace('.html', '')
            try:
                # Validate date format
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                lastmod = date_str
            except ValueError:
                lastmod = current_date
            
            urls.append({
                'url': f"{base_url}/archive/{filename}",
                'lastmod': lastmod,
                'changefreq': 'monthly',
                'priority': '0.7'
            })
    
    # Topic pages (medium priority)
    topic_files = glob.glob('topics/*.html')
    for topic_file in sorted(topic_files):
        filename = os.path.basename(topic_file)
        
        # Determine priority based on page type
        if filename.endswith('-page-2.html') or not any(f'-page-{i}.html' in filename for i in range(2, 10)):
            # Main topic pages and page 2 get higher priority
            priority = '0.7'
        else:
            # Subsequent pagination pages get lower priority
            priority = '0.6'
        
        urls.append({
            'url': f"{base_url}/topics/{filename}",
            'lastmod': current_date,
            'changefreq': 'weekly',
            'priority': priority
        })
    
    # Generate XML content
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url_data in urls:
        xml_content += '    <url>\n'
        xml_content += f'        <loc>{url_data["url"]}</loc>\n'
        xml_content += f'        <lastmod>{url_data["lastmod"]}</lastmod>\n'
        xml_content += f'        <changefreq>{url_data["changefreq"]}</changefreq>\n'
        xml_content += f'        <priority>{url_data["priority"]}</priority>\n'
        xml_content += '    </url>\n'
    
    xml_content += '</urlset>'
    
    # Write the sitemap file
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"Generated sitemap.xml with {len(urls)} total URLs:")
    print(f"  - 1 main page")
    print(f"  - {len([u for u in urls if '/about.html' in u['url'] or '/contact' in u['url'] or '/thank-you' in u['url']])} static pages")
    print(f"  - {len([u for u in urls if '/archive/' in u['url']])} archive pages")
    print(f"  - {len([u for u in urls if '/topics/' in u['url']])} topic pages")

if __name__ == "__main__":
    generate_sitemap() 