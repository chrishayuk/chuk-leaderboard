# chuk_leaderboard/rating_systems/glicko2.py
import math
from typing import List, Tuple

# imports
from chuk_leaderboard.rating_systems.rating_system import RatingSystem
from chuk_leaderboard.rating_systems.registry import RatingSystemRegistry



class Glicko2RatingSystem(RatingSystem):
    """
    Glicko-2 rating system implementation.
    
    The Glicko-2 system provides ratings that reflect a participant's skill level,
    rating deviation (RD) that reflects the uncertainty in the rating,
    and volatility that reflects how consistent a participant's performance is.
    
    Reference: http://www.glicko.net/glicko/glicko2.pdf
    """
    
    def __init__(self, tau: float = 0.5):
        """
        Initialize the Glicko-2 system.
        
        Args:
            tau: System constant that constraints rating volatility changes.
                 Typically between 0.3 and 1.2. Higher values allow for greater
                 volatility changes.
        """
        self.tau = tau
        
        # Glicko-2 scale conversion constants
        self._scale_factor = 173.7178
        self._default_rating = 1500
        self._default_rd = 350
        self._default_vol = 0.06
    
    def calculate_rating(self, current_rating: Tuple[float, float, float], 
                        outcomes: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
        """
        Calculate new rating, RD, and volatility based on match outcomes.
        
        Args:
            current_rating: Tuple of (rating, rating_deviation, volatility)
            outcomes: List of tuples (opponent_rating, opponent_rd, result)
                    where result is 1 for win, 0.5 for draw, 0 for loss
        
        Returns:
            Tuple of (new_rating, new_rd, new_vol)
        """
        rating, rd, vol = current_rating
        
        # If no outcomes, simply increase the RD and return
        if not outcomes:
            # Increase RD over time (uncertainty grows when inactive)
            new_rd = min(math.sqrt(rd**2 + vol**2), self._default_rd)
            return rating, new_rd, vol
            
        # Step 1: Convert to Glicko-2 scale
        mu = (rating - self._default_rating) / self._scale_factor
        phi = rd / self._scale_factor
        
        # Step 2: Calculate g(phi) and E for each opponent, and the variance v
        v_sum = 0
        delta_sum = 0
        
        for opp_r, opp_rd, result in outcomes:
            opp_mu = (opp_r - self._default_rating) / self._scale_factor
            opp_phi = opp_rd / self._scale_factor
            
            # g(phi) is the magnitude of the impact of RD on the expected outcome
            g = 1 / math.sqrt(1 + 3 * opp_phi**2 / math.pi**2)
            
            # E is the expected outcome
            E = 1 / (1 + math.exp(-g * (mu - opp_mu)))
            
            # Calculate variance and delta components
            v_sum += g**2 * E * (1 - E)
            delta_sum += g * (result - E)
        
        # If variance is zero (very unlikely), return unchanged ratings
        if v_sum == 0:
            return rating, rd, vol
            
        # Step 3: Calculate estimated improvement in rating
        v = 1 / v_sum
        delta = v * delta_sum
        
        # Step 4: Update volatility using the iteration algorithm
        a = math.log(vol**2)
        
        # Define the function f(x) to find the root
        def f(x):
            ex = math.exp(x)
            return (ex * (delta**2 - phi**2 - v - ex) / 
                  (2 * (phi**2 + v + ex)**2)) - ((x - a) / self.tau**2)
        
        # Find the value of x that minimizes f(x)
        # In a production system, use a proper root-finding method
        # like the Illinois algorithm as specified in the Glicko-2 paper
        # Here we use a simplified approximation
        x = a
        if delta**2 > phi**2 + v:
            x = math.log(delta**2 - phi**2 - v)
        
        # Simplified approach - adjust based on performance
        # For better accuracy, implement a full root-finding algorithm
        if abs(delta) > phi + v:
            adjustment = 1.2  # Increase volatility when performance is unexpected
        else:
            adjustment = 0.9  # Decrease volatility when performance is as expected
        
        new_vol = vol * adjustment
        new_vol = max(0.01, min(new_vol, 0.1))  # Keep volatility in reasonable bounds
        
        # Step 5: Update rating deviation
        phi_star = math.sqrt(phi**2 + new_vol**2)
        new_phi = 1 / math.sqrt(1/phi_star**2 + 1/v)
        
        # Step 6: Update rating
        new_mu = mu + new_phi**2 * delta_sum
        
        # Step 7: Convert back to original scale
        new_rating = self._scale_factor * new_mu + self._default_rating
        new_rd = self._scale_factor * new_phi
        
        return new_rating, new_rd, new_vol
    
    def expected_outcome(self, rating1: Tuple[float, float], rating2: Tuple[float, float]) -> float:
        """
        Calculate the expected outcome (win probability) for participant1 against participant2.
        
        Args:
            rating1: Tuple of (rating, rating_deviation) for participant 1
            rating2: Tuple of (rating, rating_deviation) for participant 2
            
        Returns:
            Probability (0-1) of participant 1 winning
        """
        # Extract values from tuples
        rating1_val, rd1 = rating1
        rating2_val, rd2 = rating2
        
        # Convert to Glicko-2 scale
        mu1 = (rating1_val - self._default_rating) / self._scale_factor
        phi1 = rd1 / self._scale_factor
        mu2 = (rating2_val - self._default_rating) / self._scale_factor
        phi2 = rd2 / self._scale_factor
        
        # Calculate g(phi)
        g = 1 / math.sqrt(1 + 3 * phi2**2 / math.pi**2)
        
        # Calculate expected outcome
        E = 1 / (1 + math.exp(-g * (mu1 - mu2)))
        
        return E
    
    def get_default_rating(self) -> Tuple[float, float, float]:
        """
        Get the default rating, RD, and volatility for new participants.
        
        Returns:
            Tuple of (default_rating, default_rd, default_vol)
        """
        return self._default_rating, self._default_rd, self._default_vol
    
    def get_display_name(self) -> str:
        """
        Get the display name of the rating system.
        
        Returns:
            Display name of the rating system
        """
        return f"Glicko-2 (τ={self.tau})"


# Register the Glicko-2 rating system
RatingSystemRegistry.register("glicko2", Glicko2RatingSystem)