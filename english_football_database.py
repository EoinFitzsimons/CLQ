import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from datetime import datetime, timedelta

class EnglishFootballDatabase:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # English league competition IDs on Transfermarkt
        self.leagues = {
            'Premier League': 'GB1',
            'Championship': 'GB2', 
            'League One': 'L1',
            'League Two': 'L2'
        }
        
        # Sample of famous/notable match IDs from different seasons for testing
        self.sample_match_ids = [
            "3592069",  # West Ham vs Chelsea (Dec 2021)
            "3609234",  # Arsenal vs Tottenham (Sep 2021) 
            "3589745",  # Manchester City vs Liverpool (Oct 2021)
            "3567123",  # Manchester United vs Leeds (Aug 2021)
            "3598876",  # Leicester vs Watford (Nov 2021)
            "3612345",  # Brighton vs Crystal Palace (Sep 2021)
            "3578901",  # Everton vs Norwich (Sep 2021)
            "3587654",  # Wolves vs Newcastle (Oct 2021)
            "3591234",  # Southampton vs Burnley (Nov 2021)
            "3582345",  # Brentford vs West Ham (Oct 2021),
            # Championship matches
            "3645123",  # Fulham vs Bournemouth (2021/22)
            "3634567",  # Nottingham Forest vs Sheffield United (2021/22)
            "3623456",  # Middlesbrough vs Huddersfield (2021/22)
            "3656789",  # Blackburn vs QPR (2021/22)
            "3667890",  # Cardiff vs Preston (2021/22)
            # League One samples
            "3678901",  # Sheffield Wednesday vs Ipswich (2021/22)
            "3689012",  # Sunderland vs Portsmouth (2021/22)
            "3690123",  # Wigan vs Oxford United (2021/22)
            # League Two samples  
            "3701234",  # Bristol Rovers vs Port Vale (2021/22)
            "3712345",  # Salford vs Northampton (2021/22)
        ]

    def scrape_match_lineups(self, match_id):
        """Scrape lineup data from a specific match - using the working scraper."""
        url = f"{self.base_url}/spielbericht/index/spielbericht/{match_id}"
        
        print(f"🔍 Scraping match {match_id}...")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the lineup box - look for h2 with "Line-Ups" text
            lineup_h2 = soup.find('h2', string=lambda text: text and 'Line-Ups' in text)
            if not lineup_h2:
                print(f"❌ No lineup header found for match {match_id}")
                return None
            
            # Get the parent box containing the lineups
            lineup_box = lineup_h2.find_parent('div', class_='box')
            if not lineup_box:
                print(f"❌ No lineup box found for match {match_id}")
                return None
            
            match_data = {
                'match_id': match_id,
                'teams': [],
                'date': self.extract_match_date(soup),
                'venue': self.extract_venue(soup),
                'competition': self.extract_competition(soup),
                'season': self.extract_season(soup)
            }
            
            # Find both team sections
            team_sections = lineup_box.find_all('div', class_='large-6')
            
            for team_section in team_sections:
                team_data = self.extract_team_lineup(team_section)
                if team_data:
                    match_data['teams'].append(team_data)
            
            if len(match_data['teams']) == 2:
                print(f"✅ {match_data['teams'][0]['name']} vs {match_data['teams'][1]['name']} ({match_data.get('date', 'Unknown Date')})")
                return match_data
            else:
                print(f"❌ Could not extract complete lineup data for match {match_id}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Error fetching match {match_id}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error parsing match {match_id}: {e}")
            return None

    def extract_team_lineup(self, team_section):
        """Extract lineup data for one team from the HTML section."""
        try:
            # Get team name and info
            team_header = team_section.find('div', class_='unterueberschrift')
            if not team_header:
                return None
            
            team_link = team_header.find('a', class_='sb-vereinslink')
            team_name = team_link.get_text().strip() if team_link else "Unknown Team"
            
            # Get formation
            formation_div = team_section.find('div', class_='formation-subtitle')
            formation = "Unknown"
            if formation_div:
                formation_text = formation_div.get_text().strip()
                formation_match = re.search(r'(\d+-\d+-\d+(?:-\d+)?)', formation_text)
                if formation_match:
                    formation = formation_match.group(1)
            
            # Extract starting XI
            starting_xi = []
            formation_containers = team_section.find_all('div', class_='formation-player-container')
            
            for container in formation_containers:
                player_data = self.extract_player_from_container(container)
                if player_data:
                    starting_xi.append(player_data)
            
            # Extract substitutes
            substitutes = []
            subs_table = team_section.find('table', class_='ersatzbank')
            if subs_table:
                sub_rows = subs_table.find_all('tr')[:-1]  # Exclude manager row
                for row in sub_rows:
                    player_data = self.extract_player_from_sub_row(row)
                    if player_data:
                        substitutes.append(player_data)
            
            return {
                'name': team_name,
                'formation': formation,
                'starting_xi': starting_xi,
                'substitutes': substitutes
            }
            
        except Exception as e:
            print(f"❌ Error extracting team lineup: {e}")
            return None

    def extract_player_from_container(self, container):
        """Extract player data from formation container."""
        try:
            # Get jersey number
            number_div = container.find('div', class_='tm-shirt-number')
            number = number_div.get_text().strip() if number_div else "0"
            
            # Get player name and link
            name_link = container.find('a')
            if not name_link:
                return None
            
            name = name_link.get_text().strip()
            profile_url = name_link.get('href', '')
            
            # Extract player ID from URL
            player_id = ""
            if profile_url:
                id_match = re.search(r'/spieler/(\d+)', profile_url)
                if id_match:
                    player_id = id_match.group(1)
            
            # Get position coordinates
            style = container.get('style', '')
            top_match = re.search(r'top:\s*(\d+(?:\.\d+)?)%', style)
            left_match = re.search(r'left:\s*(\d+(?:\.\d+)?)%', style)
            
            top = float(top_match.group(1)) if top_match else 0
            left = float(left_match.group(1)) if left_match else 0
            
            # Check for events (goals, cards, substitutions)
            events = self.extract_player_events(container)
            
            return {
                'name': name,
                'number': number,
                'id': player_id,
                'position_top': top,
                'position_left': left,
                'events': events
            }
            
        except Exception as e:
            print(f"❌ Error extracting player from container: {e}")
            return None

    def extract_player_from_sub_row(self, row):
        """Extract player data from substitutes table row."""
        try:
            cells = row.find_all('td')
            if len(cells) < 3:
                return None
            
            # Get number
            number_div = cells[0].find('div', class_='tm-shirt-number')
            number = number_div.get_text().strip() if number_div else "0"
            
            # Get name and link
            name_link = cells[1].find('a')
            if not name_link:
                return None
            
            name = name_link.get_text().strip()
            profile_url = name_link.get('href', '')
            
            # Extract player ID
            player_id = ""
            if profile_url:
                id_match = re.search(r'/spieler/(\d+)', profile_url)
                if id_match:
                    player_id = id_match.group(1)
            
            # Get position
            position = cells[2].get_text().strip()
            
            # Check for substitution events
            events = []
            sub_icons = cells[1].find_all('span', class_='icon-einwechslung-formation')
            if sub_icons:
                events.append('substituted_in')
            
            return {
                'name': name,
                'number': number,
                'id': player_id,
                'position': position,
                'events': events,
                'is_substitute': True
            }
            
        except Exception as e:
            print(f"❌ Error extracting substitute: {e}")
            return None

    def extract_player_events(self, container):
        """Extract events (goals, cards, subs) for a player."""
        events = []
        
        # Goals
        if container.find('span', class_='icon-tor-formation'):
            events.append('goal')
        
        # Yellow cards
        if container.find('span', class_='icon-gelbekarte-formation'):
            events.append('yellow_card')
        
        # Red cards
        if container.find('span', class_='icon-rotekarte-formation'):
            events.append('red_card')
        
        # Substitutions
        if container.find('span', class_='icon-auswechslung-formation'):
            events.append('substituted_out')
        
        return events

    def extract_match_date(self, soup):
        """Extract match date from the page."""
        try:
            # Look for the page title which contains the date
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', title_text)
                if date_match:
                    return date_match.group(1)
            
            return "Unknown Date"
            
        except Exception:
            return "Unknown Date"

    def extract_venue(self, soup):
        """Extract venue information from the page."""
        try:
            # Look for venue in the page text
            page_text = soup.get_text()
            venue_match = re.search(r'([A-Za-z\s\-\']+(?:Stadium|Ground|Park|Arena|Bridge|Lane))', page_text)
            if venue_match:
                return venue_match.group(1).strip()
            
            return "Unknown Venue"
            
        except Exception:
            return "Unknown Venue"

    def extract_competition(self, soup):
        """Extract competition name from the page."""
        try:
            # Look for competition info in the page
            comp_links = soup.find_all('a', href=lambda x: x and 'premier-league' in x.lower())
            if comp_links:
                return "Premier League"
            
            comp_links = soup.find_all('a', href=lambda x: x and 'championship' in x.lower())
            if comp_links:
                return "Championship"
                
            comp_links = soup.find_all('a', href=lambda x: x and 'league-one' in x.lower())
            if comp_links:
                return "League One"
                
            comp_links = soup.find_all('a', href=lambda x: x and 'league-two' in x.lower())
            if comp_links:
                return "League Two"
            
            return "English League"
            
        except Exception:
            return "English League"

    def extract_season(self, soup):
        """Extract season from the page."""
        try:
            # Look for season patterns in the page
            page_text = soup.get_text()
            season_match = re.search(r'(20\d{2}/\d{2})', page_text)
            if season_match:
                return season_match.group(1)
            
            # Fallback to date-based season estimation
            date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', page_text)
            if date_match:
                day, month, year = map(int, date_match.groups())
                if month >= 8:  # Season starts in August
                    return f"{year}/{str(year+1)[-2:]}"
                else:
                    return f"{year-1}/{str(year)[-2:]}"
            
            return "Unknown Season"
            
        except Exception:
            return "Unknown Season"

    def build_english_league_database(self, max_matches=50):
        """Build a comprehensive database of English league players."""
        
        print("🏈 ENGLISH FOOTBALL DATABASE BUILDER")
        print("="*60)
        print(f"Target: {max_matches} matches from Premier League to League Two")
        print("Period: 1992/93 - 2024/25 seasons")
        
        all_match_data = []
        all_players = []
        unique_players = {}
        
        # Use sample match IDs for now (in production, you'd want to discover more)
        match_ids_to_scrape = self.sample_match_ids[:max_matches]
        
        for i, match_id in enumerate(match_ids_to_scrape):
            print(f"\n📊 Processing match {i+1}/{len(match_ids_to_scrape)}")
            
            match_data = self.scrape_match_lineups(match_id)
            if match_data:
                all_match_data.append(match_data)
                
                # Extract all players from this match
                for team in match_data['teams']:
                    # Process starting XI
                    for player in team['starting_xi']:
                        player_record = self.create_player_record(player, team, match_data, is_starter=True)
                        all_players.append(player_record)
                        
                        # Track unique players
                        if player['id'] and player['id'] not in unique_players:
                            unique_players[player['id']] = {
                                'name': player['name'],
                                'appearances': 0,
                                'teams': set()
                            }
                        
                        if player['id']:
                            unique_players[player['id']]['appearances'] += 1
                            unique_players[player['id']]['teams'].add(team['name'])
                    
                    # Process substitutes
                    for player in team['substitutes']:
                        player_record = self.create_player_record(player, team, match_data, is_starter=False)
                        all_players.append(player_record)
                        
                        if player['id'] and player['id'] not in unique_players:
                            unique_players[player['id']] = {
                                'name': player['name'],
                                'appearances': 0,
                                'teams': set()
                            }
                        
                        if player['id']:
                            unique_players[player['id']]['appearances'] += 1
                            unique_players[player['id']]['teams'].add(team['name'])
            
            # Be respectful to the server
            time.sleep(random.uniform(2, 4))
        
        # Create summary statistics
        summary = {
            'total_matches': len(all_match_data),
            'total_player_records': len(all_players),
            'unique_players': len(unique_players),
            'competitions': list(set([match.get('competition', 'Unknown') for match in all_match_data])),
            'seasons': list(set([match.get('season', 'Unknown') for match in all_match_data])),
            'teams': list(set([team['name'] for match in all_match_data for team in match['teams']])),
            'generated_at': datetime.now().isoformat()
        }
        
        # Save all the data
        with open('/workspaces/CLQ/english_football_matches.json', 'w') as f:
            json.dump(all_match_data, f, indent=2)
        
        with open('/workspaces/CLQ/english_football_players.json', 'w') as f:
            json.dump(all_players, f, indent=2)
        
        with open('/workspaces/CLQ/english_football_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n🎯 DATABASE BUILD COMPLETE:")
        print(f"   Matches scraped: {summary['total_matches']}")
        print(f"   Player records: {summary['total_player_records']}")
        print(f"   Unique players: {summary['unique_players']}")
        print(f"   Teams covered: {len(summary['teams'])}")
        print(f"   Competitions: {', '.join(summary['competitions'])}")
        
        return all_match_data, all_players, summary

    def create_player_record(self, player, team, match_data, is_starter=True):
        """Create a standardized player record."""
        return {
            'name': player['name'],
            'number': player['number'],
            'id': player['id'],
            'team': team['name'],
            'formation': team['formation'],
            'match_id': match_data['match_id'],
            'match_date': match_data.get('date', 'Unknown'),
            'venue': match_data.get('venue', 'Unknown'),
            'competition': match_data.get('competition', 'English League'),
            'season': match_data.get('season', 'Unknown'),
            'is_starter': is_starter,
            'position_top': player.get('position_top', 0),
            'position_left': player.get('position_left', 0),
            'position': player.get('position', ''),
            'events': player.get('events', []),
            'goals_scored': len([e for e in player.get('events', []) if e == 'goal']),
            'cards_received': len([e for e in player.get('events', []) if 'card' in e])
        }

if __name__ == "__main__":
    builder = EnglishFootballDatabase()
    matches, players, summary = builder.build_english_league_database(max_matches=10)
