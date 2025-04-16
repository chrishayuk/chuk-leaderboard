#!/usr/bin/env python3
"""
Elo demo runner – examples 1‑5.

All rating systems auto‑register on import, so there is no manual
RatingSystemRegistry manipulation anymore.
"""
from __future__ import annotations
import argparse, os, math, random, sys, textwrap
from typing import Dict, Tuple, List

# --------------------------------------------------------------------------- #
#  Project import hook                                                        #
# --------------------------------------------------------------------------- #
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

#  ↓↓↓ merely importing registers the system ↓↓↓
from chuk_leaderboard.rating_systems import elo      # noqa: F401
from chuk_leaderboard.rating_systems.registry import (
    get_rating_system, RatingSystemRegistry,
)

from chuk_leaderboard.visualizers.rating_history_visualizer import (
    RatingHistoryVisualizer,
)
from chuk_leaderboard.visualizers.rating_comparison_visualizer import (
    RatingComparisonVisualizer,
)
from chuk_leaderboard.visualizers.expected_outcome_visualizer import (
    ExpectedOutcomeVisualizer,
)

# --------------------------------------------------------------------------- #
#  Utilities                                                                  #
# --------------------------------------------------------------------------- #
def update_pair(
    system, r_a: float, r_b: float, result_a: float
) -> Tuple[float, float]:
    """Return (new_a, new_b) after one game – snapshotting the pre‑match ratings."""
    new_a = system.calculate_rating(r_a, [(r_b, result_a)])
    new_b = system.calculate_rating(r_b, [(r_a, 1.0 - result_a)])
    return new_a, new_b


def seeded_rng(example_id: int) -> random.Random:
    """Give every example its own deterministic RNG."""
    return random.Random(42 + example_id)


def print_rating(tag: str, rating: float) -> None:
    print(f"{tag}: Rating = {rating:.1f}")


# --------------------------------------------------------------------------- #
#  Example 1 – basic                                                          #
# --------------------------------------------------------------------------- #
def example_1_basic(out_dir: str) -> None:
    print("\n=== EXAMPLE 1: BASIC RATING CHANGES ===")

    elo_sys = get_rating_system("elo")
    vis = RatingHistoryVisualizer("Basic Rating Changes (Elo)", out_dir)

    a, b = elo_sys.get_default_rating(), elo_sys.get_default_rating()
    vis.track_with_explicit_values("A", a, 0, 0)
    vis.track_with_explicit_values("B", b, 0, 0)

    print("Initial ratings:")
    print_rating("A", a)
    print_rating("B", b)

    # Match 1: A wins
    print("\nMatch 1: A wins")
    a, b = update_pair(elo_sys, a, b, 1.0)
    vis.track_with_explicit_values("A", a, 0, 0)
    vis.track_with_explicit_values("B", b, 0, 0)
    print_rating("A", a)
    print_rating("B", b)

    # Match 2: B wins
    print("\nMatch 2: B wins")
    a, b = update_pair(elo_sys, a, b, 0.0)
    vis.track_with_explicit_values("A", a, 0, 0)
    vis.track_with_explicit_values("B", b, 0, 0)
    print_rating("A", a)
    print_rating("B", b)

    # Match 3: draw
    print("\nMatch 3: Draw")
    a, b = update_pair(elo_sys, a, b, 0.5)
    vis.track_with_explicit_values("A", a, 0, 0)
    vis.track_with_explicit_values("B", b, 0, 0)
    print_rating("A", a)
    print_rating("B", b)

    vis.plot()
    vis.save("elo_basic_rating_changes.png")


