"""
Tests for data loading functionality
"""

import pytest
import json
import tempfile
import os
from clq.data_loader import DataLoader, Analyzer
from clq.models import Statistics


class TestDataLoader:
    def test_load_from_json(self):
        # Create sample JSON data
        sample_data = {
            "teams": [
                {"name": "Celtic", "country": "Scotland", "uefa_coefficient": 32.0},
                {"name": "Malmö FF", "country": "Sweden", "uefa_coefficient": 28.0}
            ],
            "matches": [
                {
                    "home_team": "Celtic",
                    "away_team": "Malmö FF",
                    "home_score": 2,
                    "away_score": 0,
                    "date": "2023-07-19",
                    "round": "Second Qualifying Round",
                    "leg": "First Leg"
                }
            ],
            "ties": []
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_data, f)
            temp_file = f.name
        
        try:
            loader = DataLoader()
            stats = loader.load_from_json(temp_file)
            
            assert len(stats.teams) == 2
            assert len(stats.matches) == 1
            assert stats.teams[0].name == "Celtic"
            assert stats.matches[0].home_score == 2
        
        finally:
            os.unlink(temp_file)


class TestAnalyzer:
    def setup_method(self):
        """Set up test data"""
        from clq.models import Team, Match
        from datetime import date
        
        teams = [
            Team("Celtic", "Scotland", 32.0),
            Team("Malmö FF", "Sweden", 28.0),
            Team("Ajax", "Netherlands", 68.0)
        ]
        
        matches = [
            Match(teams[0], teams[1], 2, 0, date(2023, 7, 19), "Second Qualifying Round", "First Leg"),
            Match(teams[1], teams[0], 1, 2, date(2023, 7, 26), "Second Qualifying Round", "Second Leg"),
            Match(teams[2], teams[0], 3, 1, date(2023, 8, 2), "Third Qualifying Round", "First Leg")
        ]
        
        self.stats = Statistics(matches, [], teams)
        self.analyzer = Analyzer(self.stats)
    
    def test_get_tournament_summary(self):
        summary = self.analyzer.get_tournament_summary()
        
        assert summary['total_matches'] == 3
        assert summary['total_teams'] == 3
        assert summary['total_goals'] == 9  # 2+0+1+2+3+1
        assert summary['average_goals_per_match'] == 3.0
    
    def test_get_round_statistics(self):
        round_stats = self.analyzer.get_round_statistics()
        
        assert "Second Qualifying Round" in round_stats
        assert "Third Qualifying Round" in round_stats
        
        second_round = round_stats["Second Qualifying Round"]
        assert second_round['matches'] == 2
        assert second_round['total_goals'] == 5  # 2+0+1+2
    
    def test_get_country_performance(self):
        country_stats = self.analyzer.get_country_performance()
        
        assert "Scotland" in country_stats
        assert "Sweden" in country_stats
        assert "Netherlands" in country_stats
        
        scotland_stats = country_stats["Scotland"]
        assert scotland_stats['teams'] == 1
        assert scotland_stats['total_matches'] == 3  # Celtic played in all 3 matches