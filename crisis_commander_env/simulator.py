"""Simulation engine for Crisis Commander."""

from __future__ import annotations

from typing import Any
from random import Random

from .grader import grade_episode
from .models import (
    ActionType,
    CrisisAction,
    CrisisObservation,
    CrisisState,
    Difficulty,
    Incident,
    IncidentKind,
    IncidentStatus,
    Resource,
    ResourceKind,
    ResourceStatus,
    ScenarioConfig,
    ScoreBreakdown,
)
from .openenv_compat import Environment, StepResult
from .scenarios import DEFAULT_SCENARIO_ID, get_scenario

DIFFICULTY_MODIFIERS: dict[Difficulty, dict[str, float]] = {
    Difficulty.EASY: {"severity": 0.9, "budget": 4, "horizon": 1},
    Difficulty.STANDARD: {"severity": 1.0, "budget": 0, "horizon": 0},
    Difficulty.ADVANCED: {"severity": 1.12, "budget": -1, "horizon": 0},
    Difficulty.EXPERT: {"severity": 1.25, "budget": -3, "horizon": -1},
}


class CrisisCommanderEnv(Environment[CrisisAction, CrisisObservation]):
    """OpenEnv-style local simulator with `reset()` and `step()` semantics."""

    def __init__(
        self,
        scenario_id: str = DEFAULT_SCENARIO_ID,
        difficulty: Difficulty = Difficulty.ADVANCED,
        step_minutes: int = 5,
    ) -> None:
        self.default_scenario_id = scenario_id
        self.default_difficulty = difficulty
        self.step_minutes = step_minutes
        self._rng = Random(7)
        self.state: CrisisState | None = None

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> StepResult[CrisisObservation]:
        options = options or {}
        if seed is not None:
            self._rng = Random(seed)

        scenario_id = options.get("scenario_id", self.default_scenario_id)
        difficulty = Difficulty(options.get("difficulty", self.default_difficulty.value))
        scenario = self._prepare_scenario(get_scenario(scenario_id), difficulty)

        self.state = CrisisState(
            scenario=scenario,
            difficulty=difficulty,
            turn=0,
            clock_minutes=0,
            max_turns=scenario.horizon,
            budget_remaining=scenario.budget,
            incidents={incident.id: incident for incident in scenario.incidents},
            resources={resource.id: resource for resource in scenario.resources},
            hospitals={hospital.id: hospital for hospital in scenario.hospitals},
            pending_schedule=list(scenario.scheduled_incidents),
        )

        for incident in self.state.incidents.values():
            incident.discovered_turn = 0

        opening = [
            f"Mission '{scenario.title}' initialized.",
            scenario.description,
        ]
        self.state.recent_events = opening
        observation = self._build_observation(opening)
        return StepResult(
            observation=observation,
            reward=0.0,
            done=False,
            info={"scenario": scenario.title, "difficulty": difficulty.value},
        )

    def step(self, action: CrisisAction) -> StepResult[CrisisObservation]:
        state = self._require_state()
        if state.done:
            observation = self._build_observation(["Episode already ended. Reset to start a new mission."])
            return StepResult(
                observation=observation,
                reward=0.0,
                done=True,
                info={"grade": grade_episode(state)},
            )

        events: list[str] = []
        step_score = ScoreBreakdown()
        state.action_history.append(action.summary())

        self._apply_action(action, step_score, events)

        state.turn += 1
        state.clock_minutes += self.step_minutes

        self._spawn_scheduled_incidents(events)
        self._advance_resources(events)
        self._advance_incidents(step_score, events)
        self._apply_fairness_pressure(step_score)

        state.cumulative_score.extend(step_score)
        self._update_done(events)
        state.recent_events = events[-8:] or ["No new events."]

        observation = self._build_observation(state.recent_events)
        return StepResult(
            observation=observation,
            reward=step_score.total(),
            done=state.done,
            info={
                "events": list(state.recent_events),
                "grade": grade_episode(state),
            },
        )

    def _prepare_scenario(self, scenario: ScenarioConfig, difficulty: Difficulty) -> ScenarioConfig:
        modifiers = DIFFICULTY_MODIFIERS[difficulty]
        scenario.budget = max(8, int(scenario.budget + modifiers["budget"]))
        scenario.horizon = max(8, int(scenario.horizon + modifiers["horizon"]))

        for incident in scenario.incidents:
            incident.severity = round(
                max(1.5, (incident.severity * modifiers["severity"]) + self._rng.uniform(-0.15, 0.15)),
                2,
            )
            incident.vulnerability = round(max(0.9, incident.vulnerability + self._rng.uniform(-0.03, 0.06)), 2)

        for scheduled in scenario.scheduled_incidents:
            scheduled.incident.severity = round(
                max(1.5, (scheduled.incident.severity * modifiers["severity"]) + self._rng.uniform(-0.15, 0.15)),
                2,
            )
            scheduled.incident.vulnerability = round(
                max(0.9, scheduled.incident.vulnerability + self._rng.uniform(-0.03, 0.06)),
                2,
            )

        if difficulty == Difficulty.EXPERT:
            scenario.budget = max(8, scenario.budget - 1)
        return scenario

    def _apply_action(self, action: CrisisAction, score: ScoreBreakdown, events: list[str]) -> None:
        if action.action_type == ActionType.WAIT:
            events.append("Command held position for a turn to gather more information.")
            score.foresight_bonus += 0.25
            return

        if action.action_type == ActionType.DISPATCH:
            self._dispatch_resource(action, score, events)
            return

        if action.action_type == ActionType.REROUTE:
            self._reroute_resource(action, score, events)
            return

        if action.action_type == ActionType.STAGE:
            self._stage_resource(action, score, events)
            return

        if action.action_type == ActionType.EXPAND_HOSPITAL:
            self._expand_hospital(action, score, events)
            return

        if action.action_type == ActionType.REQUEST_MUTUAL_AID:
            self._request_mutual_aid(action, score, events)
            return

        self._invalid_action(f"Unsupported action type '{action.action_type.value}'.", score, events)

    def _dispatch_resource(self, action: CrisisAction, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        resource = self._lookup_resource(action.resource_id)
        incident = self._lookup_incident(action.incident_id)
        if resource is None or incident is None:
            self._invalid_action("Dispatch requires a valid resource and active incident.", score, events)
            return
        if resource.status != ResourceStatus.AVAILABLE:
            self._invalid_action(f"{resource.id} is not available for dispatch.", score, events)
            return

        eta = self._travel_time(resource.current_zone, incident.zone)
        resource.status = ResourceStatus.EN_ROUTE
        resource.eta = eta
        resource.assigned_incident = incident.id
        resource.target_zone = incident.zone
        if resource.id not in incident.assigned_resources:
            incident.assigned_resources.append(resource.id)

        state.total_response_delay += eta
        score.response_delay_penalty -= round(eta * incident.severity * 0.45, 3)
        if incident.vulnerability >= 1.15:
            score.foresight_bonus += 1.2
        events.append(f"{resource.id} dispatched from {resource.current_zone} to {incident.id} in {incident.zone} (ETA {eta}).")

    def _reroute_resource(self, action: CrisisAction, score: ScoreBreakdown, events: list[str]) -> None:
        resource = self._lookup_resource(action.resource_id)
        incident = self._lookup_incident(action.incident_id)
        if resource is None or incident is None:
            self._invalid_action("Reroute requires a valid resource and active incident.", score, events)
            return
        if resource.status == ResourceStatus.STAGING:
            self._invalid_action(f"{resource.id} is still moving to its staging zone.", score, events)
            return

        current_incident = self._lookup_incident(resource.assigned_incident) if resource.assigned_incident else None
        if current_incident is not None and resource.id in current_incident.assigned_resources:
            current_incident.assigned_resources.remove(resource.id)

        origin = resource.target_zone if resource.status == ResourceStatus.EN_ROUTE else resource.current_zone
        eta = self._travel_time(origin or resource.current_zone, incident.zone)
        resource.status = ResourceStatus.EN_ROUTE
        resource.eta = eta
        resource.assigned_incident = incident.id
        resource.target_zone = incident.zone
        if resource.id not in incident.assigned_resources:
            incident.assigned_resources.append(resource.id)

        score.response_delay_penalty -= round(eta * 0.75, 3)
        score.resource_efficiency_penalty -= 1.2
        events.append(f"{resource.id} rerouted toward {incident.id}; command trades efficiency for urgency.")

    def _stage_resource(self, action: CrisisAction, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        resource = self._lookup_resource(action.resource_id)
        if resource is None or not action.target_zone:
            self._invalid_action("Stage requires a valid resource and target zone.", score, events)
            return
        if resource.status != ResourceStatus.AVAILABLE:
            self._invalid_action(f"{resource.id} cannot stage while {resource.status.value}.", score, events)
            return
        if action.target_zone not in state.scenario.zones:
            self._invalid_action(f"Unknown staging zone '{action.target_zone}'.", score, events)
            return

        eta = self._travel_time(resource.current_zone, action.target_zone)
        resource.status = ResourceStatus.STAGING
        resource.eta = eta
        resource.target_zone = action.target_zone
        resource.assigned_incident = None

        zone_vulnerability = state.scenario.vulnerability_by_zone.get(action.target_zone, 1.0)
        score.foresight_bonus += round(0.6 + ((zone_vulnerability - 1.0) * 2.0), 3)
        events.append(f"{resource.id} staged toward {action.target_zone} (ETA {eta}) for anticipated spillover.")

    def _expand_hospital(self, action: CrisisAction, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        hospital = state.hospitals.get(action.hospital_id or "")
        if hospital is None:
            self._invalid_action("Expand hospital requires a valid hospital_id.", score, events)
            return
        if state.budget_remaining < 3:
            self._invalid_action("Not enough budget left to expand surge capacity.", score, events)
            return
        if state.turn - hospital.last_expanded_turn < 2:
            self._invalid_action(f"{hospital.id} was expanded too recently.", score, events)
            return

        state.budget_remaining -= 3
        hospital.surge_capacity += 6
        hospital.last_expanded_turn = state.turn
        score.capacity_penalty -= 1.0
        if hospital.utilization >= 0.75:
            score.foresight_bonus += 2.5
        else:
            score.foresight_bonus += 0.75
        events.append(f"{hospital.id} opened 6 surge beds to absorb downstream casualties.")

    def _request_mutual_aid(self, action: CrisisAction, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        if action.resource_kind is None:
            self._invalid_action("Mutual aid requires a resource kind.", score, events)
            return
        if state.budget_remaining < 4:
            self._invalid_action("Not enough budget left to request mutual aid.", score, events)
            return

        counter = sum(1 for resource in state.resources.values() if resource.mutual_aid and resource.kind == action.resource_kind)
        new_id = f"MA-{action.resource_kind.value.upper()}-{counter + 1}"
        target_zone = action.target_zone or state.scenario.zones[0]
        incident = self._lookup_incident(action.incident_id) if action.incident_id else None
        if incident is not None:
            target_zone = incident.zone

        state.resources[new_id] = Resource(
            id=new_id,
            kind=action.resource_kind,
            home_zone=target_zone,
            current_zone=target_zone,
            effectiveness=0.95,
            status=ResourceStatus.EN_ROUTE,
            eta=2,
            assigned_incident=incident.id if incident else None,
            target_zone=target_zone,
            mutual_aid=True,
        )
        if incident is not None:
            incident.assigned_resources.append(new_id)

        state.budget_remaining -= 4
        state.mutual_aid_calls += 1
        score.resource_efficiency_penalty -= 2.5
        events.append(f"Mutual aid requested: {new_id} inbound to {target_zone} (ETA 2).")

    def _spawn_scheduled_incidents(self, events: list[str]) -> None:
        state = self._require_state()
        spawned: list[int] = []
        for idx, scheduled in enumerate(state.pending_schedule):
            if scheduled.turn == state.turn:
                incident = scheduled.incident
                incident.discovered_turn = state.turn
                state.incidents[incident.id] = incident
                events.append(f"New incident {incident.id}: {incident.notes}")
                spawned.append(idx)

        for idx in reversed(spawned):
            state.pending_schedule.pop(idx)

    def _advance_resources(self, events: list[str]) -> None:
        state = self._require_state()
        for resource in state.resources.values():
            if resource.status not in {ResourceStatus.EN_ROUTE, ResourceStatus.STAGING}:
                continue
            resource.eta = max(0, resource.eta - 1)
            if resource.eta > 0:
                continue

            resource.current_zone = resource.target_zone or resource.current_zone
            if resource.assigned_incident:
                incident = state.incidents.get(resource.assigned_incident)
                if incident is not None and incident.status == IncidentStatus.ACTIVE:
                    resource.status = ResourceStatus.ON_SCENE
                    events.append(f"{resource.id} arrived on scene at {incident.id}.")
                    continue
                resource.assigned_incident = None

            resource.status = ResourceStatus.AVAILABLE
            events.append(f"{resource.id} is now available in {resource.current_zone}.")

    def _advance_incidents(self, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        active_incidents = [
            incident for incident in state.incidents.values() if incident.status == IncidentStatus.ACTIVE
        ]
        for incident in active_incidents:
            on_scene = self._resources_on_incident(incident.id)
            coverage = self._coverage(incident, on_scene)
            age = state.turn - incident.discovered_turn
            overdue = max(0, age - incident.response_window)

            stabilization_delta = round(coverage * 1.15, 3)
            harm_delta = round(
                (incident.severity * (1.18 - min(coverage, 1.0)) * 0.8 * incident.vulnerability)
                + (overdue * 0.9)
                + (0.5 if not on_scene else 0.0),
                3,
            )
            harm_delta = max(0.2, harm_delta)

            incident.stabilization += stabilization_delta
            incident.harm += harm_delta
            state.lives_lost += round(harm_delta * 0.45, 3)
            score.harm_penalty -= round(harm_delta * 2.0, 3)
            if coverage >= 0.95:
                score.stabilization_bonus += round(1.75 + (coverage - 0.95) * 2.5, 3)

            resolution_threshold = incident.severity * 1.65
            failure_threshold = max(incident.affected_people * 0.8, incident.severity * 6.5)

            if incident.stabilization >= resolution_threshold:
                self._resolve_incident(incident, score, events)
            elif incident.harm >= failure_threshold:
                self._fail_incident(incident, score, events)

    def _resolve_incident(self, incident: Incident, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        incident.status = IncidentStatus.RESOLVED
        state.resolved_incidents += 1

        stabilized = max(1.0, incident.affected_people - (incident.harm * 0.7))
        state.lives_stabilized += round(stabilized, 2)
        score.resolution_bonus += round(10.0 + (incident.severity * 2.5), 3)
        if state.turn <= incident.discovered_turn + incident.response_window:
            score.foresight_bonus += 3.5

        patients = max(1, int(round((incident.affected_people * 0.25) + incident.severity)))
        overflow = self._admit_patients(incident.zone, patients, score, events)
        incident.admitted_patients = patients - overflow
        self._release_resources(incident.id)
        events.append(
            f"{incident.id} resolved with {max(0, patients - overflow)} patients routed to care."
        )

    def _fail_incident(self, incident: Incident, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        incident.status = IncidentStatus.FAILED
        state.failed_incidents += 1
        score.harm_penalty -= round(8.0 + (incident.severity * 2.5), 3)
        self._release_resources(incident.id)
        events.append(f"{incident.id} tipped into failure; command window was missed.")

    def _admit_patients(self, origin_zone: str, patients: int, score: ScoreBreakdown, events: list[str]) -> int:
        state = self._require_state()
        remaining = patients
        hospitals = sorted(
            state.hospitals.values(),
            key=lambda hospital: (self._travel_time(origin_zone, hospital.zone), hospital.utilization),
        )

        for hospital in hospitals:
            free_beds = hospital.total_capacity - hospital.occupied_beds
            if free_beds <= 0:
                continue
            admitted = min(remaining, free_beds)
            hospital.occupied_beds += admitted
            remaining -= admitted
            events.append(f"{admitted} patients routed to {hospital.id}.")
            if remaining <= 0:
                return 0

        if remaining > 0:
            state.hospital_overflow += remaining
            score.capacity_penalty -= round(remaining * 1.9, 3)
            events.append(f"{remaining} patients overflowed available hospital capacity.")
        return remaining

    def _release_resources(self, incident_id: str) -> None:
        state = self._require_state()
        incident = state.incidents.get(incident_id)
        if incident is not None:
            incident.assigned_resources = []
        for resource in state.resources.values():
            if resource.assigned_incident != incident_id:
                continue
            resource.assigned_incident = None
            resource.status = ResourceStatus.AVAILABLE
            resource.eta = 0
            resource.current_zone = resource.target_zone or resource.current_zone
            resource.target_zone = resource.current_zone

    def _apply_fairness_pressure(self, score: ScoreBreakdown) -> None:
        state = self._require_state()
        penalty = 0.0
        for incident in state.incidents.values():
            if incident.status != IncidentStatus.ACTIVE:
                continue
            age = state.turn - incident.discovered_turn
            if incident.vulnerability >= 1.15 and age > 1:
                penalty += age * 0.7
            if incident.vulnerability >= 1.2 and not self._resources_on_incident(incident.id):
                penalty += 0.8
        if penalty > 0:
            score.fairness_penalty -= round(penalty, 3)

    def _update_done(self, events: list[str]) -> None:
        state = self._require_state()
        active_left = any(incident.status == IncidentStatus.ACTIVE for incident in state.incidents.values())
        if state.turn >= state.max_turns:
            state.done = True
            events.append("Mission clock expired.")
        elif (not active_left) and not state.pending_schedule:
            state.done = True
            events.append("All known incidents stabilized before the mission clock expired.")

    def _coverage(self, incident: Incident, resources: list[Resource]) -> float:
        if not resources:
            return 0.0

        kind_scores = []
        for kind, required in incident.required_resources.items():
            available = sum(resource.effectiveness for resource in resources if resource.kind == kind)
            kind_scores.append(min(1.4, available / max(1, required)))

        base = sum(kind_scores) / max(1, len(kind_scores))
        if incident.kind == IncidentKind.HAZMAT and any(r.kind == ResourceKind.DRONE for r in resources):
            base += 0.15
        if incident.kind == IncidentKind.CROWD_CONTROL and any(
            r.kind == ResourceKind.POLICE_UNIT for r in resources
        ):
            base += 0.15
        if incident.kind == IncidentKind.FIRE and any(r.kind == ResourceKind.AMBULANCE for r in resources):
            base += 0.05
        return round(min(1.5, base), 3)

    def _build_observation(self, alerts: list[str]) -> CrisisObservation:
        state = self._require_state()
        incidents = [
            self._serialize_incident(incident)
            for incident in sorted(
                state.incidents.values(),
                key=lambda incident: (
                    0 if incident.status == IncidentStatus.ACTIVE else 1,
                    -incident.severity,
                    incident.id,
                ),
            )
        ]
        resources = [
            self._serialize_resource(resource)
            for resource in sorted(state.resources.values(), key=lambda resource: resource.id)
        ]
        hospitals = [
            self._serialize_hospital(hospital)
            for hospital in sorted(state.hospitals.values(), key=lambda hospital: hospital.id)
        ]
        active_count = len([incident for incident in state.incidents.values() if incident.status == IncidentStatus.ACTIVE])
        available_count = len(
            [resource for resource in state.resources.values() if resource.status == ResourceStatus.AVAILABLE]
        )

        summary = (
            f"{active_count} active incidents, {state.resolved_incidents} resolved, {available_count} units ready, "
            f"hospital overflow={state.hospital_overflow}."
        )

        return CrisisObservation(
            scenario_id=state.scenario.id,
            mission_brief=f"{state.scenario.title}: {state.scenario.description}",
            turn=state.turn,
            max_turns=state.max_turns,
            clock_minutes=state.clock_minutes,
            budget_remaining=state.budget_remaining,
            summary=summary,
            incidents=incidents,
            resources=resources,
            hospitals=hospitals,
            available_actions=[
                "dispatch(resource_id, incident_id)",
                "reroute(resource_id, incident_id)",
                "stage(resource_id, target_zone)",
                "expand_hospital(hospital_id)",
                "request_mutual_aid(resource_kind, incident_id?)",
                "wait()",
            ],
            objectives=[
                state.scenario.objective,
                "Protect high-vulnerability districts from systematic neglect.",
                "Keep hospital overflow and mutual-aid spend low.",
            ],
            alerts=alerts or ["No new alerts."],
            score_breakdown=state.cumulative_score.as_dict(),
        )

    def _serialize_incident(self, incident: Incident) -> dict[str, Any]:
        return {
            "id": incident.id,
            "kind": incident.kind.value,
            "zone": incident.zone,
            "severity": round(incident.severity, 2),
            "status": incident.status.value,
            "response_window": incident.response_window,
            "age": self._require_state().turn - incident.discovered_turn,
            "vulnerability": incident.vulnerability,
            "stabilization": round(incident.stabilization, 3),
            "harm": round(incident.harm, 3),
            "assigned_resources": list(incident.assigned_resources),
            "required_resources": {kind.value: count for kind, count in incident.required_resources.items()},
            "notes": incident.notes,
        }

    def _serialize_resource(self, resource: Resource) -> dict[str, Any]:
        return {
            "id": resource.id,
            "kind": resource.kind.value,
            "status": resource.status.value,
            "current_zone": resource.current_zone,
            "target_zone": resource.target_zone,
            "eta": resource.eta,
            "assigned_incident": resource.assigned_incident,
            "mutual_aid": resource.mutual_aid,
        }

    def _serialize_hospital(self, hospital) -> dict[str, Any]:
        return {
            "id": hospital.id,
            "zone": hospital.zone,
            "occupied_beds": hospital.occupied_beds,
            "total_capacity": hospital.total_capacity,
            "utilization": hospital.utilization,
        }

    def _resources_on_incident(self, incident_id: str) -> list[Resource]:
        state = self._require_state()
        return [
            resource
            for resource in state.resources.values()
            if resource.assigned_incident == incident_id and resource.status == ResourceStatus.ON_SCENE
        ]

    def _lookup_resource(self, resource_id: str | None) -> Resource | None:
        if resource_id is None:
            return None
        return self._require_state().resources.get(resource_id)

    def _lookup_incident(self, incident_id: str | None) -> Incident | None:
        if incident_id is None:
            return None
        incident = self._require_state().incidents.get(incident_id)
        if incident is None or incident.status != IncidentStatus.ACTIVE:
            return None
        return incident

    def _travel_time(self, origin_zone: str, target_zone: str) -> int:
        scenario = self._require_state().scenario
        zones = scenario.zones
        origin_idx = zones.index(origin_zone)
        target_idx = zones.index(target_zone)
        distance = abs(origin_idx - target_idx)
        wrapped = min(distance, len(zones) - distance)
        return max(1, wrapped + 1)

    def _invalid_action(self, reason: str, score: ScoreBreakdown, events: list[str]) -> None:
        state = self._require_state()
        state.invalid_actions += 1
        score.invalid_action_penalty -= 6.0
        events.append(f"Invalid action: {reason}")

    def _require_state(self) -> CrisisState:
        if self.state is None:
            raise RuntimeError("Environment not initialized. Call reset() before step().")
        return self.state
