#!/usr/bin/env python3
"""
Points‑based demo runner.

* Automatic rating‑system registration (import side‑effect).
* Shared CLI helper and deterministic per‑example RNG for reproducibility.
* Two examples:
  1. Fantasy football league projections
  2. Rank‑based tournament projections

Run e.g.:
    uv run debug/points_example.py                # all examples
    uv run debug/points_example.py -e 2           # only example 2
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import argparse, os, random, sys, textwrap

# --------------------------------------------------------------------------- #
# Import project root                                                       #
# --------------------------------------------------------------------------- #
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Importing the module auto‑registers the rating system
from chuk_leaderboard.rating_systems import points_based  # noqa: F401
from chuk_leaderboard.rating_systems.registry import get_rating_system, RatingSystemRegistry
from chuk_leaderboard.visualizers.season_projection_visualizer import SeasonProjectionVisualizer

# --------------------------------------------------------------------------- #
# Helpers                                                                   #
# --------------------------------------------------------------------------- #

def rng(seed_offset: int) -> random.Random:
    """Deterministic RNG per example."""
    return random.Random(142 + seed_offset)

# --------------------------------------------------------------------------- #
# Example 1 – Fantasy Football                                                 #
# --------------------------------------------------------------------------- #

def example_1_fantasy(out_dir: str) -> None:
    print("\n=== EXAMPLE 1: FANTASY FOOTBALL LEAGUE ===")
    system = get_rating_system("points")
    weeks, current = 14, 8
    vis = SeasonProjectionVisualizer("Fantasy Football Projections", out_dir, weeks_in_season=weeks, current_week=current)
    vis.set_league_info("Fantasy Football League", weeks, current)

    teams: Dict[str, Dict[str, float | List[float]]] = {
        name: {"total": 0.0, "history": []}
        for name in (
            "Touchdown Titans", "Running Rebels", "Pass Panthers", "Golden Receivers",
            "Defense Dragons", "Quarterback Kings", "Field Goal Falcons", "Injury Infernos"
        )
    }
    r = rng(1)

    for week in range(1, current + 1):
        print(f"\nWeek {week} Results:")
        for name, data in teams.items():
            mean, std = {
                "Touchdown Titans": (125, 15),
                "Running Rebels": (120, 25),
                "Quarterback Kings": (130 - 5 * week, 15),
                "Injury Infernos": (80 + 5 * week, 15)
            }.get(name, (100, 20))
            score = max(50, round(r.normalvariate(mean, std), 1))
            data["history"].append(score)
            data["total"] += score
            print(f"{name}: {score:.1f} points")

    remaining = weeks - current
    print("\nEnd-of-Season Projections:")
    for name, data in teams.items():
        current_rating: Tuple[float, List[float]] = (data["total"], data["history"])
        projection = system.project_season_finish(current_rating, remaining)
        vis.add_participant(name, data["total"], data["history"], projection)
        print(f"{name}: Projected {projection['projected_points']:.1f} (Range {projection['lower_bound']:.1f}–{projection['upper_bound']:.1f})")

    vis.plot_projections();     vis.save("fantasy_football_projections.png")
    vis.plot_weekly_trends();   vis.save("fantasy_football_weekly_trends.png")
    vis.plot_projection_ranges(); vis.save("fantasy_football_projection_ranges.png")
    print("\nDetailed Projection Table:")
    vis.print_projection_table()

# --------------------------------------------------------------------------- #
# Example 2 – Rank‑Based Tournament                                            #
# --------------------------------------------------------------------------- #

def example_2_ranked(out_dir: str) -> None:
    print("\n=== EXAMPLE 2: RANK-BASED TOURNAMENT ===")
    rank_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    system = points_based.PointsBasedRankingSystem(rank_points=rank_points)
    events, current = 10, 6
    vis = SeasonProjectionVisualizer("Tournament Standings", out_dir, weeks_in_season=events, current_week=current)
    vis.set_league_info("Racing Championship", events, current)

    drivers = {f"Driver {c}": {"total": 0.0, "history": []} for c in 'ABCDEFGHIJ'}
    weights = {d: 1.0 - i * 0.1 for i, d in enumerate(drivers)}
    r = rng(2)

    for event in range(1, current + 1):
        print(f"\nEvent {event} Results:")
        remaining = list(drivers)
        finishing: List[str] = []
        while remaining:
            w = [weights[d] for d in remaining]
            total = sum(w)
            probs = [x / total for x in w]
            pick = r.choices(remaining, weights=probs, k=1)[0]
            finishing.append(pick)
            remaining.remove(pick)
        for pos, driver in enumerate(finishing, 1):
            pts = rank_points[pos - 1] if pos <= len(rank_points) else 0
            drivers[driver]["history"].append(pos)
            drivers[driver]["total"] += pts
            print(f"{pos}. {driver}: {pts} points")

    remaining_events = events - current
    print("\nEnd-of-Season Projections:")
    for name, data in drivers.items():
        points_hist = [rank_points[p - 1] for p in data["history"]]
        current_rating: Tuple[float, List[float]] = (data["total"], points_hist)
        projection = system.project_season_finish(current_rating, remaining_events)
        vis.add_participant(name, data["total"], points_hist, projection)
        print(f"{name}: Projected {projection['projected_points']:.1f} (Range {projection['lower_bound']:.1f}–{projection['upper_bound']:.1f})")

    vis.plot_projections();   vis.save("tournament_projections.png")
    vis.plot_weekly_trends(); vis.save("tournament_weekly_trends.png")
    print("\nDetailed Projection Table:")
    vis.print_projection_table()

# --------------------------------------------------------------------------- #
# CLI & main                                                                 #
# --------------------------------------------------------------------------- #
EXAMPLES = {1: example_1_fantasy, 2: example_2_ranked}

def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Points-based demo suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              uv run debug/points_example.py -e 1
              uv run debug/points_example.py -e 2
        """),
    )
    parser.add_argument(
        "-e", "--examples",
        nargs="+",
        choices=[*map(str, EXAMPLES), "all"],
        default=["all"],
        help="Which examples to run",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Directory for output files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli()
    want = {int(x) for x in args.examples} if "all" not in args.examples else set(EXAMPLES)
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Saving outputs to {os.path.abspath(args.output_dir)}")
    print("Available systems:", ", ".join(RatingSystemRegistry.list_available()))
    for idx in sorted(want):
        EXAMPLES[idx](args.output_dir)
    print("\nAll done.")

if __name__ == "__main__":
    main()