#!/usr/bin/env python3
"""
Improved Glicko‑2 demo runner.

* Automatic rating‑system registration (import side‑effect).
* Symmetric rating updates for every head‑to‑head so both players use the
  same pre‑match snapshot.
* Shared CLI helper and deterministic per‑example RNG for reproducibility.
* Five examples:
  1. Basic rating changes
  2. Rating convergence toward "true" skill
  3. Effect of inactivity on RD
  4. Convergence from different starting ratings
  5. Expected‑outcome table

Run e.g.:
    uv run debug/glicko2_example.py                # all examples
    uv run debug/glicko2_example.py -e 3 5         # only examples 3 & 5
"""

from __future__ import annotations
from typing import Dict, Tuple
import argparse, math, os, random, sys, textwrap

# --------------------------------------------------------------------------- #
# Import project root                                                       #
# --------------------------------------------------------------------------- #
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Importing the module automatically registers the rating system
from chuk_leaderboard.rating_systems import glicko2  # noqa: F401
from chuk_leaderboard.rating_systems.registry import (
    get_rating_system,
    RatingSystemRegistry,
)
from chuk_leaderboard.visualizers.rating_history_visualizer import RatingHistoryVisualizer
from chuk_leaderboard.visualizers.rating_comparison_visualizer import RatingComparisonVisualizer
from chuk_leaderboard.visualizers.expected_outcome_visualizer import ExpectedOutcomeVisualizer

# --------------------------------------------------------------------------- #
# Helpers                                                                   #
# --------------------------------------------------------------------------- #

def pair_update(
    system, a: Tuple[float, float, float], b: Tuple[float, float, float], result_a: float
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """Return updated tuples (new_a, new_b) for head-to-head match."""
    result_b = 1.0 - result_a
    new_a = system.calculate_rating(a, [(b[0], b[1], result_a)])
    new_b = system.calculate_rating(b, [(a[0], a[1], result_b)])
    return new_a, new_b


def rng(seed_offset: int) -> random.Random:
    """Deterministic RNG per example."""
    return random.Random(240 + seed_offset)

# --------------------------------------------------------------------------- #
# Example 1 – Basic                                                          #
# --------------------------------------------------------------------------- #

def example_1_basic(out_dir: str) -> None:
    print("\n=== EXAMPLE 1: BASIC RATING CHANGES ===")
    system = get_rating_system("glicko2")
    vis = RatingHistoryVisualizer("Basic Rating Changes (Glicko-2)", out_dir)

    a = system.get_default_rating()
    b = system.get_default_rating()
    vis.track_with_explicit_values("Player A", *a)
    vis.track_with_explicit_values("Player B", *b)

    def show(label: str, vals: Tuple[float, float, float]) -> None:
        print(f"{label}: Rating={vals[0]:.1f}, RD={vals[1]:.1f}, Vol={vals[2]:.4f}")

    print("Initial ratings:")
    show("Player A", a)
    show("Player B", b)

    for match, res_a in [(1, 1.0), (2, 0.0), (3, 0.5)]:
        outcome = "wins" if res_a == 1.0 else "draws" if res_a == 0.5 else "loses"
        print(f"\nMatch {match}: Player A {outcome}")
        a, b = pair_update(system, a, b, res_a)
        vis.track_with_explicit_values("Player A", *a)
        vis.track_with_explicit_values("Player B", *b)
        show("Player A", a)
        show("Player B", b)

    vis.plot(); vis.save("glicko2_basic.png")

# --------------------------------------------------------------------------- #
# Example 2 – Rating Convergence                                              #
# --------------------------------------------------------------------------- #

def example_2_convergence(out_dir: str) -> None:
    print("\n=== EXAMPLE 2: RATING CONVERGENCE ===")
    system = get_rating_system("glicko2")
    r = rng(2)

    vis = RatingHistoryVisualizer("Glicko-2 Convergence", out_dir)
    cmp_vis = RatingComparisonVisualizer("True vs Final Rating (Glicko-2)", out_dir)

    base = system.get_default_rating()
    players: Dict[str, Dict[str, float]] = {
        "Strong": {"rating": base[0], "rd": base[1], "vol": base[2], "true": 1800},
        "Medium": {"rating": base[0], "rd": base[1], "vol": base[2], "true": 1500},
        "Weak": {"rating": base[0], "rd": base[1], "vol": base[2], "true": 1200},
    }

    pairs = [("Strong", "Medium"), ("Strong", "Weak"), ("Medium", "Weak")]
    for name, data in players.items():
        vis.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])

    for rnd in range(1, 31):
        print(f"\nRound {rnd}")
        for pa, pb in pairs:
            diff = players[pa]["true"] - players[pb]["true"]
            win_p = 1.0 / (1.0 + math.exp(-diff / 400))
            res_a = 1.0 if r.random() < win_p else 0.0
            a_tuple = (players[pa]["rating"], players[pa]["rd"], players[pa]["vol"])
            b_tuple = (players[pb]["rating"], players[pb]["rd"], players[pb]["vol"])
            new_a, new_b = pair_update(system, a_tuple, b_tuple, res_a)
            players[pa]["rating"], players[pa]["rd"], players[pa]["vol"] = new_a
            players[pb]["rating"], players[pb]["rd"], players[pb]["vol"] = new_b
            winner = pa if res_a else pb
            print(f"{pa} vs {pb}: {winner} wins")
        for name, data in players.items():
            vis.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])

    print("\nFinal ratings vs true skill:")
    for name, data in players.items():
        cmp_vis.add_comparison_with_explicit_values(name, data["rating"], data["rd"], data["true"])
        print(f"{name}: {data['rating']:.1f} (true {data['true']})")

    vis.plot(); vis.save("glicko2_convergence.png")
    cmp_vis.plot_comparison(); cmp_vis.save("glicko2_true_skill_gap.png")

