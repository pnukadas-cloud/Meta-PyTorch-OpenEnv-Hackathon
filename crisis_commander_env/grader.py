"""Episode grading helpers."""

from __future__ import annotations

from typing import Any

from .models import CrisisState, IncidentStatus


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return round(max(lower, min(upper, value)), 2)


def grade_episode(state: CrisisState) -> dict[str, Any]:
    total_incidents = len(state.incidents)
    active_left = len(
        [incident for incident in state.incidents.values() if incident.status == IncidentStatus.ACTIVE]
    )
    avg_delay = state.total_response_delay / max(1, len(state.action_history))
    avg_hospital_pressure = sum(h.utilization for h in state.hospitals.values()) / max(1, len(state.hospitals))

    high_vulnerability_harm = 0.0
    low_vulnerability_harm = 0.0
    high_count = 0
    low_count = 0
    for incident in state.incidents.values():
        if incident.vulnerability >= 1.15:
            high_vulnerability_harm += incident.harm
            high_count += 1
        else:
            low_vulnerability_harm += incident.harm
            low_count += 1

    fairness_gap = (high_vulnerability_harm / max(1, high_count)) - (
        low_vulnerability_harm / max(1, low_count)
    )

    outcome = _clamp(100 - (state.lives_lost * 3.6) - (active_left * 8) - (state.failed_incidents * 10))
    timeliness = _clamp(100 - (avg_delay * 12))
    fairness = _clamp(100 - (fairness_gap * 18) - (state.hospital_overflow * 5))
    efficiency = _clamp(100 - (state.mutual_aid_calls * 7) - (state.invalid_actions * 10))
    resilience = _clamp(
        55
        + (state.resolved_incidents * 6)
        - (avg_hospital_pressure * 25)
        - (state.failed_incidents * 8)
    )

    final_score = round(
        (outcome * 0.35)
        + (timeliness * 0.2)
        + (fairness * 0.2)
        + (efficiency * 0.1)
        + (resilience * 0.15),
        2,
    )

    return {
        "scenario": state.scenario.title,
        "difficulty": state.difficulty.value,
        "resolved_incidents": state.resolved_incidents,
        "failed_incidents": state.failed_incidents,
        "total_incidents": total_incidents,
        "lives_lost": round(state.lives_lost, 2),
        "lives_stabilized": round(state.lives_stabilized, 2),
        "remaining_budget": state.budget_remaining,
        "hospital_overflow": state.hospital_overflow,
        "dimension_scores": {
            "outcome": outcome,
            "timeliness": timeliness,
            "fairness": fairness,
            "efficiency": efficiency,
            "resilience": resilience,
        },
        "openenv_reward_total": state.cumulative_score.total(),
        "final_score": final_score,
        "verdict": _verdict(final_score),
    }


def _verdict(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 72:
        return "good"
    if score >= 60:
        return "fair"
    return "poor"
