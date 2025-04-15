import math
import pytest
from typing import List, Tuple
from chuk_leaderboard.rating_systems.points_based import PointsBasedRankingSystem

def test_get_default_rating():
    """
    Verify that get_default_rating returns the expected default points and empty history.
    """
    # Test with default settings
    points_system = PointsBasedRankingSystem()
    default_rating = points_system.get_default_rating()
    assert default_rating[0] == 0.0  # Default points should be 0
    assert default_rating[1] == []   # Default history should be empty list
    
    # Test with custom default points
    custom_points_system = PointsBasedRankingSystem(default_points=100.0)
    custom_default = custom_points_system.get_default_rating()
    assert custom_default[0] == 100.0
    assert custom_default[1] == []

def test_get_display_name():
    """
    Test that the display name is correctly generated.
    """
    # Test with regular points-based system
    points_system = PointsBasedRankingSystem()
    assert points_system.get_display_name() == "Points-Based"
    
    # Test with rank-based system
    rank_system = PointsBasedRankingSystem(rank_points=[10, 8, 6, 4, 2])
    assert rank_system.get_display_name() == "Points-Based (Ranked)"

def test_no_outcomes():
    """
    When no outcomes are provided, the points and history should remain unchanged.
    """
    points_system = PointsBasedRankingSystem()
    
    # Test with just points (no history)
    total_points = 100.0
    new_total, new_history = points_system.calculate_rating(total_points, [])
    assert new_total == total_points
    assert new_history == []
    
    # Test with points and history
    current_rating = (100.0, [20.0, 30.0, 50.0])
    new_total, new_history = points_system.calculate_rating(current_rating, [])
    assert new_total == current_rating[0]
    assert new_history == current_rating[1]

def test_calculate_rating_single_outcome():
    """
    Test calculate_rating with a single outcome.
    """
    points_system = PointsBasedRankingSystem()
    
    # Test with just points (no history)
    total_points = 100.0
    outcomes = [25.0]  # Add 25 points
    
    new_total, new_history = points_system.calculate_rating(total_points, outcomes)
    assert new_total == total_points + 25.0
    assert new_history == [25.0]
    
    # Test with points and history
    current_rating = (100.0, [20.0, 30.0, 50.0])
    outcomes = [35.0]  # Add 35 points
    
    new_total, new_history = points_system.calculate_rating(current_rating, outcomes)
    assert new_total == current_rating[0] + 35.0
    assert new_history == current_rating[1] + [35.0]

def test_calculate_rating_multiple_outcomes():
    """
    Test calculate_rating with multiple outcomes.
    """
    points_system = PointsBasedRankingSystem()
    
    # Test with multiple outcomes
    current_rating = (100.0, [20.0, 30.0])
    outcomes = [15.0, 25.0, 35.0]  # Multiple events
    
    new_total, new_history = points_system.calculate_rating(current_rating, outcomes)
    assert new_total == current_rating[0] + sum(outcomes)
    assert new_history == current_rating[1] + outcomes

def test_rank_points():
    """
    Test that the rank_points parameter correctly transforms outcomes.
    """
    # Define a system with rank points
    rank_points = [10, 8, 6, 4, 2]
    rank_system = PointsBasedRankingSystem(rank_points=rank_points)
    
    # Test with rank positions
    current_rating = (0.0, [])
    outcomes = [1, 3, 2]  # 1st, 3rd, 2nd place
    
    new_total, new_history = rank_system.calculate_rating(current_rating, outcomes)
    
    # Expected points: 10 (1st) + 6 (3rd) + 8 (2nd) = 24
    assert new_total == 24.0
    assert new_history == outcomes

def test_bonus_points():
    """
    Test that bonus points are correctly applied.
    """
    # Define a system with bonus points for scores over 100
    bonus_system = PointsBasedRankingSystem(bonus_threshold=100.0, bonus_points=10.0)
    
    # Test with various scores
    current_rating = (0.0, [])
    outcomes = [80.0, 120.0, 90.0, 150.0]  # Two scores above threshold
    
    new_total, new_history = bonus_system.calculate_rating(current_rating, outcomes)
    
    # Expected points: 80 + (120+10) + 90 + (150+10) = 460
    assert new_total == 460.0
    assert new_history == outcomes  # History stores original scores

