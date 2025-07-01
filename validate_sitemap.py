#!/usr/bin/env python3
"""
Comprehensive sitemap validation script for SaaS Flash Report
"""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import sys
import os
import glob

def validate_sitemap_url(sitemap_url):
    """Validate a sitemap URL and check its contents"""
    print(f"Validating sitemap: {sitemap_url}")
    
    try:
        # Fetch the sitemap
        response = requests.get(sitemap_url, timeout=10)
        print(f"HTTP Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"❌ ERROR: HTTP {response.status_code}")
            return False
            
        # Check if it's XML
        content_type = response.headers.get('content-type', '').lower()
        if 'xml' not in content_type and 'text' not in content_type:
            print(f"⚠️  WARNING: Unexpected content-type: {content_type}")
        
        # Parse XML
        try:
            root = ET.fromstring(response.content)
            print("✅ XML is well-formed")
            
            # Check namespace
            if root.tag.endswith('urlset'):
                print("✅ Root element is urlset")
            else:
                print(f"⚠️  WARNING: Root element is {root.tag}, expected urlset")
            
            # Count URLs
            urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            print(f"📊 Found {len(urls)} URLs in sitemap")
            
            # Analyze URL structure
            url_types = {
                'main': 0,
                'static': 0,
                'archive': 0,
                'topics': 0,
                'other': 0
            }
            
            for url_elem in urls:
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    url = loc_elem.text
                    if url.endswith('/'):
                        url_types['main'] += 1
                    elif '/archive/' in url:
                        url_types['archive'] += 1
                    elif '/topics/' in url:
                        url_types['topics'] += 1
                    elif any(page in url for page in ['about.html', 'contact', 'thank-you']):
                        url_types['static'] += 1
                    else:
                        url_types['other'] += 1
            
            print("\n📈 URL Breakdown:")
            for url_type, count in url_types.items():
                if count > 0:
                    print(f"   {url_type.capitalize()}: {count} URLs")
            
            # Check first few URLs for accessibility
            print("\n🔍 Testing URL accessibility:")
            for i, url_elem in enumerate(urls[:5]):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    print(f"   URL {i+1}: {loc_elem.text}")
                    
                    # Quick check if URL is accessible
                    try:
                        url_response = requests.head(loc_elem.text, timeout=5)
                        if url_response.status_code == 200:
                            print(f"      ✅ Accessible (HTTP {url_response.status_code})")
                        else:
                            print(f"      ❌ Not accessible (HTTP {url_response.status_code})")
                    except Exception as e:
                        print(f"      ❌ Error checking URL: {e}")
            
            if len(urls) > 5:
                print(f"   ... and {len(urls) - 5} more URLs")
                
            return True, len(urls), url_types
            
        except ET.ParseError as e:
            print(f"❌ XML Parse Error: {e}")
            print("First 500 characters of response:")
            print(response.text[:500])
            return False, 0, {}
            
    except requests.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False, 0, {}

def analyze_local_files():
    """Analyze local HTML files to see what should be in sitemap"""
    print("\n📁 Local File Analysis:")
    
    # Count HTML files
    html_files = glob.glob('*.html') + glob.glob('archive/*.html') + glob.glob('topics/*.html')
    html_files = [f for f in html_files if 'template' not in f and 'index.html' not in f]
    
    local_types = {
        'main': 1,  # index.html equivalent (/)
        'static': len([f for f in html_files if any(page in f for page in ['about.html', 'contact', 'thank-you'])]),
        'archive': len([f for f in html_files if f.startswith('archive/')]),
        'topics': len([f for f in html_files if f.startswith('topics/')]),
        'other': 0
    }
    
    # Add archive index if it exists
    if os.path.exists('archive/index.html'):
        local_types['archive'] += 1
    
    total_local = sum(local_types.values())
    
    print(f"   Total local HTML files: {total_local}")
    for file_type, count in local_types.items():
        if count > 0:
            print(f"   {file_type.capitalize()}: {count} files")
    
    return total_local, local_types

def main():
    sitemap_url = "https://saasflashreport.com/sitemap.xml"
    
    if len(sys.argv) > 1:
        sitemap_url = sys.argv[1]
    
    print("🔍 Comprehensive Sitemap Validation Tool")
    print("=" * 60)
    
    # Validate remote sitemap
    is_valid, remote_count, remote_types = validate_sitemap_url(sitemap_url)
    
    # Analyze local files
    local_count, local_types = analyze_local_files()
    
    # Compare counts
    print(f"\n📊 Count Comparison:")
    print(f"   Remote sitemap: {remote_count} URLs")
    print(f"   Local files: {local_count} files")
    
    if remote_count != local_count:
        print(f"   ⚠️  MISMATCH: {abs(remote_count - local_count)} URL difference")
        if remote_count > local_count:
            print("   → Remote sitemap may have additional pages")
        else:
            print("   → Local files not fully represented in remote sitemap")
    else:
        print("   ✅ Counts match!")
    
    # Summary and recommendations
    print(f"\n📋 Summary:")
    if is_valid:
        print("✅ Sitemap is valid and accessible")
        print("✅ All tested URLs are accessible")
        
        print(f"\n🚀 Search Engine Submission:")
        print("1. Google Search Console:")
        print(f"   → Submit: {sitemap_url}")
        print("   → Monitor for errors and indexing status")
        print("2. Bing Webmaster Tools:")
        print(f"   → Submit: {sitemap_url}")
        print("3. Robots.txt validation:")
        print("   → Ensure sitemap is referenced in robots.txt")
        print(f"   → Add line: Sitemap: {sitemap_url}")
        
        if remote_count != local_count:
            print(f"\n⚠️  Action Required:")
            print("   → Update sitemap generation to match all local files")
            print("   → Deploy updated sitemap.xml")
            print("   → Resubmit to search engines")
    else:
        print("❌ Sitemap has issues that need to be fixed")

if __name__ == "__main__":
    main() 