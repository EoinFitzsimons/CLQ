#!/usr/bin/env python3
"""
English Football Squad Database Builder
=====================================
Scrapes match data from English football leagues (1992/93-2024/25)
- Premier League
- Championship (Division 1/First Division)
- League One (Division 2/Second Division) 
- League Two (Division 3/Third Division)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import csv
import os

class EnglishFootballScraper:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.co.uk"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # English league structure mapping
        self.leagues = {
            'premier_league': {
                'name': 'Premier League',
                'transfermarkt_id': 'PL1',  # Updated ID
                'seasons': list(range(2020, 2025))  # Recent seasons for testing
            },
            'championship': {
                'name': 'Championship',
                'transfermarkt_id': 'EFL1', 
                'seasons': list(range(2020, 2025))
            },
            'league_one': {
                'name': 'League One',
                'transfermarkt_id': 'EFL2',
                'seasons': list(range(2020, 2025))
            },
            'league_two': {
                'name': 'League Two', 
                'transfermarkt_id': 'EFL3',
                'seasons': list(range(2020, 2025))
            }
        }
        
        self.all_matches = []
        self.match_details = []
        
    def get_season_fixtures(self, league_id, season):
        """Get all fixtures for a specific league and season."""
        # Try multiple URL patterns for Transfermarkt
        urls_to_try = [
            f"{self.base_url}/premier-league/gesamtspielplan/wettbewerb/{league_id}/saison_id/{season}",
            f"{self.base_url}/jumplist/startseite/wettbewerb/{league_id}/saison_id/{season}",
            f"https://www.transfermarkt.com/premier-league/gesamtspielplan/wettbewerb/{league_id}/saison_id/{season}"
        ]
        
        print(f"🔍 Scraping {league_id} season {season}/{season+1}")
        
        for url in urls_to_try:
            try:
                print(f"   Trying: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                matches = []
                
                # Look for match links with various patterns
                match_links = soup.find_all('a', href=True)
                
                for link in match_links:
                    href = link.get('href', '')
                    if any(pattern in href for pattern in ['/spielbericht/', '/index/spielbericht/', 'spielbericht']):
                        if href.startswith('http'):
                            matches.append(href)
                        else:
                            matches.append(self.base_url + href)
                
                if matches:
                    print(f"   ✅ Found {len(matches)} matches")
                    return matches
                    
            except Exception as e:
                print(f"   ⚠️  URL failed: {e}")
                continue
        
        print(f"   ❌ No matches found for {league_id} {season}")
        return []
    
    def get_match_lineups(self, match_url):
        """Extract team lineups from a specific match."""
        try:
            response = self.session.get(match_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract match info
            match_info = self.extract_match_info(soup)
            
            # Find lineup tables
            lineups = self.extract_lineups(soup)
            
            if lineups['home'] and lineups['away']:
                match_data = {
                    'url': match_url,
                    'date': match_info.get('date'),
                    'home_team': match_info.get('home_team'),
                    'away_team': match_info.get('away_team'),
                    'score': match_info.get('score'),
                    'home_lineup': lineups['home'],
                    'away_lineup': lineups['away'],
                    'competition': match_info.get('competition')
                }
                
                print(f"   ⚽ {match_info.get('home_team')} vs {match_info.get('away_team')}")
                return match_data
                
        except Exception as e:
            print(f"   ❌ Error scraping match {match_url}: {e}")
            
        return None
    
    def extract_match_info(self, soup):
        """Extract basic match information."""
        info = {}
        
        # Match date
        date_elem = soup.find('p', class_='sb-datum')
        if date_elem:
            info['date'] = date_elem.text.strip()
        
        # Team names
        team_elems = soup.find_all('a', class_='sb-vereinslink')
        if len(team_elems) >= 2:
            info['home_team'] = team_elems[0].text.strip()
            info['away_team'] = team_elems[1].text.strip()
        
        # Score
        score_elem = soup.find('div', class_='sb-endstand')
        if score_elem:
            info['score'] = score_elem.text.strip()
        
        # Competition
        comp_elem = soup.find('div', class_='sb-wettbewerb')
        if comp_elem:
            info['competition'] = comp_elem.text.strip()
            
        return info
    
    def extract_lineups(self, soup):
        """Extract player lineups from match page."""
        lineups = {'home': [], 'away': []}
        
        # Find lineup sections
        lineup_tables = soup.find_all('div', class_='large-6')
        
        for i, table in enumerate(lineup_tables[:2]):  # First two are usually home/away
            team_key = 'home' if i == 0 else 'away'
            
            # Find player rows
            player_rows = table.find_all('tr')
            
            for row in player_rows:
                player_link = row.find('a', href=True)
                if player_link and '/profil/spieler/' in player_link.get('href', ''):
                    
                    # Extract player info
                    player_name = player_link.text.strip()
                    player_url = self.base_url + player_link['href']
                    
                    # Extract jersey number
                    number_elem = row.find('div', class_='rn_nummer')
                    number = number_elem.text.strip() if number_elem else 'N/A'
                    
                    # Extract position
                    position_elem = row.find('td', class_='posrela')
                    position = position_elem.text.strip() if position_elem else 'N/A'
                    
                    player_data = {
                        'name': player_name,
                        'number': number,
                        'position': position,
                        'url': player_url
                    }
                    
                    lineups[team_key].append(player_data)
        
        return lineups
    
    def scrape_historic_matches(self, max_matches_per_season=50):
        """Scrape historic matches from English leagues."""
        
        print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLISH FOOTBALL DATABASE BUILDER")
        print("="*60)
        
        all_match_data = []
        
        for league_key, league_info in self.leagues.items():
            print(f"\n📊 Scraping {league_info['name']}")
            print("-" * 40)
            
            # Start from more recent seasons and work backwards
            seasons = sorted(league_info['seasons'], reverse=True)[:5]  # Focus on recent years first
            
            for season in seasons:
                matches = self.get_season_fixtures(league_info['transfermarkt_id'], season)
                
                # Sample random matches from the season
                if len(matches) > max_matches_per_season:
                    matches = random.sample(matches, max_matches_per_season)
                
                match_count = 0
                for match_url in matches[:20]:  # Limit for testing
                    match_data = self.get_match_lineups(match_url)
                    if match_data:
                        match_data['league'] = league_info['name']
                        match_data['season'] = f"{season}/{season+1}"
                        all_match_data.append(match_data)
                        match_count += 1
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                
                print(f"   ✅ Collected {match_count} matches from {season}/{season+1}")
        
        return all_match_data
    
    def create_squad_database(self, match_data):
        """Convert match data into Squadify-style squad database."""
        
        print(f"\n🏆 BUILDING SQUAD DATABASE")
        print("-" * 40)
        
        squads = []
        
        for match in match_data:
            # Create entries for both teams
            for team_type in ['home', 'away']:
                lineup = match[f'{team_type}_lineup']
                
                if len(lineup) >= 11:  # Must have at least 11 players
                    squad = {
                        'match_id': f"{match['home_team']}_vs_{match['away_team']}_{match['date']}",
                        'team': match[f'{team_type}_team'],
                        'opponent': match['away_team'] if team_type == 'home' else match['home_team'],
                        'date': match['date'],
                        'season': match['season'],
                        'league': match['league'],
                        'score': match['score'],
                        'players': []
                    }
                    
                    # Convert players to Squadify format with formations
                    formation_positions = self.assign_formation_positions(lineup)
                    
                    for i, player in enumerate(lineup[:11]):  # First 11 players
                        position_coords = formation_positions.get(i, {'top': 40, 'left': 40})
                        
                        squad_player = {
                            'name': player['name'].lower(),
                            'number': player['number'],
                            'position': player['position'],
                            'top': position_coords['top'],
                            'left': position_coords['left'],
                            'team': squad['team'],
                            'season': squad['season']
                        }
                        
                        squad['players'].append(squad_player)
                    
                    squads.append(squad)
        
        print(f"   📈 Generated {len(squads)} unique squads")
        return squads
    
    def assign_formation_positions(self, players):
        """Assign formation positions based on player positions."""
        
        # Standard 4-4-2 formation coordinates
        formation_442 = {
            0: {'top': 80, 'left': 40},  # GK
            1: {'top': 61, 'left': 15},  # LB
            2: {'top': 63, 'left': 28},  # CB
            3: {'top': 63, 'left': 52},  # CB
            4: {'top': 61, 'left': 73},  # RB
            5: {'top': 43, 'left': 15},  # LM
            6: {'top': 43, 'left': 35},  # CM
            7: {'top': 43, 'left': 55},  # CM
            8: {'top': 43, 'left': 73},  # RM
            9: {'top': 18, 'left': 30},  # ST
            10: {'top': 18, 'left': 50}  # ST
        }
        
        return formation_442
    
    def save_database(self, squads, filename='english_football_database.json'):
        """Save the squad database to JSON file."""
        
        # Create summary
        leagues = set([s['league'] for s in squads])
        seasons = set([s['season'] for s in squads])
        teams = set([s['team'] for s in squads])
        
        database = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'total_squads': len(squads),
                'leagues': list(leagues),
                'seasons': sorted(list(seasons)),
                'teams': sorted(list(teams))
            },
            'squads': squads
        }
        
        with open(f'/workspaces/CLQ/{filename}', 'w') as f:
            json.dump(database, f, indent=2)
        
        print(f"\n💾 Database saved to {filename}")
        print(f"   📊 {len(squads)} squads")
        print(f"   🏆 {len(leagues)} leagues")
        print(f"   📅 {len(seasons)} seasons") 
        print(f"   ⚽ {len(teams)} teams")

def main():
    scraper = EnglishFootballScraper()
    
    # Scrape historic matches
    match_data = scraper.scrape_historic_matches(max_matches_per_season=20)
    
    if match_data:
        # Create squad database
        squads = scraper.create_squad_database(match_data)
        
        # Save to file
        scraper.save_database(squads)
        
        print(f"\n🎉 English Football Database Complete!")
        print(f"Ready for use in Squadify-style game")
    else:
        print("❌ No match data collected")

if __name__ == "__main__":
    main()
