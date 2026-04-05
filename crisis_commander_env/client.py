"""Client-facing helpers for local experimentation."""

from __future__ import annotations

from typing import Any

from .models import CrisisAction
from .simulator import CrisisCommanderEnv


class CrisisCommanderEnvClient:
    """
    Lightweight local wrapper with the same `reset()` / `step()` surface judges expect.

    When `openenv-core` is installed, this project can be wired into an official remote
    `EnvClient`. For the hackathon repo, this local wrapper keeps the environment usable
    even before deployment.
    """

    def __init__(self, **env_kwargs: Any) -> None:
        self._env = CrisisCommanderEnv(**env_kwargs)

    def reset(self, seed: int | None = None, options: dict[str, Any] | None = None):
        return self._env.reset(seed=seed, options=options)

    def step(self, action: CrisisAction):
        return self._env.step(action)

    @property
    def state(self):
        return self._env.state

