import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime

class EnglishLeaguesScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Transfermarkt league IDs for English football
        self.leagues = {
            'Premier League': 'GB1',
            'Championship': 'GB2', 
            'League One': 'GB3',
            'League Two': 'GB4'
        }
        
        self.all_squads = []
    
    def get_season_teams(self, league_id, season):
        """Get all teams from a specific league season."""
        print(f"🏈 Fetching teams from {league_id} season {season}")
        
        # Transfermarkt table URL format
        url = f"https://www.transfermarkt.com/premier-league/tabelle/wettbewerb/{league_id}?saison_id={season}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find team links in the league table
            teams = []
            table = soup.find('table', {'class': 'items'})
            
            if table:
                rows = table.find_all('tr', {'class': ['odd', 'even']})
                for row in rows:
                    team_cell = row.find('td', {'class': 'hauptlink'})
                    if team_cell:
                        team_link = team_cell.find('a')
                        if team_link:
                            team_name = team_link.get_text(strip=True)
                            team_url = team_link.get('href')
                            teams.append({
                                'name': team_name,
                                'url': f"https://www.transfermarkt.com{team_url}",
                                'season': season,
                                'league': league_id
                            })
            
            print(f"   Found {len(teams)} teams")
            return teams
            
        except Exception as e:
            print(f"   ❌ Error fetching teams for {league_id} {season}: {e}")
            return []
    
    def get_team_squad(self, team_info):
        """Get squad for a specific team and season."""
        team_name = team_info['name']
        season = team_info['season']
        
        print(f"   👥 Fetching squad for {team_name} ({season})")
        
        # Extract team ID from URL and build squad URL
        try:
            team_id = team_info['url'].split('/verein/')[1].split('/')[0]
            squad_url = f"https://www.transfermarkt.com/{team_name.lower().replace(' ', '-')}/kader/verein/{team_id}/saison_id/{season}"
            
            response = self.session.get(squad_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find squad table
            squad_table = soup.find('table', {'class': 'items'})
            players = []
            
            if squad_table:
                rows = squad_table.find_all('tr', {'class': ['odd', 'even']})
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        # Extract player info
                        number_cell = cells[0]
                        name_cell = cells[1] 
                        position_cell = cells[2]
                        
                        number = number_cell.get_text(strip=True)
                        
                        # Get player name from link
                        name_link = name_cell.find('a')
                        if name_link:
                            player_name = name_link.get_text(strip=True)
                            player_id = name_link.get('href', '').split('/')[1] if name_link.get('href') else ''
                            
                            position = position_cell.get_text(strip=True)
                            
                            players.append({
                                'name': player_name,
                                'number': number,
                                'position': position,
                                'player_id': player_id,
                                'team': team_name,
                                'season': season,
                                'league': team_info['league']
                            })
            
            print(f"      ✅ Found {len(players)} players for {team_name}")
            return players
            
        except Exception as e:
            print(f"      ❌ Error fetching squad for {team_name}: {e}")
            return []
    
    def scrape_english_leagues(self, start_season=1992, end_season=2024):
        """Scrape all English leagues from start to end season."""
        print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLISH FOOTBALL LEAGUES SCRAPER")
        print("="*60)
        
        total_squads = 0
        
        for season in range(start_season, end_season + 1):
            season_str = f"{season}"
            print(f"\n📅 Processing season {season}/{season+1}")
            
            for league_name, league_id in self.leagues.items():
                print(f"\n🏆 {league_name} ({league_id})")
                
                # Get teams for this league/season
                teams = self.get_season_teams(league_id, season_str)
                
                if not teams:
                    continue
                
                # Get squad for each team
                for team in teams[:3]:  # Limit to first 3 teams per league for testing
                    squad = self.get_team_squad(team)
                    
                    if squad:
                        squad_info = {
                            'team': team['name'],
                            'season': f"{season}/{season+1}",
                            'league': league_name,
                            'players': squad,
                            'total_players': len(squad)
                        }
                        
                        self.all_squads.append(squad_info)
                        total_squads += 1
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                
                # Longer pause between leagues
                time.sleep(random.uniform(2, 4))
            
            # Break after first season for testing
            if season >= start_season:
                break
        
        print(f"\n✅ Scraping complete!")
        print(f"📊 Total squads collected: {total_squads}")
        
        return self.all_squads
    
    def save_data(self, filename="english_football_squads.json"):
        """Save collected squad data to JSON file."""
        if self.all_squads:
            with open(f"/workspaces/CLQ/{filename}", 'w') as f:
                json.dump(self.all_squads, f, indent=2)
            
            print(f"💾 Saved {len(self.all_squads)} squads to {filename}")
            
            # Print summary
            total_players = sum(squad['total_players'] for squad in self.all_squads)
            leagues = set(squad['league'] for squad in self.all_squads)
            seasons = set(squad['season'] for squad in self.all_squads)
            
            print(f"\n📈 DATA SUMMARY:")
            print(f"   Total squads: {len(self.all_squads)}")
            print(f"   Total players: {total_players}")
            print(f"   Leagues covered: {len(leagues)}")
            print(f"   Seasons covered: {len(seasons)}")

if __name__ == "__main__":
    scraper = EnglishLeaguesScraper()
    
    # Test with just 1992/93 season first
    squads = scraper.scrape_english_leagues(start_season=1992, end_season=1992)
    scraper.save_data()
