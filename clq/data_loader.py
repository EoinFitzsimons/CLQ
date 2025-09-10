"""
Data loading and analysis functionality for Champions League Qualifying statistics
"""

import json
import pandas as pd
from datetime import date, datetime
from typing import List, Dict, Any
from .models import Team, Match, Tie, Statistics


class DataLoader:
    """Loads Champions League qualifying data from various sources"""
    
    def load_from_json(self, filepath: str) -> Statistics:
        """Load statistics from a JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Parse teams
        teams = [Team(**team_data) for team_data in data.get('teams', [])]
        team_lookup = {team.name: team for team in teams}
        
        # Parse matches
        matches = []
        for match_data in data.get('matches', []):
            match = Match(
                home_team=team_lookup[match_data['home_team']],
                away_team=team_lookup[match_data['away_team']],
                home_score=match_data['home_score'],
                away_score=match_data['away_score'],
                date=datetime.strptime(match_data['date'], '%Y-%m-%d').date(),
                round=match_data['round'],
                leg=match_data['leg']
            )
            matches.append(match)
        
        # Parse ties
        ties = []
        for tie_data in data.get('ties', []):
            first_leg = next(m for m in matches if m.date.isoformat() == tie_data['first_leg_date'])
            second_leg = next(m for m in matches if m.date.isoformat() == tie_data['second_leg_date'])
            tie = Tie(first_leg=first_leg, second_leg=second_leg, round=tie_data['round'])
            ties.append(tie)
        
        return Statistics(matches=matches, ties=ties, teams=teams)
    
    def load_from_csv(self, matches_file: str, teams_file: str = None) -> Statistics:
        """Load statistics from CSV files"""
        matches_df = pd.read_csv(matches_file)
        
        # Load teams
        if teams_file:
            teams_df = pd.read_csv(teams_file)
            teams = [Team(**row.to_dict()) for _, row in teams_df.iterrows()]
        else:
            # Extract teams from matches
            team_names = set(matches_df['home_team'].tolist() + matches_df['away_team'].tolist())
            teams = [Team(name=name, country="Unknown") for name in team_names]
        
        team_lookup = {team.name: team for team in teams}
        
        # Load matches
        matches = []
        for _, row in matches_df.iterrows():
            match = Match(
                home_team=team_lookup[row['home_team']],
                away_team=team_lookup[row['away_team']],
                home_score=int(row['home_score']),
                away_score=int(row['away_score']),
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                round=row['round'],
                leg=row['leg']
            )
            matches.append(match)
        
        # Group matches into ties (simplified - assumes proper ordering)
        ties = []
        tie_groups = {}
        for match in matches:
            key = f"{match.home_team.name}_{match.away_team.name}_{match.round}"
            if key not in tie_groups:
                tie_groups[key] = []
            tie_groups[key].append(match)
        
        for group in tie_groups.values():
            if len(group) == 2:
                first_leg = min(group, key=lambda m: m.date)
                second_leg = max(group, key=lambda m: m.date)
                ties.append(Tie(first_leg=first_leg, second_leg=second_leg, round=first_leg.round))
        
        return Statistics(matches=matches, ties=ties, teams=teams)


class Analyzer:
    """Analyzes Champions League qualifying statistics"""
    
    def __init__(self, statistics: Statistics):
        self.stats = statistics
    
    def get_tournament_summary(self) -> Dict[str, Any]:
        """Get overall tournament statistics"""
        total_matches = len(self.stats.matches)
        total_goals = sum(m.total_goals for m in self.stats.matches)
        avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0
        
        return {
            'total_matches': total_matches,
            'total_teams': len(self.stats.teams),
            'total_goals': total_goals,
            'average_goals_per_match': round(avg_goals_per_match, 2),
            'total_ties': len(self.stats.ties)
        }
    
    def get_round_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics broken down by round"""
        round_stats = {}
        
        for round_name in set(m.round for m in self.stats.matches):
            round_matches = [m for m in self.stats.matches if m.round == round_name]
            total_goals = sum(m.total_goals for m in round_matches)
            
            round_stats[round_name] = {
                'matches': len(round_matches),
                'total_goals': total_goals,
                'average_goals': round(total_goals / len(round_matches), 2) if round_matches else 0,
                'highest_scoring_match': max(round_matches, key=lambda m: m.total_goals) if round_matches else None
            }
        
        return round_stats
    
    def get_country_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by country"""
        country_stats = {}
        
        for team in self.stats.teams:
            if team.country not in country_stats:
                country_stats[team.country] = {
                    'teams': 0,
                    'total_matches': 0,
                    'total_wins': 0,
                    'total_goals_for': 0,
                    'total_goals_against': 0
                }
            
            team_data = self.stats.get_team_stats(team)
            country_stats[team.country]['teams'] += 1
            country_stats[team.country]['total_matches'] += team_data['matches_played']
            country_stats[team.country]['total_wins'] += team_data['wins']
            country_stats[team.country]['total_goals_for'] += team_data['goals_for']
            country_stats[team.country]['total_goals_against'] += team_data['goals_against']
        
        return country_stats