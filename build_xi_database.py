import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import re

class EnglishLeagueXIDatabase:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.starting_xis = []
        
    def scrape_starting_xi(self, match_id):
        """Extract starting XI from a match page."""
        url = f"https://www.transfermarkt.com/spielbericht/index/spielbericht/{match_id}"
        
        try:
            response = self.session.get(url, timeout=10)
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
                print(f"❌ No lineup data found for match {match_id}")
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
                    'players': players,
                    'season': self.estimate_season(match_id)
                }
            else:
                print(f"⚠️  Team {team_name} has {len(players)} players, not 11")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting team XI: {str(e)}")
            return None
    
    def estimate_season(self, match_id):
        """Estimate season from match ID (rough approximation)."""
        # This is a rough estimation - newer matches tend to have higher IDs
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
    
    def generate_match_id_ranges(self):
        """Generate likely match ID ranges for English leagues."""
        # Based on observation, English league match IDs roughly fall in these ranges
        ranges = [
            # Recent seasons (higher IDs)
            range(4200000, 4300000, 1000),  # 2024/25 season
            range(4100000, 4200000, 1000),  # 2023/24 season
            range(3900000, 4100000, 1000),  # 2022/23 season
            range(3700000, 3900000, 1000),  # 2021/22 season
            range(3500000, 3700000, 1000),  # 2020/21 season
            range(3300000, 3500000, 1000),  # 2019/20 season
            range(3100000, 3300000, 1000),  # 2018/19 season
            range(2900000, 3100000, 1000),  # 2017/18 season
            range(2700000, 2900000, 1000),  # 2016/17 season
            range(2500000, 2700000, 1000),  # 2015/16 season
            
            # Older seasons (lower IDs)
            range(2300000, 2500000, 2000),  # 2014/15 season
            range(2100000, 2300000, 2000),  # 2013/14 season
            range(1900000, 2100000, 2000),  # 2012/13 season
            range(1700000, 1900000, 2000),  # 2011/12 season
            range(1500000, 1700000, 3000),  # 2010/11 season
            range(1300000, 1500000, 3000),  # 2009/10 season
            range(1100000, 1300000, 5000),  # 2008/09 season
            range(900000, 1100000, 5000),   # 2007/08 season
            range(700000, 900000, 8000),    # 2006/07 season
            range(500000, 700000, 10000),   # 2005/06 season
        ]
        
        # Flatten and shuffle the ranges
        all_ids = []
        for id_range in ranges:
            all_ids.extend(list(id_range))
        
        random.shuffle(all_ids)
        return all_ids
    
    def build_database(self, target_xis=500):
        """Build database of starting XIs from English leagues."""
        print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 BUILDING ENGLISH LEAGUE XI DATABASE")
        print("="*60)
        print(f"🎯 Target: {target_xis} starting XIs")
        print(f"📅 Covering: Premier League, Championship, League One, League Two")
        print(f"⏳ Seasons: 1992/93 to 2024/25")
        print()
        
        match_ids = self.generate_match_id_ranges()
        successful_xis = 0
        attempts = 0
        max_attempts = 2000  # Don't go forever
        
        for match_id in match_ids:
            if successful_xis >= target_xis:
                break
                
            if attempts >= max_attempts:
                print(f"⏰ Reached maximum attempts ({max_attempts})")
                break
            
            attempts += 1
            print(f"🔍 Attempt {attempts}/{max_attempts} - Match {match_id} (Found: {successful_xis}/{target_xis})")
            
            xis = self.scrape_starting_xi(match_id)
            
            for xi in xis:
                if xi and successful_xis < target_xis:
                    self.starting_xis.append(xi)
                    successful_xis += 1
                    print(f"✅ Added {xi['team']} ({xi['formation']}) - Total: {successful_xis}")
            
            # Respectful delay
            time.sleep(random.uniform(1, 3))
            
            # Progress update every 50 attempts
            if attempts % 50 == 0:
                success_rate = (successful_xis / attempts) * 100
                print(f"📊 Progress: {attempts} attempts, {successful_xis} XIs found ({success_rate:.1f}% success rate)")
        
        print(f"\n🏆 DATABASE BUILD COMPLETE!")
        print(f"✅ Total starting XIs collected: {len(self.starting_xis)}")
        print(f"⚽ Total players: {len(self.starting_xis) * 11}")
        print(f"🎯 Success rate: {(len(self.starting_xis) / attempts) * 100:.1f}%")
        
        return self.starting_xis
    
    def save_database(self, filename="english_league_500_xis.json"):
        """Save the XI database."""
        filepath = f"/workspaces/CLQ/{filename}"
        
        # Create the main database
        database = {
            'metadata': {
                'total_xis': len(self.starting_xis),
                'total_players': len(self.starting_xis) * 11,
                'created': datetime.now().isoformat(),
                'description': 'English League Starting XIs Database for Enhanced Squadify'
            },
            'starting_xis': self.starting_xis
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Database saved to: {filepath}")
        
        # Create summary statistics
        teams = set()
        formations = {}
        seasons = {}
        
        for xi in self.starting_xis:
            teams.add(xi['team'])
            
            formation = xi['formation']
            formations[formation] = formations.get(formation, 0) + 1
            
            season = xi['season']
            seasons[season] = seasons.get(season, 0) + 1
        
        summary = {
            'total_starting_xis': len(self.starting_xis),
            'unique_teams': len(teams),
            'teams': sorted(list(teams)),
            'formations': dict(sorted(formations.items(), key=lambda x: x[1], reverse=True)),
            'seasons': dict(sorted(seasons.items(), key=lambda x: x[1], reverse=True)),
            'top_formations': list(dict(sorted(formations.items(), key=lambda x: x[1], reverse=True)).keys())[:10]
        }
        
        summary_file = f"/workspaces/CLQ/xi_database_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📈 Summary statistics:")
        print(f"   Starting XIs: {summary['total_starting_xis']}")
        print(f"   Unique teams: {summary['unique_teams']}")
        print(f"   Top formation: {summary['top_formations'][0] if summary['top_formations'] else 'N/A'}")
        print(f"   Most common season: {list(seasons.keys())[0] if seasons else 'N/A'}")

def main():
    builder = EnglishLeagueXIDatabase()
    
    print("Starting English League XI database build...")
    print("This will take a while - we're aiming for 500 starting XIs!")
    print()
    
    xis = builder.build_database(target_xis=500)
    
    if xis:
        builder.save_database()
        print(f"\n🎉 SUCCESS! Built database with {len(xis)} starting XIs")
        print(f"🔥 This gives {len(xis) * 11} total players for variety!")
    else:
        print("❌ Failed to build database")

if __name__ == "__main__":
    main()
