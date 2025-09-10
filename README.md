# CLQ - UEFA Champions League Qualifying Quiz Generator

A comprehensive Python application for compiling, analyzing, and creating quizzes from UEFA Champions League qualifying statistics. The application supports multiple quiz formats and provides detailed statistical analysis of tournament data.

## Features

- **Data Analysis**: Compile and analyze Champions League qualifying statistics
- **Multiple Quiz Formats**: Generate quizzes in multiple choice, true/false, and short answer formats
- **Output Formats**: Export quizzes as text, JSON, or HTML
- **Statistical Insights**: Get comprehensive tournament summaries, team performance, and round statistics
- **CLI Interface**: Easy-to-use command-line interface for all functionality

## Installation

```bash
# Clone the repository
git clone https://github.com/EoinFitzsimons/CLQ.git
cd CLQ

# Install the package
pip install -e .
```

## Quick Start

### 1. Create Sample Data
```bash
clq create-sample-data
```

### 2. Analyze Statistics
```bash
clq analyze data/sample_clq_data.json
```

### 3. Generate a Quiz
```bash
# Text format quiz
clq quiz data/sample_clq_data.json --questions 10 --output-format text

# JSON format quiz saved to file
clq quiz data/sample_clq_data.json --questions 15 --output-format json --output-file my_quiz.json

# HTML format quiz
clq quiz data/sample_clq_data.json --questions 10 --output-format html --output-file quiz.html
```

## Usage

### Command Line Interface

#### Analyze Data
```bash
clq analyze <data_file> [OPTIONS]
```

Options:
- `--format`: Input format (json, csv) - default: json
- `--teams-file`: Separate teams file for CSV format

#### Generate Quiz
```bash
clq quiz <data_file> [OPTIONS]
```

Options:
- `--questions`: Number of questions (default: 15)
- `--quiz-type`: Type of quiz (mixed, multiple_choice, true_false, short_answer) - default: mixed
- `--output-format`: Output format (text, json, html) - default: text
- `--output-file`: File to save quiz to (optional)
- `--format`: Input data format (json, csv) - default: json

#### Create Sample Data
```bash
clq create-sample-data [--output-dir <directory>]
```

### Data Format

The application accepts data in JSON format with the following structure:

```json
{
  "teams": [
    {
      "name": "Real Madrid",
      "country": "Spain",
      "uefa_coefficient": 134.0
    }
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
  "ties": [
    {
      "first_leg_date": "2023-07-19",
      "second_leg_date": "2023-07-26",
      "round": "Second Qualifying Round"
    }
  ]
}
```

## Quiz Formats

### Multiple Choice
Questions with 4 options where one is correct.

### True/False
Binary questions about tournament statistics.

### Short Answer
Open-ended questions requiring specific answers.

### Mixed
Combination of all question types for comprehensive assessment.

## Output Formats

### Text
Clean, readable format suitable for printing or terminal display.

### JSON
Structured format for integration with other applications or web interfaces.

### HTML
Web-ready format with styling for online quizzes.

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Project Structure
```
clq/
├── __init__.py          # Package initialization
├── models.py            # Data models for teams, matches, ties
├── data_loader.py       # Data loading and analysis functionality
├── quiz_generator.py    # Quiz generation and formatting
└── cli.py              # Command-line interface

tests/
├── test_models.py       # Tests for data models
├── test_data_loader.py  # Tests for data loading
└── test_quiz_generator.py # Tests for quiz generation
```

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- click >= 8.0.0

## License

This project is open source and available under the MIT License.
