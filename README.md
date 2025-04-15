# CHUK Leaderboard

A Python package for implementing and comparing different rating systems for competitive games, sports, or any activity where skill rating is needed.

## Features

- Multiple rating system implementations:
  - **Elo**: Classic chess rating system with configurable K-factor
  - **Glicko2**: Advanced rating system with rating, rating deviation, and volatility
  - (More systems can be easily added)
- Visualization tools for analyzing rating data:
  - Track rating history over time
  - Compare ratings to "true skill" values
  - Visualize expected outcomes between players
- Example scripts demonstrating real-world applications
- Comprehensive test suite

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/chuk-leaderboard.git
cd chuk-leaderboard

# Install in development mode
pip install -e .
```

## Usage Examples

### Basic Elo Example

```python
from chuk_leaderboard.rating_systems.registry import get_rating_system

# Get the Elo rating system
elo = get_rating_system("elo")

# Initial ratings
player_a = 1500
player_b = 1500

# Player A wins against Player B
player_a = elo.calculate_rating(player_a, [(player_b, 1.0)])
player_b = elo.calculate_rating(player_b, [(player_a, 0.0)])

print(f"Player A's new rating: {player_a}")
print(f"Player B's new rating: {player_b}")
```

### Basic Glicko2 Example

```python
from chuk_leaderboard.rating_systems.registry import get_rating_system

# Get the Glicko2 rating system
glicko2 = get_rating_system("glicko2")

# Initial ratings (rating, rating deviation, volatility)
player_a = glicko2.get_default_rating()  # (1500, 350, 0.06)
player_b = glicko2.get_default_rating()  # (1500, 350, 0.06)

# Player A wins against Player B
player_a = glicko2.calculate_rating(player_a, [(player_b[0], player_b[1], 1.0)])
player_b = glicko2.calculate_rating(player_b, [(player_a[0], player_a[1], 0.0)])

print(f"Player A's new rating: {player_a}")
print(f"Player B's new rating: {player_b}")
```

### Visualizing Rating History

```python
from chuk_leaderboard.rating_systems.registry import get_rating_system
from chuk_leaderboard.visualizers.rating_history_visualizer import RatingHistoryVisualizer

# Initialize the rating system and visualizer
glicko2 = get_rating_system("glicko2")
visualizer = RatingHistoryVisualizer("Rating History", "output")

# Initial ratings
player_a = glicko2.get_default_rating()
player_b = glicko2.get_default_rating()

# Track initial ratings
visualizer.track_with_explicit_values("Player A", player_a[0], player_a[1], player_a[2])
visualizer.track_with_explicit_values("Player B", player_b[0], player_b[1], player_b[2])

# Simulate 5 matches
for i in range(5):
    # Player A wins
    player_a = glicko2.calculate_rating(player_a, [(player_b[0], player_b[1], 1.0)])
    player_b = glicko2.calculate_rating(player_b, [(player_a[0], player_a[1], 0.0)])
    
    # Track updates
    visualizer.track_with_explicit_values("Player A", player_a[0], player_a[1], player_a[2])
    visualizer.track_with_explicit_values("Player B", player_b[0], player_b[1], player_b[2])

# Generate and save visualization
visualizer.plot()
visualizer.save("rating_history.png")
```

## Running the Examples

The package includes comprehensive examples for both Elo and Glicko2 rating systems:

```bash
# Run Glicko2 examples
python debug/glicko2_example.py

# Run Elo examples
python debug/elo_example.py

# Run specific examples
python debug/glicko2_example.py --examples 1 3
python debug/elo_example.py --examples 2 4
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests for specific rating system
pytest tests/rating_systems/test_elo.py
pytest tests/rating_systems/test_glicko2.py
```

## Rating Systems Overview

### Elo

The Elo rating system is a method for calculating the relative skill levels of players, originally designed for chess. It uses a simple mathematical formula:

- Each player has a single rating number
- After a match, ratings are updated based on the expected vs. actual outcome
- The K-factor controls how quickly ratings change

### Glicko2

The Glicko2 rating system extends Elo with:

- **Rating**: Similar to Elo rating, represents skill level
- **Rating Deviation (RD)**: Represents the uncertainty in a rating
- **Volatility**: Represents how consistent a player's performance is

Key features:
- RD increases over time when players are inactive
- RD decreases after matches (more certainty in rating)
- Accounts for opponent rating uncertainty

## Visualization Tools

### RatingHistoryVisualizer

Tracks and visualizes how ratings change over time.

### RatingComparisonVisualizer

Compares ratings against expected or "true" values.

### ExpectedOutcomeVisualizer

Visualizes win probabilities between different players.

## Contributing

Contributions are welcome! Feel free to add:

- New rating systems
- New visualizers
- Better examples
- Bug fixes and improvements

## License

[MIT License](LICENSE)