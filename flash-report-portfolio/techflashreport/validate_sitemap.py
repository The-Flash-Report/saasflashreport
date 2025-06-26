#!/usr/bin/env python3
"""
Simple sitemap validation script to help debug sitemap issues
"""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import sys

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
            
            # Check first few URLs
            for i, url_elem in enumerate(urls[:3]):
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
            
            if len(urls) > 3:
                print(f"   ... and {len(urls) - 3} more URLs")
                
            return True
            
        except ET.ParseError as e:
            print(f"❌ XML Parse Error: {e}")
            print("First 500 characters of response:")
            print(response.text[:500])
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False

def main():
    sitemap_url = "https://aiflashreport.com/sitemap.xml"
    
    if len(sys.argv) > 1:
        sitemap_url = sys.argv[1]
    
    print("🔍 Sitemap Validation Tool")
    print("=" * 50)
    
    is_valid = validate_sitemap_url(sitemap_url)
    
    if is_valid:
        print("\n✅ Sitemap appears to be valid!")
        print("\nIf Google Search Console still shows errors, try:")
        print("1. Resubmitting the sitemap in GSC")
        print("2. Checking for any robots.txt blocking")
        print("3. Waiting 24-48 hours for Google to re-crawl")
    else:
        print("\n❌ Sitemap has issues that need to be fixed")

if __name__ == "__main__":
    main() 