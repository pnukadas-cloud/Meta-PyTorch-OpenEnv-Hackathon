"""Submission inference script for Crisis Commander."""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from urllib import error, request

from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SCENARIO_ID = os.getenv("SCENARIO_ID", "rush_hour_cascade")
DIFFICULTY = os.getenv("DIFFICULTY", "advanced")
SEED = int(os.getenv("SEED", "7"))
MAX_STEPS = int(os.getenv("MAX_STEPS", "8"))


def log_event(kind: str, payload: dict[str, Any]) -> None:
    sys.stdout.write(f"{kind} {json.dumps(payload, separators=(',', ':'))}\n")
    sys.stdout.flush()


def http_json(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(f"{ENV_BASE_URL}{path}", data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fallback_policy(snapshot: dict[str, Any]) -> str:
    critical_active = any(
        item.get("status") == "active" and float(item.get("severity", "0")) >= 4.0
        for item in snapshot.get("incidents", [])
    )
    if snapshot.get("metrics", {}).get("hospital_overflow", 0) > 0 or critical_active:
        return "fairness_aware"
    return "severity_first"


def choose_policy(snapshot: dict[str, Any]) -> str:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "EMPTY")
    prompt = {
        "summary": snapshot.get("summary"),
        "turn": snapshot.get("turn"),
        "max_turns": snapshot.get("max_turns"),
        "budget_remaining": snapshot.get("budget_remaining"),
        "metrics": snapshot.get("metrics", {}),
        "incidents": snapshot.get("incidents", []),
    }

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are choosing the next policy for an emergency-response simulator. "
                        "Return JSON only with a single key named policy. "
                        "Allowed values: fairness_aware or severity_first."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt, separators=(",", ":")),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        policy = parsed.get("policy")
        if policy in {"fairness_aware", "severity_first"}:
            return policy
    except Exception:
        pass

    return fallback_policy(snapshot)


def main() -> None:
    session = http_json(
        "POST",
        "/api/sessions",
        {
            "scenario_id": SCENARIO_ID,
            "difficulty": DIFFICULTY,
            "seed": SEED,
            "policy": "fairness_aware",
        },
    )

    session_id = session["session_id"]
    snapshot = session["snapshot"]
    log_event(
        "START",
        {
            "session_id": session_id,
            "scenario_id": SCENARIO_ID,
            "difficulty": DIFFICULTY,
            "seed": SEED,
            "env_base_url": ENV_BASE_URL,
            "api_base_url": API_BASE_URL,
            "model_name": MODEL_NAME,
            "local_image_name": LOCAL_IMAGE_NAME,
        },
    )

    step_index = 0
    while not snapshot.get("done") and step_index < MAX_STEPS:
        step_index += 1
        policy = choose_policy(snapshot)
        result = http_json(
            "POST",
            f"/api/sessions/{session_id}/step",
            {"policy": policy},
        )
        snapshot = result["snapshot"]
        log_event(
            "STEP",
            {
                "step": step_index,
                "policy": policy,
                "turn": snapshot.get("turn"),
                "reward_total": snapshot.get("reward_total"),
                "step_reward": snapshot.get("step_reward"),
                "verdict": snapshot.get("verdict"),
                "done": snapshot.get("done"),
            },
        )

    log_event(
        "END",
        {
            "session_id": session_id,
            "turn": snapshot.get("turn"),
            "done": snapshot.get("done"),
            "reward_total": snapshot.get("reward_total"),
            "verdict": snapshot.get("verdict"),
            "metrics": snapshot.get("metrics", {}),
        },
    )


if __name__ == "__main__":
    try:
        main()
    except error.HTTPError as exc:
        log_event("END", {"status": "error", "code": exc.code, "message": exc.reason})
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - CLI failure path
        log_event("END", {"status": "error", "message": str(exc)})
        sys.exit(1)
