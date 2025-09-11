import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin
import re

class TransfermarktMatchScraper:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_match_lineups(self, match_id):
        """Scrape lineup data from a specific match."""
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
                'venue': self.extract_venue(soup)
            }
            
            # Find both team sections
            team_sections = lineup_box.find_all('div', class_='large-6')
            
            for team_section in team_sections:
                team_data = self.extract_team_lineup(team_section)
                if team_data:
                    match_data['teams'].append(team_data)
            
            if len(match_data['teams']) == 2:
                print(f"✅ Successfully scraped {match_data['teams'][0]['name']} vs {match_data['teams'][1]['name']}")
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
            
            # Extract player ID from URL (/player-name/profil/spieler/123456)
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
            # Look for date in the match info section
            match_info = soup.find('div', class_='sb-matchinfo')
            if match_info:
                date_text = match_info.get_text()
                date_match = re.search(r'(\w+,\s+\d{1,2}/\d{1,2}/\d{2,4})', date_text)
                if date_match:
                    return date_match.group(1)
            
            return "Unknown Date"
            
        except Exception:
            return "Unknown Date"

    def extract_venue(self, soup):
        """Extract venue information from the page."""
        try:
            # Look for venue in match info
            venue_text = soup.find(string=re.compile(r'Stadium|Ground|Park|Arena'))
            if venue_text:
                venue_match = re.search(r'([A-Za-z\s]+(?:Stadium|Ground|Park|Arena))', str(venue_text))
                if venue_match:
                    return venue_match.group(1).strip()
            
            return "Unknown Venue"
            
        except Exception:
            return "Unknown Venue"

if __name__ == "__main__":
    # Test with the West Ham vs Chelsea match
    scraper = TransfermarktMatchScraper()
    match_data = scraper.scrape_match_lineups("3592069")
    
    if match_data:
        print("\n🏆 MATCH DATA EXTRACTED:")
        print(f"Date: {match_data['date']}")
        print(f"Venue: {match_data['venue']}")
        
        for team in match_data['teams']:
            print(f"\n📋 {team['name']} ({team['formation']}):")
            print("Starting XI:")
            for player in team['starting_xi']:
                events_str = f" [{', '.join(player['events'])}]" if player['events'] else ""
                print(f"   #{player['number']:2} {player['name']:15} ({player['position_top']:4.1f}%, {player['position_left']:4.1f}%){events_str}")
            
            print("Substitutes:")
            for player in team['substitutes']:
                events_str = f" [{', '.join(player['events'])}]" if player['events'] else ""
                print(f"   #{player['number']:2} {player['name']:15} ({player.get('position', 'N/A')}){events_str}")
        
        # Save the data
        with open('/workspaces/CLQ/match_3592069_data.json', 'w') as f:
            json.dump(match_data, f, indent=2)
        
        print("\n💾 Match data saved to match_3592069_data.json")