# --------------------------------------------------------------------------- #
#  Example 2 – different K                                                    #
# --------------------------------------------------------------------------- #
def example_2_different_k(out_dir: str) -> None:
    print("\n=== EXAMPLE 2: DIFFERENT K‑FACTORS ===")

    rng = seeded_rng(2)
    low  = elo.EloRatingSystem(k_factor=16)
    med  = elo.EloRatingSystem(k_factor=32)
    high = elo.EloRatingSystem(k_factor=64)
    systems = {
        "Low‑K (16)":  {"sys": low,  "rating": low.get_default_rating()},
        "Med‑K (32)":  {"sys": med,  "rating": med.get_default_rating()},
        "High‑K (64)": {"sys": high, "rating": high.get_default_rating()},
    }

    vis = RatingHistoryVisualizer("Elo – Different K", out_dir)
    for name, d in systems.items():
        vis.track_with_explicit_values(name, d["rating"], 0, 0)
    print_rating("All players", systems["Low‑K (16)"]["rating"])

    for m in range(1, 21):
        opp = rng.uniform(1300, 1700)
        weaker = opp < 1500
        result = 1.0 if rng.random() < (0.6 if weaker else 0.4) else 0.0
        outcome = "win" if result else "loss"
        print(f"\nMatch {m}: {outcome} vs {'weaker' if weaker else 'stronger'} opp ({opp:.1f})")

        for name, d in systems.items():
            before = d["rating"]
            d["rating"] = d["sys"].calculate_rating(before, [(opp, result)])
            delta = d["rating"] - before
            print(f"{name}: {before:.1f} → {d['rating']:.1f} ({delta:+.1f})")
            vis.track_with_explicit_values(name, d["rating"], 0, 0)

    vis.plot()
    vis.save("elo_different_k.png")


# --------------------------------------------------------------------------- #
#  Example 3 – convergence                                                    #
# --------------------------------------------------------------------------- #
def example_3_convergence(out_dir: str) -> None:
    print("\n=== EXAMPLE 3: RATING CONVERGENCE ===")

    rng = seeded_rng(3)
    elo_sys = get_rating_system("elo")
    vis = RatingHistoryVisualizer("Elo Rating Convergence", out_dir)
    cmp_vis = RatingComparisonVisualizer("True Skill vs Elo", out_dir)

    players: Dict[str, Dict[str, float]] = {
        "Strong": {"rating": elo_sys.get_default_rating(), "true": 1800},
        "Medium": {"rating": elo_sys.get_default_rating(), "true": 1500},
        "Weak":   {"rating": elo_sys.get_default_rating(), "true": 1200},
    }

    print("Initial ratings:")
    for n, d in players.items():
        vis.track_with_explicit_values(n, d["rating"], 0, 0)
        print_rating(n, d["rating"])

    pairs = [("Strong", "Medium"), ("Strong", "Weak"), ("Medium", "Weak")]

    for rnd in range(1, 31):
        print(f"\nRound {rnd}:")
        for a, b in pairs:
            diff = players[a]["true"] - players[b]["true"]
            win_p = 1.0 / (1.0 + math.exp(-diff / 400.0))
            result = 1.0 if rng.random() < win_p else 0.0
            players[a]["rating"], players[b]["rating"] = update_pair(
                elo_sys, players[a]["rating"], players[b]["rating"], result
            )
            print(f"{a} vs {b}: {a if result else b} wins")

        for n, d in players.items():
            vis.track_with_explicit_values(n, d["rating"], 0, 0)

    print("\nFinal ratings vs true skill:")
    for n, d in players.items():
        cmp_vis.add_comparison_with_explicit_values(n, d["rating"], 0, d["true"])
        diff = d["rating"] - d["true"]
        print(f"{n}: {d['rating']:.1f} (Δ {diff:+.1f})")

    vis.plot();         vis.save("elo_convergence.png")
    cmp_vis.plot_comparison(); cmp_vis.save("elo_true_skill_gap.png")


