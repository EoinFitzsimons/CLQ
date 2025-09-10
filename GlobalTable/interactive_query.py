#!/usr/bin/env python3
"""
Interactive CLI for querying UEFA Champions League Qualifying scorers data.
Run this script to get an interactive interface for data analysis.
"""

from analyze_scorers import CLQScorersAnalyzer
import pandas as pd

def interactive_menu():
    """Display interactive menu for data queries."""
    analyzer = CLQScorersAnalyzer()
    
    if analyzer.df is None:
        print("Error: Could not load data. Please ensure the CSV file exists.")
        return
    
    while True:
        print("\n" + "="*60)
        print("🏆 UEFA CHAMPIONS LEAGUE QUALIFYING - INTERACTIVE ANALYSIS")
        print("="*60)
        print("1. Search for a specific player")
        print("2. Best goals per game (custom filters)")
        print("3. Filter by nationality")
        print("4. Filter by position")
        print("5. Filter by club")
        print("6. Custom query (advanced)")
        print("7. Show summary statistics")
        print("8. Generate visualizations")
        print("9. Exit")
        print("-" * 60)
        
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == '1':
            player_search(analyzer)
        elif choice == '2':
            custom_goals_per_game(analyzer)
        elif choice == '3':
            filter_by_nationality(analyzer)
        elif choice == '4':
            filter_by_position(analyzer)
        elif choice == '5':
            filter_by_club(analyzer)
        elif choice == '6':
            custom_query(analyzer)
        elif choice == '7':
            analyzer.summary_stats()
        elif choice == '8':
            analyzer.create_visualizations()
        elif choice == '9':
            print("Thanks for using the CLQ Scorers Analyzer! 🏆")
            break
        else:
            print("Invalid choice. Please enter a number between 1-9.")

def player_search(analyzer):
    """Search for specific players."""
    player_name = input("Enter player name (partial names work): ").strip()
    if player_name:
        analyzer.query_player(player_name)
    else:
        print("Please enter a player name.")

def custom_goals_per_game(analyzer):
    """Custom goals per game analysis with user-defined filters."""
    try:
        min_matches = int(input("Minimum matches played (default 10): ") or "10")
        top_n = int(input("How many players to show (default 20): ") or "20")
        analyzer.best_goals_per_game(min_matches=min_matches, top_n=top_n)
    except ValueError:
        print("Please enter valid numbers.")

def filter_by_nationality(analyzer):
    """Filter and analyze by nationality."""
    print("\nAvailable nationalities:")
    countries = analyzer.df['Nationality'].value_counts()
    for i, (country, count) in enumerate(countries.head(20).items(), 1):
        print(f"{i:2d}. {country} ({count} players)")
    
    country = input("\nEnter country name: ").strip()
    if country:
        filtered_df = analyzer.df[analyzer.df['Nationality'].str.contains(country, case=False, na=False)]
        if not filtered_df.empty:
            print(f"\n🌍 PLAYERS FROM {country.upper()}")
            print("="*60)
            top_players = filtered_df.nlargest(15, 'Goals')
            for idx, (_, player) in enumerate(top_players.iterrows(), 1):
                print(f"{idx:2d}. {player['Player']:<25} | "
                      f"{player['Goals']:2.0f} goals | "
                      f"{player['Goals_Per_Match']:.3f} goals/match | "
                      f"{player['Position']}")
        else:
            print(f"No players found from {country}")

def filter_by_position(analyzer):
    """Filter and analyze by position."""
    print("\nAvailable positions:")
    positions = analyzer.df['Position'].value_counts()
    for i, (position, count) in enumerate(positions.items(), 1):
        print(f"{i:2d}. {position} ({count} players)")
    
    position = input("\nEnter position: ").strip()
    if position:
        filtered_df = analyzer.df[analyzer.df['Position'].str.contains(position, case=False, na=False)]
        if not filtered_df.empty:
            print(f"\n⚽ {position.upper()} PLAYERS")
            print("="*60)
            top_players = filtered_df.nlargest(15, 'Goals_Per_Match')
            for idx, (_, player) in enumerate(top_players.iterrows(), 1):
                print(f"{idx:2d}. {player['Player']:<25} | "
                      f"{player['Goals']:2.0f} goals | "
                      f"{player['Goals_Per_Match']:.3f} goals/match | "
                      f"{player['Club(s)']}")
        else:
            print(f"No players found for position {position}")

def filter_by_club(analyzer):
    """Filter and analyze by club."""
    club = input("Enter club name (partial names work): ").strip()
    if club:
        filtered_df = analyzer.df[analyzer.df['Club(s)'].str.contains(club, case=False, na=False)]
        if not filtered_df.empty:
            print(f"\n🏆 PLAYERS FROM CLUBS MATCHING '{club.upper()}'")
            print("="*60)
            top_players = filtered_df.nlargest(15, 'Goals')
            for idx, (_, player) in enumerate(top_players.iterrows(), 1):
                print(f"{idx:2d}. {player['Player']:<25} | "
                      f"{player['Goals']:2.0f} goals | "
                      f"{player['Goals_Per_Match']:.3f} goals/match | "
                      f"{player['Club(s)']}")
        else:
            print(f"No players found for clubs matching '{club}'")

def custom_query(analyzer):
    """Allow custom pandas queries."""
    print("\nCustom Query Interface")
    print("You can use pandas syntax. The DataFrame is available as 'df'")
    print("Example: df[df['Goals'] > 10].sort_values('Goals_Per_Match', ascending=False)")
    print("Available columns:", list(analyzer.df.columns))
    
    query = input("\nEnter your query: ").strip()
    if query:
        try:
            df = analyzer.df  # Make df available for the query
            result = eval(query)
            if isinstance(result, pd.DataFrame):
                if len(result) > 20:
                    print(f"\nShowing first 20 of {len(result)} results:")
                    print(result.head(20).to_string())
                else:
                    print(f"\nResults ({len(result)} rows):")
                    print(result.to_string())
            else:
                print(f"\nResult: {result}")
        except Exception as e:
            print(f"Error in query: {e}")

if __name__ == "__main__":
    interactive_menu()
