# chuk_leaderboard/rating_systems/rating_system.py
from abc import ABC, abstractmethod
from typing import List, Any


class RatingSystem(ABC):
    """
    Abstract base class for rating systems.
    
    This provides a common interface for different rating systems (Elo, Glicko2, etc.)
    to be used interchangeably in the leaderboard system.
    """
    
    @abstractmethod
    def calculate_rating(self, current_rating: Any, outcomes: List[Any]) -> Any:
        """
        Calculate new rating based on match outcomes.
        
        Args:
            current_rating: Current rating information (format depends on rating system)
            outcomes: List of match outcomes (format depends on rating system)
        
        Returns:
            Updated rating information (format depends on rating system)
        """
        pass
    
    @abstractmethod
    def expected_outcome(self, rating1: Any, rating2: Any) -> float:
        """
        Calculate the expected outcome (win probability) between two ratings.
        
        Args:
            rating1: Rating information for first participant
            rating2: Rating information for second participant
        
        Returns:
            Probability (0-1) of the first participant winning
        """
        pass
    
    @abstractmethod
    def get_default_rating(self) -> Any:
        """
        Get the default rating for new participants.
        
        Returns:
            Default rating information for new participants
        """
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """
        Get the display name of the rating system.
        
        Returns:
            Display name of the rating system
        """
        pass
