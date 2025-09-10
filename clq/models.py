"""
Data models for Champions League Qualifying statistics
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import date


@dataclass
class Team:
    """Represents a football team in Champions League qualifying"""
    name: str
    country: str
    uefa_coefficient: Optional[float] = None
    
    def __str__(self):
        return f"{self.name} ({self.country})"


@dataclass
class Match:
    """Represents a single Champions League qualifying match"""
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int
    date: date
    round: str  # e.g., "First Qualifying Round", "Second Qualifying Round"
    leg: str   # "First Leg" or "Second Leg"
    
    @property
    def winner(self) -> Optional[Team]:
        """Returns the winner of the match, None if draw"""
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None
    
    @property
    def total_goals(self) -> int:
        """Returns total goals scored in the match"""
        return self.home_score + self.away_score
    
    def __str__(self):
        return f"{self.home_team.name} {self.home_score}-{self.away_score} {self.away_team.name}"


@dataclass
class Tie:
    """Represents a two-legged tie in Champions League qualifying"""
    first_leg: Match
    second_leg: Match
    round: str
    
    @property
    def aggregate_home_score(self) -> int:
        """Total goals scored by first leg home team across both legs"""
        return self.first_leg.home_score + self.second_leg.away_score
    
    @property
    def aggregate_away_score(self) -> int:
        """Total goals scored by first leg away team across both legs"""
        return self.first_leg.away_score + self.second_leg.home_score
    
    @property
    def winner(self) -> Team:
        """Returns the winner of the tie"""
        if self.aggregate_home_score > self.aggregate_away_score:
            return self.first_leg.home_team
        elif self.aggregate_away_score > self.aggregate_home_score:
            return self.first_leg.away_team
        else:
            # Away goals rule or other tiebreaker logic could go here
            # For now, return first leg home team if tied
            return self.first_leg.home_team
    
    def __str__(self):
        return f"{self.first_leg.home_team.name} vs {self.first_leg.away_team.name} ({self.aggregate_home_score}-{self.aggregate_away_score} agg.)"


@dataclass 
class Statistics:
    """Container for compiled Champions League qualifying statistics"""
    matches: List[Match]
    ties: List[Tie]
    teams: List[Team]
    
    def get_team_stats(self, team: Team) -> Dict[str, Any]:
        """Get comprehensive statistics for a specific team"""
        team_matches = [m for m in self.matches if m.home_team == team or m.away_team == team]
        
        wins = sum(1 for m in team_matches if m.winner == team)
        draws = sum(1 for m in team_matches if m.winner is None)
        losses = len(team_matches) - wins - draws
        
        goals_for = sum(m.home_score if m.home_team == team else m.away_score for m in team_matches)
        goals_against = sum(m.away_score if m.home_team == team else m.home_score for m in team_matches)
        
        return {
            'matches_played': len(team_matches),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goals_for - goals_against
        }
    
    def get_top_scorers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top scoring teams"""
        team_stats = [
            {'team': team, **self.get_team_stats(team)} 
            for team in self.teams
        ]
        return sorted(team_stats, key=lambda x: x['goals_for'], reverse=True)[:limit]
    
    def get_highest_scoring_matches(self, limit: int = 10) -> List[Match]:
        """Get matches with most goals"""
        return sorted(self.matches, key=lambda m: m.total_goals, reverse=True)[:limit]