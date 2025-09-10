"""
Quiz generation functionality supporting multiple formats
"""

import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import Statistics, Team, Match
from .data_loader import Analyzer


class Question(ABC):
    """Base class for quiz questions"""
    
    def __init__(self, question_text: str, correct_answer: str, difficulty: str = "medium"):
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.difficulty = difficulty
    
    @abstractmethod
    def format_question(self) -> Dict[str, Any]:
        """Format the question for output"""
        pass
    
    @abstractmethod
    def check_answer(self, answer: str) -> bool:
        """Check if the provided answer is correct"""
        pass


class MultipleChoiceQuestion(Question):
    """Multiple choice question with options"""
    
    def __init__(self, question_text: str, correct_answer: str, wrong_answers: List[str], difficulty: str = "medium"):
        super().__init__(question_text, correct_answer, difficulty)
        self.options = [correct_answer] + wrong_answers
        random.shuffle(self.options)
        self.correct_index = self.options.index(correct_answer)
    
    def format_question(self) -> Dict[str, Any]:
        return {
            "type": "multiple_choice",
            "question": self.question_text,
            "options": self.options,
            "correct_index": self.correct_index,
            "difficulty": self.difficulty
        }
    
    def check_answer(self, answer: str) -> bool:
        try:
            answer_index = int(answer)
            return answer_index == self.correct_index
        except (ValueError, IndexError):
            return answer.strip().lower() == self.correct_answer.lower()


class TrueFalseQuestion(Question):
    """True/False question"""
    
    def __init__(self, question_text: str, is_true: bool, difficulty: str = "medium"):
        correct_answer = "True" if is_true else "False"
        super().__init__(question_text, correct_answer, difficulty)
        self.is_true = is_true
    
    def format_question(self) -> Dict[str, Any]:
        return {
            "type": "true_false",
            "question": self.question_text,
            "correct_answer": self.is_true,
            "difficulty": self.difficulty
        }
    
    def check_answer(self, answer: str) -> bool:
        answer = answer.strip().lower()
        if answer in ["true", "t", "yes", "y", "1"]:
            return self.is_true
        elif answer in ["false", "f", "no", "n", "0"]:
            return not self.is_true
        return False


class ShortAnswerQuestion(Question):
    """Short answer question"""
    
    def __init__(self, question_text: str, correct_answer: str, acceptable_answers: List[str] = None, difficulty: str = "medium"):
        super().__init__(question_text, correct_answer, difficulty)
        self.acceptable_answers = acceptable_answers or [correct_answer]
    
    def format_question(self) -> Dict[str, Any]:
        return {
            "type": "short_answer",
            "question": self.question_text,
            "correct_answer": self.correct_answer,
            "difficulty": self.difficulty
        }
    
    def check_answer(self, answer: str) -> bool:
        answer = answer.strip().lower()
        return any(acc.lower() == answer for acc in self.acceptable_answers)


