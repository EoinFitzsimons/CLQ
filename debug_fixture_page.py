import requests
from bs4 import BeautifulSoup
import re

def debug_fixture_page():
    """Debug what the Premier League fixture page actually contains."""
    
    url = "https://www.transfermarkt.com/premier-league/gesamtspielplan/wettbewerb/GB1?saison_id=2023&spieltagVon=1&spieltagBis=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Debugging fixture page: {url}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Response status: {response.status_code}")
        print(f"📄 Content length: {len(response.content)} bytes")
        print()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for any links that might be matches
        print("🔗 LOOKING FOR MATCH LINKS:")
        print("-" * 40)
        
        # Try different selectors for match links
        match_patterns = [
            ('spielbericht links', soup.find_all('a', href=re.compile(r'spielbericht'))),
            ('match report links', soup.find_all('a', href=re.compile(r'/.*?/.*?/.*?/\d+'))),
            ('any numeric links', soup.find_all('a', href=re.compile(r'/\d+'))),
        ]
        
        for pattern_name, links in match_patterns:
            print(f"\n{pattern_name}: {len(links)} found")
            for i, link in enumerate(links[:5]):  # Show first 5
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"  {i+1}. {href} -> '{text}'")
        
        # Look for table structures
        print(f"\n📊 TABLE STRUCTURES:")
        print("-" * 40)
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables[:3]):  # Check first 3 tables
            print(f"\nTable {i+1}:")
            print(f"  Class: {table.get('class', [])}")
            rows = table.find_all('tr')
            print(f"  Rows: {len(rows)}")
            
            # Check first few rows for content
            for j, row in enumerate(rows[:3]):
                cells = row.find_all(['td', 'th'])
                print(f"    Row {j+1}: {len(cells)} cells")
                if cells:
                    cell_texts = [cell.get_text(strip=True)[:30] for cell in cells[:3]]
                    print(f"      Content: {cell_texts}")
        
        # Look for specific German terms
        print(f"\n🔍 GERMAN TERMS SEARCH:")
        print("-" * 40)
        german_terms = ['Spieltag', 'Datum', 'Heimteam', 'Gast', 'Ergebnis', 'Uhrzeit']
        
        for term in german_terms:
            elements = soup.find_all(string=re.compile(term, re.IGNORECASE))
            print(f"'{term}': {len(elements)} occurrences")
        
        # Check for any div with match-like content
        print(f"\n🏈 MATCH-LIKE CONTENT:")
        print("-" * 40)
        
        # Look for team names or scores
        score_pattern = re.compile(r'\d+:\d+')
        team_divs = soup.find_all('div', string=score_pattern)
        print(f"Score patterns (x:x): {len(team_divs)}")
        
        # Save a sample of the HTML for inspection
        with open('/workspaces/CLQ/fixture_page_sample.html', 'w', encoding='utf-8') as f:
            f.write(str(soup)[:10000])  # First 10k characters
        
        print(f"\n💾 Saved first 10k characters to fixture_page_sample.html")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_fixture_page()
