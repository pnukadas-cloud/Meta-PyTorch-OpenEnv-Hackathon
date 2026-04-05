import unittest

from crisis_commander_env.grader import grade_episode
from crisis_commander_env.models import ActionType, CrisisAction, Difficulty, ResourceStatus
from crisis_commander_env.simulator import CrisisCommanderEnv


class CrisisCommanderEnvTests(unittest.TestCase):
    def test_reset_builds_initial_observation(self):
        env = CrisisCommanderEnv(difficulty=Difficulty.STANDARD)
        result = env.reset(seed=7, options={"scenario_id": "rush_hour_cascade", "difficulty": "standard"})

        self.assertEqual(result.observation.scenario_id, "rush_hour_cascade")
        self.assertEqual(result.observation.turn, 0)
        self.assertGreaterEqual(len(result.observation.incidents), 2)

    def test_dispatch_changes_resource_state(self):
        env = CrisisCommanderEnv(difficulty=Difficulty.STANDARD)
        env.reset(seed=3, options={"scenario_id": "rush_hour_cascade", "difficulty": "standard"})

        result = env.step(CrisisAction(action_type=ActionType.DISPATCH, resource_id="AMB-1", incident_id="INC-1"))

        self.assertIn(env.state.resources["AMB-1"].status, {ResourceStatus.EN_ROUTE, ResourceStatus.ON_SCENE})
        self.assertEqual(result.observation.turn, 1)

    def test_mutual_aid_spends_budget(self):
        env = CrisisCommanderEnv(difficulty=Difficulty.STANDARD)
        env.reset(seed=11, options={"scenario_id": "festival_blackout", "difficulty": "standard"})
        starting_budget = env.state.budget_remaining

        env.step(
            CrisisAction(
                action_type=ActionType.REQUEST_MUTUAL_AID,
                resource_kind=env.state.resources["AMB-1"].kind,
                incident_id="FEST-1",
            )
        )

        self.assertEqual(env.state.budget_remaining, starting_budget - 4)
        self.assertGreaterEqual(env.state.mutual_aid_calls, 1)

    def test_grade_episode_returns_hackathon_summary(self):
        env = CrisisCommanderEnv(difficulty=Difficulty.STANDARD)
        env.reset(seed=5, options={"scenario_id": "industrial_storm", "difficulty": "standard"})
        env.step(CrisisAction(action_type=ActionType.DISPATCH, resource_id="FIRE-1", incident_id="STORM-1"))
        report = grade_episode(env.state)

        self.assertIn("final_score", report)
        self.assertIn("verdict", report)


if __name__ == "__main__":
    unittest.main()

