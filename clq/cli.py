"""
Command Line Interface for the CLQ application
"""

import click
import json
import os
from .data_loader import DataLoader, Analyzer
from .quiz_generator import QuizGenerator, QuizFormatter


@click.group()
@click.version_option(version="0.1.0")
def main():
    """UEFA Champions League Qualifying Statistics and Quiz Generator"""
    pass


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--format', 'file_format', default='json', type=click.Choice(['json', 'csv']),
              help='Format of the input data file')
@click.option('--teams-file', type=click.Path(exists=True), 
              help='Separate teams file for CSV format')
def analyze(data_file, file_format, teams_file):
    """Analyze Champions League qualifying statistics from data file"""
    loader = DataLoader()
    
    try:
        if file_format == 'json':
            stats = loader.load_from_json(data_file)
        else:
            stats = loader.load_from_csv(data_file, teams_file)
        
        analyzer = Analyzer(stats)
        
        # Display tournament summary
        summary = analyzer.get_tournament_summary()
        click.echo("\n📊 Tournament Summary")
        click.echo("=" * 40)
        click.echo(f"Total Teams: {summary['total_teams']}")
        click.echo(f"Total Matches: {summary['total_matches']}")
        click.echo(f"Total Goals: {summary['total_goals']}")
        click.echo(f"Average Goals per Match: {summary['average_goals_per_match']}")
        click.echo(f"Total Ties: {summary['total_ties']}")
        
        # Display top scorers
        click.echo("\n🏆 Top Scoring Teams")
        click.echo("=" * 40)
        top_scorers = stats.get_top_scorers(5)
        for i, scorer in enumerate(top_scorers, 1):
            team = scorer['team']
            goals = scorer['goals_for']
            click.echo(f"{i}. {team.name} ({team.country}) - {goals} goals")
        
        # Display round statistics
        click.echo("\n📈 Round Statistics")
        click.echo("=" * 40)
        round_stats = analyzer.get_round_statistics()
        for round_name, stats_data in round_stats.items():
            click.echo(f"{round_name}: {stats_data['matches']} matches, "
                      f"{stats_data['total_goals']} goals (avg: {stats_data['average_goals']})")
        
    except Exception as e:
        click.echo(f"Error analyzing data: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--format', 'file_format', default='json', type=click.Choice(['json', 'csv']),
              help='Format of the input data file')
@click.option('--teams-file', type=click.Path(exists=True),
              help='Separate teams file for CSV format')
@click.option('--questions', default=15, help='Number of questions to generate')
@click.option('--quiz-type', default='mixed', 
              type=click.Choice(['mixed', 'multiple_choice', 'true_false', 'short_answer']),
              help='Type of quiz to generate')
@click.option('--output-format', default='text',
              type=click.Choice(['text', 'json', 'html']),
              help='Output format for the quiz')
@click.option('--output-file', type=click.Path(),
              help='File to save the quiz to (optional)')
def quiz(data_file, file_format, teams_file, questions, quiz_type, output_format, output_file):
    """Generate a quiz from Champions League qualifying statistics"""
    loader = DataLoader()
    
    try:
        # Load data
        if file_format == 'json':
            stats = loader.load_from_json(data_file)
        else:
            stats = loader.load_from_csv(data_file, teams_file)
        
        # Generate quiz
        generator = QuizGenerator(stats)
        
        if quiz_type == 'mixed':
            quiz_questions = generator.generate_mixed_quiz(questions)
        elif quiz_type == 'multiple_choice':
            quiz_questions = generator.generate_multiple_choice_questions(questions)
        elif quiz_type == 'true_false':
            quiz_questions = generator.generate_true_false_questions(questions)
        elif quiz_type == 'short_answer':
            quiz_questions = generator.generate_short_answer_questions(questions)
        
        # Format output
        if output_format == 'json':
            output_content = json.dumps(QuizFormatter.format_as_json(quiz_questions), indent=2)
        elif output_format == 'html':
            output_content = QuizFormatter.format_as_html(quiz_questions)
        else:
            output_content = QuizFormatter.format_as_text(quiz_questions)
        
        # Output or save
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_content)
            click.echo(f"Quiz saved to {output_file}")
        else:
            click.echo(output_content)
    
    except Exception as e:
        click.echo(f"Error generating quiz: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option('--output-dir', default='./data', help='Directory to create sample data in')
def create_sample_data(output_dir):
    """Create sample Champions League qualifying data for testing"""
    os.makedirs(output_dir, exist_ok=True)
    
    sample_data = {
        "teams": [
            {"name": "Real Madrid", "country": "Spain", "uefa_coefficient": 134.0},
            {"name": "Manchester City", "country": "England", "uefa_coefficient": 125.0},
            {"name": "Bayern Munich", "country": "Germany", "uefa_coefficient": 120.0},
            {"name": "PSG", "country": "France", "uefa_coefficient": 112.0},
            {"name": "Juventus", "country": "Italy", "uefa_coefficient": 89.0},
            {"name": "Ajax", "country": "Netherlands", "uefa_coefficient": 68.0},
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
            },
            {
                "home_team": "Malmö FF",
                "away_team": "Celtic",
                "home_score": 1,
                "away_score": 2,
                "date": "2023-07-26",
                "round": "Second Qualifying Round",
                "leg": "Second Leg"
            },
            {
                "home_team": "Ajax",
                "away_team": "Juventus",
                "home_score": 1,
                "away_score": 3,
                "date": "2023-08-02",
                "round": "Third Qualifying Round",
                "leg": "First Leg"
            },
            {
                "home_team": "Juventus",
                "away_team": "Ajax",
                "home_score": 2,
                "away_score": 1,
                "date": "2023-08-09",
                "round": "Third Qualifying Round",
                "leg": "Second Leg"
            }
        ],
        "ties": [
            {
                "first_leg_date": "2023-07-19",
                "second_leg_date": "2023-07-26",
                "round": "Second Qualifying Round"
            },
            {
                "first_leg_date": "2023-08-02",
                "second_leg_date": "2023-08-09",
                "round": "Third Qualifying Round"
            }
        ]
    }
    
    output_file = os.path.join(output_dir, 'sample_clq_data.json')
    with open(output_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    click.echo(f"Sample data created at {output_file}")
    click.echo("You can now run: clq analyze data/sample_clq_data.json")
    click.echo("Or generate a quiz: clq quiz data/sample_clq_data.json")


if __name__ == '__main__':
    main()