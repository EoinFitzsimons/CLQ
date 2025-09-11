import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import re

class EnglishLeagueFixtureScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # English league competition codes on Transfermarkt
        self.leagues = {
            'Premier League': 'GB1',
            'Championship': 'GB2', 
            'League One': 'GB3',
            'League Two': 'GB4'
        }
        
        self.starting_xis = []
        
    def get_season_fixtures(self, league_code, season_year):
        """Get all match IDs for a specific league and season."""
        match_ids = []
        
        # Try different matchdays (usually 1-38 for Premier League, 1-46 for others)
        max_matchdays = 38 if league_code == 'GB1' else 46
        
        for matchday in range(1, max_matchdays + 1):
            fixture_url = f"https://www.transfermarkt.com/premier-league/gesamtspielplan/wettbewerb/{league_code}"
            params = {
                'saison_id': season_year,
                'spieltagVon': matchday,
                'spieltagBis': matchday
            }
            
            try:
                print(f"🔍 Fetching {league_code} season {season_year}, matchday {matchday}")
                
                response = self.session.get(fixture_url, params=params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for match result links with class "ergebnis-link"  
                match_links = soup.find_all('a', class_='ergebnis-link')
                
                for link in match_links:
                    # Get match ID from the id attribute
                    match_id = link.get('id')
                    if match_id and match_id.isdigit():
                        match_id = int(match_id)
                        if match_id not in match_ids:
                            match_ids.append(match_id)
                    
                    # Also check href as backup
                    href = link.get('href', '')
                    match_id_search = re.search(r'/spielbericht/(\d+)', href)
                    if match_id_search:
                        match_id = int(match_id_search.group(1))
                        if match_id not in match_ids:
                            match_ids.append(match_id)
                
                print(f"✅ Found {len(match_links)} matches on matchday {matchday}")
                
                # Be respectful with delays
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"❌ Error fetching matchday {matchday}: {str(e)}")
                continue
        
        print(f"📊 Total match IDs found for {league_code} {season_year}: {len(match_ids)}")
        return match_ids
    
    def scrape_starting_xi(self, match_id):
        """Extract starting XI from a match page."""
        url = f"https://www.transfermarkt.com/spielbericht/index/spielbericht/{match_id}"
        
        try:
            max_retries = 3
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10  # 10, 20, 30 seconds
                        print(f"⏰ Timeout on attempt {attempt + 1}, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"⚠️  Request error on attempt {attempt + 1}, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
            
            if response is None:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the Line-Ups box
            lineup_box = None
            boxes = soup.find_all('div', class_='box')
            for box in boxes:
                h2 = box.find('h2', class_='content-box-headline')
                if h2 and 'Line-Ups' in h2.get_text():
                    lineup_box = box
                    break
            
            if not lineup_box:
                return []
            
            # Extract both team lineups
            team_boxes = lineup_box.find_all('div', class_='large-6')
            
            extracted_xis = []
            for i, team_box in enumerate(team_boxes):
                if i >= 2:  # Only process first 2 teams
                    break
                    
                xi = self.extract_team_xi(team_box, match_id)
                if xi and len(xi['players']) == 11:  # Must be exactly 11 players
                    extracted_xis.append(xi)
            
            return extracted_xis
            
        except Exception as e:
            print(f"❌ Error scraping match {match_id}: {str(e)}")
            return []
    
    def extract_team_xi(self, team_box, match_id):
        """Extract starting XI for one team."""
        try:
            # Get team name
            team_link = team_box.find('a', class_='sb-vereinslink')
            team_name = team_link.get_text(strip=True) if team_link else "Unknown Team"
            
            # Get formation
            formation_element = team_box.find('div', class_='formation-subtitle')
            formation = "4-4-2"  # Default
            if formation_element:
                formation_text = formation_element.get_text()
                formation_match = re.search(r'(\d-\d-\d(?:-\d)?)', formation_text)
                if formation_match:
                    formation = formation_match.group(1)
            
            # Extract players from formation positions
            players = []
            formation_containers = team_box.find_all('div', class_='formation-player-container')
            
            for container in formation_containers:
                # Get shirt number
                number_div = container.find('div', class_='tm-shirt-number')
                shirt_number = number_div.get_text(strip=True) if number_div else "0"
                
                # Get player name and link
                name_link = container.find('a', href=re.compile(r'/profil/spieler/'))
                if name_link:
                    player_name = name_link.get_text(strip=True)
                    player_id = re.search(r'/profil/spieler/(\d+)', name_link['href'])
                    player_id = player_id.group(1) if player_id else None
                    
                    # Get position from style (top/left coordinates)
                    style = container.get('style', '')
                    top_match = re.search(r'top:\s*(\d+)%', style)
                    left_match = re.search(r'left:\s*(\d+)%', style)
                    
                    position_top = int(top_match.group(1)) if top_match else 50
                    position_left = int(left_match.group(1)) if left_match else 50
                    
                    players.append({
                        'name': player_name,
                        'number': shirt_number,
                        'id': player_id,
                        'position_top': position_top,
                        'position_left': position_left
                    })
            
            if len(players) == 11:  # Valid starting XI
                return {
                    'team': team_name,
                    'formation': formation,
                    'match_id': match_id,
                    'players': players
                }
            else:
                return None
                
        except Exception as e:
            return None
    
    def build_comprehensive_database(self, target_xis=500):
        """Build database by systematically going through English leagues."""
        print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 BUILDING COMPREHENSIVE ENGLISH LEAGUE DATABASE")
        print("="*70)
        print(f"🎯 Target: {target_xis} starting XIs")
        print(f"📅 Method: Systematic league fixture scraping")
        print()
        
        # Define seasons to scrape (recent years first for better success rate)
        seasons = [2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012]
        
        total_xis = 0
        
        for league_name, league_code in self.leagues.items():
            print(f"\n🏆 PROCESSING {league_name.upper()} ({league_code})")
            print("-" * 50)
            
            for season in seasons:
                if total_xis >= target_xis:
                    print(f"🎯 Reached target of {target_xis} XIs!")
                    break
                
                print(f"📅 Season {season}/{season+1}")
                
                # Get all match IDs for this league/season
                match_ids = self.get_season_fixtures(league_code, season)
                
                if not match_ids:
                    print(f"❌ No matches found for {league_name} {season}/{season+1}")
                    continue
                
                print(f"⚽ Processing {len(match_ids)} matches...")
                
                # Process matches (sample if too many)
                if len(match_ids) > 50:  # Don't overwhelm - sample from the season
                    match_ids = random.sample(match_ids, 50)
                
                for i, match_id in enumerate(match_ids):
                    if total_xis >= target_xis:
                        break
                    
                    print(f"🔍 Match {i+1}/{len(match_ids)}: {match_id} (Total XIs: {total_xis})")
                    
                    xis = self.scrape_starting_xi(match_id)
                    
                    for xi in xis:
                        if xi and total_xis < target_xis:
                            xi['league'] = league_name
                            xi['season'] = f"{season}/{season+1}"
                            self.starting_xis.append(xi)
                            total_xis += 1
                            print(f"✅ Added {xi['team']} ({xi['formation']}) - Total: {total_xis}")
                    
            # Longer delay to avoid rate limiting
            time.sleep(random.uniform(3, 8))
            print(f"📊 {league_name} {season}/{season+1}: Added XIs, total now {total_xis}")
            
            if total_xis >= target_xis:
                    break
            
            if total_xis >= target_xis:
                break
        
        print(f"\n🏆 DATABASE BUILD COMPLETE!")
        print(f"✅ Total starting XIs: {len(self.starting_xis)}")
        print(f"⚽ Total players: {len(self.starting_xis) * 11}")
        
        return self.starting_xis
    
    def save_database(self, filename="english_league_500_xis.json"):
        """Save the comprehensive XI database."""
        filepath = f"/workspaces/CLQ/{filename}"
        
        database = {
            'metadata': {
                'total_xis': len(self.starting_xis),
                'total_players': len(self.starting_xis) * 11,
                'created': datetime.now().isoformat(),
                'description': 'Comprehensive English League Starting XIs Database',
                'leagues_covered': list(self.leagues.keys())
            },
            'starting_xis': self.starting_xis
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Database saved to: {filepath}")
        
        # Statistics
        leagues = {}
        teams = set()
        formations = {}
        
        for xi in self.starting_xis:
            league = xi.get('league', 'Unknown')
            leagues[league] = leagues.get(league, 0) + 1
            teams.add(xi['team'])
            formation = xi['formation']
            formations[formation] = formations.get(formation, 0) + 1
        
        print(f"\n📈 FINAL STATISTICS:")
        print(f"   Starting XIs: {len(self.starting_xis)}")
        print(f"   Total players: {len(self.starting_xis) * 11}")
        print(f"   Unique teams: {len(teams)}")
        print(f"   League breakdown:")
        for league, count in leagues.items():
            print(f"     {league}: {count} XIs")
        print(f"   Top formations: {list(dict(sorted(formations.items(), key=lambda x: x[1], reverse=True)).keys())[:5]}")

def main():
    scraper = EnglishLeagueFixtureScraper()
    
    print("🚀 Starting systematic English league scraping...")
    print("This approach goes through official league fixtures!")
    print()
    
    xis = scraper.build_comprehensive_database(target_xis=500)
    
    if xis:
        scraper.save_database()
    else:
        print("❌ No XIs collected")

if __name__ == "__main__":
    main()
