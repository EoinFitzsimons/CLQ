import json
import re
import base64
from urllib.parse import unquote

def extract_squadify_logic(har_file_path):
    """Extract and analyze the core game logic from Squadify's JavaScript."""
    
    print("🔧 EXTRACTING SQUADIFY GAME LOGIC")
    print("="*60)
    
    with open(har_file_path, 'r') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    # Find the main page JavaScript that contains game logic
    main_js = None
    for entry in entries:
        url = entry['request']['url']
        if 'page-' in url and url.endswith('.js'):
            if 'content' in entry['response'] and entry['response']['content'].get('text'):
                main_js = entry['response']['content']['text']
                print(f"📄 Found main game JavaScript: {url.split('/')[-1]}")
                break
    
    if not main_js:
        print("❌ Could not find main game JavaScript")
        return
    
    # Extract team/squad data patterns
    print("\n🏈 EXTRACTING TEAM DATA PATTERNS:")
    print("-" * 40)
    
    # Look for team names and squad data
    team_patterns = re.findall(r'["\']([A-Z\s]+(?:FC|CITY|UNITED|ARSENAL|CHELSEA|LIVERPOOL|TOTTENHAM|MANCHESTER)[^"\']*)["\']', main_js, re.IGNORECASE)
    if team_patterns:
        print("   Team names found:")
        for team in set(team_patterns[:10]):  # Show unique teams
            print(f"   - {team}")
    
    # Look for player data structures
    player_patterns = re.findall(r'["\']([a-z]+\.[a-z]+)["\']', main_js)  # Format like 'h.kane'
    if player_patterns:
        print("\n👤 PLAYER NAME PATTERNS:")
        unique_players = list(set(player_patterns[:20]))  # First 20 unique
        for player in unique_players:
            print(f"   - {player}")
    
    # Look for formation patterns
    formation_patterns = re.findall(r'["\'](\d-\d-\d(?:-\d)?)["\']', main_js)
    if formation_patterns:
        print(f"\n⚽ FORMATIONS FOUND:")
        for formation in set(formation_patterns):
            print(f"   - {formation}")
    
    # Look for API endpoints or data fetching
    print(f"\n🔗 API/DATA FETCHING PATTERNS:")
    print("-" * 40)
    
    api_patterns = re.findall(r'["\']([/a-zA-Z0-9-_]+(?:api|data|teams|players|squads)[/a-zA-Z0-9-_]*)["\']', main_js)
    if api_patterns:
        print("   API endpoints found:")
        for endpoint in set(api_patterns[:10]):
            print(f"   - {endpoint}")
    else:
        print("   ❌ No obvious API endpoints found")
        print("   💡 Data is likely embedded or hardcoded")
    
    # Look for daily challenge logic
    print(f"\n📅 DAILY CHALLENGE LOGIC:")
    print("-" * 40)
    
    daily_patterns = re.findall(r'(daily|today|challenge|reset|12:00|midnight|EST)', main_js, re.IGNORECASE)
    if daily_patterns:
        print(f"   Daily challenge keywords found: {len(daily_patterns)} occurrences")
        print(f"   Keywords: {', '.join(set(daily_patterns))}")
    else:
        print("   ❌ No obvious daily challenge logic found")
    
    # Look for localStorage usage
    storage_patterns = re.findall(r'(localStorage|sessionStorage)\.([a-zA-Z0-9_]+)', main_js)
    if storage_patterns:
        print(f"\n💾 CLIENT STORAGE USAGE:")
        for storage_type, key in set(storage_patterns):
            print(f"   - {storage_type}.{key}")
    
    # Look for game state management
    print(f"\n🎮 GAME STATE PATTERNS:")
    print("-" * 40)
    
    state_patterns = re.findall(r'(squad|team|player|position|formation|draft|select)', main_js, re.IGNORECASE)
    if state_patterns:
        print(f"   Game state keywords found: {len(state_patterns)} occurrences")
        print(f"   Top keywords: {', '.join(list(set(state_patterns))[:10])}")
    
    # Try to find embedded data structures
    print(f"\n📊 EMBEDDED DATA STRUCTURES:")
    print("-" * 40)
    
    # Look for JSON-like structures
    json_patterns = re.findall(r'\{[^{}]*(?:["\'](?:name|team|player|position)["\'][^{}]*){2,}[^{}]*\}', main_js)
    if json_patterns:
        print(f"   Found {len(json_patterns)} potential data objects")
        for i, pattern in enumerate(json_patterns[:3]):  # Show first 3
            print(f"   Object {i+1}: {pattern[:100]}...")
    
    # Look for array structures with team/player data
    array_patterns = re.findall(r'\[[^\[\]]*(?:["\'](?:kane|lloris|son|eriksen|tottenham)["\'][^\[\]]*){1,}[^\[\]]*\]', main_js, re.IGNORECASE)
    if array_patterns:
        print(f"   Found {len(array_patterns)} potential data arrays")
        for i, pattern in enumerate(array_patterns[:2]):  # Show first 2
            print(f"   Array {i+1}: {pattern[:150]}...")
    
    # Extract any hardcoded squad data
    print(f"\n🏆 SQUAD DATA EXTRACTION:")
    print("-" * 40)
    
    # Look for the Tottenham 15/16 squad specifically
    spurs_patterns = re.findall(r'tottenham|15/16|lloris|kane|son|eriksen|alderweireld', main_js, re.IGNORECASE)
    if spurs_patterns:
        print(f"   Tottenham 15/16 references: {len(spurs_patterns)}")
        print(f"   Keywords: {', '.join(set(spurs_patterns))}")
    
    # Try to extract the actual squad data structure
    squad_structure = re.search(r'(\{[^{}]*(?:lloris|kane)[^{}]*\})', main_js, re.IGNORECASE)
    if squad_structure:
        print(f"   Squad structure found: {squad_structure.group(1)[:200]}...")
    
    return main_js

def analyze_javascript_structure(js_content):
    """Analyze the structure of the JavaScript to understand the game flow."""
    
    print(f"\n🔍 JAVASCRIPT STRUCTURE ANALYSIS:")
    print("="*60)
    
    # Count different types of constructs
    functions = len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*:\s*function', js_content))
    objects = len(re.findall(r'\{[^{}]*\}', js_content))
    arrays = len(re.findall(r'\[[^\[\]]*\]', js_content))
    
    print(f"📈 Code Statistics:")
    print(f"   Functions: {functions}")
    print(f"   Objects: {objects}")
    print(f"   Arrays: {arrays}")
    print(f"   Total size: {len(js_content)} characters")
    
    # Look for React components
    react_components = re.findall(r'function\s+([A-Z]\w*)|const\s+([A-Z]\w*)\s*=', js_content)
    if react_components:
        print(f"\n⚛️ React Components Found:")
        for match in react_components[:10]:
            component = match[0] or match[1]
            if component:
                print(f"   - {component}")

if __name__ == "__main__":
    har_file = "/workspaces/CLQ/www.squadify.cc_Archive [25-09-11 10-43-59].har"
    js_content = extract_squadify_logic(har_file)
    
    if js_content:
        analyze_javascript_structure(js_content)
