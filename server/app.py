"""FastAPI application for Crisis Commander."""

from __future__ import annotations

import os
import argparse
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from crisis_commander_env.models import CrisisAction, CrisisObservation, CrisisState, Difficulty
from server.crisis_commander_environment import CrisisCommanderEnvironment
from server.runtime import build_manifest, create_session, require_session, step_session

try:
    from fastapi import Body, FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
except ImportError:
    Body = None
    FastAPI = None
    HTTPException = None
    CORSMiddleware = None
    FileResponse = None
    StaticFiles = None
    BaseModel = object


ROOT_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT_DIR / "index.html"
ADMIN_LOGIN_FILE = ROOT_DIR / "admin-login.html"
USER_LOGIN_FILE = ROOT_DIR / "user-login.html"
STATIC_DIR = ROOT_DIR / "static"
OPENENV_ENVS: dict[str, CrisisCommanderEnvironment] = {}


class CreateSessionRequest(BaseModel):
    scenario_id: str = "rush_hour_cascade"
    difficulty: str = "advanced"
    seed: int = 7
    policy: str = "fairness_aware"


class StepSessionRequest(BaseModel):
    policy: str | None = None


def _serialize_value(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _serialize_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    return value


def _serialize_step_result(result, episode_id: str) -> dict[str, Any]:
    return {
        "episode_id": episode_id,
        "observation": _serialize_value(result.observation),
        "reward": result.reward,
        "done": result.done,
        "info": _serialize_value(getattr(result, "info", {})),
    }


def _schema_for_dataclass(model_type: type) -> dict[str, Any]:
    return {
        "name": model_type.__name__,
        "fields": [
            {
                "name": field.name,
                "type": str(field.type),
            }
            for field in fields(model_type)
        ],
    }


def _get_or_create_openenv_env(episode_id: str) -> CrisisCommanderEnvironment:
    if episode_id not in OPENENV_ENVS:
        OPENENV_ENVS[episode_id] = CrisisCommanderEnvironment()
    return OPENENV_ENVS[episode_id]


def _build_app():
    if FastAPI is None:
        return None

    app = FastAPI(title="Crisis Commander")

    if CORSMiddleware is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if StaticFiles is not None and STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.post("/reset")
    def openenv_reset(payload: dict[str, Any] = Body(default_factory=dict)):
        episode_id = str(payload.get("episode_id") or "default")
        seed = payload.get("seed")
        options = dict(payload.get("options") or {})
        if "scenario_id" in payload:
            options["scenario_id"] = payload["scenario_id"]
        if "difficulty" in payload:
            options["difficulty"] = payload["difficulty"]

        env = _get_or_create_openenv_env(episode_id)
        result = env.reset(seed=seed, options=options)
        return _serialize_step_result(result, episode_id)

    @app.post("/step")
    def openenv_step(payload: dict[str, Any] = Body(default_factory=dict)):
        episode_id = str(payload.get("episode_id") or "default")
        env = OPENENV_ENVS.get(episode_id)
        if env is None:
            raise HTTPException(status_code=404, detail="Episode not found")

        action_payload = payload.get("action") or payload
        action_payload = {key: value for key, value in action_payload.items() if key != "episode_id"}
        try:
            action = CrisisAction(**action_payload)
        except TypeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid action payload: {exc}") from exc

        result = env.step(action)
        return _serialize_step_result(result, episode_id)

    @app.get("/state")
    def openenv_state(episode_id: str = "default"):
        env = OPENENV_ENVS.get(episode_id)
        if env is None or env.state is None:
            raise HTTPException(status_code=404, detail="Episode not found")
        return _serialize_value(env.state)

    @app.get("/schema")
    def openenv_schema():
        return {
            "env_name": "crisis_commander_env",
            "action": _schema_for_dataclass(CrisisAction),
            "observation": _schema_for_dataclass(CrisisObservation),
            "state": _schema_for_dataclass(CrisisState),
            "defaults": {
                "scenario_id": "rush_hour_cascade",
                "difficulty": Difficulty.ADVANCED.value,
            },
        }

    @app.get("/api/health")
    def health():
        return {
            "ok": True,
            "ui": INDEX_FILE.exists(),
            "admin_login": ADMIN_LOGIN_FILE.exists(),
            "user_login": USER_LOGIN_FILE.exists(),
            "static": STATIC_DIR.exists(),
        }

    @app.get("/api/manifest")
    def manifest():
        return build_manifest()

    @app.post("/api/sessions")
    def start_session(payload: CreateSessionRequest):
        try:
            return create_session(
                scenario_id=payload.scenario_id,
                difficulty=payload.difficulty,
                seed=payload.seed,
                policy=payload.policy,
            )
        except Exception as exc:  # pragma: no cover - surfaced to UI
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/sessions/{session_id}")
    def get_session(session_id: str):
        try:
            record = require_session(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {
            "session_id": record.session_id,
            "snapshot": record.latest_snapshot,
        }

    @app.post("/api/sessions/{session_id}/step")
    def run_step(session_id: str, payload: StepSessionRequest):
        try:
            snapshot = step_session(session_id, payload.policy)
        except KeyError as exc:
            message = str(exc)
            status_code = 404 if "session" in message.lower() else 400
            raise HTTPException(status_code=status_code, detail=message) from exc
        except Exception as exc:  # pragma: no cover - surfaced to UI
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "session_id": session_id,
            "snapshot": snapshot,
        }

    @app.get("/ui", include_in_schema=False)
    def ui():
        if not INDEX_FILE.exists():
            raise HTTPException(status_code=503, detail="UI assets are missing from this deployment.")
        return FileResponse(INDEX_FILE)

    @app.get("/dashboard", include_in_schema=False)
    def dashboard():
        if not INDEX_FILE.exists():
            raise HTTPException(status_code=503, detail="UI assets are missing from this deployment.")
        return FileResponse(INDEX_FILE)

    @app.get("/admin-login", include_in_schema=False)
    @app.get("/admin-login.html", include_in_schema=False)
    def admin_login():
        if not ADMIN_LOGIN_FILE.exists():
            raise HTTPException(status_code=503, detail="Admin login page is missing from this deployment.")
        return FileResponse(ADMIN_LOGIN_FILE)

    @app.get("/user-login", include_in_schema=False)
    @app.get("/user-login.html", include_in_schema=False)
    def user_login():
        if not USER_LOGIN_FILE.exists():
            raise HTTPException(status_code=503, detail="User login page is missing from this deployment.")
        return FileResponse(USER_LOGIN_FILE)

    @app.get("/", include_in_schema=False)
    def root():
        if not INDEX_FILE.exists():
            raise HTTPException(status_code=503, detail="UI assets are missing from this deployment.")
        return FileResponse(INDEX_FILE)

    return app


app = _build_app()


def main(argv: list[str] | None = None) -> None:
    if app is None:
        raise RuntimeError("Install fastapi, pydantic, and uvicorn to run the server.")

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the Crisis Commander server.")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    args = parser.parse_args(argv)

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