# --------------------------------------------------------------------------- #
#  Example 4 – expected outcomes                                              #
# --------------------------------------------------------------------------- #
def example_4_expected(out_dir: str) -> None:
    print("\n=== EXAMPLE 4: EXPECTED OUTCOMES ===")

    elo_sys = get_rating_system("elo")
    vis = ExpectedOutcomeVisualizer("Elo – Win Probabilities", out_dir)

    tests = [
        ("Equal", 1500, "Equal", 1500),
        ("+100",  1550, "-100", 1450),
        ("+200",  1600, "-200", 1400),
        ("+600",  1800, "-600", 1200),
        ("+1000", 2000, "-1000", 1000),
    ]
    print("Expected win probabilities:")
    for p1, r1, p2, r2 in tests:
        prob = elo_sys.expected_outcome(r1, r2)
        vis.add_matchup_with_explicit_values(p1, r1, 0, p2, r2, 0, prob)
        print(f"{p1} ({r1}) vs {p2} ({r2}): {prob:.4f}")

    vis.print_matchup_table()
    vis.plot_matchups()
    vis.save("elo_expected_outcomes.png")


# --------------------------------------------------------------------------- #
#  Example 5 – dynamic K                                                      #
# --------------------------------------------------------------------------- #
def example_5_dynamic_k(out_dir: str) -> None:
    print("\n=== EXAMPLE 5: STANDARD vs DYNAMIC K ===")

    rng = seeded_rng(5)
    fixed   = elo.EloRatingSystem(k_factor=32)
    dynamic = elo.EloRatingSystem(k_factor=32)
    players = {
        "Fixed K":   {"rating": fixed.get_default_rating(),   "sys": fixed},
        "Dynamic K": {"rating": dynamic.get_default_rating(), "sys": dynamic},
    }
    vis = RatingHistoryVisualizer("Standard vs Dynamic K", out_dir)
    for n, d in players.items():
        vis.track_with_explicit_values(n, d["rating"], 0, 0)
    print_rating("Both players", players["Fixed K"]["rating"])

    for m in range(1, 51):
        weaker = m <= 20
        opp    = 1300 if weaker else 1900
        result = 1.0 if weaker else 0.0
        desc   = "weaker" if weaker else "stronger"
        outcome = "Win" if result else "Loss"
        print(f"\nMatch {m}: {outcome} vs {desc} opp ({opp})")

        for n, d in players.items():
            before = d["rating"]
            if n == "Dynamic K":
                k = d["sys"].adjust_k_factor(before)
                d["rating"] = d["sys"].get_rating_with_dynamic_k(before, [(opp, result)])
                print(f"{n}: {before:.1f} → {d['rating']:.1f} (K={k})")
            else:
                d["rating"] = d["sys"].calculate_rating(before, [(opp, result)])
                print(f"{n}: {before:.1f} → {d['rating']:.1f} (K=32)")
            vis.track_with_explicit_values(n, d["rating"], 0, 0)

    vis.plot()
    vis.save("elo_dynamic_k.png")


# --------------------------------------------------------------------------- #
#  CLI                                                                        #
# --------------------------------------------------------------------------- #
EXAMPLES = {
    1: example_1_basic,
    2: example_2_different_k,
    3: example_3_convergence,
    4: example_4_expected,
    5: example_5_dynamic_k,
}


def parse_cli() -> argparse.Namespace:
    epilog = textwrap.dedent(
        """
        Examples:
          uv run debug/elo_example.py                # run all
          uv run debug/elo_example.py -e 1 4         # only ex 1 & 4
        """
    )
    p = argparse.ArgumentParser(
        description="Elo demo suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    p.add_argument(
        "-e",
        "--examples",
        nargs="+",
        choices=[str(i) for i in EXAMPLES] + ["all"],
        default=["all"],
        help="Which examples to run",
    )
    p.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Where to save pngs (created if absent)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_cli()
    wanted = {int(x) for x in args.examples} if "all" not in args.examples else set(EXAMPLES)
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Results will be saved to {os.path.abspath(args.output_dir)}")
    print("Available rating systems:", ", ".join(RatingSystemRegistry.list_available()))

    for idx in sorted(wanted):
        EXAMPLES[idx](args.output_dir)

    print(f"\nDone! Charts are in {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()