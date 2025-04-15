# chuk_leaderboard/visualizers/expected_outcome_visualizer.py
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from tabulate import tabulate

# imports
from chuk_leaderboard.visualizers.rating_visualizer import RatingVisualizer


class ExpectedOutcomeVisualizer(RatingVisualizer):
    """
    Visualizer for expected outcome probabilities.
    """
    def __init__(self, title: str = "Expected Outcomes", output_dir: str = "output"):
        super().__init__(title, output_dir)
        self.matchups = []
    
    def add_matchup(self, player1_name: str, player1_rating: Any,
                   player2_name: str, player2_rating: Any,
                   win_probability: float) -> None:
        """
        Add a matchup with expected outcome.
        
        Args:
            player1_name: Name of player 1
            player1_rating: Rating data for player 1 in any supported format
            player2_name: Name of player 2
            player2_rating: Rating data for player 2 in any supported format
            win_probability: Probability of player 1 winning
        """
        # Convert rating data to standard format
        p1_rating, p1_rd, _ = self._convert_to_display_format(player1_rating)
        p2_rating, p2_rd, _ = self._convert_to_display_format(player2_rating)
        
        self.matchups.append({
            "player1": {
                "name": player1_name,
                "rating": p1_rating,
                "rd": p1_rd
            },
            "player2": {
                "name": player2_name,
                "rating": p2_rating,
                "rd": p2_rd
            },
            "win_prob": win_probability
        })
    
    def add_matchup_with_explicit_values(self, player1_name: str, player1_rating: float, player1_rd: float,
                                        player2_name: str, player2_rating: float, player2_rd: float,
                                        win_probability: float) -> None:
        """
        Add a matchup with explicit values.
        
        Args:
            player1_name: Name of player 1
            player1_rating: Rating of player 1
            player1_rd: Rating deviation of player 1
            player2_name: Name of player 2
            player2_rating: Rating of player 2
            player2_rd: Rating deviation of player 2
            win_probability: Probability of player 1 winning
        """
        self.matchups.append({
            "player1": {
                "name": player1_name,
                "rating": player1_rating,
                "rd": player1_rd
            },
            "player2": {
                "name": player2_name,
                "rating": player2_rating,
                "rd": player2_rd
            },
            "win_prob": win_probability
        })
    
    def plot_matchups(self, figsize: Tuple[int, int] = (10, 6)) -> None:
        """
        Plot expected outcomes for matchups.
        
        Args:
            figsize: Figure size as (width, height)
        """
        if not self.matchups:
            print("No matchups to display")
            return
            
        plt.figure(figsize=figsize)
        
        labels = []
        win_probs = []
        
        for matchup in self.matchups:
            p1 = matchup["player1"]
            p2 = matchup["player2"]
            labels.append(f"{p1['name']} ({p1['rating']:.0f}) vs\n{p2['name']} ({p2['rating']:.0f})")
            win_probs.append(matchup["win_prob"])
        
        x = range(len(labels))
        
        plt.bar(x, win_probs, color='skyblue')
        plt.axhline(y=0.5, color='r', linestyle='--', label="Even match (50%)")
        
        for i, prob in enumerate(win_probs):
            plt.text(i, prob + 0.02, f"{prob:.2f}", ha='center')
        
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.ylabel("Win Probability")
        plt.title(self.title)
        plt.ylim(0, 1.1)
        plt.legend()
        plt.tight_layout()
    
    def print_matchup_table(self) -> None:
        """Print a table of matchups and expected outcomes."""
        if not self.matchups:
            print("No matchups to display")
            return
            
        # Check if we have RD values
        has_rd = any(matchup["player1"]["rd"] > 0 or matchup["player2"]["rd"] > 0 
                    for matchup in self.matchups)
        
        table_data = []
        for matchup in self.matchups:
            p1 = matchup["player1"]
            p2 = matchup["player2"]
            
            if has_rd:
                table_data.append([
                    f"{p1['name']} ({p1['rating']:.0f}, RD={p1['rd']:.0f})",
                    f"{p2['name']} ({p2['rating']:.0f}, RD={p2['rd']:.0f})",
                    f"{matchup['win_prob']:.4f}",
                    f"{(1-matchup['win_prob']):.4f}"
                ])
            else:
                table_data.append([
                    f"{p1['name']} ({p1['rating']:.0f})",
                    f"{p2['name']} ({p2['rating']:.0f})",
                    f"{matchup['win_prob']:.4f}",
                    f"{(1-matchup['win_prob']):.4f}"
                ])
        
        print(tabulate(table_data, 
                      headers=["Player 1", "Player 2", "P1 Win Prob", "P2 Win Prob"]))