def test_expected_outcome_with_total_points():
    """
    Test expected outcome calculation based solely on total points.
    """
    points_system = PointsBasedRankingSystem(points_history_weight=0.0)
    
    # Test with equal points
    prob = points_system.expected_outcome(1000.0, 1000.0)
    assert math.isclose(prob, 0.5, abs_tol=1e-6)
    
    # Test with higher player1 points
    prob = points_system.expected_outcome(1200.0, 1000.0)
    assert prob > 0.5
    
    # Test with lower player1 points
    prob = points_system.expected_outcome(800.0, 1000.0)
    assert prob < 0.5
    
    # Test symmetry
    prob1 = points_system.expected_outcome(1200.0, 1000.0)
    prob2 = points_system.expected_outcome(1000.0, 1200.0)
    assert math.isclose(prob1 + prob2, 1.0, abs_tol=1e-6)

def test_expected_outcome_with_history_weight():
    """
    Test expected outcome calculation with history weight.
    """
    # System with 50% weight on recent performance
    points_system = PointsBasedRankingSystem(points_history_weight=0.5)
    
    # Player with high total but poor recent performance
    player1 = (1200.0, [20.0, 30.0, 40.0])  # Poor recent
    
    # Player with lower total but great recent performance
    player2 = (1000.0, [80.0, 90.0, 100.0])  # Strong recent
    
    # Calculate probabilities
    prob = points_system.expected_outcome(player1, player2)
    
    # Due to recent performance weight, player2 should have higher probability
    # despite lower total points
    assert prob < 0.5

def test_project_season_finish():
    """
    Test season projection calculations.
    """
    points_system = PointsBasedRankingSystem()
    
    # Test with consistent performance
    current_rating = (300.0, [20.0, 20.0, 20.0, 20.0])
    remaining_events = 6
    
    projection = points_system.project_season_finish(current_rating, remaining_events)
    
    # Expected: 300 + (20 * 6) = 420
    assert math.isclose(projection["projected_points"], 420.0, abs_tol=1e-6)
    
    # Min and max should be same (all performances identical)
    assert math.isclose(projection["min_points"], 300.0 + 20.0 * remaining_events, abs_tol=1e-6)
    assert math.isclose(projection["max_points"], 300.0 + 20.0 * remaining_events, abs_tol=1e-6)
    
    # Test with varied performance
    current_rating = (300.0, [10.0, 20.0, 30.0, 40.0])
    remaining_events = 6
    
    projection = points_system.project_season_finish(current_rating, remaining_events)
    
    # Expected: 300 + (avg of 10,20,30,40) * 6 = 300 + 25 * 6 = 450
    assert math.isclose(projection["projected_points"], 450.0, abs_tol=1e-6)
    
    # Min points: 300 + (10 * 6) = 360
    assert math.isclose(projection["min_points"], 360.0, abs_tol=1e-6)
    
    # Max points: 300 + (40 * 6) = 540
    assert math.isclose(projection["max_points"], 540.0, abs_tol=1e-6)

def test_get_trend():
    """
    Test trend calculation.
    """
    points_system = PointsBasedRankingSystem()
    
    # Test improving trend
    history = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    trend = points_system.get_trend(history)
    assert trend == "up"
    
    # Test declining trend
    history = [60.0, 50.0, 40.0, 30.0, 20.0, 10.0]
    trend = points_system.get_trend(history)
    assert trend == "down"
    
    # Test stable trend
    history = [25.0, 24.0, 26.0, 25.0, 24.0, 26.0]
    trend = points_system.get_trend(history)
    assert trend == "stable"
    
    # Test not enough data
    history = [25.0, 30.0, 35.0]
    trend = points_system.get_trend(history)
    assert trend == "stable"  # Default with insufficient data

def test_rank_participants():
    """
    Test participant ranking functionality.
    """
    points_system = PointsBasedRankingSystem()
    
    # Create a set of participants with different point totals
    participants = {
        "Player A": (120.0, [30.0, 40.0, 50.0]),
        "Player B": (150.0, [40.0, 50.0, 60.0]),
        "Player C": (100.0, [20.0, 30.0, 50.0]),
        "Player D": (180.0, [50.0, 60.0, 70.0])
    }
    
    # Get the rankings
    rankings = points_system.rank_participants(participants)
    
    # Check the ranking order
    assert rankings[0][0] == "Player D"  # 1st place
    assert rankings[1][0] == "Player B"  # 2nd place
    assert rankings[2][0] == "Player A"  # 3rd place
    assert rankings[3][0] == "Player C"  # 4th place
    
    # Check the ranking values
    assert rankings[0][1] == 180.0
    assert rankings[1][1] == 150.0
    assert rankings[2][1] == 120.0
    assert rankings[3][1] == 100.0