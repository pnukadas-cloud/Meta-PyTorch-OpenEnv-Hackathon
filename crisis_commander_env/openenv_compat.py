"""Small compatibility shim so the project remains readable without OpenEnv installed."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

ActT = TypeVar("ActT")
ObsT = TypeVar("ObsT")

try:
    from openenv.core import Action, Environment, Observation, State, StepResult
except ImportError:
    class Action:
        """Fallback marker class for actions."""

    class Observation:
        """Fallback marker class for observations."""

    class State:
        """Fallback marker class for state."""

    @dataclass
    class StepResult(Generic[ObsT]):
        observation: ObsT
        reward: float
        done: bool
        info: dict[str, Any] = field(default_factory=dict)

    class Environment(Generic[ActT, ObsT]):
        """Minimal interface matching the parts of OpenEnv this repo relies on."""

        def reset(self, *args: Any, **kwargs: Any) -> StepResult[ObsT]:
            raise NotImplementedError

        def step(self, action: ActT) -> StepResult[ObsT]:
            raise NotImplementedError

