import requests
from bs4 import BeautifulSoup
import json

def test_transfermarkt_structure():
    """Test and understand Transfermarkt URL structure for English leagues."""
    
    print("🔍 TESTING TRANSFERMARKT STRUCTURE")
    print("="*50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Test different URL patterns for Premier League
    test_urls = [
        "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1",
        "https://www.transfermarkt.com/premier-league/tabelle/wettbewerb/GB1/saison_id/2023",
        "https://www.transfermarkt.com/premier-league/tabelle/wettbewerb/GB1?saison_id=2023",
        "https://www.transfermarkt.com/jumplist/startseite/wettbewerb/GB1",
        "https://www.transfermarkt.com/premier-league/vereine/wettbewerb/GB1/saison_id/2023"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        
        try:
            response = session.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"   Title: {title.get_text()[:100]}")
                
                # Look for team/club links
                team_links = soup.find_all('a', href=True)
                team_count = 0
                
                for link in team_links[:50]:  # Check first 50 links
                    href = link.get('href', '')
                    if '/verein/' in href and 'saison_id' not in href:
                        team_count += 1
                        if team_count <= 3:  # Show first 3 teams
                            print(f"   Team: {link.get_text(strip=True)} -> {href}")
                
                if team_count > 0:
                    print(f"   ✅ Found {team_count} team links")
                else:
                    print(f"   ❌ No team links found")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def find_competition_pages():
    """Find the correct pages for English competitions."""
    
    print(f"\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 FINDING ENGLISH COMPETITION PAGES")
    print("-"*50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Try to find the competitions overview
    search_terms = [
        "https://www.transfermarkt.com/england",
        "https://www.transfermarkt.com/premier-league",
        "https://www.transfermarkt.com/championship",
    ]
    
    for term in search_terms:
        print(f"\nSearching: {term}")
        
        try:
            response = session.get(term)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for competition links
                competition_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    if 'wettbewerb' in href and any(comp in text for comp in ['premier', 'championship', 'league']):
                        competition_links.append((text, href))
                
                print(f"   Found {len(set(competition_links))} competition links:")
                for text, href in list(set(competition_links))[:5]:
                    print(f"   - {text} -> {href}")
        
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_transfermarkt_structure()
    find_competition_pages()
