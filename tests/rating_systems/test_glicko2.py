import math
import pytest
from chuk_leaderboard.rating_systems.glicko2 import Glicko2RatingSystem


def test_get_default_rating():
    """
    Verify that get_default_rating returns the expected
    default rating, rating deviation, and volatility.
    """
    g = Glicko2RatingSystem()
    default_rating, default_rd, default_vol = g.get_default_rating()
    assert default_rating == 1500
    assert default_rd == 350
    assert default_vol == 0.06


def test_get_display_name():
    """
    Test that the display name includes the tau parameter.
    """
    g = Glicko2RatingSystem(tau=0.5)
    assert g.get_display_name() == "Glicko-2 (τ=0.5)"
    
    g2 = Glicko2RatingSystem(tau=0.3)
    assert g2.get_display_name() == "Glicko-2 (τ=0.3)"


def test_no_outcomes():
    """
    When no outcomes are provided, the rating and volatility should
    remain unchanged, while the rating deviation (rd) should increase
    according to the formula sqrt(rd^2 + vol^2), capped at the default RD.
    """
    g = Glicko2RatingSystem()
    
    # Test with different starting RD values
    test_cases = [
        (1500, 100, 0.06),  # Low RD
        (1500, 200, 0.06),  # Medium RD
        (1500, 300, 0.06),  # High RD
        (1500, 350, 0.06),  # Default RD
    ]
    
    for rating, rd, vol in test_cases:
        current_rating = (rating, rd, vol)
        new_rating, new_rd, new_vol = g.calculate_rating(current_rating, [])
        
        # The rating should be unchanged
        assert new_rating == rating
        # Volatility should be unchanged
        assert new_vol == vol
        
        # Calculate expected new RD from inactivity
        expected_new_rd = min(math.sqrt(rd**2 + vol**2), 350)
        assert math.isclose(new_rd, expected_new_rd, rel_tol=1e-6)


def test_expected_outcome():
    """
    Test the expected outcome computation between players with distinct ratings.
    """
    g = Glicko2RatingSystem()
    
    # Test: equal ratings and RDs should result in 0.5 win probability
    equal_probability = g.expected_outcome((1500, 100), (1500, 100))
    assert math.isclose(equal_probability, 0.5, abs_tol=1e-6)
    
    # Test: higher rating should have higher win probability
    higher_probability = g.expected_outcome((1600, 100), (1400, 100))
    assert 0.5 < higher_probability < 1.0
    
    # Test: lower rating should have lower win probability
    lower_probability = g.expected_outcome((1400, 100), (1600, 100))
    assert 0.0 < lower_probability < 0.5
    
    # Test: symmetry property
    p_a = g.expected_outcome((1700, 100), (1500, 100))
    p_b = g.expected_outcome((1500, 100), (1700, 100))
    assert math.isclose(p_a + p_b, 1.0, abs_tol=1e-6)
    
    # High RD impact check
    high_rd_prob = g.expected_outcome((1700, 300), (1500, 50))
    assert 0.5 < high_rd_prob < 1.0

@pytest.mark.parametrize("result", [1.0, 0.5, 0.0])
def test_calculate_rating_single_outcome(result):
    """
    Test calculate_rating for a single match. Rating should move,
    RD decrease, and vol within bounds.
    """
    g = Glicko2RatingSystem()
    start = (1500, 200, 0.06)
    new_rating, new_rd, new_vol = g.calculate_rating(start, [(1600, 30, result)])

    # Direction check
    if result > 0.5:
        assert new_rating > start[0]
    elif result < 0.5:
        assert new_rating < start[0]
    # RD decreases
    assert new_rd < start[1]
    # Vol stays in [0.01,0.1]
    assert 0.01 <= new_vol <= 0.1


def test_calculate_rating_multiple_outcomes():
    """
    Test calculate_rating over multiple matches. RD drops significantly,
    vol remains bounded.
    """
    g = Glicko2RatingSystem()
    start = (1500, 200, 0.06)
    outcomes = [(1600, 30, 1.0), (1400, 100, 0.0), (1500, 50, 0.5)]
    new_rating, new_rd, new_vol = g.calculate_rating(start, outcomes)

    assert new_rd < 200 * 0.8
    assert 0.01 <= new_vol <= 0.1


def test_rating_consistency():
    """
    Players who always win should grow; always lose should fall; RD shrinks.
    """
    g = Glicko2RatingSystem()
    w = {"rating":1500,"rd":350,"vol":0.06}
    l = {"rating":1500,"rd":350,"vol":0.06}
    for _ in range(10):
        w_tuple=(w["rating"],w["rd"],w["vol"])
        l_tuple=(l["rating"],l["rd"],l["vol"])
        w_new, l_new = g.calculate_rating(w_tuple, [(l["rating"], l["rd"], 1.0)]), \
                      g.calculate_rating(l_tuple, [(w_tuple[0], w_tuple[1], 0.0)])
        w["rating"],w["rd"],w["vol"] = w_new
        l["rating"],l["rd"],l["vol"] = l_new
    assert w["rating"]>1500
    assert l["rating"]<1500
    assert w["rd"]<350 and l["rd"]<350


def test_extreme_rating_differences():
    """
    Extreme match correctness and significant rating shifts.
    """
    g = Glicko2RatingSystem()
    high=(2200,50,0.06)
    low=(800,50,0.06)
    p = g.expected_outcome(high[:2], low[:2])
    assert p>0.99
    new_high,_,_ = g.calculate_rating(high, [(low[0],low[1],0.0)])
    new_low,_,_ = g.calculate_rating(low, [(high[0],high[1],1.0)])
    assert new_high<high[0]-10
    assert new_low>low[0]+10


def test_tau_parameter():
    """
    Different tau values run without error and produce bounded outputs.
    """
    g1=Glicko2RatingSystem(tau=0.3)
    g2=Glicko2RatingSystem(tau=1.2)
    start=(1500,200,0.06)
    out1=g1.calculate_rating(start,[(1000,30,0.0)])
    out2=g2.calculate_rating(start,[(1000,30,0.0)])
    for val in (out1+out2):
        assert isinstance(val,float)


def test_rd_effects_on_rating_change():
    """
    Higher RD => larger shifts when winning.
    """
    g=Glicko2RatingSystem()
    certain=(1500,30,0.06)
    uncertain=(1500,300,0.06)
    opp=(1500,100,0.5)
    new_c,_,_ = g.calculate_rating(certain, [(opp[0],opp[1],1.0)])
    new_u,_,_ = g.calculate_rating(uncertain,[(opp[0],opp[1],1.0)])
    assert abs(new_u-uncertain[0])>abs(new_c-certain[0])


def test_inactivity_periods():
    """
    Multiple inactivity periods inflate RD without changing rating or vol.
    """
    g=Glicko2RatingSystem()
    start=(1500,50,0.06)
    cur=start
    for _ in range(5):
        cur=g.calculate_rating(cur,[])
    assert cur[0]==1500
    assert 50<cur[1]<=350
    assert cur[2]==0.06
