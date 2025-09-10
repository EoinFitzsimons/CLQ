import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.transfermarkt.com/uefa-champions-league-qualifying/ewigetorschuetzenliste/pokalwettbewerb/CLQ/plus/1/galerie/0"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Get just the first page to debug
resp = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(resp.text, 'html.parser')
table = soup.find('table', class_='items')

if table:
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    # Debug first row
    first_row = rows[0]
    cols = first_row.find_all('td')
    
    print(f"Number of columns: {len(cols)}")
    print("="*50)
    
    for i, col in enumerate(cols):
        print(f"Column {i}:")
        print(f"Text: '{col.get_text(strip=True)}'")
        print(f"HTML: {str(col)[:200]}...")
        print("-"*30)
        
    # Focus on the player column (should be column 1)
    if len(cols) > 1:
        player_col = cols[1]
        print("\nDetailed analysis of player column:")
        print(f"Full HTML: {str(player_col)}")
        
        # Try to find the nested table
        inline_table = player_col.find('table', class_='inline-table')
        if inline_table:
            print("\nFound inline table!")
            print(f"Inline table HTML: {str(inline_table)}")
        else:
            print("\nNo inline table found!")
