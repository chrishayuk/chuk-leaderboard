import math
import pytest
from chuk_leaderboard.rating_systems.elo import EloRatingSystem

def test_get_default_rating():
    """
    Verify that get_default_rating returns the expected default rating.
    """
    elo = EloRatingSystem()
    default_rating = elo.get_default_rating()
    assert default_rating == 1500
    
    # Test with custom default rating
    custom_elo = EloRatingSystem(default_rating=2000)
    custom_default = custom_elo.get_default_rating()
    assert custom_default == 2000

def test_get_display_name():
    """
    Test that the display name includes the K-factor.
    """
    elo = EloRatingSystem(k_factor=32)
    assert elo.get_display_name() == "Elo (K=32)"
    
    elo2 = EloRatingSystem(k_factor=16)
    assert elo2.get_display_name() == "Elo (K=16)"

def test_no_outcomes():
    """
    When no outcomes are provided, the rating should remain unchanged.
    """
    elo = EloRatingSystem()
    rating = 1500
    new_rating = elo.calculate_rating(rating, [])
    
    # The rating should be unchanged.
    assert new_rating == rating

def test_expected_outcome():
    """
    Test the expected outcome computation between two players with distinct ratings.
    """
    elo = EloRatingSystem()
    
    # Test: equal ratings should result in 0.5 win probability
    equal_probability = elo.expected_outcome(1500, 1500)
    assert math.isclose(equal_probability, 0.5, abs_tol=1e-6)
    
    # Test: higher rating should have higher win probability
    higher_probability = elo.expected_outcome(1600, 1400)
    assert higher_probability > 0.5 and higher_probability < 1.0
    
    # Test: lower rating should have lower win probability
    lower_probability = elo.expected_outcome(1400, 1600)
    assert lower_probability < 0.5 and lower_probability > 0.0
    
    # Test: symmetry property - P(A beats B) + P(B beats A) should be 1
    p_a_beats_b = elo.expected_outcome(1700, 1500)
    p_b_beats_a = elo.expected_outcome(1500, 1700)
    assert math.isclose(p_a_beats_b + p_b_beats_a, 1.0, abs_tol=1e-6)

@pytest.mark.parametrize("result", [1.0, 0.5, 0.0])
def test_calculate_rating_single_outcome(result):
    """
    Test calculate_rating when a single match outcome is provided.
    We test for a win (result = 1), draw (result = 0.5), and loss (result = 0).
    """
    elo = EloRatingSystem(k_factor=32)
    rating = 1500
    opponent_rating = 1500
    
    # Calculate expected change based on the Elo formula: K * (result - expected)
    expected_result = elo.expected_outcome(rating, opponent_rating)
    expected_change = 32 * (result - expected_result)
    expected_new_rating = rating + expected_change
    
    # Calculate actual new rating
    new_rating = elo.calculate_rating(rating, [(opponent_rating, result)])
    
    # The new rating should match our expectation
    assert math.isclose(new_rating, expected_new_rating, abs_tol=1e-6)
    
    # Check the direction of rating change:
    if result > expected_result:  # Better than expected result
        assert new_rating > rating
    elif result < expected_result:  # Worse than expected result
        assert new_rating < rating
    else:  # Result matches expectation
        assert math.isclose(new_rating, rating, abs_tol=1e-6)

def test_calculate_rating_change():
    """
    Test the rating change calculation for a single match.
    """
    elo = EloRatingSystem(k_factor=20)
    
    # Win against equal opponent (expected = 0.5)
    change = elo.calculate_rating_change(1500, 1500, 1.0)
    assert math.isclose(change, 20 * 0.5, abs_tol=1e-6)
    
    # Loss against weaker opponent (expected > 0.5)
    change = elo.calculate_rating_change(1600, 1400, 0.0)
    assert change < 0  # Should lose more rating than expected
    
    # Draw against stronger opponent (expected < 0.5)
    change = elo.calculate_rating_change(1400, 1600, 0.5)
    assert change > 0  # Should gain rating

def test_calculate_rating_multiple_outcomes():
    """
    Test calculate_rating when multiple match outcomes are provided.
    This verifies that the aggregation over several matches works as expected.
    """
    elo = EloRatingSystem(k_factor=24)
    rating = 1500
    
    # Three outcomes: win against stronger, loss against weaker, draw against equal
    outcomes = [(1600, 1.0), (1400, 0.0), (1500, 0.5)]
    
    # Calculate expected changes for each match
    expected_changes = []
    for opponent_rating, result in outcomes:
        expected = elo.expected_outcome(rating, opponent_rating)
        expected_changes.append(24 * (result - expected))
    
    expected_new_rating = rating + sum(expected_changes)
    
    # Calculate actual new rating
    new_rating = elo.calculate_rating(rating, outcomes)
    
    # The new rating should match our expectation
    assert math.isclose(new_rating, expected_new_rating, abs_tol=1e-6)

def test_adjust_k_factor():
    """
    Test that the adjust_k_factor method returns different K values based on rating.
    """
    elo = EloRatingSystem()
    
    # Below 2100 should get K=32
    assert elo.adjust_k_factor(1500) == 32
    assert elo.adjust_k_factor(2099) == 32
    
    # Between 2100 and 2400 should get K=24
    assert elo.adjust_k_factor(2100) == 24
    assert elo.adjust_k_factor(2300) == 24
    assert elo.adjust_k_factor(2399) == 24
    
    # Above 2400 should get K=16
    assert elo.adjust_k_factor(2400) == 16
    assert elo.adjust_k_factor(2500) == 16

def test_get_rating_with_dynamic_k():
    """
    Test the dynamic K-factor rating calculation.
    """
    elo = EloRatingSystem()
    
    # Calculate new rating with dynamic K for a player just crossing the 2100 threshold
    rating = 2090
    outcomes = [(2000, 1.0)]  # Win against weaker opponent
    
    # First with standard K=32
    new_rating_standard = elo.calculate_rating(rating, outcomes)
    
    # Then with dynamic K
    new_rating_dynamic = elo.get_rating_with_dynamic_k(rating, outcomes)
    
    # Dynamic K should use K=32 for this rating
    assert math.isclose(new_rating_standard, new_rating_dynamic, abs_tol=1e-6)
    
    # Now test with a higher-rated player (should use K=24)
    rating = 2200
    outcomes = [(2000, 1.0)]  # Win against weaker opponent
    
    # Calculate with explicit K=24
    elo_explicit = EloRatingSystem(k_factor=24)
    new_rating_explicit = elo_explicit.calculate_rating(rating, outcomes)
    
    # Calculate with dynamic K
    new_rating_dynamic = elo.get_rating_with_dynamic_k(rating, outcomes)
    
    # Should be the same since dynamic K should use K=24 for this rating
    assert math.isclose(new_rating_explicit, new_rating_dynamic, abs_tol=1e-6)