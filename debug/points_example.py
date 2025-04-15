# debug/points_example.py
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
from chuk_leaderboard.rating_systems.points_based import PointsBasedRankingSystem
from chuk_leaderboard.rating_systems.registry import RatingSystemRegistry

# Explicitly register the rating system
RatingSystemRegistry.register("points", PointsBasedRankingSystem)

# Now import other components
from chuk_leaderboard.rating_systems.registry import get_rating_system
from chuk_leaderboard.visualizers.season_projection_visualizer import SeasonProjectionVisualizer

def print_points_info(name: str, total_points: float, points_history: List[float]) -> None:
    """Print formatted points information for a participant."""
    recent = points_history[-3:] if len(points_history) >= 3 else points_history
    recent_avg = sum(recent) / len(recent) if recent else 0
    
    print(f"{name}: Total Points = {total_points:.1f}, Recent Avg = {recent_avg:.1f}")


def example_1_fantasy_football(output_dir: str):
    """
    Example of a fantasy football league with points-based ranking.
    """
    print("\n=== EXAMPLE 1: FANTASY FOOTBALL LEAGUE ===")
    
    # Initialize rating system
    points_system = get_rating_system("points")
    
    # Set up visualizer for a 14-week fantasy football season
    # Currently after week 8
    visualizer = SeasonProjectionVisualizer("Fantasy Football Projections", output_dir)
    visualizer.set_league_info("Fantasy Football League", 14, 8)
    
    # Create some fictional teams with realistic fantasy football scoring
    teams = {
        "Touchdown Titans": {"total": 0, "history": []},
        "Running Rebels": {"total": 0, "history": []},
        "Pass Panthers": {"total": 0, "history": []},
        "Golden Receivers": {"total": 0, "history": []},
        "Defense Dragons": {"total": 0, "history": []},
        "Quarterback Kings": {"total": 0, "history": []},
        "Field Goal Falcons": {"total": 0, "history": []},
        "Injury Infernos": {"total": 0, "history": []}
    }
    
    # Simulate 8 weeks of a fantasy football season
    # Typical fantasy football scores range from 70-150 points
    for week in range(1, 9):
        print(f"\nWeek {week} Results:")
        
        for team_name, team_data in teams.items():
            # Generate a score using a normal distribution
            # Different teams have different mean scores to show variety
            if team_name == "Touchdown Titans":
                # Consistently good team
                score = random.normalvariate(125, 15)
            elif team_name == "Running Rebels":
                # Good but inconsistent team
                score = random.normalvariate(120, 25)
            elif team_name == "Quarterback Kings":
                # Started strong but declining
                base = 130 - (week * 5)
                score = random.normalvariate(base, 15)
            elif team_name == "Injury Infernos":
                # Started weak but improving
                base = 80 + (week * 5)
                score = random.normalvariate(base, 15)
            else:
                # Average teams
                score = random.normalvariate(100, 20)
            
            # Ensure score is positive and round to 1 decimal place
            score = max(50, round(score, 1))
            
            # Update team data
            team_data["history"].append(score)
            team_data["total"] += score
            
            print(f"{team_name}: {score:.1f} points")
    
    # Print current standings
    print("\nCurrent Standings after Week 8:")
    
    # Sort teams by total points
    sorted_teams = sorted(teams.items(), key=lambda x: x[1]["total"], reverse=True)
    
    for rank, (team_name, team_data) in enumerate(sorted_teams, 1):
        history_str = ", ".join([f"{score:.1f}" for score in team_data["history"][-3:]])
        print(f"{rank}. {team_name}: {team_data['total']:.1f} points (Last 3 weeks: {history_str})")
    
    # Project end-of-season results
    print("\nEnd-of-Season Projections:")
    
    # Remaining weeks in the season
    remaining_weeks = 14 - 8  # 14-week season, after week 8
    
    for team_name, team_data in teams.items():
        # Create current rating tuple (total_points, points_history)
        current_rating = (team_data["total"], team_data["history"])
        
        # Project season finish
        projection = points_system.project_season_finish(current_rating, remaining_weeks)
        
        # Add to visualizer
        visualizer.add_participant(team_name, team_data["total"], team_data["history"], projection)
        
        # Print projection
        print(f"{team_name}:")
        print(f"  Current: {team_data['total']:.1f} points")
        print(f"  Projected: {projection['projected_points']:.1f} points")
        print(f"  Range: {projection['min_points']:.1f} - {projection['max_points']:.1f}")
        print(f"  95% Confidence: {projection['lower_bound']:.1f} - {projection['upper_bound']:.1f}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer.plot_projections()
    visualizer.save("fantasy_football_projections.png")
    
    visualizer.plot_weekly_trends()
    visualizer.save("fantasy_football_weekly_trends.png")
    
    visualizer.plot_projection_ranges()
    visualizer.save("fantasy_football_projection_ranges.png")
    
    # Print final projection table
    print("\nDetailed Projection Table:")
    visualizer.print_projection_table()


def example_2_rank_based_tournament(output_dir: str):
    """
    Example of a rank-based tournament where points are awarded based on finishing position.
    """
    print("\n=== EXAMPLE 2: RANK-BASED TOURNAMENT ===")
    
    # Initialize rating system with rank points
    # Points awarded: 1st place: 25, 2nd: 18, 3rd: 15, etc.
    rank_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    points_system = PointsBasedRankingSystem(rank_points=rank_points)
    
    # Set up visualizer for a 10-event tournament
    # Currently after event 6
    visualizer = SeasonProjectionVisualizer("Tournament Standings", output_dir)
    visualizer.set_league_info("Racing Championship", 10, 6)
    
    # Create some participants
    participants = {
        "Driver A": {"total": 0, "history": []},
        "Driver B": {"total": 0, "history": []},
        "Driver C": {"total": 0, "history": []},
        "Driver D": {"total": 0, "history": []},
        "Driver E": {"total": 0, "history": []},
        "Driver F": {"total": 0, "history": []},
        "Driver G": {"total": 0, "history": []},
        "Driver H": {"total": 0, "history": []},
        "Driver I": {"total": 0, "history": []},
        "Driver J": {"total": 0, "history": []},
    }
    
    # Simulate 6 events of the tournament
    for event in range(1, 7):
        print(f"\nEvent {event} Results:")
        
        # Assign random finishing positions
        # Some drivers have better odds of finishing high
        drivers = list(participants.keys())
        
        # Different drivers have different skill levels affecting their likely position
        weights = {
            "Driver A": 0.9,  # Very good
            "Driver B": 0.8,  # Very good
            "Driver C": 0.7,  # Good
            "Driver D": 0.6,  # Good
            "Driver E": 0.5,  # Average
            "Driver F": 0.5,  # Average
            "Driver G": 0.4,  # Below average
            "Driver H": 0.3,  # Below average
            "Driver I": 0.2,  # Weak
            "Driver J": 0.1,  # Weak
        }
        
        # Simulate finishing positions with weighted randomness
        positions = []
        drivers_left = drivers.copy()
        
        for position in range(1, len(drivers) + 1):
            # Calculate weighted probabilities for remaining drivers
            driver_weights = [weights[d] for d in drivers_left]
            total_weight = sum(driver_weights)
            if total_weight == 0:
                # Avoid division by zero
                driver_weights = [1/len(drivers_left)] * len(drivers_left)
            else:
                driver_weights = [w/total_weight for w in driver_weights]
            
            # Select a driver based on weights
            selected_driver = random.choices(drivers_left, weights=driver_weights, k=1)[0]
            positions.append(selected_driver)
            drivers_left.remove(selected_driver)
        
        # Print and update results
        for position, driver in enumerate(positions, 1):
            # Points are based on position (using the rank_points array)
            points = rank_points[position-1] if position <= len(rank_points) else 0
            
            # Update driver data
            participants[driver]["history"].append(position)  # Store actual position
            participants[driver]["total"] += points
            
            print(f"{position}. {driver}: {points} points")
    
    # Print current standings
    print("\nCurrent Standings after Event 6:")
    
    # Sort participants by total points
    sorted_participants = sorted(participants.items(), key=lambda x: x[1]["total"], reverse=True)
    
    for rank, (name, data) in enumerate(sorted_participants, 1):
        positions = [str(pos) for pos in data["history"][-3:]]
        position_str = ", ".join(positions)
        points = data["total"]
        print(f"{rank}. {name}: {points} points (Last 3 events: {position_str})")
    
    # Project end-of-season results
    print("\nEnd-of-Season Projections:")
    
    # Remaining events in the tournament
    remaining_events = 10 - 6  # 10-event tournament, after event 6
    
    # Transform position history to points history for projections
    for name, data in participants.items():
        # Convert positions to points for the projection system
        points_history = []
        for position in data["history"]:
            points = rank_points[position-1] if position <= len(rank_points) else 0
            points_history.append(points)
        
        # Create current rating tuple (total_points, points_history)
        current_rating = (data["total"], points_history)
        
        # Project tournament finish
        projection = points_system.project_season_finish(current_rating, remaining_events)
        
        # Add to visualizer
        visualizer.add_participant(name, data["total"], points_history, projection)
        
        # Print projection
        print(f"{name}:")
        print(f"  Current: {data['total']} points")
        print(f"  Projected: {projection['projected_points']:.1f} points")
        print(f"  Range: {projection['min_points']:.1f} - {projection['max_points']:.1f}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer.plot_projections()
    visualizer.save("tournament_projections.png")
    
    visualizer.plot_weekly_trends()
    visualizer.save("tournament_weekly_trends.png")
    
    # Print final projection table
    print("\nDetailed Projection Table:")
    visualizer.print_projection_table()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run points-based ranking system examples.')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save output files (default: output)')
    parser.add_argument('--examples', type=str, nargs='+',
                        choices=['1', '2', 'all'],
                        default=['all'],
                        help='Examples to run (1-2 or all)')
    return parser.parse_args()


def main():
    """Run the points-based examples."""
    # Parse command line arguments
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Results will be saved to: {os.path.abspath(args.output_dir)}")
    
    # Seed random for reproducibility
    random.seed(42)
    
    # Determine which examples to run
    examples_to_run = set()
    if 'all' in args.examples:
        examples_to_run = {1, 2}
    else:
        for example in args.examples:
            examples_to_run.add(int(example))
    
    # Run examples
    if 1 in examples_to_run:
        example_1_fantasy_football(args.output_dir)
    
    if 2 in examples_to_run:
        example_2_rank_based_tournament(args.output_dir)
    
    print(f"\nExamples complete. Visualization charts have been saved to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()