class QuizGenerator:
    """Generates quizzes from Champions League qualifying statistics"""
    
    def __init__(self, statistics: Statistics):
        self.stats = statistics
        self.analyzer = Analyzer(statistics)
    
    def generate_multiple_choice_questions(self, count: int = 5) -> List[MultipleChoiceQuestion]:
        """Generate multiple choice questions"""
        questions = []
        
        # Top scorer question
        top_scorers = self.stats.get_top_scorers(4)
        if len(top_scorers) >= 4:
            correct_team = top_scorers[0]['team']
            wrong_teams = [scorer['team'].name for scorer in top_scorers[1:4]]
            questions.append(MultipleChoiceQuestion(
                f"Which team scored the most goals in Champions League qualifying?",
                correct_team.name,
                wrong_teams
            ))
        
        # Highest scoring match question
        highest_scoring = self.stats.get_highest_scoring_matches(1)
        if highest_scoring:
            match = highest_scoring[0]
            correct_answer = f"{match.total_goals}"
            wrong_answers = [str(match.total_goals - 1), str(match.total_goals + 1), str(match.total_goals - 2)]
            questions.append(MultipleChoiceQuestion(
                f"How many total goals were scored in the highest-scoring match ({match})?",
                correct_answer,
                wrong_answers
            ))
        
        # Country representation question
        countries = list(set(team.country for team in self.stats.teams))
        if len(countries) >= 4:
            random.shuffle(countries)
            correct_country = countries[0]
            country_teams = [team for team in self.stats.teams if team.country == correct_country]
            wrong_answers = countries[1:4]
            questions.append(MultipleChoiceQuestion(
                f"Which country had {len(country_teams)} teams in the qualifying rounds?",
                correct_country,
                wrong_answers
            ))
        
        return questions[:count]
    
    def generate_true_false_questions(self, count: int = 5) -> List[TrueFalseQuestion]:
        """Generate true/false questions"""
        questions = []
        
        # Tournament statistics
        summary = self.analyzer.get_tournament_summary()
        
        # Average goals question
        avg_goals = summary['average_goals_per_match']
        is_above_2 = avg_goals > 2.0
        questions.append(TrueFalseQuestion(
            f"The average goals per match in the qualifying rounds was above 2.0",
            is_above_2
        ))
        
        # Total matches question
        total_matches = summary['total_matches']
        is_above_50 = total_matches > 50
        questions.append(TrueFalseQuestion(
            f"More than 50 matches were played in the qualifying rounds",
            is_above_50
        ))
        
        # Team participation
        if self.stats.teams:
            random_team = random.choice(self.stats.teams)
            team_stats = self.stats.get_team_stats(random_team)
            played_more_than_2 = team_stats['matches_played'] > 2
            questions.append(TrueFalseQuestion(
                f"{random_team.name} played more than 2 matches in the qualifying rounds",
                played_more_than_2
            ))
        
        return questions[:count]
    
    def generate_short_answer_questions(self, count: int = 5) -> List[ShortAnswerQuestion]:
        """Generate short answer questions"""
        questions = []
        
        # Top scoring team
        top_scorers = self.stats.get_top_scorers(1)
        if top_scorers:
            top_team = top_scorers[0]['team']
            goals = top_scorers[0]['goals_for']
            questions.append(ShortAnswerQuestion(
                f"Which team scored the most goals ({goals}) in the qualifying rounds?",
                top_team.name,
                [top_team.name.lower(), top_team.name.upper()]
            ))
        
        # Tournament totals
        summary = self.analyzer.get_tournament_summary()
        questions.append(ShortAnswerQuestion(
            f"How many teams participated in the Champions League qualifying rounds?",
            str(summary['total_teams'])
        ))
        
        questions.append(ShortAnswerQuestion(
            f"How many total goals were scored across all qualifying matches?",
            str(summary['total_goals'])
        ))
        
        return questions[:count]
    
    def generate_mixed_quiz(self, total_questions: int = 15) -> List[Question]:
        """Generate a mixed quiz with different question types"""
        mc_count = total_questions // 3
        tf_count = total_questions // 3
        sa_count = total_questions - mc_count - tf_count
        
        questions = []
        questions.extend(self.generate_multiple_choice_questions(mc_count))
        questions.extend(self.generate_true_false_questions(tf_count))
        questions.extend(self.generate_short_answer_questions(sa_count))
        
        random.shuffle(questions)
        return questions


class QuizFormatter:
    """Formats quizzes for different output formats"""
    
    @staticmethod
    def format_as_json(questions: List[Question]) -> Dict[str, Any]:
        """Format quiz as JSON"""
        return {
            "quiz_type": "Champions League Qualifying Quiz",
            "total_questions": len(questions),
            "questions": [q.format_question() for q in questions]
        }
    
    @staticmethod
    def format_as_text(questions: List[Question]) -> str:
        """Format quiz as plain text"""
        output = ["UEFA Champions League Qualifying Quiz", "=" * 40, ""]
        
        for i, question in enumerate(questions, 1):
            formatted = question.format_question()
            output.append(f"Question {i}: {formatted['question']}")
            
            if formatted['type'] == 'multiple_choice':
                for j, option in enumerate(formatted['options']):
                    output.append(f"  {chr(65 + j)}. {option}")
            elif formatted['type'] == 'true_false':
                output.append("  True / False")
            
            output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def format_as_html(questions: List[Question]) -> str:
        """Format quiz as HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Champions League Qualifying Quiz</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .question { margin-bottom: 20px; }
                .options { margin-left: 20px; }
                .option { margin-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>UEFA Champions League Qualifying Quiz</h1>
        """
        
        for i, question in enumerate(questions, 1):
            formatted = question.format_question()
            html += f'<div class="question">'
            html += f'<h3>Question {i}: {formatted["question"]}</h3>'
            
            if formatted['type'] == 'multiple_choice':
                html += '<div class="options">'
                for j, option in enumerate(formatted['options']):
                    html += f'<div class="option"><input type="radio" name="q{i}" value="{j}"> {chr(65 + j)}. {option}</div>'
                html += '</div>'
            elif formatted['type'] == 'true_false':
                html += '<div class="options">'
                html += f'<div class="option"><input type="radio" name="q{i}" value="true"> True</div>'
                html += f'<div class="option"><input type="radio" name="q{i}" value="false"> False</div>'
                html += '</div>'
            elif formatted['type'] == 'short_answer':
                html += f'<input type="text" name="q{i}" placeholder="Your answer...">'
            
            html += '</div>'
        
        html += """
        </body>
        </html>
        """
        return html