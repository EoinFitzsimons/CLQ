import requests
from bs4 import BeautifulSoup

def debug_transfermarkt_page():
    """Debug the structure of the Transfermarkt match page."""
    
    url = "https://www.transfermarkt.com/spielbericht/index/spielbericht/3592069"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Debugging URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch page. Status: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for different possible containers
        print("\n📋 SEARCHING FOR LINEUP CONTAINERS:")
        print("-" * 50)
        
        # Look for any divs containing "Line" or "Aufstellung"
        lineup_candidates = soup.find_all('div', string=lambda text: text and ('Line' in text or 'Aufstellung' in text))
        print(f"Found {len(lineup_candidates)} divs with 'Line' or 'Aufstellung'")
        
        for i, candidate in enumerate(lineup_candidates[:5]):
            print(f"  {i+1}: {candidate.get_text()[:100]}")
        
        # Look for any h2 headers that might contain lineup info
        headers_h2 = soup.find_all('h2')
        print(f"\nFound {len(headers_h2)} h2 headers:")
        for i, header in enumerate(headers_h2[:10]):
            print(f"  {i+1}: {header.get_text()[:80]}")
        
        # Look for formation containers
        formation_containers = soup.find_all('div', class_='formation-player-container')
        print(f"\nFound {len(formation_containers)} formation-player-container divs")
        
        # Look for any divs with 'aufstellung' class
        aufstellung_divs = soup.find_all('div', class_=lambda x: x and 'aufstellung' in x.lower())
        print(f"Found {len(aufstellung_divs)} divs with 'aufstellung' in class name:")
        for div in aufstellung_divs[:5]:
            classes = div.get('class', [])
            print(f"  Classes: {classes}")
        
        # Look for any divs with 'box' class
        box_divs = soup.find_all('div', class_='box')
        print(f"\nFound {len(box_divs)} divs with 'box' class")
        
        if box_divs:
            for i, box in enumerate(box_divs):
                content = box.get_text()[:200].replace('\n', ' ').strip()
                print(f"  Box {i+1}: {content}")
        
        # Check if this might be a different language version
        page_title = soup.find('title')
        if page_title:
            print(f"\nPage title: {page_title.get_text()}")
        
        # Look for any text containing team names from the example
        west_ham_refs = soup.find_all(string=lambda text: text and 'West Ham' in text)
        chelsea_refs = soup.find_all(string=lambda text: text and 'Chelsea' in text)
        
        print(f"\nWest Ham references: {len(west_ham_refs)}")
        print(f"Chelsea references: {len(chelsea_refs)}")
        
        # Save a portion of the HTML for manual inspection
        with open('/workspaces/CLQ/debug_transfermarkt_sample.html', 'w', encoding='utf-8') as f:
            f.write(str(soup)[:10000])  # First 10k characters
        
        print("\n💾 Sample HTML saved to debug_transfermarkt_sample.html")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_transfermarkt_page()
