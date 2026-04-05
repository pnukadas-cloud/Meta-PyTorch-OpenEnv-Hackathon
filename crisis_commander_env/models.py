"""Core data models for Crisis Commander."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .openenv_compat import Action, Observation, State


class Difficulty(str, Enum):
    EASY = "easy"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ActionType(str, Enum):
    DISPATCH = "dispatch"
    REROUTE = "reroute"
    STAGE = "stage"
    EXPAND_HOSPITAL = "expand_hospital"
    REQUEST_MUTUAL_AID = "request_mutual_aid"
    WAIT = "wait"


class ResourceKind(str, Enum):
    AMBULANCE = "ambulance"
    FIRE_ENGINE = "fire_engine"
    POLICE_UNIT = "police_unit"
    DRONE = "drone"


class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    STAGING = "staging"


class IncidentKind(str, Enum):
    MEDICAL = "medical"
    FIRE = "fire"
    HAZMAT = "hazmat"
    GRID_FAILURE = "grid_failure"
    CROWD_CONTROL = "crowd_control"


class IncidentStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    FAILED = "failed"


@dataclass
class ScoreBreakdown:
    resolution_bonus: float = 0.0
    stabilization_bonus: float = 0.0
    foresight_bonus: float = 0.0
    harm_penalty: float = 0.0
    response_delay_penalty: float = 0.0
    fairness_penalty: float = 0.0
    capacity_penalty: float = 0.0
    resource_efficiency_penalty: float = 0.0
    invalid_action_penalty: float = 0.0

    def total(self) -> float:
        return round(
            self.resolution_bonus
            + self.stabilization_bonus
            + self.foresight_bonus
            + self.harm_penalty
            + self.response_delay_penalty
            + self.fairness_penalty
            + self.capacity_penalty
            + self.resource_efficiency_penalty
            + self.invalid_action_penalty,
            3,
        )

    def extend(self, other: "ScoreBreakdown") -> None:
        self.resolution_bonus += other.resolution_bonus
        self.stabilization_bonus += other.stabilization_bonus
        self.foresight_bonus += other.foresight_bonus
        self.harm_penalty += other.harm_penalty
        self.response_delay_penalty += other.response_delay_penalty
        self.fairness_penalty += other.fairness_penalty
        self.capacity_penalty += other.capacity_penalty
        self.resource_efficiency_penalty += other.resource_efficiency_penalty
        self.invalid_action_penalty += other.invalid_action_penalty

    def as_dict(self) -> dict[str, float]:
        return {
            "resolution_bonus": round(self.resolution_bonus, 3),
            "stabilization_bonus": round(self.stabilization_bonus, 3),
            "foresight_bonus": round(self.foresight_bonus, 3),
            "harm_penalty": round(self.harm_penalty, 3),
            "response_delay_penalty": round(self.response_delay_penalty, 3),
            "fairness_penalty": round(self.fairness_penalty, 3),
            "capacity_penalty": round(self.capacity_penalty, 3),
            "resource_efficiency_penalty": round(self.resource_efficiency_penalty, 3),
            "invalid_action_penalty": round(self.invalid_action_penalty, 3),
            "total": self.total(),
        }


@dataclass
class Incident:
    id: str
    kind: IncidentKind
    zone: str
    severity: float
    response_window: int
    affected_people: int
    vulnerability: float
    required_resources: dict[ResourceKind, int]
    notes: str
    discovered_turn: int = 0
    stabilization: float = 0.0
    harm: float = 0.0
    status: IncidentStatus = IncidentStatus.ACTIVE
    assigned_resources: list[str] = field(default_factory=list)
    admitted_patients: int = 0


@dataclass
class Resource:
    id: str
    kind: ResourceKind
    home_zone: str
    current_zone: str
    effectiveness: float = 1.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    eta: int = 0
    assigned_incident: str | None = None
    target_zone: str | None = None
    mutual_aid: bool = False


@dataclass
class Hospital:
    id: str
    zone: str
    base_capacity: int
    occupied_beds: int = 0
    surge_capacity: int = 0
    last_expanded_turn: int = -99

    @property
    def total_capacity(self) -> int:
        return self.base_capacity + self.surge_capacity

    @property
    def utilization(self) -> float:
        if self.total_capacity == 0:
            return 1.0
        return round(self.occupied_beds / self.total_capacity, 3)


@dataclass
class ScheduledIncident:
    turn: int
    incident: Incident


@dataclass
class ScenarioConfig:
    id: str
    title: str
    description: str
    objective: str
    horizon: int
    budget: int
    zones: list[str]
    vulnerability_by_zone: dict[str, float]
    resources: list[Resource]
    hospitals: list[Hospital]
    incidents: list[Incident]
    scheduled_incidents: list[ScheduledIncident]
    submission_story: str


@dataclass
class CrisisAction(Action):
    action_type: ActionType
    resource_id: str | None = None
    incident_id: str | None = None
    target_zone: str | None = None
    hospital_id: str | None = None
    resource_kind: ResourceKind | None = None
    notes: str = ""

    @classmethod
    def wait(cls, notes: str = "") -> "CrisisAction":
        return cls(action_type=ActionType.WAIT, notes=notes)

    def summary(self) -> str:
        payload = [
            self.action_type.value,
            self.resource_id or "-",
            self.incident_id or "-",
            self.target_zone or "-",
            self.hospital_id or "-",
            self.resource_kind.value if self.resource_kind else "-",
        ]
        return " | ".join(payload)


@dataclass
class CrisisObservation(Observation):
    scenario_id: str
    mission_brief: str
    turn: int
    max_turns: int
    clock_minutes: int
    budget_remaining: int
    summary: str
    incidents: list[dict[str, Any]]
    resources: list[dict[str, Any]]
    hospitals: list[dict[str, Any]]
    available_actions: list[str]
    objectives: list[str]
    alerts: list[str]
    score_breakdown: dict[str, float]

    @property
    def text(self) -> str:
        lines = [
            self.mission_brief,
            f"Turn {self.turn}/{self.max_turns} | Clock {self.clock_minutes} min | Budget {self.budget_remaining}",
            self.summary,
            "Alerts:",
        ]
        lines.extend(f"- {alert}" for alert in self.alerts)
        lines.append("Active incidents:")
        lines.extend(
            f"- {incident['id']} in {incident['zone']} severity={incident['severity']} status={incident['status']}"
            for incident in self.incidents
        )
        return "\n".join(lines)


@dataclass
class CrisisState(State):
    scenario: ScenarioConfig
    difficulty: Difficulty
    turn: int
    clock_minutes: int
    max_turns: int
    budget_remaining: int
    incidents: dict[str, Incident]
    resources: dict[str, Resource]
    hospitals: dict[str, Hospital]
    pending_schedule: list[ScheduledIncident]
    cumulative_score: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    resolved_incidents: int = 0
    failed_incidents: int = 0
    total_response_delay: float = 0.0
    lives_lost: float = 0.0
    lives_stabilized: float = 0.0
    invalid_actions: int = 0
    mutual_aid_calls: int = 0
    hospital_overflow: int = 0
    action_history: list[str] = field(default_factory=list)
    recent_events: list[str] = field(default_factory=list)
    done: bool = False

