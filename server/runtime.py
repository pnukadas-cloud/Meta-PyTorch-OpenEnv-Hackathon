"""Session and serialization helpers for the command-center UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from crisis_commander_env.baselines import fairness_aware_policy, severity_first_policy
from crisis_commander_env.grader import grade_episode
from crisis_commander_env.models import CrisisAction, CrisisState, Difficulty, IncidentStatus
from crisis_commander_env.scenarios import DEFAULT_SCENARIO_ID, SCENARIOS
from server.crisis_commander_environment import CrisisCommanderEnvironment

PolicyFactory = Callable[[CrisisState], CrisisAction]


POLICIES: dict[str, tuple[str, PolicyFactory]] = {
    "fairness_aware": ("Fairness-Aware Baseline", fairness_aware_policy),
    "severity_first": ("Severity-First Baseline", severity_first_policy),
}


@dataclass
class SessionRecord:
    session_id: str
    env: CrisisCommanderEnvironment
    scenario_id: str
    difficulty: str
    seed: int
    policy: str
    latest_snapshot: dict | None = None


SESSIONS: dict[str, SessionRecord] = {}


def build_manifest() -> dict:
    scenarios = []
    for scenario_id, scenario in SCENARIOS.items():
        scenarios.append(
            {
                "id": scenario_id,
                "label": scenario.title,
                "title": scenario.title,
                "description": scenario.description,
                "objective": scenario.objective,
                "budget": scenario.budget,
                "horizon": scenario.horizon,
                "zones": list(scenario.zones),
            }
        )

    return {
        "name": "crisis_commander_env",
        "default_scenario": DEFAULT_SCENARIO_ID,
        "default_difficulty": Difficulty.ADVANCED.value,
        "scenarios": scenarios,
        "difficulties": [difficulty.value for difficulty in Difficulty],
        "policies": [
            {"id": policy_id, "label": label}
            for policy_id, (label, _) in POLICIES.items()
        ],
    }


def create_session(
    scenario_id: str = DEFAULT_SCENARIO_ID,
    difficulty: str = Difficulty.ADVANCED.value,
    seed: int = 7,
    policy: str = "fairness_aware",
) -> dict:
    env = CrisisCommanderEnvironment(
        scenario_id=scenario_id,
        difficulty=Difficulty(difficulty),
    )
    result = env.reset(
        seed=seed,
        options={"scenario_id": scenario_id, "difficulty": difficulty},
    )

    session_id = str(uuid4())
    record = SessionRecord(
        session_id=session_id,
        env=env,
        scenario_id=scenario_id,
        difficulty=difficulty,
        seed=seed,
        policy=policy,
    )
    snapshot = build_snapshot(
        record=record,
        result=result,
        action=None,
        action_source="Mission initialization",
        step_reward=0.0,
    )
    record.latest_snapshot = snapshot
    SESSIONS[session_id] = record
    return {
        "session_id": session_id,
        "snapshot": snapshot,
    }


def step_session(session_id: str, policy: str | None = None) -> dict:
    record = require_session(session_id)
    policy_id = policy or record.policy
    if policy_id not in POLICIES:
        raise KeyError(f"Unknown policy '{policy_id}'. Available: {', '.join(sorted(POLICIES))}")

    state = record.env.state
    if state is None:
        raise RuntimeError("Session has no initialized environment.")

    if state.done and record.latest_snapshot is not None:
        return record.latest_snapshot

    record.policy = policy_id
    policy_label, policy_factory = POLICIES[policy_id]
    action = policy_factory(state)
    result = record.env.step(action)

    snapshot = build_snapshot(
        record=record,
        result=result,
        action=action,
        action_source=policy_label,
        step_reward=result.reward,
    )
    record.latest_snapshot = snapshot
    return snapshot


def require_session(session_id: str) -> SessionRecord:
    if session_id not in SESSIONS:
        raise KeyError(f"Unknown session '{session_id}'.")
    return SESSIONS[session_id]


def build_snapshot(
    record: SessionRecord,
    result,
    action: CrisisAction | None,
    action_source: str,
    step_reward: float,
) -> dict:
    state = record.env.state
    if state is None:
        raise RuntimeError("Environment state missing during snapshot serialization.")

    observation = result.observation
    grade = result.info.get("grade") if isinstance(result.info, dict) else None
    if not grade:
        grade = grade_episode(state)

    return {
        "session_id": record.session_id,
        "scenario_id": state.scenario.id,
        "scenario_title": state.scenario.title,
        "scenario_description": state.scenario.description,
        "scenario_objective": state.scenario.objective,
        "difficulty": record.difficulty,
        "seed": record.seed,
        "policy": record.policy,
        "policy_label": POLICIES[record.policy][0],
        "turn": state.turn,
        "max_turns": state.max_turns,
        "clock_minutes": state.clock_minutes,
        "budget_remaining": state.budget_remaining,
        "summary": observation.summary,
        "done": state.done,
        "step_reward": round(step_reward, 3),
        "reward_total": state.cumulative_score.total(),
        "reward_signals": _serialize_reward_signals(state),
        "verdict": grade["verdict"],
        "grade": grade["dimension_scores"],
        "metrics": {
            "resolved": state.resolved_incidents,
            "failed": state.failed_incidents,
            "lives_lost": round(state.lives_lost, 2),
            "lives_stabilized": round(state.lives_stabilized, 2),
            "hospital_overflow": state.hospital_overflow,
        },
        "action_headline": _action_headline(action, action_source),
        "action_notes": _action_notes(action, result.info.get("events", []), state),
        "incidents": _serialize_incidents(observation.incidents),
        "resources": _serialize_resources(observation.resources, observation.hospitals),
        "events": _serialize_events(action, result.info.get("events", [])),
        "zones": list(state.scenario.zones),
    }


def _serialize_reward_signals(state: CrisisState) -> list[dict]:
    score = state.cumulative_score
    return [
        _bar("Resolution", score.resolution_bonus, positive=True, scale=4.0),
        _bar("Stabilization", score.stabilization_bonus, positive=True, scale=5.0),
        _bar("Foresight", score.foresight_bonus, positive=True, scale=5.0),
        _bar("Fairness", score.fairness_penalty, positive=False, scale=10.0),
        _bar("Capacity", score.capacity_penalty, positive=False, scale=10.0),
    ]


def _bar(label: str, value: float, positive: bool, scale: float) -> dict:
    if positive:
        percent = max(8, min(100, int(abs(value) * scale) + 12))
    else:
        percent = max(8, min(100, 100 - int(abs(value) * scale)))
    return {
        "label": label,
        "percent": percent,
        "value": f"{value:+.1f}",
    }


def _serialize_incidents(incidents: list[dict]) -> list[dict]:
    serialized = []
    for incident in incidents:
        status = incident["status"]
        severity = float(incident["severity"])
        if status == IncidentStatus.RESOLVED.value:
            tone = "stable"
        elif status == IncidentStatus.FAILED.value or severity >= 4.2:
            tone = "critical"
        else:
            tone = "warning"

        serialized.append(
            {
                "id": incident["id"],
                "title": _title_case(incident["kind"]),
                "zone": incident["zone"],
                "severity": f"{severity:.1f}",
                "status": status,
                "tone": tone,
                "meta": (
                    f"Age {incident['age']} turns, window {incident['response_window']}, "
                    f"resources {max(0, len(incident['assigned_resources']))}"
                ),
            }
        )
    return serialized


def _serialize_resources(resources: list[dict], hospitals: list[dict]) -> list[dict]:
    serialized = []
    for resource in resources:
        zone = resource["target_zone"] or resource["current_zone"]
        meta = f"{resource['kind'].replace('_', ' ').title()} in {zone}"
        if resource["eta"]:
            meta = f"{meta}, ETA {resource['eta']}"
        serialized.append(
            {
                "id": resource["id"],
                "type": resource["kind"].replace("_", " ").title(),
                "status": resource["status"],
                "zone": zone,
                "meta": meta,
            }
        )

    for hospital in hospitals:
        utilization = float(hospital["utilization"]) * 100
        status = "surge open" if hospital["total_capacity"] > hospital["occupied_beds"] and utilization > 75 else "stable"
        serialized.append(
            {
                "id": hospital["id"],
                "type": "Hospital",
                "status": status,
                "zone": hospital["zone"],
                "meta": f"{hospital['occupied_beds']}/{hospital['total_capacity']} beds in use ({utilization:.0f}% utilized)",
            }
        )
    return serialized


def _serialize_events(action: CrisisAction | None, events: list[str]) -> list[dict]:
    payload = []
    if action is not None:
        payload.append(
            {
                "title": "Policy action",
                "body": action.summary(),
            }
        )

    for event in events or ["No new operational events recorded."]:
        payload.append(
            {
                "title": _event_title(event),
                "body": event,
            }
        )
    return payload


def _action_headline(action: CrisisAction | None, action_source: str) -> str:
    if action is None:
        return action_source
    return f"{action_source}: {action.action_type.value.replace('_', ' ').title()}"


def _action_notes(action: CrisisAction | None, events: list[str], state: CrisisState) -> str:
    if action is not None and action.notes:
        return action.notes
    if events:
        return events[0]
    return state.scenario.objective


def _event_title(event: str) -> str:
    lowered = event.lower()
    if "resolved" in lowered:
        return "Incident resolved"
    if "invalid action" in lowered:
        return "Invalid action"
    if "mission" in lowered:
        return "Mission update"
    if "new incident" in lowered:
        return "Cascade event"
    if "overflow" in lowered:
        return "Capacity warning"
    return "Ops update"


def _title_case(value: str) -> str:
    return value.replace("_", " ").title()