# --------------------------------------------------------------------------- #
# Example 3 – Inactive Players                                                 #
# --------------------------------------------------------------------------- #

def example_3_inactive(out_dir: str) -> None:
    print("\n=== EXAMPLE 3: INACTIVE PLAYERS ===")
    system = get_rating_system("glicko2")
    r = rng(3)

    rating_viz = RatingHistoryVisualizer("Inactive – Rating", out_dir)
    rd_viz = RatingHistoryVisualizer("Inactive – RD", out_dir)

    base = system.get_default_rating()
    players = {
        "Active":     {"rating": base[0], "rd": 150, "vol": base[2]},
        "Occasional": {"rating": base[0], "rd": 150, "vol": base[2]},
        "Inactive":   {"rating": base[0], "rd": 150, "vol": base[2]},
    }

    # Initial track
    for name, data in players.items():
        rating_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
        rd_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])

    opponent_rd = 150
    for period in range(1, 16):
        # Active plays every period
        a = players["Active"]
        opp = r.uniform(1300, 1700)
        res = 1.0 if r.random() < 0.5 else 0.0
        new_a, _ = pair_update(system, (a["rating"], a["rd"], a["vol"]), (opp, opponent_rd, a["vol"]), res)
        a["rating"], a["rd"], a["vol"] = new_a

        # Occasional plays every 5th
        o = players["Occasional"]
        if period % 5 == 0:
            opp = r.uniform(1300, 1700)
            res = 1.0 if r.random() < 0.5 else 0.0
            update_o, _ = pair_update(system, (o["rating"], o["rd"], o["vol"]), (opp, opponent_rd, o["vol"]), res)
            o["rating"], o["rd"], o["vol"] = update_o
        else:
            no_game = (o["rating"], o["rd"], o["vol"])
            o["rating"], o["rd"], o["vol"] = system.calculate_rating(no_game, [])

        # Inactive never plays
        i = players["Inactive"]
        no_game_i = (i["rating"], i["rd"], i["vol"])
        i["rating"], i["rd"], i["vol"] = system.calculate_rating(no_game_i, [])

        # Track after each period
        for name, data in players.items():
            rating_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])
            rd_viz.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])

        if period in (1, 5, 10, 15):
            print(f"\nAfter period {period}:")
            for name, data in players.items():
                print(f"{name}: Rating={data['rating']:.1f}, RD={data['rd']:.1f}")

    rating_viz.plot(); rating_viz.save("glicko2_inactive_ratings.png")
    rd_viz.plot(show_volatility=False); rd_viz.save("glicko2_inactive_rd.png")

# --------------------------------------------------------------------------- #
# Example 4 – Different Starting Ratings                                      #
# --------------------------------------------------------------------------- #

