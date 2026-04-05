"""FastAPI application for Crisis Commander."""

from __future__ import annotations

from crisis_commander_env.models import CrisisAction, CrisisObservation
from crisis_commander_env.scenarios import list_scenarios
from server.crisis_commander_environment import CrisisCommanderEnvironment

try:
    from openenv.core.env_server import create_app  # type: ignore
except ImportError:
    try:
        from openenv.core.env_server.http_server import create_app  # type: ignore
    except ImportError:
        create_app = None

try:
    from fastapi import FastAPI
except ImportError:
    FastAPI = None


if create_app is not None:
    app = create_app(
        CrisisCommanderEnvironment,
        CrisisAction,
        CrisisObservation,
        env_name="crisis_commander_env",
    )
elif FastAPI is not None:
    app = FastAPI(title="Crisis Commander")

    @app.get("/")
    def root():
        return {
            "name": "crisis_commander_env",
            "message": "Install openenv-core to expose the full OpenEnv server surface.",
            "scenarios": list_scenarios(),
        }
else:
    app = None


def main() -> None:
    if app is None:
        raise RuntimeError("Install fastapi and openenv-core to run the server.")

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

