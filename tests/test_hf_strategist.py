import os
import unittest
from unittest.mock import patch

from server.hf_strategist import _build_messages, strategist_status


class HFStrategistTests(unittest.TestCase):
    def test_build_messages_includes_core_snapshot_fields(self):
        snapshot = {
            "scenario_title": "Rush Hour Cascade",
            "difficulty": "advanced",
            "turn": 2,
            "max_turns": 10,
            "clock_minutes": 10,
            "budget_remaining": 14,
            "verdict": "good",
            "action_headline": "Fairness-Aware Baseline: Dispatch",
            "summary": "3 active incidents, 1 resolved.",
            "incidents": [
                {
                    "id": "INC-3",
                    "title": "Hazmat",
                    "zone": "East",
                    "severity": "4.7",
                    "status": "active",
                    "meta": "Age 0 turns, window 3, resources 1",
                }
            ],
            "resources": [
                {
                    "id": "DRN-1",
                    "type": "Drone",
                    "status": "on_scene",
                    "zone": "East",
                    "meta": "Drone in East",
                }
            ],
            "events": [{"title": "Cascade event", "body": "New incident INC-3"}],
        }

        messages = _build_messages(snapshot)

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Rush Hour Cascade", messages[1]["content"])
        self.assertIn("INC-3", messages[1]["content"])
        self.assertIn("DRN-1", messages[1]["content"])

    def test_status_reports_missing_token(self):
        with patch.dict(os.environ, {"HF_TOKEN": ""}, clear=False), patch(
            "server.hf_strategist.get_token", return_value=None
        ):
            status = strategist_status()

        self.assertFalse(status["configured"])
        self.assertIn("HF_TOKEN", status["message"])


if __name__ == "__main__":
    unittest.main()