def example_4_starting(out_dir: str) -> None:
    print("\n=== EXAMPLE 4: DIFFERENT STARTING RATINGS ===")
    system = get_rating_system("glicko2")
    r = rng(4)

    vis = RatingHistoryVisualizer("Different Starting Ratings", out_dir)
    cmp_vis = RatingComparisonVisualizer("Convergence to True Skill", out_dir)

    _, base_rd, base_vol = system.get_default_rating()
    players = {
        "Underrated": {"rating": 1200, "rd": base_rd, "vol": base_vol, "true": 1500},
        "Accurate":   {"rating": 1500, "rd": 150,    "vol": base_vol, "true": 1500},
        "Overrated":  {"rating": 1800, "rd": base_rd, "vol": base_vol, "true": 1500},
    }

    for name, data in players.items():
        vis.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])

    for rnd in range(1, 21):
        for name, data in players.items():
            outcomes: List[Tuple[float, float, float]] = []
            for opp_skill in (1300, 1500, 1700):
                diff = data["true"] - opp_skill
                res = 1.0 if r.random() < 1/(1+math.exp(-diff/400)) else 0.0
                outcomes.append((opp_skill, 150, res))
            new_vals = system.calculate_rating(
                (data["rating"], data["rd"], data["vol"]), outcomes
            )
            data["rating"], data["rd"], data["vol"] = new_vals
        for name, data in players.items():
            vis.track_with_explicit_values(name, data["rating"], data["rd"], data["vol"])

    vis.plot(); vis.save("glicko2_starting_ratings.png")

    print("\nFinal difference from true skill:")
    for name, data in players.items():
        cmp_vis.add_comparison_with_explicit_values(name, data["rating"], data["rd"], data["true"])
        diff = data["rating"] - data["true"]
        print(f"{name}: {diff:+.1f}")

    cmp_vis.plot_comparison(); cmp_vis.save("glicko2_starting_gap.png")

# --------------------------------------------------------------------------- #
# Example 5 – Expected Outcomes                                               #
# --------------------------------------------------------------------------- #

def example_5_expected(out_dir: str) -> None:
    print("\n=== EXAMPLE 5: EXPECTED OUTCOMES ===")
    system = get_rating_system("glicko2")
    vis = ExpectedOutcomeVisualizer("Expected Win Probabilities", out_dir)

    scenarios = [
        ("Equal", 1500, 30, "Equal", 1500, 30),
        ("Slightly Better", 1550, 30, "Slightly Worse", 1450, 30),
        ("Much Better", 1800, 30, "Much Worse", 1200, 30),
        ("Better Uncertain", 1600, 200, "Worse Certain", 1400, 30),
        ("Better vs Uncertain", 1550, 30, "Worse Uncertain", 1450, 350),
    ]
    for p1, r1, rd1, p2, r2, rd2 in scenarios:
        prob = system.expected_outcome((r1, rd1), (r2, rd2))
        vis.add_matchup_with_explicit_values(p1, r1, rd1, p2, r2, rd2, prob)
        print(f"{p1} ({r1}, RD={rd1}) vs {p2} ({r2}, RD={rd2}): {prob:.4f}")

    vis.print_matchup_table()
    vis.plot_matchups(); vis.save("glicko2_expected.png")

# --------------------------------------------------------------------------- #
# CLI & main                                                                 #
# --------------------------------------------------------------------------- #
EXAMPLES = {
    1: example_1_basic,
    2: example_2_convergence,
    3: example_3_inactive,
    4: example_4_starting,
    5: example_5_expected,
}

def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Glicko-2 demo suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              uv run debug/glicko2_example.py -e 1 4
              uv run debug/glicko2_example.py -e all
        """),
    )
    parser.add_argument(
        "-e", "--examples",
        nargs="+",
        choices=[*map(str, EXAMPLES), "all"],
        default=["all"],
        help="Examples to run",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Directory for output PNGs",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli()
    want = {int(x) for x in args.examples} if "all" not in args.examples else set(EXAMPLES)
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Saving to {os.path.abspath(args.output_dir)}")
    print("Available systems:", ", ".join(RatingSystemRegistry.list_available()))
    for idx in sorted(want):
        EXAMPLES[idx](args.output_dir)
    print("\nDone.")

if __name__ == "__main__":
    main()