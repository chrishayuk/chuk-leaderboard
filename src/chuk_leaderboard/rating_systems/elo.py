# chuk_leaderboard/rating_systems/elo.py
import math
from typing import List, Tuple

# imports
from chuk_leaderboard.rating_systems.rating_system import RatingSystem
from chuk_leaderboard.rating_systems.registry import RatingSystemRegistry

class EloRatingSystem(RatingSystem):
    """
    Elo rating system implementation.
    
    The Elo rating system is a method for calculating the relative skill levels
    of players in zero-sum games such as chess. It is named after its creator
    Arpad Elo, a Hungarian-American physics professor.
    """
    
    def __init__(self, k_factor: int = 32, default_rating: int = 1500):
        """
        Initialize the Elo rating system.
        
        Args:
            k_factor: The maximum change in rating after a single game.
                     Higher values mean faster rating changes.
                     Common values:
                     - 32: for beginners
                     - 24: for players under 2100
                     - 16: for players between 2100 and 2400
                     - 12: for players above 2400
            default_rating: The default rating for new players
        """
        self.k_factor = k_factor
        self._default_rating = default_rating
    
    def calculate_rating(self, current_rating: float, 
                        outcomes: List[Tuple[float, float]]) -> float:
        """
        Calculate new rating based on match outcomes.
        
        Args:
            current_rating: Current rating
            outcomes: List of tuples (opponent_rating, result)
                     where result is 1 for win, 0.5 for draw, 0 for loss
        
        Returns:
            New rating
        """
        if not outcomes:
            return current_rating
        
        # Calculate new rating based on all matches
        new_rating = current_rating
        
        for opponent_rating, result in outcomes:
            # Expected score
            expected = self.expected_outcome(current_rating, opponent_rating)
            
            # Calculate rating change
            new_rating += self.k_factor * (result - expected)
        
        return new_rating
    
    def calculate_rating_change(self, rating: float, opponent_rating: float, result: float) -> float:
        """
        Calculate the rating change for a single match.
        
        Args:
            rating: Current rating
            opponent_rating: Opponent's rating
            result: 1 for win, 0.5 for draw, 0 for loss
            
        Returns:
            Change in rating
        """
        expected = self.expected_outcome(rating, opponent_rating)
        return self.k_factor * (result - expected)
    
    def expected_outcome(self, rating1: float, rating2: float) -> float:
        """
        Calculate the expected outcome (win probability) for player1 against player2.
        
        Args:
            rating1: Rating of player 1
            rating2: Rating of player 2
            
        Returns:
            Probability (0-1) of player 1 winning against player 2
        """
        return 1.0 / (1.0 + math.pow(10, (rating2 - rating1) / 400.0))
    
    def get_default_rating(self) -> float:
        """
        Get the default rating for new players.
        
        Returns:
            Default rating
        """
        return self._default_rating
    
    def get_display_name(self) -> str:
        """
        Get the display name of the rating system.
        
        Returns:
            Display name of the rating system
        """
        return f"Elo (K={self.k_factor})"
    
    def adjust_k_factor(self, rating: float) -> int:
        """
        Adjust the K-factor based on player rating.
        
        Args:
            rating: Player's current rating
            
        Returns:
            Adjusted K-factor
        """
        if rating < 2100:
            return 32
        elif rating < 2400:
            return 24
        else:
            return 16
    
    def get_rating_with_dynamic_k(self, rating: float, outcomes: List[Tuple[float, float]]) -> float:
        """
        Calculate new rating with dynamic K-factor based on rating.
        
        Args:
            rating: Current rating
            outcomes: List of tuples (opponent_rating, result)
                     where result is 1 for win, 0.5 for draw, 0 for loss
                     
        Returns:
            New rating
        """
        if not outcomes:
            return rating
        
        # Calculate new rating based on all matches with dynamic K
        new_rating = rating
        k = self.adjust_k_factor(rating)
        
        for opponent_rating, result in outcomes:
            # Expected score
            expected = self.expected_outcome(rating, opponent_rating)
            
            # Calculate rating change
            new_rating += k * (result - expected)
        
        return new_rating


# Register the Elo rating system
RatingSystemRegistry.register("elo", EloRatingSystem)