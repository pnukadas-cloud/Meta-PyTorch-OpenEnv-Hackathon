"""FastAPI application for Crisis Commander."""

from __future__ import annotations

import os
from pathlib import Path

from crisis_commander_env.models import CrisisAction, CrisisObservation
from server.crisis_commander_environment import CrisisCommanderEnvironment
from server.hf_strategist import HFStrategistError, generate_strategy, strategist_status
from server.runtime import build_manifest, create_session, require_session, step_session

try:
    from openenv.core.env_server import create_app  # type: ignore
except ImportError:
    try:
        from openenv.core.env_server.http_server import create_app  # type: ignore
    except ImportError:
        create_app = None

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    HTTPException = None
    CORSMiddleware = None
    FileResponse = None
    StaticFiles = None
    BaseModel = object


ROOT_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT_DIR / "index.html"
STATIC_DIR = ROOT_DIR / "static"


class CreateSessionRequest(BaseModel):
    scenario_id: str = "rush_hour_cascade"
    difficulty: str = "advanced"
    seed: int = 7
    policy: str = "fairness_aware"


class StepSessionRequest(BaseModel):
    policy: str | None = None


class HFStrategistRequest(BaseModel):
    snapshot_index: int | None = None


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

    if create_app is not None:
        openenv_app = create_app(
            CrisisCommanderEnvironment,
            CrisisAction,
            CrisisObservation,
            env_name="crisis_commander_env",
        )
        app.mount("/openenv", openenv_app)

    if StaticFiles is not None and STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/api/health")
    def health():
        return {
            "ok": True,
            "ui": INDEX_FILE.exists(),
            "static": STATIC_DIR.exists(),
        }

    @app.get("/api/manifest")
    def manifest():
        payload = build_manifest()
        payload["hf"] = strategist_status()
        return payload

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

    @app.get("/api/hf/status")
    def hf_status():
        return strategist_status()

    @app.post("/api/sessions/{session_id}/advisor")
    def hf_advisor(session_id: str, payload: HFStrategistRequest):
        try:
            record = require_session(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        snapshot = record.latest_snapshot
        if snapshot is None:
            raise HTTPException(status_code=400, detail="Session has no snapshot yet.")

        try:
            result = generate_strategy(snapshot)
        except HFStrategistError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - surfaced to UI
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return {
            "session_id": session_id,
            "advisor": result,
        }

    @app.get("/ui", include_in_schema=False)
    def ui():
        if not INDEX_FILE.exists():
            raise HTTPException(status_code=503, detail="UI assets are missing from this deployment.")
        return FileResponse(INDEX_FILE)

    @app.get("/", include_in_schema=False)
    def root():
        if not INDEX_FILE.exists():
            raise HTTPException(status_code=503, detail="UI assets are missing from this deployment.")
        return FileResponse(INDEX_FILE)

    return app


app = _build_app()


def main() -> None:
    if app is None:
        raise RuntimeError("Install fastapi, pydantic, and uvicorn to run the server.")

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
