import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class CLQScorersAnalyzer:
    def __init__(self, csv_path='GlobalTable/top_1000_scorers.csv'):
        """Initialize the analyzer with the scraped data."""
        self.csv_path = csv_path
        self.df = None
        self.load_data()
        self.clean_data()
    
    def load_data(self):
        """Load the CSV data into a pandas DataFrame."""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"Loaded {len(self.df)} players from {self.csv_path}")
        except FileNotFoundError:
            print(f"Error: Could not find {self.csv_path}")
            return
    
    def clean_data(self):
        """Clean and prepare the data for analysis."""
        if self.df is None:
            return
        
        # Convert numeric columns, handling '-' as NaN
        numeric_columns = ['Age', 'Seasons', 'Matches', 'SubOn', 'SubOff', 'Assists', 'Penalties', 'Goals']
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col].replace('-', np.nan), errors='coerce')
        
        # Create calculated metrics
        self.df['Goals_Per_Match'] = self.df['Goals'] / self.df['Matches']
        self.df['Goals_Per_Season'] = self.df['Goals'] / self.df['Seasons']
        self.df['Assists_Per_Match'] = self.df['Assists'] / self.df['Matches']
        self.df['Total_Contributions'] = self.df['Goals'] + self.df['Assists'].fillna(0)
        self.df['Contributions_Per_Match'] = self.df['Total_Contributions'] / self.df['Matches']
        
        # Clean up infinity values
        self.df = self.df.replace([np.inf, -np.inf], np.nan)
        
        print("Data cleaned and metrics calculated!")
    
    def summary_stats(self):
        """Display summary statistics of the dataset."""
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        
        print(f"Total Players: {len(self.df)}")
        print(f"Total Goals: {self.df['Goals'].sum()}")
        print(f"Total Matches: {self.df['Matches'].sum()}")
        print(f"Average Goals per Player: {self.df['Goals'].mean():.2f}")
        print(f"Average Matches per Player: {self.df['Matches'].mean():.2f}")
        print(f"Overall Goals per Match: {self.df['Goals'].sum() / self.df['Matches'].sum():.3f}")
        
        print("\nTop Countries by Player Count:")
        country_counts = self.df['Nationality'].value_counts().head(10)
        for country, count in country_counts.items():
            print(f"  {country}: {count} players")
    
    def best_goals_per_game(self, min_matches=10, top_n=20):
        """Find players with the best goals per game ratio."""
        print(f"\n" + "="*60)
        print(f"BEST GOALS PER MATCH (min {min_matches} matches)")
        print("="*60)
        
        filtered_df = self.df[self.df['Matches'] >= min_matches].copy()
        top_scorers = filtered_df.nlargest(top_n, 'Goals_Per_Match')
        
        for idx, (_, player) in enumerate(top_scorers.iterrows(), 1):
            print(f"{idx:2d}. {player['Player']:<25} | "
                  f"{player['Goals_Per_Match']:.3f} goals/match | "
                  f"{player['Goals']:2.0f} goals in {player['Matches']:2.0f} matches | "
                  f"{player['Position']}")
        
        return top_scorers
    
    def most_prolific_scorers(self, top_n=20):
        """Find the most prolific goal scorers overall."""
        print(f"\n" + "="*60)
        print("MOST PROLIFIC SCORERS (Total Goals)")
        print("="*60)
        
        top_scorers = self.df.nlargest(top_n, 'Goals')
        
        for idx, (_, player) in enumerate(top_scorers.iterrows(), 1):
            print(f"{idx:2d}. {player['Player']:<25} | "
                  f"{player['Goals']:2.0f} goals | "
                  f"{player['Matches']:2.0f} matches | "
                  f"{player['Goals_Per_Match']:.3f} goals/match | "
                  f"{player['Club(s)']}")
        
        return top_scorers
    
    def best_contributors(self, min_matches=10, top_n=20):
        """Find players with best total contributions (goals + assists)."""
        print(f"\n" + "="*60)
        print(f"BEST TOTAL CONTRIBUTORS (Goals + Assists, min {min_matches} matches)")
        print("="*60)
        
        filtered_df = self.df[self.df['Matches'] >= min_matches].copy()
        top_contributors = filtered_df.nlargest(top_n, 'Contributions_Per_Match')
        
        for idx, (_, player) in enumerate(top_contributors.iterrows(), 1):
            goals = player['Goals'] if not pd.isna(player['Goals']) else 0
            assists = player['Assists'] if not pd.isna(player['Assists']) else 0
            print(f"{idx:2d}. {player['Player']:<25} | "
                  f"{player['Contributions_Per_Match']:.3f} contrib/match | "
                  f"{goals:.0f}G + {assists:.0f}A = {player['Total_Contributions']:.0f} | "
                  f"{player['Matches']:2.0f} matches")
        
        return top_contributors
    
    def analyze_by_position(self):
        """Analyze performance by playing position."""
        print(f"\n" + "="*60)
        print("ANALYSIS BY POSITION")
        print("="*60)
        
        position_stats = self.df.groupby('Position').agg({
            'Player': 'count',
            'Goals': ['sum', 'mean'],
            'Matches': 'mean',
            'Goals_Per_Match': 'mean',
            'Age': 'mean'
        }).round(3)
        
        position_stats.columns = ['Player_Count', 'Total_Goals', 'Avg_Goals', 'Avg_Matches', 'Goals_Per_Match', 'Avg_Age']
        position_stats = position_stats.sort_values('Goals_Per_Match', ascending=False)
        
        print(f"{'Position':<20} | {'Count':<5} | {'Goals/Match':<11} | {'Avg Goals':<9} | {'Avg Matches':<11}")
        print("-" * 75)
        
        for position, stats in position_stats.iterrows():
            if stats['Player_Count'] >= 5:  # Only show positions with 5+ players
                print(f"{position:<20} | {stats['Player_Count']:<5.0f} | "
                      f"{stats['Goals_Per_Match']:<11.3f} | {stats['Avg_Goals']:<9.1f} | "
                      f"{stats['Avg_Matches']:<11.1f}")
        
        return position_stats
    
    def analyze_by_nationality(self, top_n=15):
        """Analyze performance by nationality."""
        print(f"\n" + "="*60)
        print(f"TOP {top_n} COUNTRIES BY TOTAL GOALS")
        print("="*60)
        
        country_stats = self.df.groupby('Nationality').agg({
            'Player': 'count',
            'Goals': ['sum', 'mean'],
            'Goals_Per_Match': 'mean'
        }).round(3)
        
        country_stats.columns = ['Player_Count', 'Total_Goals', 'Avg_Goals_Per_Player', 'Avg_Goals_Per_Match']
        country_stats = country_stats.sort_values('Total_Goals', ascending=False).head(top_n)
        
        print(f"{'Country':<15} | {'Players':<7} | {'Total Goals':<11} | {'Avg Goals/Player':<15} | {'Goals/Match':<11}")
        print("-" * 80)
        
        for country, stats in country_stats.iterrows():
            print(f"{country:<15} | {stats['Player_Count']:<7.0f} | "
                  f"{stats['Total_Goals']:<11.0f} | {stats['Avg_Goals_Per_Player']:<15.1f} | "
                  f"{stats['Avg_Goals_Per_Match']:<11.3f}")
        
        return country_stats
    
    def longevity_analysis(self):
        """Analyze players with longest careers."""
        print(f"\n" + "="*60)
        print("LONGEVITY ANALYSIS (Most Seasons)")
        print("="*60)
        
        long_careers = self.df.nlargest(20, 'Seasons')
        
        for idx, (_, player) in enumerate(long_careers.iterrows(), 1):
            print(f"{idx:2d}. {player['Player']:<25} | "
                  f"{player['Seasons']:2.0f} seasons | "
                  f"{player['Matches']:3.0f} matches | "
                  f"{player['Goals']:2.0f} goals | "
                  f"{player['Goals_Per_Season']:.1f} goals/season")
        
        return long_careers
    
    def query_player(self, player_name):
        """Query specific player statistics."""
        matches = self.df[self.df['Player'].str.contains(player_name, case=False, na=False)]
        
        if matches.empty:
            print(f"No player found matching '{player_name}'")
            return None
        
        print(f"\n" + "="*60)
        print(f"PLAYER SEARCH RESULTS for '{player_name}'")
        print("="*60)
        
        for _, player in matches.iterrows():
            print(f"\nPlayer: {player['Player']}")
            print(f"Position: {player['Position']}")
            print(f"Club(s): {player['Club(s)']}")
            print(f"Nationality: {player['Nationality']}")
            print(f"Age: {player['Age']}")
            print(f"Rank: #{player['Rank']}")
            print(f"Career: {player['Seasons']} seasons, {player['Matches']} matches")
            print(f"Goals: {player['Goals']} ({player['Goals_Per_Match']:.3f} per match)")
            if not pd.isna(player['Assists']):
                print(f"Assists: {player['Assists']} ({player['Assists_Per_Match']:.3f} per match)")
            print(f"Total Contributions: {player['Total_Contributions']} ({player['Contributions_Per_Match']:.3f} per match)")
        
        return matches
    
    def create_visualizations(self):
        """Create visualization plots."""
        if self.df is None:
            return
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Goals per match distribution
        axes[0,0].hist(self.df['Goals_Per_Match'].dropna(), bins=30, alpha=0.7, color='skyblue')
        axes[0,0].set_title('Distribution of Goals per Match')
        axes[0,0].set_xlabel('Goals per Match')
        axes[0,0].set_ylabel('Number of Players')
        
        # 2. Goals vs Matches scatter plot
        axes[0,1].scatter(self.df['Matches'], self.df['Goals'], alpha=0.6, color='coral')
        axes[0,1].set_title('Goals vs Matches Played')
        axes[0,1].set_xlabel('Matches Played')
        axes[0,1].set_ylabel('Total Goals')
        
        # 3. Top positions by average goals per match
        pos_stats = self.df.groupby('Position')['Goals_Per_Match'].mean().sort_values(ascending=True).tail(10)
        axes[1,0].barh(range(len(pos_stats)), pos_stats.values, color='lightgreen')
        axes[1,0].set_yticks(range(len(pos_stats)))
        axes[1,0].set_yticklabels(pos_stats.index)
        axes[1,0].set_title('Average Goals per Match by Position')
        axes[1,0].set_xlabel('Goals per Match')
        
        # 4. Age distribution
        axes[1,1].hist(self.df['Age'].dropna(), bins=20, alpha=0.7, color='gold')
        axes[1,1].set_title('Age Distribution of Players')
        axes[1,1].set_xlabel('Age')
        axes[1,1].set_ylabel('Number of Players')
        
        plt.tight_layout()
        plt.savefig('GlobalTable/clq_scorers_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved as 'GlobalTable/clq_scorers_analysis.png'")
        plt.show()
    
    def run_full_analysis(self):
        """Run a comprehensive analysis of the data."""
        print("🏆 UEFA CHAMPIONS LEAGUE QUALIFYING - TOP SCORERS ANALYSIS")
        print("="*80)
        
        self.summary_stats()
        self.best_goals_per_game()
        self.most_prolific_scorers()
        self.best_contributors()
        self.analyze_by_position()
        self.analyze_by_nationality()
        self.longevity_analysis()
        
        print(f"\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print("Available methods:")
        print("- analyzer.query_player('player_name') - Search for specific player")
        print("- analyzer.create_visualizations() - Generate charts")
        print("- analyzer.df - Access the full DataFrame for custom analysis")

def main():
    """Main function to run the analysis."""
    analyzer = CLQScorersAnalyzer()
    
    if analyzer.df is not None:
        analyzer.run_full_analysis()
        
        # Create visualizations
        try:
            analyzer.create_visualizations()
        except Exception as e:
            print(f"Could not create visualizations: {e}")
        
        return analyzer
    
    return None

if __name__ == "__main__":
    analyzer = main()
