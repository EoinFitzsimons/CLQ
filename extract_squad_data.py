import json
import re

def extract_squad_data(har_file_path):
    """Extract the actual squad player data from Squadify's JavaScript."""
    
    print("🏆 SQUADIFY DATA EXTRACTION")
    print("="*60)
    
    with open(har_file_path, 'r') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    # Find the main JavaScript file
    main_js = None
    for entry in entries:
        url = entry['request']['url']
        if 'page-' in url and url.endswith('.js'):
            if 'content' in entry['response'] and entry['response']['content'].get('text'):
                main_js = entry['response']['content']['text']
                print(f"📄 Analyzing: {url.split('/')[-1]}")
                break
    
    if not main_js:
        print("❌ Could not find main JavaScript")
        return
    
    # Extract player data structures - they seem to follow the pattern:
    # {name:"hugo lloris",number:"1",id:"17965",top:80,left:40,team:"Spurs",season:"15/16"}
    
    print("\n👤 EXTRACTING PLAYER DATA:")
    print("-" * 40)
    
    # Pattern for player objects
    player_pattern = r'\{name:"([^"]+)",number:"([^"]+)",id:"([^"]+)",top:(\d+),left:(\d+),team:"([^"]+)",season:"([^"]+)"\}'
    
    players = re.findall(player_pattern, main_js)
    
    if players:
        print(f"Found {len(players)} players in the embedded data:")
        print()
        
        squad_data = []
        for name, number, player_id, top, left, team, season in players:
            player_info = {
                'name': name,
                'number': number,
                'id': player_id,
                'position_top': int(top),
                'position_left': int(left),
                'team': team,
                'season': season
            }
            squad_data.append(player_info)
            print(f"   #{number:2} {name:20} ({team} {season}) - Position: ({left}, {top})")
        
        # Save to JSON for analysis
        with open('/workspaces/CLQ/squadify_players.json', 'w') as f:
            json.dump(squad_data, f, indent=2)
        
        print(f"\n💾 Saved {len(squad_data)} players to squadify_players.json")
        
        # Analyze the formation positioning
        print(f"\n⚽ FORMATION ANALYSIS:")
        print("-" * 40)
        
        # Group by position zones (rough estimation)
        goalkeeper = [p for p in squad_data if p['position_top'] > 70]
        defenders = [p for p in squad_data if 50 <= p['position_top'] <= 70]
        midfielders = [p for p in squad_data if 30 <= p['position_top'] < 50]
        forwards = [p for p in squad_data if p['position_top'] < 30]
        
        print(f"   Goalkeepers: {len(goalkeeper)}")
        print(f"   Defenders: {len(defenders)}")
        print(f"   Midfielders: {len(midfielders)}")
        print(f"   Forwards: {len(forwards)}")
        
        return squad_data
    
    # If the above pattern doesn't work, try a more flexible approach
    print("❌ Specific pattern not found. Trying flexible extraction...")
    
    # Look for any JSON-like structures with player names
    flexible_pattern = r'\{[^{}]*name[^{}]*lloris[^{}]*\}'
    flexible_matches = re.findall(flexible_pattern, main_js, re.IGNORECASE)
    
    if flexible_matches:
        print(f"Found {len(flexible_matches)} flexible matches:")
        for i, match in enumerate(flexible_matches[:3]):
            print(f"   Match {i+1}: {match}")
    
    # Try to find all Tottenham players
    print(f"\n🏃‍♂️ TOTTENHAM SQUAD EXTRACTION:")
    print("-" * 40)
    
    # Look for common Tottenham player names
    spurs_names = ['lloris', 'kane', 'son', 'eriksen', 'alderweireld', 'dembele', 'walker', 'rose', 'vertonghen', 'lamela', 'chadli', 'mason', 'bentaleb', 'vorm', 'dier', 'alli', 'trippier', 'wimmer', 'davies']
    
    found_players = []
    for name in spurs_names:
        # Look for patterns containing this name
        name_pattern = fr'\{{[^}}]*{name}[^}}]*\}}'
        matches = re.findall(name_pattern, main_js, re.IGNORECASE)
        if matches:
            found_players.extend([(name, match) for match in matches])
    
    if found_players:
        print(f"Found player data for {len(found_players)} Tottenham players:")
        for name, data in found_players[:10]:  # Show first 10
            print(f"   {name}: {data}")
    
    return None

def analyze_game_mechanics(js_content):
    """Analyze how the game mechanics work."""
    
    print(f"\n🎮 GAME MECHANICS ANALYSIS:")
    print("="*60)
    
    # Look for daily reset logic
    reset_patterns = re.findall(r'(12:00|midnight|EST|UTC|reset|daily)', js_content, re.IGNORECASE)
    if reset_patterns:
        print(f"📅 Daily Reset Logic:")
        print(f"   Keywords found: {', '.join(set(reset_patterns))}")
        
        # Look for specific time handling
        time_patterns = re.findall(r'(new Date|getTime|setHours|12:00|EST)', js_content)
        if time_patterns:
            print(f"   Time handling: {', '.join(set(time_patterns))}")
    
    # Look for scoring logic
    print(f"\n🏆 SCORING SYSTEM:")
    print("-" * 40)
    
    score_patterns = re.findall(r'(score|point|correct|wrong|guess)', js_content, re.IGNORECASE)
    if score_patterns:
        print(f"   Score keywords: {len(score_patterns)} occurrences")
    
    # Look for game state management
    state_patterns = re.findall(r'(useState|useEffect|gameState|completed)', js_content)
    if state_patterns:
        print(f"   State management: {', '.join(set(state_patterns))}")

if __name__ == "__main__":
    har_file = "/workspaces/CLQ/www.squadify.cc_Archive [25-09-11 10-43-59].har"
    squad_data = extract_squad_data(har_file)
    
    # Get the JavaScript content for further analysis
    with open(har_file, 'r') as f:
        har_data = json.load(f)
    
    for entry in har_data['log']['entries']:
        url = entry['request']['url']
        if 'page-' in url and url.endswith('.js'):
            if 'content' in entry['response']:
                js_content = entry['response']['content'].get('text', '')
                if js_content:
                    analyze_game_mechanics(js_content)
                    break
