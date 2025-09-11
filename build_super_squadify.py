"""
Build Super Squadify with Real English League Data
=================================================

This script combines our verified English league match scraper 
with the Super Squadify engine to create a massive database.
"""

import json
from english_football_database import EnglishFootballDatabase
from super_squadify import SuperSquadifyEngine

def build_complete_english_squadify():
    """Build Super Squadify with comprehensive English league data."""
    
    print("🏈 BUILDING SUPER SQUADIFY WITH REAL ENGLISH DATA")
    print("="*70)
    
    # Step 1: Load verified match IDs
    print("📋 Step 1: Loading verified English league matches...")
    
    try:
        with open('/workspaces/CLQ/discovered_english_matches.json', 'r') as f:
            discovery_data = json.load(f)
        
        verified_matches = discovery_data['working_matches']
        print(f"   Found {len(verified_matches)} verified match IDs")
        
    except FileNotFoundError:
        print("   ❌ No verified matches found. Using sample matches...")
        verified_matches = ["3592069"]  # Fallback to our known working match
    
    # Step 2: Build comprehensive database with real match data
    print("\n📊 Step 2: Scraping comprehensive match data...")
    
    db_builder = EnglishFootballDatabase()
    
    # Override the sample match IDs with our verified ones
    db_builder.sample_match_ids = verified_matches
    
    # Build the database with more matches
    _, players, summary = db_builder.build_english_league_database(max_matches=len(verified_matches))
    
    print(f"   ✅ Database built with {summary['total_player_records']} player records")
    print(f"   ✅ Covers {len(summary['teams'])} different teams")
    print(f"   ✅ Spans competitions: {', '.join(summary['competitions'])}")
    
    # Step 3: Initialize Super Squadify with real data
    print("\n🎮 Step 3: Initializing Super Squadify with real data...")
    
    # Convert the scraped data to Super Squadify format
    formatted_players = []
    for player in players:
        if player.get('name') and player.get('team'):
            formatted_player = {
                'name': player['name'],
                'id': player['id'] or f"uk_{len(formatted_players)}",
                'team': player['team'],
                'season': player.get('season', 'Unknown'),
                'position': estimate_position_from_coordinates(
                    player.get('position_top', 50), 
                    player.get('position_left', 40)
                ),
                'number': player['number'],
                'competition': player.get('competition', 'English League'),
                'position_top': player.get('position_top', 50),
                'position_left': player.get('position_left', 40),
                'match_date': player.get('match_date', 'Unknown'),
                'venue': player.get('venue', 'Unknown'),
                'events': player.get('events', [])
            }
            formatted_players.append(formatted_player)
    
    print(f"   ✅ Formatted {len(formatted_players)} players for Super Squadify")
    
    # Step 4: Create enhanced Super Squadify engine
    print("\n🚀 Step 4: Creating enhanced Super Squadify engine...")
    
    # Save the formatted database
    with open('/workspaces/CLQ/super_squadify_players.json', 'w') as f:
        json.dump(formatted_players, f, indent=2)
    
    # Initialize engine with real data
    engine = SuperSquadifyEngine('/workspaces/CLQ/super_squadify_players.json')
    
    # Step 5: Generate sample challenges
    print("\n🎯 Step 5: Generating sample daily challenges...")
    
    # Generate today's challenge
    today_challenge = engine.generate_daily_squad()
    
    if today_challenge:
        print("\n✨ TODAY'S CHALLENGE PREVIEW:")
        print(f"   Theme: {today_challenge['theme']}")
        print(f"   Formation: {today_challenge['formation']}")
        print(f"   Difficulty: {today_challenge['difficulty']}/5")
        print(f"   Players from {len(set([p['team'] for p in today_challenge['squad']]))} different teams")
    
    # Generate a week's worth
    weekly_challenges = engine.generate_multiple_challenges(7)
    
    # Step 6: Export final product
    print("\n💾 Step 6: Exporting Super Squadify...")
    
    web_export = engine.export_for_web(weekly_challenges, '/workspaces/CLQ/super_squadify_complete.json')
    
    # Final statistics
    print(f"\n🏆 SUPER SQUADIFY - FINAL STATISTICS:")
    print("="*50)
    print(f"   Total players: {len(formatted_players):,}")
    print(f"   Unique teams: {len(set([p['team'] for p in formatted_players]))}")
    print(f"   Competitions: {', '.join(set([p['competition'] for p in formatted_players]))}")
    print(f"   Seasons covered: {len(set([p['season'] for p in formatted_players if p['season'] != 'Unknown']))}")
    print(f"   Formations available: {len(engine.formations)}")
    print(f"   Daily challenges: Virtually unlimited combinations")
    
    improvement_factor = len(formatted_players) / 101  # Original Squadify had 101 players
    print(f"\n📈 IMPROVEMENT OVER ORIGINAL:")
    print(f"   {improvement_factor:.1f}x more players!")
    print(f"   {len(set([p['team'] for p in formatted_players])) / 11:.1f}x more teams!")
    print(f"   Focus: Exclusively English football (1992-2025)")
    
    return engine, formatted_players, web_export

def estimate_position_from_coordinates(top, left):
    """Estimate playing position from formation coordinates."""
    
    if top >= 75:
        return 'GK'
    elif top >= 55:
        if left <= 25:
            return 'LB'
        elif left >= 65:
            return 'RB'
        else:
            return 'CB'
    elif top >= 25:
        if left <= 25:
            return 'LM'
        elif left >= 65:
            return 'RM'
        elif top >= 40:
            return 'CDM'
        else:
            return 'CAM'
    else:
        if left <= 25:
            return 'LW'
        elif left >= 65:
            return 'RW'
        else:
            return 'ST'

if __name__ == "__main__":
    engine, players, export = build_complete_english_squadify()
    
    print("\n🎮 Super Squadify is ready!")
    print("🔗 Export file: super_squadify_complete.json")
    print("📊 Player database: super_squadify_players.json")
