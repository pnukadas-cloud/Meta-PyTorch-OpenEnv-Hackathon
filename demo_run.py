"""Small local runner for quickly verifying the environment from VS Code."""

from __future__ import annotations

import argparse
import json

from crisis_commander_env.baselines import fairness_aware_policy
from crisis_commander_env.grader import grade_episode
from crisis_commander_env.simulator import CrisisCommanderEnv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a short Crisis Commander rollout.")
    parser.add_argument("--scenario", default="rush_hour_cascade", help="Scenario id to run.")
    parser.add_argument(
        "--difficulty",
        default="advanced",
        choices=["easy", "standard", "advanced", "expert"],
        help="Difficulty level.",
    )
    parser.add_argument("--seed", type=int, default=7, help="Seed for deterministic playback.")
    parser.add_argument("--steps", type=int, default=5, help="Maximum number of steps to simulate.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    env = CrisisCommanderEnv()
    result = env.reset(
        seed=args.seed,
        options={"scenario_id": args.scenario, "difficulty": args.difficulty},
    )

    print("\n=== INITIAL OBSERVATION ===")
    print(result.observation.text)

    for step_idx in range(args.steps):
        if env.state is None or env.state.done:
            break

        action = fairness_aware_policy(env.state)
        result = env.step(action)

        print(f"\n=== STEP {step_idx + 1} ===")
        print(f"Action: {action.summary()}")
        print(f"Reward: {result.reward}")
        print("Recent events:")
        for event in result.info.get("events", []):
            print(f"- {event}")

    if env.state is None:
        return

    print("\n=== GRADE SUMMARY ===")
    print(json.dumps(grade_episode(env.state), indent=2))


if __name__ == "__main__":
    main()

