import unittest

from crisis_commander_env.baselines import fairness_aware_policy, severity_first_policy
from crisis_commander_env.models import ActionType, Difficulty
from crisis_commander_env.simulator import CrisisCommanderEnv


class BaselinePolicyTests(unittest.TestCase):
    def test_severity_policy_returns_action(self):
        env = CrisisCommanderEnv(difficulty=Difficulty.STANDARD)
        env.reset(seed=13, options={"scenario_id": "rush_hour_cascade", "difficulty": "standard"})
        action = severity_first_policy(env.state)

        self.assertIsNotNone(action)
        self.assertIn(action.action_type, {ActionType.DISPATCH, ActionType.EXPAND_HOSPITAL, ActionType.WAIT})

    def test_fairness_policy_returns_action(self):
        env = CrisisCommanderEnv(difficulty=Difficulty.STANDARD)
        env.reset(seed=17, options={"scenario_id": "festival_blackout", "difficulty": "standard"})
        action = fairness_aware_policy(env.state)

        self.assertIsNotNone(action)
        self.assertIn(
            action.action_type,
            {ActionType.DISPATCH, ActionType.STAGE, ActionType.REQUEST_MUTUAL_AID, ActionType.WAIT},
        )


if __name__ == "__main__":
    unittest.main()

