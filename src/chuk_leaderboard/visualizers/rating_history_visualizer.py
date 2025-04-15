# chuk_leaderboard/visualizers/rating_history_visualizer.py
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple

# imports
from chuk_leaderboard.visualizers.rating_visualizer import RatingVisualizer


class RatingHistoryVisualizer(RatingVisualizer):
    """
    Visualizer for tracking and plotting rating histories of multiple participants.
    """
    def __init__(self, title: str = "Rating History", output_dir: str = "output"):
        super().__init__(title, output_dir)
        self.history: Dict[str, Dict[str, List]] = {}
    
    def track(self, name: str, rating_data: Any) -> None:
        """
        Track rating history for a participant.
        
        Args:
            name: Participant name
            rating_data: Rating data in any supported format
        """
        if name not in self.history:
            self.history[name] = {"ratings": [], "rds": [], "vols": []}
        
        # Convert rating data to standard format
        rating, rd, vol = self._convert_to_display_format(rating_data)
        
        # Track the values
        self.history[name]["ratings"].append(rating)
        self.history[name]["rds"].append(rd)
        self.history[name]["vols"].append(vol)
    
    def track_with_explicit_values(self, name: str, rating: float, rd: float, vol: float) -> None:
        """
        Track rating history with explicit values.
        
        Args:
            name: Participant name
            rating: Rating value
            rd: Rating deviation
            vol: Volatility
        """
        if name not in self.history:
            self.history[name] = {"ratings": [], "rds": [], "vols": []}
        
        self.history[name]["ratings"].append(rating)
        self.history[name]["rds"].append(rd)
        self.history[name]["vols"].append(vol)
    
    def plot(self, figsize: Tuple[int, int] = (12, 8), show_volatility: bool = True,
             show_rd: bool = True) -> None:
        """
        Plot the rating history for all tracked participants.
        
        Args:
            figsize: Figure size as (width, height)
            show_volatility: Whether to show the volatility subplot
            show_rd: Whether to show the rating deviation subplot
        """
        plt.figure(figsize=figsize)
        
        # Determine number of subplots
        n_plots = 1
        if show_rd:
            n_plots += 1
        if show_volatility:
            n_plots += 1
            
        # Always plot ratings
        plt.subplot(n_plots, 1, 1)
        for name, data in self.history.items():
            plt.plot(data["ratings"], marker='o', label=name)
        plt.title(f"{self.title}")
        plt.ylabel("Rating")
        plt.grid(True)
        plt.legend()
        
        current_plot = 1
        
        # Plot rating deviations if requested
        if show_rd:
            current_plot += 1
            plt.subplot(n_plots, 1, current_plot)
            
            # Check if we have meaningful RD values to plot
            has_rd = any(sum(data["rds"]) > 0 for data in self.history.values())
            
            if has_rd:
                for name, data in self.history.items():
                    plt.plot(data["rds"], marker='s', label=name)
                plt.title("Rating Deviation")
                plt.ylabel("RD")
                plt.grid(True)
            else:
                plt.text(0.5, 0.5, "Rating Deviation not available", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=plt.gca().transAxes)
                plt.axis('off')
        
        # Plot volatility if requested
        if show_volatility:
            current_plot += 1
            plt.subplot(n_plots, 1, current_plot)
            
            # Check if we have meaningful volatility values to plot
            has_vol = any(sum(data["vols"]) > 0 for data in self.history.values())
            
            if has_vol:
                for name, data in self.history.items():
                    plt.plot(data["vols"], marker='^', label=name)
                plt.title("Volatility")
                plt.ylabel("Volatility")
                plt.grid(True)
            else:
                plt.text(0.5, 0.5, "Volatility not available", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=plt.gca().transAxes)
                plt.axis('off')
        
        plt.xlabel("Match Number")
        plt.tight_layout()
    
    def get_final_ratings(self) -> Dict[str, Dict[str, float]]:
        """
        Get the final ratings for all participants.
        
        Returns:
            Dictionary of participant names to their final ratings, RDs, and volatilities
        """
        result = {}
        for name, data in self.history.items():
            result[name] = {
                "rating": data["ratings"][-1] if data["ratings"] else None,
                "rd": data["rds"][-1] if data["rds"] else None,
                "vol": data["vols"][-1] if data["vols"] else None
            }
        return result
    
    def print_history_at_intervals(self, intervals: List[int]) -> None:
        """
        Print rating history at specified intervals.
        
        Args:
            intervals: List of match/round numbers to print
        """
        if not self.history:
            print("No rating history to display")
            return
            
        first_participant = next(iter(self.history.values()))
        max_length = len(first_participant["ratings"])
        
        for interval in intervals:
            if interval >= max_length:
                continue
                
            print(f"\nRatings after match/round {interval}:")
            for name, data in self.history.items():
                if interval < len(data["ratings"]):
                    # Check if we have meaningful RD and volatility
                    has_rd = data["rds"][interval] > 0
                    has_vol = data["vols"][interval] > 0
                    
                    # Format output based on what data we have
                    if has_rd and has_vol:
                        print(f"{name}: Rating = {data['ratings'][interval]:.1f}, "
                              f"RD = {data['rds'][interval]:.1f}, "
                              f"Vol = {data['vols'][interval]:.4f}")
                    elif has_rd:
                        print(f"{name}: Rating = {data['ratings'][interval]:.1f}, "
                              f"RD = {data['rds'][interval]:.1f}")
                    else:
                        print(f"{name}: Rating = {data['ratings'][interval]:.1f}")