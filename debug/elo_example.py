# debug/elo_example.py
import math
import random
import os
import sys
import argparse
from typing import List, Dict, Any, Optional, Tuple

# Add the project root to the Python path if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# First, manually import and register the rating systems to ensure they're available
from chuk_leaderboard.rating_systems.elo import EloRatingSystem
from chuk_leaderboard.rating_systems.registry import RatingSystemRegistry

# Explicitly register the rating system
RatingSystemRegistry.register("elo", EloRatingSystem)

# Now import other components
from chuk_leaderboard.rating_systems.registry import get_rating_system
from chuk_leaderboard.visualizers.rating_history_visualizer import RatingHistoryVisualizer
from chuk_leaderboard.visualizers.rating_comparison_visualizer import RatingComparisonVisualizer
from chuk_leaderboard.visualizers.expected_outcome_visualizer import ExpectedOutcomeVisualizer

def print_rating_info(name: str, rating: float) -> None:
    """Print formatted rating information for a player."""
    print(f"{name}: Rating = {rating:.1f}")


def example_1_basic(output_dir: str):
    """
    Basic example showing the rating changes after a few matches.
    """
    print("\n=== EXAMPLE 1: BASIC RATING CHANGES ===")
    
    # Initialize rating system with default K-factor (32)
    elo = get_rating_system("elo")
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Basic Rating Changes (Elo)", output_dir)
    
    # Initial ratings for two players
    playerA_rating = elo.get_default_rating()
    playerB_rating = elo.get_default_rating()
    
    # Track initial ratings (Elo has no RD or volatility)
    visualizer.track_with_explicit_values("Player A", playerA_rating, 0, 0)
    visualizer.track_with_explicit_values("Player B", playerB_rating, 0, 0)
    
    print("Initial ratings:")
    print_rating_info("Player A", playerA_rating)
    print_rating_info("Player B", playerB_rating)
    
    # Match 1: Player A wins
    print("\nMatch 1: Player A wins")
    playerA_rating = elo.calculate_rating(playerA_rating, [(playerB_rating, 1.0)])
    playerB_rating = elo.calculate_rating(playerB_rating, [(playerA_rating, 0.0)])
    
    # Track ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, 0, 0)
    visualizer.track_with_explicit_values("Player B", playerB_rating, 0, 0)
    
    print("After Match 1:")
    print_rating_info("Player A", playerA_rating)
    print_rating_info("Player B", playerB_rating)
    
    # Match 2: Player B wins
    print("\nMatch 2: Player B wins")
    playerA_rating = elo.calculate_rating(playerA_rating, [(playerB_rating, 0.0)])
    playerB_rating = elo.calculate_rating(playerB_rating, [(playerA_rating, 1.0)])
    
    # Track ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, 0, 0)
    visualizer.track_with_explicit_values("Player B", playerB_rating, 0, 0)
    
    print("After Match 2:")
    print_rating_info("Player A", playerA_rating)
    print_rating_info("Player B", playerB_rating)
    
    # Match 3: Draw
    print("\nMatch 3: Draw")
    playerA_rating = elo.calculate_rating(playerA_rating, [(playerB_rating, 0.5)])
    playerB_rating = elo.calculate_rating(playerB_rating, [(playerA_rating, 0.5)])
    
    # Track ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, 0, 0)
    visualizer.track_with_explicit_values("Player B", playerB_rating, 0, 0)
    
    print("After Match 3:")
    print_rating_info("Player A", playerA_rating)
    print_rating_info("Player B", playerB_rating)
    
    # Generate visualization
    visualizer.plot()
    visualizer.save("elo_basic_rating_changes.png")


def example_2_different_k_factors(output_dir: str):
    """
    Shows how different K-factors affect rating changes.
    """
    print("\n=== EXAMPLE 2: DIFFERENT K-FACTORS ===")
    
    # Initialize rating systems with different K-factors
    elo_low_k = EloRatingSystem(k_factor=16)
    elo_med_k = EloRatingSystem(k_factor=32)
    elo_high_k = EloRatingSystem(k_factor=64)
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Elo Ratings with Different K-Factors", output_dir)
    
    # Initial ratings for players
    default_rating = elo_med_k.get_default_rating()
    
    # Create players with same starting rating but different K-factors
    players = {
        "Low-K (16)": {"rating": default_rating, "k_factor": 16, "system": elo_low_k},
        "Med-K (32)": {"rating": default_rating, "k_factor": 32, "system": elo_med_k},
        "High-K (64)": {"rating": default_rating, "k_factor": 64, "system": elo_high_k},
    }
    
    # Track initial ratings (all the same at start)
    for name, data in players.items():
        visualizer.track_with_explicit_values(name, data["rating"], 0, 0)
    
    print("Initial ratings (all players):")
    print_rating_info("All Players", default_rating)
    
    # Simulate 20 matches against opponents of varying strength
    for match_num in range(1, 21):
        # Create an opponent with random rating - sometimes stronger, sometimes weaker
        opponent_rating = random.uniform(default_rating - 200, default_rating + 200)
        
        # Determine the outcome based on skill difference (same for all players)
        # Win 60% against weaker opponents, 40% against stronger ones
        is_stronger = opponent_rating < default_rating
        win_prob = 0.6 if is_stronger else 0.4
        result = 1.0 if random.random() < win_prob else 0.0
        
        outcome_str = "win" if result == 1.0 else "loss"
        opponent_str = "weaker" if is_stronger else "stronger"
        print(f"\nMatch {match_num}: {outcome_str} against {opponent_str} opponent (rating {opponent_rating:.1f})")
        
        # Update ratings for each player
        for name, data in players.items():
            old_rating = data["rating"]
            data["rating"] = data["system"].calculate_rating(data["rating"], [(opponent_rating, result)])
            
            # Track the new rating
            visualizer.track_with_explicit_values(name, data["rating"], 0, 0)
            
            # Print change
            rating_change = data["rating"] - old_rating
            print(f"{name}: {old_rating:.1f} → {data['rating']:.1f} (change: {rating_change:+.1f})")
    
    # Generate visualization
    visualizer.plot()
    visualizer.save("elo_different_k_factors.png")


