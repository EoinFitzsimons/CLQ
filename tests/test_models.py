"""
Tests for CLQ models
"""

import pytest
from datetime import date
from clq.models import Team, Match, Tie, Statistics


class TestTeam:
    def test_team_creation(self):
        team = Team("Real Madrid", "Spain", 134.0)
        assert team.name == "Real Madrid"
        assert team.country == "Spain"
        assert team.uefa_coefficient == 134.0
    
    def test_team_str(self):
        team = Team("Barcelona", "Spain")
        assert str(team) == "Barcelona (Spain)"


class TestMatch:
    def test_match_creation(self):
        home_team = Team("Celtic", "Scotland")
        away_team = Team("Malmö FF", "Sweden")
        match = Match(home_team, away_team, 2, 1, date(2023, 7, 19), "Second Qualifying Round", "First Leg")
        
        assert match.home_team == home_team
        assert match.away_team == away_team
        assert match.home_score == 2
        assert match.away_score == 1
    
    def test_match_winner(self):
        home_team = Team("Celtic", "Scotland")
        away_team = Team("Malmö FF", "Sweden")
        
        # Home team wins
        match1 = Match(home_team, away_team, 2, 1, date(2023, 7, 19), "Test Round", "First Leg")
        assert match1.winner == home_team
        
        # Away team wins
        match2 = Match(home_team, away_team, 1, 2, date(2023, 7, 19), "Test Round", "First Leg")
        assert match2.winner == away_team
        
        # Draw
        match3 = Match(home_team, away_team, 1, 1, date(2023, 7, 19), "Test Round", "First Leg")
        assert match3.winner is None
    
    def test_total_goals(self):
        home_team = Team("Celtic", "Scotland")
        away_team = Team("Malmö FF", "Sweden")
        match = Match(home_team, away_team, 3, 2, date(2023, 7, 19), "Test Round", "First Leg")
        assert match.total_goals == 5


class TestTie:
    def test_tie_creation(self):
        home_team = Team("Celtic", "Scotland")
        away_team = Team("Malmö FF", "Sweden")
        
        first_leg = Match(home_team, away_team, 2, 0, date(2023, 7, 19), "Test Round", "First Leg")
        second_leg = Match(away_team, home_team, 1, 2, date(2023, 7, 26), "Test Round", "Second Leg")
        
        tie = Tie(first_leg, second_leg, "Test Round")
        assert tie.first_leg == first_leg
        assert tie.second_leg == second_leg
    
    def test_aggregate_scores(self):
        home_team = Team("Celtic", "Scotland")
        away_team = Team("Malmö FF", "Sweden")
        
        first_leg = Match(home_team, away_team, 2, 0, date(2023, 7, 19), "Test Round", "First Leg")
        second_leg = Match(away_team, home_team, 1, 2, date(2023, 7, 26), "Test Round", "Second Leg")
        
        tie = Tie(first_leg, second_leg, "Test Round")
        # Celtic: 2 (home in first leg) + 2 (away in second leg) = 4
        # Malmö: 0 (away in first leg) + 1 (home in second leg) = 1
        assert tie.aggregate_home_score == 4
        assert tie.aggregate_away_score == 1
    
    def test_tie_winner(self):
        home_team = Team("Celtic", "Scotland")
        away_team = Team("Malmö FF", "Sweden")
        
        first_leg = Match(home_team, away_team, 2, 0, date(2023, 7, 19), "Test Round", "First Leg")
        second_leg = Match(away_team, home_team, 1, 2, date(2023, 7, 26), "Test Round", "Second Leg")
        
        tie = Tie(first_leg, second_leg, "Test Round")
        assert tie.winner == home_team


class TestStatistics:
    def test_statistics_creation(self):
        teams = [Team("Celtic", "Scotland"), Team("Malmö FF", "Sweden")]
        matches = []
        ties = []
        
        stats = Statistics(matches, ties, teams)
        assert len(stats.teams) == 2
        assert len(stats.matches) == 0
        assert len(stats.ties) == 0
    
    def test_get_team_stats(self):
        celtic = Team("Celtic", "Scotland")
        malmo = Team("Malmö FF", "Sweden")
        
        match1 = Match(celtic, malmo, 2, 0, date(2023, 7, 19), "Test Round", "First Leg")
        match2 = Match(malmo, celtic, 1, 2, date(2023, 7, 26), "Test Round", "Second Leg")
        
        stats = Statistics([match1, match2], [], [celtic, malmo])
        celtic_stats = stats.get_team_stats(celtic)
        
        assert celtic_stats['matches_played'] == 2
        assert celtic_stats['wins'] == 2
        assert celtic_stats['draws'] == 0
        assert celtic_stats['losses'] == 0
        assert celtic_stats['goals_for'] == 4
        assert celtic_stats['goals_against'] == 1
        assert celtic_stats['goal_difference'] == 3