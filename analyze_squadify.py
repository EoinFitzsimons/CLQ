import json
import urllib.parse
from datetime import datetime

def analyze_squadify_har(har_file_path):
    """Analyze the Squadify.cc HAR file to understand how the game works."""
    
    print("🔍 ANALYZING SQUADIFY.CC NETWORK TRAFFIC")
    print("="*60)
    
    with open(har_file_path, 'r') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    # Categorize requests
    api_requests = []
    static_assets = []
    data_requests = []
    
    for entry in entries:
        url = entry['request']['url']
        method = entry['request']['method']
        status = entry['response']['status']
        
        # Categorize by URL pattern
        if '/api/' in url or url.endswith('.json'):
            api_requests.append(entry)
        elif any(ext in url for ext in ['.js', '.css', '.png', '.jpg', '.woff', '.ico']):
            static_assets.append(entry)
        else:
            data_requests.append(entry)
    
    print(f"📊 REQUEST SUMMARY:")
    print(f"   Total Requests: {len(entries)}")
    print(f"   API/Data Requests: {len(api_requests)}")
    print(f"   Static Assets: {len(static_assets)}")
    print(f"   Other Requests: {len(data_requests)}")
    print()
    
    # Analyze API requests
    if api_requests:
        print("🔗 API/DATA REQUESTS:")
        print("-" * 40)
        for req in api_requests:
            url = req['request']['url']
            method = req['request']['method']
            status = req['response']['status']
            print(f"   {method} {status} - {url}")
            
            # Check for response content
            if 'content' in req['response'] and req['response']['content'].get('text'):
                try:
                    response_text = req['response']['content']['text']
                    if response_text.strip().startswith('{') or response_text.strip().startswith('['):
                        response_data = json.loads(response_text)
                        print(f"      Response: {str(response_data)[:200]}...")
                except:
                    print(f"      Response: {response_text[:100]}...")
        print()
    
    # Look for specific Squadify patterns
    print("🎮 SQUADIFY GAME ANALYSIS:")
    print("-" * 40)
    
    game_related_requests = []
    team_data = []
    player_data = []
    
    for entry in entries:
        url = entry['request']['url']
        response = entry['response']
        
        # Look for game-related URLs
        if any(keyword in url.lower() for keyword in ['squad', 'team', 'player', 'game', 'daily', 'challenge']):
            game_related_requests.append(entry)
        
        # Check response content for team/player data
        if 'content' in response and response['content'].get('text'):
            try:
                content = response['content']['text']
                if any(keyword in content.lower() for keyword in ['tottenham', 'arsenal', 'chelsea', 'liverpool']):
                    team_data.append({'url': url, 'content': content[:500]})
                if any(keyword in content.lower() for keyword in ['kane', 'lloris', 'eriksen', 'son']):
                    player_data.append({'url': url, 'content': content[:500]})
            except:
                pass
    
    if game_related_requests:
        print("   Game-related requests found:")
        for req in game_related_requests:
            print(f"   - {req['request']['url']}")
    
    if team_data:
        print("   Team data found in:")
        for data in team_data:
            print(f"   - {data['url']}")
            print(f"     Content: {data['content'][:200]}...")
    
    if player_data:
        print("   Player data found in:")
        for data in player_data:
            print(f"   - {data['url']}")
            print(f"     Content: {data['content'][:200]}...")
    
    # Look for JavaScript files that might contain game logic
    print("\n📜 JAVASCRIPT FILES (Potential Game Logic):")
    print("-" * 40)
    
    js_files = [entry for entry in entries if entry['request']['url'].endswith('.js')]
    for js_file in js_files[:10]:  # Show first 10 JS files
        url = js_file['request']['url']
        size = js_file['response'].get('bodySize', 0)
        print(f"   {url.split('/')[-1]} ({size} bytes)")
        
        # Check if JS contains game-related keywords
        if 'content' in js_file['response'] and js_file['response']['content'].get('text'):
            content = js_file['response']['content']['text']
            if any(keyword in content.lower() for keyword in ['squad', 'team', 'player', 'daily']):
                print(f"     ⚡ Contains game-related code")
    
    # Check for localStorage or sessionStorage usage
    print("\n💾 CLIENT-SIDE STORAGE:")
    print("-" * 40)
    
    storage_found = False
    for entry in entries:
        if 'content' in entry['response'] and entry['response']['content'].get('text'):
            content = entry['response']['content']['text']
            if 'localStorage' in content or 'sessionStorage' in content:
                print(f"   Storage usage found in: {entry['request']['url'].split('/')[-1]}")
                storage_found = True
    
    if not storage_found:
        print("   No client-side storage usage detected")
    
    # Look for Next.js specific patterns
    print("\n⚛️ NEXT.JS FRAMEWORK ANALYSIS:")
    print("-" * 40)
    
    nextjs_files = [entry for entry in entries if '_next' in entry['request']['url']]
    if nextjs_files:
        print(f"   Next.js application detected ({len(nextjs_files)} framework files)")
        
        # Look for page data
        page_data_files = [f for f in nextjs_files if 'pageData' in f['request']['url'] or '_buildManifest' in f['request']['url']]
        if page_data_files:
            print("   Page data files found:")
            for file in page_data_files:
                print(f"   - {file['request']['url']}")
    
    print("\n🎯 CONCLUSIONS:")
    print("-" * 40)
    
    if not api_requests and not game_related_requests:
        print("   ❌ No obvious API calls detected")
        print("   📱 Game logic likely embedded in JavaScript bundles")
        print("   🔧 Team/player data may be hardcoded or bundled")
    
    if team_data or player_data:
        print("   ✅ Team/player data found in responses")
        print("   🎮 Game state likely managed client-side")
    
    print("   💡 Recommendations:")
    print("   - Examine JavaScript bundles for embedded data")
    print("   - Check for WebSocket connections (real-time updates)")
    print("   - Look for service worker for offline gameplay")
    
    return {
        'api_requests': api_requests,
        'static_assets': static_assets,
        'team_data': team_data,
        'player_data': player_data,
        'js_files': js_files
    }

if __name__ == "__main__":
    har_file = "/workspaces/CLQ/www.squadify.cc_Archive [25-09-11 10-43-59].har"
    analysis = analyze_squadify_har(har_file)