def example_3_rating_convergence(output_dir: str):
    """
    Shows how ratings converge over many matches between players of different true skill.
    """
    print("\n=== EXAMPLE 3: RATING CONVERGENCE ===")
    
    # Initialize rating system
    elo = get_rating_system("elo")
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Elo Rating Convergence", output_dir)
    comparison = RatingComparisonVisualizer("True Skill vs. Final Elo Rating", output_dir)
    
    # Get default rating
    default_rating = elo.get_default_rating()
    
    # Initial ratings for players
    players = {
        "Strong": {"rating": default_rating, "true_skill": 1800},
        "Medium": {"rating": default_rating, "true_skill": 1500},
        "Weak": {"rating": default_rating, "true_skill": 1200},
    }
    
    # Print initial ratings
    print("Initial ratings:")
    for name, data in players.items():
        print_rating_info(name, data["rating"])
        visualizer.track_with_explicit_values(name, data["rating"], 0, 0)
    
    # Simulate 30 rounds of matches
    for round_num in range(1, 31):
        print(f"\nRound {round_num}:")
        
        # All players play against each other
        player_pairs = [
            ("Strong", "Medium"),
            ("Strong", "Weak"),
            ("Medium", "Weak")
        ]
        
        for player1_name, player2_name in player_pairs:
            player1 = players[player1_name]
            player2 = players[player2_name]
            
            # Determine match outcome based on true skill
            # This simulates the "true" outcome with some randomness
            skill_diff = player1["true_skill"] - player2["true_skill"]
            win_prob = 1.0 / (1.0 + math.exp(-skill_diff / 400.0))
            result = 1.0 if random.random() < win_prob else 0.0
            
            # Update player1's rating
            player1["rating"] = elo.calculate_rating(player1["rating"], [(player2["rating"], result)])
            
            # Update player2's rating
            player2["rating"] = elo.calculate_rating(player2["rating"], [(player1["rating"], 1.0 - result)])
            
            winner = player1_name if result == 1.0 else player2_name
            print(f"{player1_name} vs {player2_name}: {winner} wins")
        
        # Track ratings after each round
        for name, data in players.items():
            visualizer.track_with_explicit_values(name, data["rating"], 0, 0)
    
    # Print final ratings
    print("\nFinal ratings compared to true skill:")
    for name, data in players.items():
        comparison.add_comparison_with_explicit_values(name, data["rating"], 0, data["true_skill"])
        print(f"{name}: Rating = {data['rating']:.1f}, True Skill = {data['true_skill']}, " 
              f"Difference = {data['rating'] - data['true_skill']:.1f}")
    
    # Generate visualizations
    visualizer.plot()
    visualizer.save("elo_rating_convergence.png")
    
    comparison.plot_comparison()
    comparison.save("elo_true_skill_comparison.png")


def example_4_expected_outcomes(output_dir: str):
    """
    Demonstrates the expected outcome calculations with Elo.
    """
    print("\n=== EXAMPLE 4: EXPECTED OUTCOMES ===")
    
    # Initialize rating system
    elo = get_rating_system("elo")
    
    # Set up visualizer
    visualizer = ExpectedOutcomeVisualizer("Elo Expected Win Probabilities", output_dir)
    
    # Define some matchups with different rating differences
    scenarios = [
        {"player1": {"name": "Equal", "rating": 1500}, 
         "player2": {"name": "Equal", "rating": 1500}},
        
        {"player1": {"name": "Slightly Better", "rating": 1550}, 
         "player2": {"name": "Slightly Worse", "rating": 1450}},
        
        {"player1": {"name": "Better", "rating": 1600}, 
         "player2": {"name": "Worse", "rating": 1400}},
        
        {"player1": {"name": "Much Better", "rating": 1800}, 
         "player2": {"name": "Much Worse", "rating": 1200}},
        
        {"player1": {"name": "Vastly Better", "rating": 2000}, 
         "player2": {"name": "Vastly Worse", "rating": 1000}},
    ]
    
    # Calculate and print expected outcomes
    print("Expected win probabilities:")
    
    for scenario in scenarios:
        p1 = scenario["player1"]
        p2 = scenario["player2"]
        
        # Calculate expected outcome
        win_prob = elo.expected_outcome(p1["rating"], p2["rating"])
        
        # Add to visualizer
        visualizer.add_matchup_with_explicit_values(
            p1["name"], p1["rating"], 0,
            p2["name"], p2["rating"], 0,
            win_prob
        )
        
        # Rating diff for display
        rating_diff = p1["rating"] - p2["rating"]
        print(f"{p1['name']} vs {p2['name']} (diff: {rating_diff:+.0f}): {win_prob:.4f} win probability")
    
    # Print table
    visualizer.print_matchup_table()
    
    # Generate visualization
    visualizer.plot_matchups()
    visualizer.save("elo_expected_outcomes.png")


