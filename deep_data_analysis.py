import json
import re
from urllib.parse import unquote, parse_qs

def deep_analyze_data_sources(har_file_path):
    """Deep dive into Squadify's actual data sources and APIs."""
    
    print("🔍 DEEP DATA SOURCE ANALYSIS")
    print("="*60)
    
    with open(har_file_path, 'r') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    print(f"📊 Total network requests analyzed: {len(entries)}")
    
    # Analyze all requests for hidden data sources
    print(f"\n🌐 COMPREHENSIVE REQUEST ANALYSIS:")
    print("-" * 50)
    
    for i, entry in enumerate(entries):
        url = entry['request']['url']
        method = entry['request']['method']
        
        # Check for any external APIs or data endpoints
        if any(keyword in url.lower() for keyword in ['api', 'data', 'players', 'teams', 'squads', 'football', 'soccer']):
            print(f"   🎯 POTENTIAL DATA ENDPOINT:")
            print(f"      URL: {url}")
            print(f"      Method: {method}")
            
            # Check request headers for API keys or tokens
            headers = entry['request']['headers']
            for header in headers:
                if any(key in header['name'].lower() for key in ['auth', 'token', 'key', 'api']):
                    print(f"      Auth Header: {header['name']}: {header['value']}")
            
            # Check response for data structure
            if 'content' in entry['response']:
                content = entry['response']['content'].get('text', '')
                if content and len(content) > 100:
                    print(f"      Response size: {len(content)} chars")
                    # Look for JSON data
                    try:
                        json_data = json.loads(content)
                        print(f"      Contains JSON: {type(json_data)}")
                        if isinstance(json_data, dict) and json_data:
                            print(f"      JSON keys: {list(json_data.keys())[:5]}")
                    except:
                        pass
            print()
    
    # Look for third-party services
    print(f"\n🔗 THIRD-PARTY SERVICES:")
    print("-" * 50)
    
    domains = set()
    for entry in entries:
        url = entry['request']['url']
        domain = url.split('/')[2] if len(url.split('/')) > 2 else url
        domains.add(domain)
    
    external_domains = [d for d in domains if 'squadify' not in d.lower()]
    for domain in sorted(external_domains):
        # Check if it's a football/sports data provider
        if any(keyword in domain.lower() for keyword in ['football', 'soccer', 'sport', 'api', 'data']):
            print(f"   ⚽ SPORTS DATA: {domain}")
        else:
            print(f"   📡 External: {domain}")
    
    # Analyze JavaScript for hidden data fetching
    print(f"\n💾 JAVASCRIPT DATA FETCHING ANALYSIS:")
    print("-" * 50)
    
    main_js = None
    for entry in entries:
        url = entry['request']['url']
        if 'page-' in url and url.endswith('.js'):
            if 'content' in entry['response']:
                main_js = entry['response']['content'].get('text', '')
                break
    
    if main_js:
        # Look for fetch calls, XMLHttpRequest, or other data loading
        fetch_patterns = re.findall(r'fetch\([^)]+\)|XMLHttpRequest|axios|\.get\(|\.post\(', main_js)
        if fetch_patterns:
            print(f"   🔄 Data fetching calls found: {len(fetch_patterns)}")
            for pattern in set(fetch_patterns[:5]):
                print(f"      - {pattern}")
        
        # Look for external API URLs in the code
        url_patterns = re.findall(r'https?://[^"\s\)]+', main_js)
        if url_patterns:
            print(f"   🌐 External URLs in code:")
            for url in set(url_patterns):
                if 'squadify' not in url.lower():
                    print(f"      - {url}")
        
        # Look for API key patterns
        key_patterns = re.findall(r'["\']([a-zA-Z0-9]{20,})["\']', main_js)
        if key_patterns:
            print(f"   🔑 Potential API keys/tokens:")
            for key in set(key_patterns[:3]):  # First 3 to avoid spam
                if len(key) >= 20:
                    print(f"      - {key[:10]}...{key[-10:]}")
        
        # Look for database or CMS references
        cms_patterns = re.findall(r'(contentful|strapi|sanity|airtable|firebase|supabase)', main_js, re.IGNORECASE)
        if cms_patterns:
            print(f"   🗄️  CMS/Database references:")
            for cms in set(cms_patterns):
                print(f"      - {cms}")
        
        # Look for environment variables or config
        env_patterns = re.findall(r'process\.env\.[A-Z_]+|NEXT_PUBLIC_[A-Z_]+', main_js)
        if env_patterns:
            print(f"   ⚙️  Environment variables:")
            for env in set(env_patterns):
                print(f"      - {env}")
    
    # Check for data embedded in HTML or other files
    print(f"\n📄 CHECKING ALL FILE CONTENTS FOR DATA:")
    print("-" * 50)
    
    for entry in entries:
        if 'content' in entry['response']:
            content = entry['response']['content'].get('text', '')
            url = entry['request']['url']
            
            # Look for large JSON arrays (potential player data)
            json_arrays = re.findall(r'\[[^\[\]]{200,}\]', content)
            if json_arrays:
                print(f"   📊 Large JSON arrays in {url.split('/')[-1]}:")
                for i, array in enumerate(json_arrays[:2]):
                    print(f"      Array {i+1}: {len(array)} chars")
                    # Try to extract sample data
                    try:
                        data = json.loads(array)
                        if isinstance(data, list) and len(data) > 0:
                            print(f"      Sample item: {str(data[0])[:100]}...")
                    except:
                        pass
    
    return main_js

def analyze_build_files():
    """Check if there are build manifests or other files that might reveal data sources."""
    
    print(f"\n🔨 BUILD MANIFEST ANALYSIS:")
    print("-" * 50)
    
    # This would check for _next/static files, webpack manifests, etc.
    # that might reveal additional data loading strategies
    
    print("   Note: This would require access to the full _next/static/ directory")
    print("   to analyze webpack chunks and build manifests for hidden data sources.")

if __name__ == "__main__":
    har_file = "/workspaces/CLQ/www.squadify.cc_Archive [25-09-11 10-43-59].har"
    main_js = deep_analyze_data_sources(har_file)
    analyze_build_files()
