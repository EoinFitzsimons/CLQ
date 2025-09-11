import json
import re
import requests
from bs4 import BeautifulSoup
import time

def analyze_transfermarkt_sources():
    """Analyze the Transfermarkt URLs found in Squadify's code."""
    
    print("🏆 TRANSFERMARKT DATA SOURCE ANALYSIS")
    print("="*60)
    
    # Extract Transfermarkt URLs from the previous analysis
    transfermarkt_urls = [
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/958430",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/36866", 
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/4374159",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/932408",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/3839079",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/2872218",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/39246",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/1000115", 
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/2578147",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/2258919",
        "http://www.transfermarkt.com/spielbericht/index/spielbericht/4113124"
    ]
    
    print(f"📊 Found {len(transfermarkt_urls)} Transfermarkt match reports")
    print("These are 'spielbericht' (match report) URLs - specific historical matches!")
    
    # Let's identify what these matches might be based on the IDs
    print(f"\n🎯 MATCH IDENTIFICATION:")
    print("-" * 50)
    
    # Try to fetch one URL to understand the structure
    sample_url = transfermarkt_urls[0]
    print(f"📄 Analyzing sample match: {sample_url}")
    
    try:
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(sample_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract match information
            title = soup.find('title')
            if title:
                print(f"   📋 Page title: {title.get_text()}")
            
            # Look for team names
            team_elements = soup.find_all('a', href=re.compile(r'/.*verein/.*'))
            teams = []
            for elem in team_elements[:10]:  # First 10 to avoid spam
                if elem.get_text().strip() and len(elem.get_text().strip()) > 2:
                    teams.append(elem.get_text().strip())
            
            if teams:
                print(f"   ⚽ Teams found: {', '.join(list(set(teams))[:4])}")
            
            # Look for lineup information
            lineup_section = soup.find('div', class_=re.compile(r'lineup|formation'))
            if lineup_section:
                print(f"   👥 Lineup section detected")
            
        else:
            print(f"   ❌ Could not fetch match data (Status: {response.status_code})")
            
    except Exception as e:
        print(f"   ⚠️  Error fetching match data: {e}")
    
    # Analyze the match ID patterns
    print(f"\n🔢 MATCH ID ANALYSIS:")
    print("-" * 50)
    
    match_ids = [url.split('/')[-1] for url in transfermarkt_urls]
    print(f"Match IDs: {', '.join(match_ids)}")
    
    # Sort by ID to see chronological pattern
    sorted_ids = sorted([int(id) for id in match_ids])
    print(f"Sorted IDs: {sorted_ids}")
    print(f"ID range: {min(sorted_ids)} to {max(sorted_ids)}")
    
    # This suggests the matches span different time periods
    print(f"\n💡 DATA SOURCE STRATEGY:")
    print("-" * 50)
    print("🎯 Squadify's Approach:")
    print("   1. Uses specific Transfermarkt match reports (spielbericht)")
    print("   2. Each URL corresponds to a historic match lineup")
    print("   3. 11 URLs = 11 different matches/squads")
    print("   4. Match IDs span different ranges = different seasons/years")
    print("   5. Extracts starting XI formations from these specific matches")
    
    print(f"\n🚀 IMPROVEMENT OPPORTUNITIES:")
    print("-" * 50)
    print("📈 To expand the database:")
    print("   • Scrape more Transfermarkt match reports")
    print("   • Target famous matches from different eras:")
    print("     - Champions League finals")
    print("     - World Cup matches") 
    print("     - Historic league matches")
    print("     - Derby matches")
    print("   • Each match provides 22 players (both teams)")
    print("   • Could easily expand to 100+ different squads")
    
    print(f"\n🔍 SPECIFIC MATCH EXAMPLES TO ADD:")
    print("-" * 50)
    famous_matches = [
        "Barcelona 6-1 PSG (2017) - The Remontada",
        "Liverpool 4-0 Barcelona (2019) - Anfield Miracle", 
        "Manchester City vs Liverpool (2019) - Title race",
        "Real Madrid vs Barcelona (2017) - El Clasico",
        "Arsenal Invincibles season matches (2003-04)",
        "Leicester City title season (2015-16)",
        "Ajax vs Real Madrid (2019) - Youth vs Experience"
    ]
    
    for match in famous_matches:
        print(f"   ⚽ {match}")
    
    return match_ids

def create_expansion_plan():
    """Create a plan for expanding Squadify's database."""
    
    print(f"\n📋 SQUADIFY EXPANSION PLAN:")
    print("="*60)
    
    print("🎯 CURRENT LIMITATIONS:")
    print("   • Only 11 historic squads")
    print("   • Repeats frequently") 
    print("   • Limited era coverage")
    
    print(f"\n🚀 EXPANSION STRATEGY:")
    print("   1. TARGET SOURCES:")
    print("      • Transfermarkt match reports (spielbericht)")
    print("      • Focus on memorable/iconic matches")
    print("      • Cover different leagues and eras")
    
    print("   2. CATEGORIES TO ADD:")
    print("      • Champions League finals (1992-2024)")
    print("      • World Cup knockout matches")
    print("      • Premier League title deciders") 
    print("      • Historic derbies (El Clasico, North London, etc)")
    print("      • Underdog victories (Leicester, Porto, Ajax)")
    print("      • Individual brilliance matches (Messi/Ronaldo)")
    
    print("   3. IMPLEMENTATION:")
    print("      • Scrape ~50-100 additional match reports")
    print("      • Extract starting XI + formation data")
    print("      • Store with match context for added engagement")
    print("      • Daily rotation from expanded pool")
    
    print("   4. ENHANCED FEATURES:")
    print("      • Match context clues (year, competition)")
    print("      • Difficulty levels (recent vs historic)")
    print("      • Team vs individual player focus")
    
    return True

if __name__ == "__main__":
    match_ids = analyze_transfermarkt_sources()
    create_expansion_plan()
