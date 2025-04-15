# chuk_leaderboard/visualizers/rating_visualizer.py
from typing import Any, Tuple

# imports
from chuk_leaderboard.visualizers.base_visualizer import BaseVisualizer


class RatingVisualizer(BaseVisualizer):
    """
    Base class for rating-related visualizers.
    """
    def __init__(self, title: str = "Rating Analysis", output_dir: str = "output"):
        super().__init__(title, output_dir)
    
    def _convert_to_display_format(self, rating_data: Any) -> Tuple[float, float, float]:
        """
        Convert different rating formats to a standard display format.
        
        Args:
            rating_data: Rating data in various formats (Elo, Glicko2, etc.)
            
        Returns:
            Tuple of (rating, rating_deviation, volatility) for display
            For rating systems without RD or volatility, these values are 0
        """
        # Handle different rating system formats
        if isinstance(rating_data, tuple) and len(rating_data) >= 3:
            # Glicko2-style rating (rating, rd, vol)
            return rating_data[0], rating_data[1], rating_data[2]
        elif isinstance(rating_data, tuple) and len(rating_data) == 2:
            # Rating with RD but no volatility
            return rating_data[0], rating_data[1], 0.0
        elif isinstance(rating_data, (int, float)):
            # Simple rating like Elo
            return float(rating_data), 0.0, 0.0
        else:
            # Unknown format, default to zeros
            return 0.0, 0.0, 0.0
        
        