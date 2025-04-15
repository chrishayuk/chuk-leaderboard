# debug/glicko2_example.py
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
from chuk_leaderboard.rating_systems.glicko2 import Glicko2RatingSystem
from chuk_leaderboard.rating_systems.registry import RatingSystemRegistry

# Explicitly register the rating system
RatingSystemRegistry.register("glicko2", Glicko2RatingSystem)

# Now import other components
from chuk_leaderboard.rating_systems.registry import get_rating_system
from chuk_leaderboard.visualizers.rating_history_visualizer import RatingHistoryVisualizer
from chuk_leaderboard.visualizers.rating_comparison_visualizer import RatingComparisonVisualizer
from chuk_leaderboard.visualizers.expected_outcome_visualizer import ExpectedOutcomeVisualizer

def print_rating_info(name: str, rating: float, rd: float, vol: float) -> None:
    """Print formatted rating information for a player."""
    print(f"{name}: Rating = {rating:.1f}, RD = {rd:.1f}, Vol = {vol:.4f}")


def example_1_basic(output_dir: str):
    """
    Basic example showing the rating changes after a few matches.
    """
    print("\n=== EXAMPLE 1: BASIC RATING CHANGES ===")
    
    # Initialize rating system
    glicko = get_rating_system("glicko2")
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Basic Rating Changes (Glicko2)", output_dir)
    
    # Initial ratings for two players
    default_rating = glicko.get_default_rating()
    playerA_rating, playerA_rd, playerA_vol = default_rating
    playerB_rating, playerB_rd, playerB_vol = default_rating
    
    # Track initial ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, playerA_rd, playerA_vol)
    visualizer.track_with_explicit_values("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    print("Initial ratings:")
    print_rating_info("Player A", playerA_rating, playerA_rd, playerA_vol)
    print_rating_info("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    # Match 1: Player A wins
    print("\nMatch 1: Player A wins")
    playerA_rating, playerA_rd, playerA_vol = glicko.calculate_rating(
        (playerA_rating, playerA_rd, playerA_vol), 
        [(playerB_rating, playerB_rd, 1.0)]
    )
    
    playerB_rating, playerB_rd, playerB_vol = glicko.calculate_rating(
        (playerB_rating, playerB_rd, playerB_vol), 
        [(playerA_rating, playerA_rd, 0.0)]
    )
    
    # Track ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, playerA_rd, playerA_vol)
    visualizer.track_with_explicit_values("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    print("After Match 1:")
    print_rating_info("Player A", playerA_rating, playerA_rd, playerA_vol)
    print_rating_info("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    # Match 2: Player B wins
    print("\nMatch 2: Player B wins")
    playerA_rating, playerA_rd, playerA_vol = glicko.calculate_rating(
        (playerA_rating, playerA_rd, playerA_vol), 
        [(playerB_rating, playerB_rd, 0.0)]
    )
    
    playerB_rating, playerB_rd, playerB_vol = glicko.calculate_rating(
        (playerB_rating, playerB_rd, playerB_vol), 
        [(playerA_rating, playerA_rd, 1.0)]
    )
    
    # Track ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, playerA_rd, playerA_vol)
    visualizer.track_with_explicit_values("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    print("After Match 2:")
    print_rating_info("Player A", playerA_rating, playerA_rd, playerA_vol)
    print_rating_info("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    # Match 3: Draw
    print("\nMatch 3: Draw")
    playerA_rating, playerA_rd, playerA_vol = glicko.calculate_rating(
        (playerA_rating, playerA_rd, playerA_vol), 
        [(playerB_rating, playerB_rd, 0.5)]
    )
    
    playerB_rating, playerB_rd, playerB_vol = glicko.calculate_rating(
        (playerB_rating, playerB_rd, playerB_vol), 
        [(playerA_rating, playerA_rd, 0.5)]
    )
    
    # Track ratings
    visualizer.track_with_explicit_values("Player A", playerA_rating, playerA_rd, playerA_vol)
    visualizer.track_with_explicit_values("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    print("After Match 3:")
    print_rating_info("Player A", playerA_rating, playerA_rd, playerA_vol)
    print_rating_info("Player B", playerB_rating, playerB_rd, playerB_vol)
    
    # Generate visualization
    visualizer.plot()
    visualizer.save("glicko2_basic_rating_changes.png")


def example_2_rating_convergence(output_dir: str):
    """
    Shows how ratings converge over many matches between players of different true skill.
    """
    print("\n=== EXAMPLE 2: RATING CONVERGENCE ===")
    
    # Initialize rating system
    glicko = get_rating_system("glicko2")
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Rating Convergence (Glicko2)", output_dir)
    comparison = RatingComparisonVisualizer("True Skill vs. Final Rating (Glicko2)", output_dir)
    
    # Get default ratings
    default_rating, default_rd, default_vol = glicko.get_default_rating()
    
    # Initial ratings for players
    players = {
        "Strong": {"rating": default_rating, "rd": default_rd, "vol": default_vol, "true_skill": 1800},
        "Medium": {"rating": default_rating, "rd": default_rd, "vol": default_vol, "true_skill": 1500},
        "Weak": {"rating": default_rating, "rd": default_rd, "vol": default_vol, "true_skill": 1200},
    }
    
    # Print initial ratings
    print("Initial ratings:")
    for name, data in players.items():
        print_rating_info(name, data["rating"], data["rd"], data["vol"])
        visualizer.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
    
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
            new_rating = glicko.calculate_rating(
                (player1["rating"], player1["rd"], player1["vol"]),
                [(player2["rating"], player2["rd"], result)]
            )
            player1["rating"], player1["rd"], player1["vol"] = new_rating
            
            # Update player2's rating
            new_rating = glicko.calculate_rating(
                (player2["rating"], player2["rd"], player2["vol"]),
                [(player1["rating"], player1["rd"], 1.0 - result)]
            )
            player2["rating"], player2["rd"], player2["vol"] = new_rating
            
            winner = player1_name if result == 1.0 else player2_name
            print(f"{player1_name} vs {player2_name}: {winner} wins")
        
        # Track ratings after each round
        for name, data in players.items():
            visualizer.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
    
    # Print ratings at specific intervals
    visualizer.print_history_at_intervals([1, 5, 10, 20, 30])
    
    # Create comparison visualization
    print("\nFinal ratings compared to true skill:")
    for name, data in players.items():
        comparison.add_comparison_with_explicit_values(
            name, 
            data["rating"], 
            data["rd"], 
            data["true_skill"]
        )
    
    # Print comparison table
    comparison.print_comparison_table()
    
    # Generate visualizations
    visualizer.plot()
    visualizer.save("glicko2_rating_convergence.png")
    
    comparison.plot_comparison()
    comparison.save("glicko2_true_skill_comparison.png")


def example_3_inactive_players(output_dir: str):
    """
    Shows how ratings change when players become inactive.
    """
    print("\n=== EXAMPLE 3: INACTIVE PLAYERS ===")
    
    # Initialize rating system
    glicko = get_rating_system("glicko2")
    
    # Set up visualizer
    rating_viz = RatingHistoryVisualizer("Ratings of Inactive Players (Glicko2)", output_dir)
    rd_viz = RatingHistoryVisualizer("Rating Deviation of Inactive Players (Glicko2)", output_dir)
    
    # Initial ratings for players - start with smaller RD for clarity
    default_rating, _, default_vol = glicko.get_default_rating()
    initial_rd = 150  # Smaller than default for clearer demonstration
    
    players = {
        "Active": {"rating": default_rating, "rd": initial_rd, "vol": default_vol},
        "Occasional": {"rating": default_rating, "rd": initial_rd, "vol": default_vol},
        "Inactive": {"rating": default_rating, "rd": initial_rd, "vol": default_vol},
    }
    
    # Print initial ratings
    print("Initial ratings:")
    for name, data in players.items():
        print_rating_info(name, data["rating"], data["rd"], data["vol"])
        rating_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
        rd_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
    
    # Simulate 15 rating periods
    for period in range(1, 16):
        print(f"\nPeriod {period}:")
        
        # Active player plays every period
        active = players["Active"]
        
        # Create an opponent with random rating
        opponent_rating = random.uniform(1300, 1700)
        opponent_rd = 150
        
        # 50% chance of winning
        result = 1.0 if random.random() > 0.5 else 0.0
        
        # Update active player
        active["rating"], active["rd"], active["vol"] = glicko.calculate_rating(
            (active["rating"], active["rd"], active["vol"]),
            [(opponent_rating, opponent_rd, result)]
        )
        
        # Occasional player plays every 5 periods
        occasional = players["Occasional"]
        if period % 5 == 0:
            opponent_rating = random.uniform(1300, 1700)
            result = 1.0 if random.random() > 0.5 else 0.0
            
            occasional["rating"], occasional["rd"], occasional["vol"] = glicko.calculate_rating(
                (occasional["rating"], occasional["rd"], occasional["vol"]),
                [(opponent_rating, opponent_rd, result)]
            )
        else:
            # No matches, just update RD due to inactivity
            occasional["rating"], occasional["rd"], occasional["vol"] = glicko.calculate_rating(
                (occasional["rating"], occasional["rd"], occasional["vol"]), 
                []
            )
        
        # Inactive player never plays
        inactive = players["Inactive"]
        inactive["rating"], inactive["rd"], inactive["vol"] = glicko.calculate_rating(
            (inactive["rating"], inactive["rd"], inactive["vol"]), 
            []
        )
        
        # Track ratings
        for name, data in players.items():
            rating_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
            rd_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
        
        # Print just a few periods to avoid excessive output
        if period in [1, 5, 10, 15]:
            print(f"Ratings after period {period}:")
            for name, data in players.items():
                print_rating_info(name, data["rating"], data["rd"], data["vol"])
    
    # Generate visualizations
    rating_viz.plot()
    rating_viz.save("glicko2_inactive_players_ratings.png")
    
    # Focus on RD specifically for this example
    rd_viz.plot(show_volatility=False)
    rd_viz.save("glicko2_inactive_players_rd.png")


def example_4_different_starting_ratings(output_dir: str):
    """
    Shows how players with different starting ratings converge.
    """
    print("\n=== EXAMPLE 4: DIFFERENT STARTING RATINGS ===")
    
    # Initialize rating system
    glicko = get_rating_system("glicko2")
    
    # Set up visualizer
    visualizer = RatingHistoryVisualizer("Different Starting Ratings (Glicko2)", output_dir)
    
    # Default values
    _, default_rd, default_vol = glicko.get_default_rating()
    
    # Initial ratings for players with the same true skill
    players = {
        "Underrated": {"rating": 1200, "rd": default_rd, "vol": default_vol, "true_skill": 1500},
        "Accurate": {"rating": 1500, "rd": 150, "vol": default_vol, "true_skill": 1500},
        "Overrated": {"rating": 1800, "rd": default_rd, "vol": default_vol, "true_skill": 1500},
    }
    
    # Print initial ratings
    print("Initial ratings (all players have the same true skill of 1500):")
    for name, data in players.items():
        print_rating_info(name, data["rating"], data["rd"], data["vol"])
        visualizer.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
    
    # Simulate 20 rounds of matches
    for round_num in range(1, 21):
        print(f"\nRound {round_num}:")
        
        # Each player plays against a pool of opponents with evenly distributed skills
        for name, player in players.items():
            # Play 3 matches per round against opponents with true skills 1300, 1500, 1700
            opponent_skills = [1300, 1500, 1700]
            
            outcomes = []
            for opp_skill in opponent_skills:
                # Determine match outcome based on true skill
                skill_diff = player["true_skill"] - opp_skill
                win_prob = 1.0 / (1.0 + math.exp(-skill_diff / 400.0))
                result = 1.0 if random.random() < win_prob else 0.0
                
                # Assume opponent has accurate rating and moderate RD
                outcomes.append((opp_skill, 150, result))
            
            # Update player's rating based on all 3 matches
            player["rating"], player["rd"], player["vol"] = glicko.calculate_rating(
                (player["rating"], player["rd"], player["vol"]),
                outcomes
            )
        
        # Track ratings
        for name, data in players.items():
            visualizer.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
    
    # Print ratings at specific intervals
    visualizer.print_history_at_intervals([1, 5, 10, 20])
    
    # Generate visualization
    visualizer.plot()
    visualizer.save("glicko2_different_starting_ratings.png")
    
    # Print final differences from true skill
    print("\nFinal differences from true skill:")
    comparison = RatingComparisonVisualizer("Convergence to True Skill (Glicko2)", output_dir)
    
    for name, data in players.items():
        comparison.add_comparison_with_explicit_values(
            name, data["rating"], data["rd"], data["true_skill"]
        )
        print(f"{name}: Rating = {data['rating']:.1f}, "
              f"Difference from true skill = {data['rating'] - data['true_skill']:.1f}")
    
    comparison.plot_comparison()
    comparison.save("glicko2_starting_rating_convergence.png")


def example_5_expected_outcomes(output_dir: str):
    """
    Demonstrates the expected outcome calculations.
    """
    print("\n=== EXAMPLE 5: EXPECTED OUTCOMES ===")
    
    # Initialize rating system
    glicko = get_rating_system("glicko2")
    
    # Set up visualizer
    visualizer = ExpectedOutcomeVisualizer("Expected Win Probabilities (Glicko2)", output_dir)
    
    # Define some players with different ratings and RDs
    scenarios = [
        {"player1": {"name": "Equal", "rating": 1500, "rd": 30}, 
         "player2": {"name": "Equal", "rating": 1500, "rd": 30}},
        
        {"player1": {"name": "Slightly Better", "rating": 1550, "rd": 30}, 
         "player2": {"name": "Slightly Worse", "rating": 1450, "rd": 30}},
        
        {"player1": {"name": "Much Better", "rating": 1800, "rd": 30}, 
         "player2": {"name": "Much Worse", "rating": 1200, "rd": 30}},
        
        {"player1": {"name": "Better but Uncertain", "rating": 1600, "rd": 200}, 
         "player2": {"name": "Worse but Certain", "rating": 1400, "rd": 30}},
        
        {"player1": {"name": "Slightly Better", "rating": 1550, "rd": 30}, 
         "player2": {"name": "Slightly Worse but Very Uncertain", "rating": 1450, "rd": 350}},
    ]
    
    # Calculate and print expected outcomes
    print("Expected win probabilities:")
    
    for scenario in scenarios:
        p1 = scenario["player1"]
        p2 = scenario["player2"]
        
        # Calculate expected outcome
        win_prob = glicko.expected_outcome(
            (p1["rating"], p1["rd"]), 
            (p2["rating"], p2["rd"])
        )
        
        # Add to visualizer
        visualizer.add_matchup_with_explicit_values(
            p1["name"], p1["rating"], p1["rd"],
            p2["name"], p2["rating"], p2["rd"],
            win_prob
        )
        
        print(f"{p1['name']} vs {p2['name']}: {win_prob:.4f} win probability")
    
    # Print table
    visualizer.print_matchup_table()
    
    # Generate visualization
    visualizer.plot_matchups()
    visualizer.save("glicko2_expected_outcomes.png")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Glicko2 rating system examples.')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save output files (default: output)')
    parser.add_argument('--examples', type=str, nargs='+',
                        choices=['1', '2', '3', '4', '5', 'all'],
                        default=['all'],
                        help='Examples to run (1-5 or all)')
    return parser.parse_args()


def main():
    """Run the Glicko2 examples."""
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
        example_2_rating_convergence(args.output_dir)
    
    if 3 in examples_to_run:
        example_3_inactive_players(args.output_dir)
    
    if 4 in examples_to_run:
        example_4_different_starting_ratings(args.output_dir)
    
    if 5 in examples_to_run:
        example_5_expected_outcomes(args.output_dir)
    
    print(f"\nExamples complete. Visualization charts have been saved to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()