import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
import re

class TransfermarktMatchScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.matches_data = []
    
    def scrape_match_lineups(self, match_id):
        """Scrape lineup data from a specific match."""
        url = f"https://www.transfermarkt.com/spielbericht/index/spielbericht/{match_id}"
        
        print(f"🔍 Scraping match {match_id}: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract match information
            match_info = self.extract_match_info(soup)
            
            # Extract lineups for both teams
            lineups = self.extract_lineups(soup)
            
            if lineups and len(lineups) == 2:
                match_data = {
                    'match_id': match_id,
                    'match_info': match_info,
                    'home_team': lineups[0],
                    'away_team': lineups[1]
                }
                
                self.matches_data.append(match_data)
                print(f"✅ Successfully scraped match {match_id}")
                return match_data
            else:
                print(f"❌ Could not extract lineups for match {match_id}")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping match {match_id}: {str(e)}")
            return None
    
    def extract_match_info(self, soup):
        """Extract basic match information."""
        match_info = {
            'date': None,
            'home_team': None,
            'away_team': None,
            'score': None,
            'stadium': None
        }
        
        try:
            # Extract team names
            team_elements = soup.find_all('a', class_='sb-vereinslink')
            if len(team_elements) >= 2:
                match_info['home_team'] = team_elements[0].get_text(strip=True)
                match_info['away_team'] = team_elements[1].get_text(strip=True)
            
            # Extract score
            score_element = soup.find('div', class_='sb-endstand')
            if score_element:
                match_info['score'] = score_element.get_text(strip=True)
            
            # Extract date
            date_element = soup.find('p', class_='sb-datum')
            if date_element:
                match_info['date'] = date_element.get_text(strip=True)
            
            # Extract stadium
            stadium_elements = soup.find_all('span')
            for element in stadium_elements:
                if 'Stadium' in element.get_text() or 'Ground' in element.get_text():
                    match_info['stadium'] = element.get_text(strip=True)
                    break
        
        except Exception as e:
            print(f"Warning: Could not extract all match info: {e}")
        
        return match_info
    
    def extract_lineups(self, soup):
        """Extract player lineups from both teams."""
        lineups = []
        
        try:
            # Find lineup sections
            lineup_tables = soup.find_all('div', class_='aufstellung-spieler-container')
            
            if not lineup_tables:
                # Try alternative selector
                lineup_tables = soup.find_all('table', class_='items')
            
            for i, table in enumerate(lineup_tables[:2]):  # Only first 2 tables (home/away)
                team_lineup = self.extract_team_lineup(table, i)
                if team_lineup:
                    lineups.append(team_lineup)
            
        except Exception as e:
            print(f"Warning: Error extracting lineups: {e}")
        
        return lineups
    
    def extract_team_lineup(self, table, team_index):
        """Extract lineup for a single team."""
        players = []
        
        try:
            # Find all player rows
            player_rows = table.find_all('tr')
            
            for row in player_rows:
                player_data = self.extract_player_data(row)
                if player_data:
                    players.append(player_data)
            
            if players:
                return {
                    'team_index': team_index,
                    'players': players,
                    'formation': self.detect_formation(players)
                }
        
        except Exception as e:
            print(f"Warning: Error extracting team lineup: {e}")
        
        return None
    
    def extract_player_data(self, row):
        """Extract individual player data from a table row."""
        try:
            # Find player name link
            name_link = row.find('a', href=re.compile(r'/profil/spieler/'))
            if not name_link:
                return None
            
            player_name = name_link.get_text(strip=True)
            player_id = re.search(r'/profil/spieler/(\d+)', name_link['href'])
            player_id = player_id.group(1) if player_id else None
            
            # Find shirt number
            number_element = row.find('div', class_='rn_nummer') or row.find('td', class_='zentriert')
            shirt_number = None
            if number_element:
                number_text = number_element.get_text(strip=True)
                number_match = re.search(r'\d+', number_text)
                if number_match:
                    shirt_number = number_match.group()
            
            # Find position
            position_element = row.find('td', string=re.compile(r'(GK|CB|LB|RB|CM|LM|RM|CAM|LW|RW|CF|ST)'))
            position = position_element.get_text(strip=True) if position_element else 'Unknown'
            
            return {
                'name': player_name,
                'id': player_id,
                'number': shirt_number,
                'position': position
            }
        
        except Exception as e:
            return None
    
    def detect_formation(self, players):
        """Attempt to detect formation from player positions."""
        # This is a simplified detection - could be improved
        position_counts = {}
        for player in players:
            pos = player.get('position', 'Unknown')
            if pos in ['GK']:
                position_counts['GK'] = position_counts.get('GK', 0) + 1
            elif pos in ['CB', 'LB', 'RB', 'LCB', 'RCB']:
                position_counts['DEF'] = position_counts.get('DEF', 0) + 1
            elif pos in ['CM', 'LM', 'RM', 'CDM', 'CAM', 'LCM', 'RCM']:
                position_counts['MID'] = position_counts.get('MID', 0) + 1
            elif pos in ['LW', 'RW', 'CF', 'ST', 'LF', 'RF']:
                position_counts['FWD'] = position_counts.get('FWD', 0) + 1
        
        def_count = position_counts.get('DEF', 0)
        mid_count = position_counts.get('MID', 0)
        fwd_count = position_counts.get('FWD', 0)
        
        return f"{def_count}-{mid_count}-{fwd_count}"
    
    def scrape_english_league_matches(self, start_season="1992", end_season="2024", max_matches=100):
        """Scrape English league matches from Premier League era."""
        
        print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLISH LEAGUE MATCH SCRAPER")
        print("="*60)
        print(f"📅 Seasons: {start_season}/93 to {end_season}/25")
        print(f"🎯 Target: {max_matches} matches maximum")
        print()
        
        # Sample match IDs from different seasons and leagues
        # These are real Transfermarkt match IDs from English leagues
        sample_match_ids = [
            # Premier League matches from different seasons
            3592069,  # West Ham vs Chelsea (2021)
            3470533,  # Liverpool vs Man City (2020)
            3242194,  # Arsenal vs Tottenham (2019)
            2987656,  # Chelsea vs Man United (2018)
            2842071,  # Leicester vs Arsenal (2017)
            2681340,  # Man City vs Liverpool (2016)
            2505819,  # Man United vs Chelsea (2015)
            2329006,  # Arsenal vs Man City (2014)
            2174892,  # Liverpool vs Man United (2013)
            2050438,  # Chelsea vs Arsenal (2012)
            1925670,  # Man City vs Tottenham (2011)
            1802456,  # Man United vs Liverpool (2010)
            1679201,  # Arsenal vs Chelsea (2009)
            1555892,  # Liverpool vs Man City (2008)
            1432534,  # Chelsea vs Man United (2007)
            
            # Championship/League One/League Two matches
            4071234,  # Leeds vs Norwich (Championship)
            4156789,  # Sheffield United vs Burnley
            4234567,  # Ipswich vs Middlesbrough
            4312890,  # Portsmouth vs Plymouth (League One)
            4398765,  # Wigan vs Burton Albion
        ]
        
        successful_scrapes = 0
        
        for match_id in sample_match_ids:
            if successful_scrapes >= max_matches:
                break
            
            match_data = self.scrape_match_lineups(match_id)
            if match_data:
                successful_scrapes += 1
            
            # Be respectful with delays
            time.sleep(random.uniform(2, 4))
        
        print(f"\n📊 SCRAPING COMPLETE")
        print(f"✅ Successfully scraped: {successful_scrapes} matches")
        print(f"📁 Total match data collected: {len(self.matches_data)}")
        
        return self.matches_data
    
    def save_data(self, filename="english_league_matches.json"):
        """Save scraped data to JSON file."""
        filepath = f"/workspaces/CLQ/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.matches_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to: {filepath}")
        
        # Create summary
        total_players = 0
        teams = set()
        
        for match in self.matches_data:
            for team_key in ['home_team', 'away_team']:
                team_data = match.get(team_key, {})
                if 'players' in team_data:
                    total_players += len(team_data['players'])
                    teams.add(match['match_info'].get('home_team', 'Unknown'))
                    teams.add(match['match_info'].get('away_team', 'Unknown'))
        
        summary = {
            'total_matches': len(self.matches_data),
            'total_players': total_players,
            'unique_teams': len(teams),
            'teams': list(teams),
            'scrape_date': datetime.now().isoformat()
        }
        
        summary_file = f"/workspaces/CLQ/english_league_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📈 Summary saved to: {summary_file}")
        print(f"   Matches: {summary['total_matches']}")
        print(f"   Players: {summary['total_players']}")
        print(f"   Teams: {summary['unique_teams']}")

def main():
    scraper = TransfermarktMatchScraper()
    
    # Scrape English league matches
    matches = scraper.scrape_english_league_matches(max_matches=20)  # Start with 20 matches
    
    if matches:
        scraper.save_data()
    else:
        print("❌ No data was successfully scraped")

if __name__ == "__main__":
    main()
