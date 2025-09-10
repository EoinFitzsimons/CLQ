import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.transfermarkt.com/uefa-champions-league-qualifying/ewigetorschuetzenliste/pokalwettbewerb/CLQ/plus/1/galerie/0"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Number of players per page
PLAYERS_PER_PAGE = 25
# Number of players to scrape
TOTAL_PLAYERS = 1000
# Calculate number of pages
NUM_PAGES = (TOTAL_PLAYERS + PLAYERS_PER_PAGE - 1) // PLAYERS_PER_PAGE


def parse_row(row):
    cols = row.find_all('td')
    if len(cols) < 10:
        return None
    # Extract player name from the first column (with <a> tag)
    player_tag = cols[1].find('a', class_='spielprofil_tooltip')
    player_name = player_tag.get_text(strip=True) if player_tag else cols[1].get_text(strip=True)
    # Extract position from the second column (with <table> or <span> tag)
    position_tag = cols[1].find('table') or cols[1].find('span')
    position = position_tag.get_text(strip=True) if position_tag else ''
    # Extract club(s) from the third column
    clubs = cols[2].get_text(strip=True)
    # Extract nationality from the fourth column (with <img> alt attribute)
    nat_img = cols[3].find('img')
    nationality = nat_img['alt'] if nat_img and nat_img.has_attr('alt') else cols[3].get_text(strip=True)
    # Extract age, seasons, matches, goals, assists
    age = cols[4].get_text(strip=True)
    seasons = cols[5].get_text(strip=True)
    matches = cols[6].get_text(strip=True)
    goals = cols[7].get_text(strip=True)
    assists = cols[8].get_text(strip=True)
    return {
        'Rank': cols[0].get_text(strip=True),
        'Player': player_name,
        'Position': position,
        'Club(s)': clubs,
        'Nationality': nationality,
        'Age': age,
        'Seasons': seasons,
        'Matches': matches,
        'Goals': goals,
        'Assists': assists,
    }

def scrape_top_scorers():
    all_players = []
    for page in range(1, NUM_PAGES + 1):
        params = {"page": page}
        print(f"Scraping page {page}...")
        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print(f"Failed to fetch page {page}")
            break
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', class_='items')
        if not table:
            print(f"No table found on page {page}")
            break
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 14:
                continue
            
            # Based on debug analysis, the correct column mapping is:
            # Column 0: Rank
            # Column 3: Player name (from inline table)
            # Column 4: Position (from inline table)
            # Column 5: Club
            # Column 6: Nationality
            # Column 7: Age
            # Column 8: Seasons
            # Column 9: Matches
            # Column 10: SubOn
            # Column 11: SubOff
            # Column 12: Assists
            # Column 13: Penalties
            # Column 14: Goals
            
            rank = cols[0].get_text(strip=True)
            player_name = cols[3].get_text(strip=True)
            position = cols[4].get_text(strip=True)
            
            # Club(s) from column 5
            club_name = ''
            club_link = cols[5].find('a')
            if club_link and club_link.has_attr('title'):
                club_name = club_link['title']
            else:
                club_img = cols[5].find('img')
                if club_img and club_img.has_attr('title'):
                    club_name = club_img['title']
                else:
                    club_name = cols[5].get_text(strip=True)
            
            # Nationality from column 6
            nationality = ''
            nat_img = cols[6].find('img', class_='flaggenrahmen')
            if nat_img and nat_img.has_attr('title'):
                nationality = nat_img['title']
            else:
                nationality = cols[6].get_text(strip=True)
            
            # Numeric data columns
            age = cols[7].get_text(strip=True)
            seasons = cols[8].get_text(strip=True)
            matches = cols[9].get_text(strip=True)
            sub_on = cols[10].get_text(strip=True)
            sub_off = cols[11].get_text(strip=True)
            assists = cols[12].get_text(strip=True)
            penalties = cols[13].get_text(strip=True)
            goals = cols[14].get_text(strip=True)
            
            all_players.append({
                'Rank': rank,
                'Player': player_name,
                'Position': position,
                'Club(s)': club_name,
                'Nationality': nationality,
                'Age': age,
                'Seasons': seasons,
                'Matches': matches,
                'SubOn': sub_on,
                'SubOff': sub_off,
                'Assists': assists,
                'Penalties': penalties,
                'Goals': goals,
            })
            if len(all_players) >= TOTAL_PLAYERS:
                break
        if len(all_players) >= TOTAL_PLAYERS:
            break
        time.sleep(1)  # Be polite to the server
    # Save to CSV
    keys = all_players[0].keys() if all_players else []
    with open('GlobalTable/top_1000_scorers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_players)
    print(f"Saved {len(all_players)} players to GlobalTable/top_1000_scorers.csv")
    # Save to CSV
    keys = all_players[0].keys() if all_players else []
    with open('GlobalTable/top_1000_scorers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_players)
    print(f"Saved {len(all_players)} players to GlobalTable/top_1000_scorers.csv")

if __name__ == "__main__":
    scrape_top_scorers()
