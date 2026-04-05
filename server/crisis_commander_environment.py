"""Server-side environment entrypoint."""

from crisis_commander_env.simulator import CrisisCommanderEnv


class CrisisCommanderEnvironment(CrisisCommanderEnv):
    """Thin alias used by the HTTP server."""

