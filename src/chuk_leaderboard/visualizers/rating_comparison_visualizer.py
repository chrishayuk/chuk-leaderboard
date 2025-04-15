# chuk_leaderboard/visualizers/rating_comparison_visualizer.py
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from tabulate import tabulate

# imports
from chuk_leaderboard.visualizers.rating_visualizer import RatingVisualizer

class RatingComparisonVisualizer(RatingVisualizer):
    """
    Visualizer for comparing ratings with expected or true values.
    """
    def __init__(self, title: str = "Rating Comparison", output_dir: str = "output"):
        super().__init__(title, output_dir)
        self.data = []
    
    def add_comparison(self, name: str, rating_data: Any, 
                      expected_value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a comparison entry.
        
        Args:
            name: Participant name
            rating_data: Rating data in any supported format
            expected_value: Expected or true value to compare against
            metadata: Additional metadata to store
        """
        # Convert rating data to standard format
        rating, rd, _ = self._convert_to_display_format(rating_data)
        
        self.data.append({
            "name": name,
            "rating": rating,
            "rd": rd,
            "expected": expected_value,
            "difference": rating - expected_value,
            "metadata": metadata or {}
        })
    
    def add_comparison_with_explicit_values(self, name: str, rating: float, rd: float,
                                          expected_value: float, 
                                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a comparison entry with explicit values.
        
        Args:
            name: Participant name
            rating: Rating value
            rd: Rating deviation
            expected_value: Expected or true value to compare against
            metadata: Additional metadata to store
        """
        self.data.append({
            "name": name,
            "rating": rating,
            "rd": rd,
            "expected": expected_value,
            "difference": rating - expected_value,
            "metadata": metadata or {}
        })
    
    def plot_comparison(self, figsize: Tuple[int, int] = (10, 6)) -> None:
        """
        Plot rating vs. expected value comparison.
        
        Args:
            figsize: Figure size as (width, height)
        """
        plt.figure(figsize=figsize)
        
        names = [item["name"] for item in self.data]
        ratings = [item["rating"] for item in self.data]
        expected = [item["expected"] for item in self.data]
        
        # Check if we have meaningful RD values
        has_rd = any(item["rd"] > 0 for item in self.data)
        rds = [item["rd"] for item in self.data] if has_rd else None
        
        x = range(len(names))
        
        if has_rd:
            plt.errorbar(x, ratings, yerr=rds, fmt='o', label="Current Rating")
        else:
            plt.plot(x, ratings, 'o', label="Current Rating")
            
        plt.plot(x, expected, 'rx', markersize=10, label="Expected/True Value")
        
        for i, item in enumerate(self.data):
            plt.annotate(f"{item['difference']:.1f}", 
                        (i, (ratings[i] + expected[i])/2),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha='center')
        
        plt.xticks(x, names)
        plt.ylabel("Rating")
        plt.title(self.title)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
    
    def print_comparison_table(self) -> None:
        """Print a comparison table of ratings vs. expected values."""
        if not self.data:
            print("No comparison data to display")
            return
            
        # Check if we have RD values
        has_rd = any(item["rd"] > 0 for item in self.data)
        
        table_data = []
        for item in self.data:
            if has_rd:
                table_data.append([
                    item["name"],
                    f"{item['rating']:.1f}",
                    f"{item['rd']:.1f}",
                    f"{item['expected']:.1f}",
                    f"{item['difference']:.1f}"
                ])
            else:
                table_data.append([
                    item["name"],
                    f"{item['rating']:.1f}",
                    f"{item['expected']:.1f}",
                    f"{item['difference']:.1f}"
                ])
        
        if has_rd:
            headers = ["Name", "Rating", "RD", "Expected/True", "Difference"]
        else:
            headers = ["Name", "Rating", "Expected/True", "Difference"]
            
        print(tabulate(table_data, headers=headers))