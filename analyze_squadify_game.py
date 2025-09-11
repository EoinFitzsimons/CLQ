import json

def analyze_squadify_data():
    """Analyze the extracted Squadify player data to understand game mechanics."""
    
    print("🏆 SQUADIFY GAME ANALYSIS")
    print("="*60)
    
    # Load the extracted data
    with open('/workspaces/CLQ/squadify_players.json', 'r') as f:
        players = json.load(f)
    
    print(f"📊 Total players in database: {len(players)}")
    
    # Analyze teams and seasons
    teams_seasons = {}
    for player in players:
        key = f"{player['team']} {player['season']}"
        if key not in teams_seasons:
            teams_seasons[key] = []
        teams_seasons[key].append(player)
    
    print(f"\n🏈 TEAMS & SEASONS:")
    print("-" * 40)
    for team_season, squad in teams_seasons.items():
        print(f"   {team_season}: {len(squad)} players")
    
    # Analyze formations for each team
    print(f"\n⚽ FORMATION ANALYSIS BY TEAM:")
    print("-" * 40)
    
    for team_season, squad in teams_seasons.items():
        # Count players by position zones
        gk = len([p for p in squad if p['position_top'] >= 80])
        def_line = len([p for p in squad if 60 <= p['position_top'] < 80])
        mid_line = len([p for p in squad if 25 <= p['position_top'] < 60])
        att_line = len([p for p in squad if p['position_top'] < 25])
        
        print(f"   {team_season:20} -> GK:{gk} DEF:{def_line} MID:{mid_line} ATT:{att_line}")
    
    # Daily Challenge Mechanism Analysis
    print(f"\n📅 DAILY CHALLENGE MECHANICS:")
    print("-" * 40)
    
    print("   🎯 How it works:")
    print("   • Each day at 12:00 EST, a new squad is selected")
    print("   • Players must correctly identify all 11 players")
    print("   • Formation and positions are shown as visual hints")
    print("   • Game state is stored in localStorage")
    print("   • Multiple historic squads are available in rotation")
    
    # Position mapping analysis
    print(f"\n🎯 POSITION COORDINATE SYSTEM:")
    print("-" * 40)
    
    # Analyze the coordinate system
    all_tops = sorted(set([p['position_top'] for p in players]))
    all_lefts = sorted(set([p['position_left'] for p in players]))
    
    print(f"   Top positions (Y-axis): {all_tops}")
    print(f"   Left positions (X-axis): {all_lefts}")
    
    # Map common positions
    position_map = {
        (40, 80): "Goalkeeper",
        (28, 63): "Left Center-back",
        (55, 35): "Right Center-back", 
        (73, 61): "Right-back",
        (15, 61): "Left-back",
        (40, 43): "Defensive Midfielder",
        (28, 43): "Left Central Midfielder",
        (52, 43): "Right Central Midfielder",
        (40, 23): "Attacking Midfielder",
        (15, 18): "Left Winger",
        (65, 18): "Right Winger",
        (40, 3): "Striker",
        (30, 2): "Left Striker",
        (50, 2): "Right Striker"
    }
    
    print(f"\n📍 COMMON POSITION MAPPINGS:")
    print("-" * 40)
    for (left, top), position in position_map.items():
        count = len([p for p in players if p['position_left'] == left and p['position_top'] == top])
        if count > 0:
            print(f"   ({left:2}, {top:2}) -> {position:20} ({count} players)")
    
    # Identify the current daily squad (most likely the first one - Spurs 15/16)
    spurs_squad = [p for p in players if p['team'] == 'Spurs' and p['season'] == '15/16']
    
    print(f"\n🏃‍♂️ TODAY'S CHALLENGE - TOTTENHAM 15/16:")
    print("-" * 40)
    
    # Sort by position for formation display
    formation_lines = {
        'GK': [p for p in spurs_squad if p['position_top'] >= 80],
        'DEF': [p for p in spurs_squad if 60 <= p['position_top'] < 80],
        'MID': [p for p in spurs_squad if 25 <= p['position_top'] < 60],
        'ATT': [p for p in spurs_squad if p['position_top'] < 25]
    }
    
    for line_name, line_players in formation_lines.items():
        if line_players:
            print(f"   {line_name}: ", end="")
            sorted_players = sorted(line_players, key=lambda x: x['position_left'])
            for player in sorted_players:
                print(f"{player['name']} ({player['number']}), ", end="")
            print()
    
    # Game difficulty analysis
    print(f"\n🎮 GAME DIFFICULTY FACTORS:")
    print("-" * 40)
    
    # Count unique names across all teams
    all_names = set([p['name'].lower() for p in players])
    duplicate_names = []
    for name in all_names:
        count = len([p for p in players if p['name'].lower() == name])
        if count > 1:
            duplicate_names.append((name, count))
    
    print(f"   • Total unique players: {len(all_names)}")
    print(f"   • Players appearing in multiple teams: {len(duplicate_names)}")
    if duplicate_names:
        print("   Duplicate players:")
        for name, count in sorted(duplicate_names, key=lambda x: x[1], reverse=True)[:5]:
            print(f"     - {name}: {count} teams")
    
    return players, teams_seasons

if __name__ == "__main__":
    players, teams = analyze_squadify_data()
