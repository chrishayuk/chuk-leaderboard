# chuk_leaderboard/rating_systems/points_based.py
import math
import statistics
from typing import List, Tuple, Dict, Optional, Any, Union
import numpy as np

# imports
from chuk_leaderboard.rating_systems.rating_system import RatingSystem
from chuk_leaderboard.rating_systems.registry import RatingSystemRegistry

class PointsBasedRankingSystem(RatingSystem):
    """
    Points-based ranking system implementation.
    
    This system ranks participants based on accumulated points, with optional
    weighting factors and bonus points. Suitable for fantasy sports leagues,
    season-long competitions, or any point-accumulation ranking system.
    """
    
    def __init__(self, 
                 default_points: float = 0.0,
                 points_history_weight: float = 0.0,
                 rank_points: Optional[List[float]] = None,
                 weekly_average_window: int = 3,
                 bonus_threshold: Optional[float] = None,
                 bonus_points: float = 0.0):
        """
        Initialize the points-based ranking system.
        
        Args:
            default_points: Starting points for new participants
            points_history_weight: Weight for historical performance (0.0-1.0)
                                  0.0 means only total points matter
                                  1.0 means only recent performance matters
            rank_points: Points awarded for specific ranks [1st, 2nd, 3rd, ...]
                       If None, raw point values are used instead
            weekly_average_window: Number of recent events to use for trend analysis
            bonus_threshold: Threshold for awarding bonus points (e.g., > 100 points)
            bonus_points: Extra points awarded when exceeding the bonus threshold
        """
        self._default_points = default_points
        self.points_history_weight = max(0.0, min(1.0, points_history_weight))
        self.rank_points = rank_points
        self.weekly_average_window = max(1, weekly_average_window)
        self.bonus_threshold = bonus_threshold
        self.bonus_points = bonus_points
    
    def calculate_rating(self, current_rating: Union[float, Tuple[float, List[float]]], 
                        outcomes: List[float]) -> Tuple[float, List[float]]:
        """
        Calculate new point total and update performance history.
        
        Args:
            current_rating: Current (total_points, points_history) or just total_points
            outcomes: List of point values earned in recent events
        
        Returns:
            Tuple of (new_total_points, updated_points_history)
        """
        # Handle different input formats
        if isinstance(current_rating, tuple) and len(current_rating) == 2:
            total_points, points_history = current_rating
        else:
            total_points = current_rating
            points_history = []
        
        if not outcomes:
            return (total_points, points_history)
        
        # Keep a copy of the original outcomes for history
        original_outcomes = outcomes.copy()
        
        # Process outcomes for scoring while preserving the original values for history
        processed_outcomes = outcomes.copy()
        
        # Apply rank points if specified
        if self.rank_points is not None:
            transformed = []
            for score in processed_outcomes:
                # Convert the score to a rank (assuming higher numbers indicate better rank)
                # and then use the corresponding rank points.
                rank = int(score) - 1  # Convert to 0-based index
                if 0 <= rank < len(self.rank_points):
                    transformed.append(self.rank_points[rank])
                else:
                    transformed.append(0.0)  # Default for ranks beyond the specified list
            processed_outcomes = transformed
        
        # Apply bonus points if threshold is specified
        if self.bonus_threshold is not None:
            processed_outcomes = [
                score + self.bonus_points if score > self.bonus_threshold else score
                for score in processed_outcomes
            ]
        
        # Calculate new total points using the processed outcomes
        additional_points = sum(processed_outcomes)
        new_total_points = total_points + additional_points
        
        # Update points history with the original outcomes
        updated_history = points_history + original_outcomes
        
        return (new_total_points, updated_history)

    def expected_outcome(self, rating1: Union[float, Tuple[float, List[float]]], 
                        rating2: Union[float, Tuple[float, List[float]]]) -> float:
        """
        Estimate the probability that participant1 will outscore participant2 in the next event.
        
        Args:
            rating1: (total_points, points_history) or just total_points for participant 1
            rating2: (total_points, points_history) or just total_points for participant 2
            
        Returns:
            Probability (0-1) of participant1 outscoring participant2
        """
        # Extract total points and history
        if isinstance(rating1, tuple) and len(rating1) == 2:
            total1, history1 = rating1
        else:
            total1, history1 = rating1, []
            
        if isinstance(rating2, tuple) and len(rating2) == 2:
            total2, history2 = rating2
        else:
            total2, history2 = rating2, []
        
        # If no history weight is set, just compare total points
        if self.points_history_weight == 0.0:
            # Simple sigmoid function to convert point difference to probability
            point_diff = total1 - total2
            return 1.0 / (1.0 + math.exp(-point_diff / 100.0))
        
        # Get recent performance for both participants
        recent1 = history1[-self.weekly_average_window:] if history1 else [total1 / 10]
        recent2 = history2[-self.weekly_average_window:] if history2 else [total2 / 10]
        
        # Calculate average recent performance
        avg_recent1 = sum(recent1) / len(recent1) if recent1 else 0
        avg_recent2 = sum(recent2) / len(recent2) if recent2 else 0
        
        # Blend total points with recent performance
        blended1 = (1 - self.points_history_weight) * total1 + self.points_history_weight * avg_recent1 * 10
        blended2 = (1 - self.points_history_weight) * total2 + self.points_history_weight * avg_recent2 * 10
        
        # Convert to probability
        point_diff = blended1 - blended2
        return 1.0 / (1.0 + math.exp(-point_diff / 100.0))
    
    def get_default_rating(self) -> Tuple[float, List[float]]:
        """
        Get the default rating for new participants.
        
        Returns:
            Tuple of (default_points, empty_history)
        """
        return (self._default_points, [])
    
    def get_display_name(self) -> str:
        """
        Get the display name of the rating system.
        
        Returns:
            Display name of the rating system
        """
        if self.rank_points is not None:
            return "Points-Based (Ranked)"
        return "Points-Based"
    
    def project_season_finish(self, current_rating: Tuple[float, List[float]], 
                             remaining_events: int, 
                             confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Project the final season points and potential range.
        
        Args:
            current_rating: (total_points, points_history)
            remaining_events: Number of events remaining in the season
            confidence_level: Confidence level for the projection range (0-1)
            
        Returns:
            Dictionary with projected points, min, max, and confidence interval
        """
        total_points, points_history = current_rating
        
        if not points_history:
            return {
                "projected_points": total_points,
                "min_points": total_points,
                "max_points": total_points,
                "lower_bound": total_points,
                "upper_bound": total_points
            }
        
        # Calculate average points per event
        avg_points = sum(points_history) / len(points_history)
        
        # Calculate standard deviation
        if len(points_history) > 1:
            std_dev = statistics.stdev(points_history)
        else:
            # Default to 20% of average if only one data point
            std_dev = avg_points * 0.2
        
        # Project final points
        projected_additional = avg_points * remaining_events
        projected_total = total_points + projected_additional
        
        # Calculate confidence interval
        # For 95% confidence, use ~2 standard deviations
        z_score = 1.96 if confidence_level == 0.95 else 1.645 if confidence_level == 0.90 else 2.576
        margin = z_score * (std_dev / math.sqrt(len(points_history))) * math.sqrt(remaining_events)
        
        # Calculate bounds
        lower_bound = projected_total - margin
        upper_bound = projected_total + margin
        
        # Calculate min/max scenarios (best/worst case based on history)
        if len(points_history) > 0:
            min_points_per_event = min(points_history)
            max_points_per_event = max(points_history)
        else:
            min_points_per_event = avg_points * 0.5
            max_points_per_event = avg_points * 1.5
            
        min_projected = total_points + (min_points_per_event * remaining_events)
        max_projected = total_points + (max_points_per_event * remaining_events)
        
        return {
            "projected_points": projected_total,
            "min_points": min_projected,
            "max_points": max_projected,
            "lower_bound": max(lower_bound, min_projected),
            "upper_bound": min(upper_bound, max_projected)
        }
    
    def get_trend(self, points_history: List[float], window: int = 3) -> str:
        """
        Determine if a participant's performance is trending up, down, or stable.
        
        Args:
            points_history: List of historical point values
            window: Number of recent events to analyze
            
        Returns:
            Trend indicator: "up", "down", or "stable"
        """
        if len(points_history) < window * 2:
            return "stable"  # Not enough data
            
        # Get recent and previous windows
        recent = points_history[-window:]
        previous = points_history[-(window*2):-window]
        
        recent_avg = sum(recent) / window
        previous_avg = sum(previous) / window
        
        # Calculate percent change
        percent_change = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
        
        # Determine trend
        if percent_change > 0.1:  # 10% improvement
            return "up"
        elif percent_change < -0.1:  # 10% decline
            return "down"
        else:
            return "stable"
    
    def rank_participants(self, ratings: Dict[str, Tuple[float, List[float]]]) -> List[Tuple[str, float]]:
        """
        Rank all participants based on their total points.
        
        Args:
            ratings: Dictionary mapping participant IDs to their (total_points, history)
            
        Returns:
            List of (participant_id, total_points) sorted by points (highest first)
        """
        # Sort by total points (first element of the tuple)
        return sorted(
            [(pid, rating[0]) for pid, rating in ratings.items()],
            key=lambda x: x[1],
            reverse=True
        )


# Register the Points-based ranking system
RatingSystemRegistry.register("points", PointsBasedRankingSystem)