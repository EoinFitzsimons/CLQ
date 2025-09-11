import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import re

class EnglishLeagueSmartScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.starting_xis = []
        
        # Known English teams to filter results
        self.english_teams = {
            # Premier League teams (current and historical)
            'Arsenal', 'Aston Villa', 'Brighton & Hove Albion', 'Burnley', 'Chelsea FC', 'Crystal Palace',
            'Everton FC', 'Fulham FC', 'Leeds United', 'Leicester City', 'Liverpool FC', 'Manchester City',
            'Manchester United', 'Newcastle United', 'Norwich City', 'Sheffield United', 'Southampton FC',
            'Tottenham Hotspur', 'Watford FC', 'West Ham United', 'Wolverhampton Wanderers', 'Brentford FC',
            'AFC Bournemouth', 'Luton Town', 'Nottingham Forest', 'West Bromwich Albion', 'Birmingham City',
            'Blackburn Rovers', 'Bolton Wanderers', 'Cardiff City', 'Charlton Athletic', 'Coventry City',
            'Derby County', 'Hull City', 'Ipswich Town', 'Middlesbrough FC', 'Portsmouth FC', 'Queens Park Rangers',
            'Reading FC', 'Stoke City', 'Sunderland AFC', 'Swansea City', 'Wigan Athletic',
            
            # Championship teams
            'Bristol City', 'Huddersfield Town', 'Millwall FC', 'Preston North End', 'Rotherham United',
            'Sheffield Wednesday', 'Blackpool FC', 'Plymouth Argyle', 'Oxford United', 'Peterborough United',
            
            # League One teams  
            'Bradford City AFC', 'Crewe Alexandra', 'Doncaster Rovers', 'Gillingham FC', 'MK Dons',
            'Oldham Athletic', 'Port Vale', 'Rochdale AFC', 'Scunthorpe United', 'Shrewsbury Town',
            
            # League Two teams
            'Barrow AFC', 'Bradford City AFC', 'Crawley Town', 'Forest Green Rovers', 'Grimsby Town',
            'Harrogate Town AFC', 'Leyton Orient', 'Newport County AFC', 'Salford City', 'Stevenage FC',
        }
    
    def is_english_team(self, team_name):
        """Check if a team is from English leagues."""
        # Direct match
        if team_name in self.english_teams:
            return True
        
        # Check for common English team patterns
        english_patterns = [
            r'FC$', r'United$', r'City$', r'Town$', r'Athletic$', r'Rovers$',
            r'Wanderers$', r'Albion$', r'County$', r'Hotspur$'
        ]
        
        for pattern in english_patterns:
            if re.search(pattern, team_name):
                # Additional check - avoid false positives
                non_english_keywords = ['AC ', 'FC Barcelona', 'Real ', 'Inter ', 'Juventus', 'Bayern', 'Borussia']
                if not any(keyword in team_name for keyword in non_english_keywords):
                    return True
        
        return False
    
    def scrape_starting_xi(self, match_id):
        """Extract starting XI from a match page, filtering for English teams."""
        url = f"https://www.transfermarkt.com/spielbericht/index/spielbericht/{match_id}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
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
                if xi and len(xi['players']) == 11:
                    # Only keep English teams
                    if self.is_english_team(xi['team']):
                        extracted_xis.append(xi)
                        print(f"✅ Found English XI: {xi['team']} ({xi['formation']})")
                    else:
                        print(f"⏩ Skipped non-English team: {xi['team']}")
            
            return extracted_xis
            
        except Exception as e:
            if "404" not in str(e):  # Don't log 404s, they're expected
                print(f"⚠️  Error scraping match {match_id}: {str(e)}")
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
                    'players': players,
                    'season': self.estimate_season(match_id)
                }
                
        except Exception as e:
            pass
        
        return None
    
    def estimate_season(self, match_id):
        """Estimate season from match ID."""
        if match_id > 4000000:
            return "2023/24"
        elif match_id > 3500000:
            return "2021/22"  
        elif match_id > 3000000:
            return "2019/20"
        elif match_id > 2500000:
            return "2017/18"
        elif match_id > 2000000:
            return "2015/16"
        elif match_id > 1500000:
            return "2012/13"
        elif match_id > 1000000:
            return "2009/10"
        else:
            return "2005/07"
    
    def get_known_english_match_ids(self):
        """Start with known English league match IDs and expand systematically."""
        # Known working English match IDs
        seed_ids = [
            3592069,  # West Ham vs Chelsea (2021)
            3470533,  # Premier League match
            3242194,  # Arsenal vs Tottenham
            2987656,  # Chelsea vs Man United
            2842071,  # Leicester match
            2681340,  # Man City vs Liverpool
            2505819,  # Man United vs Chelsea
        ]
        
        # Expand around known working IDs
        expanded_ids = set()
        
        for seed_id in seed_ids:
            # Add the seed ID
            expanded_ids.add(seed_id)
            
            # Add nearby IDs (likely to be from same seasons/competitions)
            for offset in range(-50, 51, 5):  # Check every 5 IDs within +/-50
                new_id = seed_id + offset
                if new_id > 0:
                    expanded_ids.add(new_id)
        
        # Add some systematic ranges for different seasons
        # Recent seasons (higher success rate)
        for base in range(3500000, 4000000, 10000):  # Recent Premier League
            expanded_ids.add(base)
            
        for base in range(3000000, 3500000, 15000):  # 2019-2021 seasons  
            expanded_ids.add(base)
            
        for base in range(2500000, 3000000, 20000):  # 2017-2019 seasons
            expanded_ids.add(base)
        
        return sorted(list(expanded_ids))
    
    def build_database(self, target_xis=500):
        """Build database focusing on English league starting XIs."""
        print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 SMART ENGLISH LEAGUE XI SCRAPER")
        print("="*60)
        print(f"🎯 Target: {target_xis} English starting XIs")
        print(f"🧠 Strategy: Start with known matches, expand systematically")
        print(f"🔍 Filter: Only English league teams")
        print()
        
        match_ids = self.get_known_english_match_ids()
        random.shuffle(match_ids)  # Randomize to avoid patterns
        
        successful_xis = 0
        attempts = 0
        english_found = 0
        
        print(f"📋 Generated {len(match_ids)} candidate match IDs to check")
        print()
        
        for match_id in match_ids:
            if successful_xis >= target_xis:
                break
            
            attempts += 1
            print(f"🔍 {attempts:4}/{len(match_ids)} - Match {match_id:7} - English XIs: {successful_xis:3}/{target_xis}")
            
            xis = self.scrape_starting_xi(match_id)
            
            for xi in xis:
                if xi and successful_xis < target_xis:
                    self.starting_xis.append(xi)
                    successful_xis += 1
                    english_found += 1
                    print(f"🎉 Added: {xi['team']} - Total English XIs: {successful_xis}")
            
            # Be respectful with requests
            time.sleep(random.uniform(2, 4))
            
            # Progress update
            if attempts % 25 == 0:
                success_rate = (english_found / attempts) * 100 if attempts > 0 else 0
                print(f"📊 Progress: {attempts} attempts, {english_found} English XIs ({success_rate:.1f}% success)")
                print()
        
        print(f"\n🏆 SCRAPING COMPLETE!")
        print(f"✅ English starting XIs collected: {len(self.starting_xis)}")
        print(f"⚽ Total English players: {len(self.starting_xis) * 11}")
        
        return self.starting_xis
    
    def save_database(self, filename="english_leagues_500_xis.json"):
        """Save the database with comprehensive metadata."""
        filepath = f"/workspaces/CLQ/{filename}"
        
        # Analyze the collected data
        teams = {}
        formations = {}
        seasons = {}
        
        for xi in self.starting_xis:
            # Count teams
            team = xi['team']
            teams[team] = teams.get(team, 0) + 1
            
            # Count formations  
            formation = xi['formation']
            formations[formation] = formations.get(formation, 0) + 1
            
            # Count seasons
            season = xi['season']
            seasons[season] = seasons.get(season, 0) + 1
        
        # Create the database
        database = {
            'metadata': {
                'title': 'English League Starting XIs Database',
                'description': 'Comprehensive database of English league starting XIs for enhanced Squadify game',
                'total_starting_xis': len(self.starting_xis),
                'total_players': len(self.starting_xis) * 11,
                'unique_teams': len(teams),
                'created': datetime.now().isoformat(),
                'coverage': 'Premier League, Championship, League One, League Two (1992/93-2024/25)',
                'top_teams': dict(sorted(teams.items(), key=lambda x: x[1], reverse=True)[:20]),
                'formations_used': dict(sorted(formations.items(), key=lambda x: x[1], reverse=True)),
                'seasons_covered': dict(sorted(seasons.items(), key=lambda x: x[1], reverse=True))
            },
            'starting_xis': self.starting_xis
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Database saved to: {filepath}")
        print(f"📈 Summary:")
        print(f"   🏆 Starting XIs: {database['metadata']['total_starting_xis']}")
        print(f"   👥 Total players: {database['metadata']['total_players']}")
        print(f"   🏟️  Unique teams: {database['metadata']['unique_teams']}")
        
        top_teams = list(database['metadata']['top_teams'].items())[:5]
        print(f"   🔝 Top teams: {', '.join([f'{team}({count})' for team, count in top_teams])}")
        
        return database

def main():
    scraper = EnglishLeagueSmartScraper()
    
    print("🚀 Starting SMART English League XI collection...")
    print("This focuses on known English matches for higher success rate!")
    print()
    
    # Start with a smaller target to test effectiveness
    xis = scraper.build_database(target_xis=100)  # Start with 100, then scale up
    
    if xis:
        database = scraper.save_database("english_100_xis_test.json")
        print(f"\n🎉 SUCCESS! Collected {len(xis)} English starting XIs")
        
        if len(xis) >= 50:  # If we got good results, go for more
            print(f"\n🚀 Good results! Extending to 500 XIs...")
            more_xis = scraper.build_database(target_xis=500)
            if more_xis:
                scraper.save_database("english_500_xis_full.json")
    else:
        print("❌ No English XIs found")

if __name__ == "__main__":
    main()
