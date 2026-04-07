"""Scenario bank for Crisis Commander."""

from __future__ import annotations

from copy import deepcopy

from .models import (
    Hospital,
    Incident,
    IncidentKind,
    Resource,
    ResourceKind,
    ScenarioConfig,
    ScheduledIncident,
)

DEFAULT_SCENARIO_ID = "rush_hour_cascade"


def _incident(
    incident_id: str,
    kind: IncidentKind,
    zone: str,
    severity: float,
    window: int,
    affected_people: int,
    vulnerability: float,
    required: dict[ResourceKind, int],
    notes: str,
) -> Incident:
    return Incident(
        id=incident_id,
        kind=kind,
        zone=zone,
        severity=severity,
        response_window=window,
        affected_people=affected_people,
        vulnerability=vulnerability,
        required_resources=required,
        notes=notes,
    )


def _resource(resource_id: str, kind: ResourceKind, zone: str, effectiveness: float = 1.0) -> Resource:
    return Resource(
        id=resource_id,
        kind=kind,
        home_zone=zone,
        current_zone=zone,
        effectiveness=effectiveness,
    )


SCENARIOS: dict[str, ScenarioConfig] = {
    "rush_hour_cascade": ScenarioConfig(
        id="rush_hour_cascade",
        title="Rush Hour Cascade",
        description=(
            "A dense city center suffers a multi-site commuter collapse: a bus crash, a warehouse fire, "
            "and a late-arriving hazmat plume that stretches limited responders."
        ),
        objective="Keep casualties low while containing the cascade before hospitals overflow.",
        horizon=10,
        budget=18,
        zones=["North", "East", "South", "West", "Central"],
        vulnerability_by_zone={
            "North": 0.95,
            "East": 1.0,
            "South": 1.2,
            "West": 1.05,
            "Central": 1.1,
        },
        resources=[
            _resource("AMB-1", ResourceKind.AMBULANCE, "North", 1.0),
            _resource("AMB-2", ResourceKind.AMBULANCE, "East", 1.0),
            _resource("FIRE-1", ResourceKind.FIRE_ENGINE, "Central", 1.2),
            _resource("FIRE-2", ResourceKind.FIRE_ENGINE, "West", 1.0),
            _resource("POL-1", ResourceKind.POLICE_UNIT, "Central", 1.0),
            _resource("POL-2", ResourceKind.POLICE_UNIT, "South", 0.95),
            _resource("DRN-1", ResourceKind.DRONE, "Central", 1.15),
        ],
        hospitals=[
            Hospital(id="HOSP-CENTRAL", zone="Central", base_capacity=24),
            Hospital(id="HOSP-EAST", zone="East", base_capacity=16),
        ],
        incidents=[
            _incident(
                "INC-1",
                IncidentKind.MEDICAL,
                "Central",
                severity=4.4,
                window=3,
                affected_people=22,
                vulnerability=1.15,
                required={
                    ResourceKind.AMBULANCE: 1,
                    ResourceKind.POLICE_UNIT: 1,
                },
                notes="Bus crash with multiple critical injuries near the metro hub.",
            ),
            _incident(
                "INC-2",
                IncidentKind.FIRE,
                "West",
                severity=3.8,
                window=4,
                affected_people=14,
                vulnerability=1.0,
                required={
                    ResourceKind.FIRE_ENGINE: 1,
                    ResourceKind.AMBULANCE: 1,
                },
                notes="Warehouse blaze threatens nearby apartments.",
            ),
        ],
        scheduled_incidents=[
            ScheduledIncident(
                turn=2,
                incident=_incident(
                    "INC-3",
                    IncidentKind.HAZMAT,
                    "East",
                    severity=4.6,
                    window=3,
                    affected_people=20,
                    vulnerability=1.05,
                    required={
                        ResourceKind.FIRE_ENGINE: 1,
                        ResourceKind.POLICE_UNIT: 1,
                        ResourceKind.DRONE: 1,
                    },
                    notes="Chemical leak from a logistics yard with uncertain plume direction.",
                ),
            ),
            ScheduledIncident(
                turn=4,
                incident=_incident(
                    "INC-4",
                    IncidentKind.GRID_FAILURE,
                    "South",
                    severity=3.0,
                    window=2,
                    affected_people=10,
                    vulnerability=1.25,
                    required={
                        ResourceKind.POLICE_UNIT: 1,
                        ResourceKind.DRONE: 1,
                    },
                    notes="Substation failure knocks out signals in a high-vulnerability district.",
                ),
            ),
        ],
    ),
    "festival_blackout": ScenarioConfig(
        id="festival_blackout",
        title="Festival Blackout",
        description=(
            "A citywide festival turns dangerous when a stage fire, a crowd surge, and a district blackout land within "
            "minutes of each other."
        ),
        objective="Protect the crowd, route patients fast, and prevent a panic feedback loop.",
        horizon=11,
        budget=20,
        zones=["Arena", "OldTown", "Riverfront", "South", "Central"],
        vulnerability_by_zone={
            "Arena": 1.15,
            "OldTown": 1.05,
            "Riverfront": 1.1,
            "South": 1.3,
            "Central": 1.0,
        },
        resources=[
            _resource("AMB-1", ResourceKind.AMBULANCE, "Central", 1.0),
            _resource("AMB-2", ResourceKind.AMBULANCE, "South", 1.0),
            _resource("AMB-3", ResourceKind.AMBULANCE, "Arena", 1.05),
            _resource("FIRE-1", ResourceKind.FIRE_ENGINE, "Central", 1.15),
            _resource("FIRE-2", ResourceKind.FIRE_ENGINE, "Riverfront", 1.0),
            _resource("POL-1", ResourceKind.POLICE_UNIT, "Arena", 1.1),
            _resource("POL-2", ResourceKind.POLICE_UNIT, "South", 1.0),
            _resource("DRN-1", ResourceKind.DRONE, "Central", 1.2),
        ],
        hospitals=[
            Hospital(id="HOSP-ARENA", zone="Arena", base_capacity=18),
            Hospital(id="HOSP-SOUTH", zone="South", base_capacity=14),
        ],
        incidents=[
            _incident(
                "FEST-1",
                IncidentKind.CROWD_CONTROL,
                "Arena",
                severity=4.7,
                window=2,
                affected_people=30,
                vulnerability=1.15,
                required={
                    ResourceKind.POLICE_UNIT: 1,
                    ResourceKind.AMBULANCE: 1,
                },
                notes="Crowd surge near the main stage after power fluctuations.",
            ),
            _incident(
                "FEST-2",
                IncidentKind.FIRE,
                "Riverfront",
                severity=3.9,
                window=3,
                affected_people=12,
                vulnerability=1.05,
                required={
                    ResourceKind.FIRE_ENGINE: 1,
                    ResourceKind.AMBULANCE: 1,
                },
                notes="Food court transformer fire close to vendor fuel storage.",
            ),
        ],
        scheduled_incidents=[
            ScheduledIncident(
                turn=3,
                incident=_incident(
                    "FEST-3",
                    IncidentKind.GRID_FAILURE,
                    "South",
                    severity=3.8,
                    window=2,
                    affected_people=16,
                    vulnerability=1.35,
                    required={
                        ResourceKind.POLICE_UNIT: 1,
                        ResourceKind.DRONE: 1,
                    },
                    notes="Blackout hits underserved neighborhoods, freezing traffic signals.",
                ),
            ),
        ],
    ),
    "industrial_storm": ScenarioConfig(
        id="industrial_storm",
        title="Industrial Storm",
        description=(
            "A severe storm compounds an industrial accident, producing fires, roadway blockages, and scattered medical calls."
        ),
        objective="Balance immediate containment with medium-term system resilience.",
        horizon=12,
        budget=19,
        zones=["Port", "North", "South", "Industrial", "Central"],
        vulnerability_by_zone={
            "Port": 1.0,
            "North": 1.05,
            "South": 1.2,
            "Industrial": 1.1,
            "Central": 1.0,
        },
        resources=[
            _resource("AMB-1", ResourceKind.AMBULANCE, "Central", 1.0),
            _resource("AMB-2", ResourceKind.AMBULANCE, "Port", 1.0),
            _resource("FIRE-1", ResourceKind.FIRE_ENGINE, "Industrial", 1.25),
            _resource("FIRE-2", ResourceKind.FIRE_ENGINE, "Central", 1.05),
            _resource("POL-1", ResourceKind.POLICE_UNIT, "North", 1.0),
            _resource("POL-2", ResourceKind.POLICE_UNIT, "South", 1.0),
            _resource("DRN-1", ResourceKind.DRONE, "Port", 1.2),
            _resource("DRN-2", ResourceKind.DRONE, "Central", 1.05),
        ],
        hospitals=[
            Hospital(id="HOSP-CENTRAL", zone="Central", base_capacity=20),
            Hospital(id="HOSP-SOUTH", zone="South", base_capacity=15),
        ],
        incidents=[
            _incident(
                "STORM-1",
                IncidentKind.HAZMAT,
                "Industrial",
                severity=4.8,
                window=3,
                affected_people=18,
                vulnerability=1.1,
                required={
                    ResourceKind.FIRE_ENGINE: 1,
                    ResourceKind.DRONE: 1,
                    ResourceKind.POLICE_UNIT: 1,
                },
                notes="Storm damage ruptures a storage line in the industrial corridor.",
            )
        ],
        scheduled_incidents=[
            ScheduledIncident(
                turn=2,
                incident=_incident(
                    "STORM-2",
                    IncidentKind.MEDICAL,
                    "South",
                    severity=3.7,
                    window=2,
                    affected_people=15,
                    vulnerability=1.3,
                    required={
                        ResourceKind.AMBULANCE: 1,
                        ResourceKind.POLICE_UNIT: 1,
                    },
                    notes="Flooded underpass causes a multi-vehicle pileup in the south district.",
                ),
            ),
            ScheduledIncident(
                turn=5,
                incident=_incident(
                    "STORM-3",
                    IncidentKind.FIRE,
                    "Port",
                    severity=4.1,
                    window=3,
                    affected_people=13,
                    vulnerability=1.0,
                    required={
                        ResourceKind.FIRE_ENGINE: 1,
                        ResourceKind.AMBULANCE: 1,
                    },
                    notes="Lightning strike ignites stacked containers at the port.",
                ),
            ),
        ],
    ),
}


def list_scenarios() -> list[str]:
    return list(SCENARIOS.keys())


def get_scenario(scenario_id: str) -> ScenarioConfig:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"Unknown scenario '{scenario_id}'. Available: {', '.join(sorted(SCENARIOS))}")
    return deepcopy(SCENARIOS[scenario_id])