def example_5_elo_vs_dynamic_k(output_dir: str):
    """
    Compares standard Elo with a dynamic K-factor version.
    """
    print("\n=== EXAMPLE 5: STANDARD ELO VS DYNAMIC K-FACTOR ===")
    
    # Initialize rating systems
    elo_standard = EloRatingSystem(k_factor=32)
    elo_dynamic = EloRatingSystem(k_factor=32)  # We'll use the adjust_k_factor method
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Standard vs Dynamic K-Factor", output_dir)
    
    # Initial ratings for players
    default_rating = elo_standard.get_default_rating()
    
    # Create players - one using standard, one using dynamic K
    players = {
        "Standard K=32": {"rating": default_rating, "system": elo_standard, "dynamic": False},
        "Dynamic K": {"rating": default_rating, "system": elo_dynamic, "dynamic": True},
    }
    
    # Track initial ratings
    for name, data in players.items():
        visualizer.track_with_explicit_values(name, data["rating"], 0, 0)
    
    print("Initial ratings (both players):")
    print_rating_info("Both Players", default_rating)
    
    # Simulate 50 matches where players gain rating rapidly then face stronger opponents
    for match_num in range(1, 51):
        # First 20 matches: Play against weaker opponents to gain rating
        # Next 30 matches: Play against stronger opponents
        if match_num <= 20:
            opponent_rating = default_rating - 200  # Weaker opponent
            result = 1.0  # Always win
            print(f"\nMatch {match_num}: Win against weaker opponent (rating {opponent_rating:.1f})")
        else:
            opponent_rating = default_rating + 400  # Stronger opponent
            result = 0.0  # Always lose
            print(f"\nMatch {match_num}: Loss against stronger opponent (rating {opponent_rating:.1f})")
        
        # Update ratings for each player
        for name, data in players.items():
            old_rating = data["rating"]
            
            if data["dynamic"]:
                # Use dynamic K-factor based on rating
                k = data["system"].adjust_k_factor(old_rating)
                data["rating"] = data["system"].get_rating_with_dynamic_k(old_rating, [(opponent_rating, result)])
                print(f"{name}: {old_rating:.1f} → {data['rating']:.1f} (K={k})")
            else:
                # Use standard fixed K-factor
                data["rating"] = data["system"].calculate_rating(old_rating, [(opponent_rating, result)])
                print(f"{name}: {old_rating:.1f} → {data['rating']:.1f} (K=32)")
            
            # Track the new rating
            visualizer.track_with_explicit_values(name, data["rating"], 0, 0)
    
    # Generate visualization
    visualizer.plot()
    visualizer.save("elo_dynamic_k_factor.png")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Elo rating system examples.')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save output files (default: output)')
    parser.add_argument('--examples', type=str, nargs='+',
                        choices=['1', '2', '3', '4', '5', 'all'],
                        default=['all'],
                        help='Examples to run (1-5 or all)')
    return parser.parse_args()


def main():
    """Run the Elo examples."""
    # Parse command line arguments
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Results will be saved to: {os.path.abspath(args.output_dir)}")
    
    # Print available rating systems for debugging
    print(f"Available rating systems: {', '.join(RatingSystemRegistry.list_available())}")
    
    # Seed random for reproducibility
    random.seed(42)
    
    # Determine which examples to run
    examples_to_run = set()
    if 'all' in args.examples:
        examples_to_run = {1, 2, 3, 4, 5}
    else:
        for example in args.examples:
            examples_to_run.add(int(example))
    
    # Run examples
    if 1 in examples_to_run:
        example_1_basic(args.output_dir)
    
    if 2 in examples_to_run:
        example_2_different_k_factors(args.output_dir)
    
    if 3 in examples_to_run:
        example_3_rating_convergence(args.output_dir)
    
    if 4 in examples_to_run:
        example_4_expected_outcomes(args.output_dir)
    
    if 5 in examples_to_run:
        example_5_elo_vs_dynamic_k(args.output_dir)
    
    print(f"\nExamples complete. Visualization charts have been saved to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()