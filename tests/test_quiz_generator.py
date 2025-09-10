"""
Tests for quiz generation functionality
"""

import pytest
from clq.models import Team, Match, Statistics
from clq.quiz_generator import (
    MultipleChoiceQuestion, TrueFalseQuestion, ShortAnswerQuestion,
    QuizGenerator, QuizFormatter
)
from datetime import date


class TestQuestions:
    def test_multiple_choice_question(self):
        question = MultipleChoiceQuestion(
            "What is the capital of Spain?",
            "Madrid",
            ["Barcelona", "Seville", "Valencia"]
        )
        
        formatted = question.format_question()
        assert formatted['type'] == 'multiple_choice'
        assert 'Madrid' in formatted['options']
        assert len(formatted['options']) == 4
        
        # Test answer checking
        correct_index = formatted['correct_index']
        assert question.check_answer(str(correct_index))
        assert question.check_answer("Madrid")
    
    def test_true_false_question(self):
        question = TrueFalseQuestion("Real Madrid is from Spain", True)
        
        formatted = question.format_question()
        assert formatted['type'] == 'true_false'
        assert formatted['correct_answer'] is True
        
        # Test answer checking
        assert question.check_answer("true")
        assert question.check_answer("True")
        assert question.check_answer("yes")
        assert not question.check_answer("false")
    
    def test_short_answer_question(self):
        question = ShortAnswerQuestion(
            "What team is from Madrid?",
            "Real Madrid",
            ["Real Madrid", "real madrid", "REAL MADRID"]
        )
        
        formatted = question.format_question()
        assert formatted['type'] == 'short_answer'
        assert formatted['correct_answer'] == "Real Madrid"
        
        # Test answer checking
        assert question.check_answer("Real Madrid")
        assert question.check_answer("real madrid")
        assert not question.check_answer("Barcelona")


class TestQuizGenerator:
    def setup_method(self):
        """Set up test data"""
        self.teams = [
            Team("Celtic", "Scotland", 32.0),
            Team("Malmö FF", "Sweden", 28.0),
            Team("Ajax", "Netherlands", 68.0),
            Team("Juventus", "Italy", 89.0)
        ]
        
        self.matches = [
            Match(self.teams[0], self.teams[1], 2, 0, date(2023, 7, 19), "Second Qualifying Round", "First Leg"),
            Match(self.teams[1], self.teams[0], 1, 2, date(2023, 7, 26), "Second Qualifying Round", "Second Leg"),
            Match(self.teams[2], self.teams[3], 1, 3, date(2023, 8, 2), "Third Qualifying Round", "First Leg"),
            Match(self.teams[3], self.teams[2], 2, 1, date(2023, 8, 9), "Third Qualifying Round", "Second Leg")
        ]
        
        self.stats = Statistics(self.matches, [], self.teams)
        self.generator = QuizGenerator(self.stats)
    
    def test_generate_multiple_choice_questions(self):
        questions = self.generator.generate_multiple_choice_questions(3)
        assert len(questions) <= 3
        
        for question in questions:
            assert isinstance(question, MultipleChoiceQuestion)
            formatted = question.format_question()
            assert len(formatted['options']) >= 2
    
    def test_generate_true_false_questions(self):
        questions = self.generator.generate_true_false_questions(3)
        assert len(questions) <= 3
        
        for question in questions:
            assert isinstance(question, TrueFalseQuestion)
            formatted = question.format_question()
            assert formatted['type'] == 'true_false'
    
    def test_generate_short_answer_questions(self):
        questions = self.generator.generate_short_answer_questions(3)
        assert len(questions) <= 3
        
        for question in questions:
            assert isinstance(question, ShortAnswerQuestion)
            formatted = question.format_question()
            assert formatted['type'] == 'short_answer'
    
    def test_generate_mixed_quiz(self):
        questions = self.generator.generate_mixed_quiz(9)
        assert len(questions) <= 9
        
        # Should have different types of questions
        question_types = set(q.format_question()['type'] for q in questions)
        assert len(question_types) > 1


class TestQuizFormatter:
    def setup_method(self):
        """Set up test questions"""
        self.questions = [
            MultipleChoiceQuestion("Test MC", "Answer A", ["Answer B", "Answer C"]),
            TrueFalseQuestion("Test TF", True),
            ShortAnswerQuestion("Test SA", "Test Answer")
        ]
    
    def test_format_as_json(self):
        result = QuizFormatter.format_as_json(self.questions)
        
        assert 'quiz_type' in result
        assert 'total_questions' in result
        assert 'questions' in result
        assert result['total_questions'] == 3
        assert len(result['questions']) == 3
    
    def test_format_as_text(self):
        result = QuizFormatter.format_as_text(self.questions)
        
        assert "UEFA Champions League Qualifying Quiz" in result
        assert "Question 1:" in result
        assert "Question 2:" in result
        assert "Question 3:" in result
    
    def test_format_as_html(self):
        result = QuizFormatter.format_as_html(self.questions)
        
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "Champions League Qualifying Quiz" in result
        assert "Question 1:" in result