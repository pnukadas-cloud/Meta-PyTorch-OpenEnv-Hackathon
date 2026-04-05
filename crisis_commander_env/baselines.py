"""Baseline heuristics for showcasing the environment."""

from __future__ import annotations

from .models import ActionType, CrisisAction, CrisisState, IncidentStatus, ResourceKind, ResourceStatus


def severity_first_policy(state: CrisisState) -> CrisisAction:
    active_incidents = sorted(
        [incident for incident in state.incidents.values() if incident.status == IncidentStatus.ACTIVE],
        key=lambda incident: (-incident.severity, incident.response_window, incident.id),
    )
    available_resources = [resource for resource in state.resources.values() if resource.status == ResourceStatus.AVAILABLE]

    for incident in active_incidents:
        for kind in incident.required_resources:
            for resource in available_resources:
                if resource.kind == kind:
                    return CrisisAction(
                        action_type=ActionType.DISPATCH,
                        resource_id=resource.id,
                        incident_id=incident.id,
                        notes="Greedy severity-first dispatch.",
                    )

    if any(hospital.utilization >= 0.85 for hospital in state.hospitals.values()) and state.budget_remaining >= 3:
        hospital = max(state.hospitals.values(), key=lambda item: item.utilization)
        return CrisisAction(action_type=ActionType.EXPAND_HOSPITAL, hospital_id=hospital.id)

    return CrisisAction.wait("No matching dispatch available.")


def fairness_aware_policy(state: CrisisState) -> CrisisAction:
    active_incidents = sorted(
        [incident for incident in state.incidents.values() if incident.status == IncidentStatus.ACTIVE],
        key=lambda incident: (
            -(incident.severity * incident.vulnerability),
            incident.response_window,
            incident.id,
        ),
    )
    available_resources = [resource for resource in state.resources.values() if resource.status == ResourceStatus.AVAILABLE]

    for incident in active_incidents:
        candidate = _best_matching_resource(available_resources, incident.required_resources)
        if candidate is not None:
            return CrisisAction(
                action_type=ActionType.DISPATCH,
                resource_id=candidate.id,
                incident_id=incident.id,
                notes="Fairness-aware dispatch.",
            )

    vulnerable_zones = [
        zone
        for zone, vulnerability in state.scenario.vulnerability_by_zone.items()
        if vulnerability >= 1.15
    ]
    for resource in available_resources:
        if resource.kind in {ResourceKind.AMBULANCE, ResourceKind.POLICE_UNIT} and vulnerable_zones:
            return CrisisAction(
                action_type=ActionType.STAGE,
                resource_id=resource.id,
                target_zone=vulnerable_zones[0],
                notes="Pre-stage near vulnerable zone.",
            )

    if state.budget_remaining >= 4 and active_incidents:
        top_incident = active_incidents[0]
        missing_kind = next(iter(top_incident.required_resources.keys()))
        return CrisisAction(
            action_type=ActionType.REQUEST_MUTUAL_AID,
            resource_kind=missing_kind,
            incident_id=top_incident.id,
            notes="Patch a high-risk coverage gap.",
        )

    return CrisisAction.wait("No fairness-improving move found.")


def _best_matching_resource(available_resources, required_resources):
    for kind in required_resources:
        for resource in available_resources:
            if resource.kind == kind:
                return resource
    return available_resources[0] if available_resources else None

