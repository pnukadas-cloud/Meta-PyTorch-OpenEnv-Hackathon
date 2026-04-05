"""Hugging Face model integration for live strategy assistance."""

from __future__ import annotations

import os
from typing import Any

try:
    from huggingface_hub import InferenceClient, get_token
except ImportError:  # pragma: no cover - only hit when dependency missing
    InferenceClient = None

    def get_token() -> str | None:  # type: ignore
        return None


DEFAULT_MODEL = os.getenv("HF_STRATEGIST_MODEL", "Qwen/Qwen2.5-7B-Instruct")
DEFAULT_PROVIDER = os.getenv("HF_INFERENCE_PROVIDER", "auto")
DEFAULT_MAX_TOKENS = int(os.getenv("HF_STRATEGIST_MAX_TOKENS", "220"))
DEFAULT_TEMPERATURE = float(os.getenv("HF_STRATEGIST_TEMPERATURE", "0.2"))


class HFStrategistError(RuntimeError):
    """Raised when the Hugging Face strategist cannot serve a request."""


def strategist_status() -> dict[str, Any]:
    token = _resolve_token()
    return {
        "configured": bool(token),
        "model": DEFAULT_MODEL,
        "provider": DEFAULT_PROVIDER,
        "auth_source": "HF_TOKEN or local hf auth login",
        "message": (
            "HF strategist is ready."
            if token
            else "Set HF_TOKEN or run `hf auth login` to enable the Hugging Face strategist."
        ),
    }


def generate_strategy(snapshot: dict[str, Any]) -> dict[str, Any]:
    if InferenceClient is None:
        raise HFStrategistError(
            "huggingface_hub is not installed. Install dependencies before using the HF strategist."
        )

    token = _resolve_token()
    if not token:
        raise HFStrategistError(
            "No Hugging Face token detected. Set HF_TOKEN or run `hf auth login` first."
        )

    client = InferenceClient(token=token)
    completion = client.chat_completion(
        model=DEFAULT_MODEL,
        provider=DEFAULT_PROVIDER,
        messages=_build_messages(snapshot),
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
    )
    content = _extract_text(completion)
    if not content:
        raise HFStrategistError("The Hugging Face strategist returned an empty response.")

    return {
        "configured": True,
        "model": DEFAULT_MODEL,
        "provider": DEFAULT_PROVIDER,
        "content": content.strip(),
    }


def _resolve_token() -> str | None:
    return os.getenv("HF_TOKEN") or get_token()


def _build_messages(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    incidents = "\n".join(
        f"- {incident['id']} | {incident['title']} | zone={incident['zone']} | severity={incident['severity']} | status={incident['status']} | {incident['meta']}"
        for incident in snapshot.get("incidents", [])[:8]
    )
    resources = "\n".join(
        f"- {resource['id']} | {resource['type']} | status={resource['status']} | zone={resource['zone']} | {resource['meta']}"
        for resource in snapshot.get("resources", [])[:10]
    )
    events = "\n".join(
        f"- {event['title']}: {event['body']}"
        for event in snapshot.get("events", [])[:8]
    )

    system_prompt = (
        "You are an emergency-response strategist embedded inside a reinforcement-learning environment. "
        "Give short, practical command advice grounded only in the provided mission state. "
        "Do not invent incidents, resources, or capabilities. "
        "Respond in markdown with exactly four headings: "
        "`Situation`, `Best Next Move`, `Why This Works`, and `Watch Out`."
    )
    user_prompt = (
        f"Scenario: {snapshot.get('scenario_title')}\n"
        f"Difficulty: {snapshot.get('difficulty')}\n"
        f"Turn: {snapshot.get('turn')}/{snapshot.get('max_turns')} at {snapshot.get('clock_minutes')} minutes\n"
        f"Budget remaining: {snapshot.get('budget_remaining')}\n"
        f"Verdict so far: {snapshot.get('verdict')}\n"
        f"Current action headline: {snapshot.get('action_headline')}\n"
        f"Summary: {snapshot.get('summary')}\n\n"
        f"Incidents:\n{incidents or '- None'}\n\n"
        f"Resources:\n{resources or '- None'}\n\n"
        f"Recent events:\n{events or '- None'}\n\n"
        "Give the next best operational recommendation for the command center."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _extract_text(completion: Any) -> str:
    try:
        choices = getattr(completion, "choices", None)
        if choices:
            message = choices[0].message
            content = getattr(message, "content", "")
            if isinstance(content, list):
                return "".join(
                    item.get("text", "") if isinstance(item, dict) else str(item)
                    for item in content
                )
            return str(content)
    except Exception:
        pass

    if isinstance(completion, dict):
        try:
            content = completion["choices"][0]["message"]["content"]
            if isinstance(content, list):
                return "".join(
                    item.get("text", "") if isinstance(item, dict) else str(item)
                    for item in content
                )
            return str(content)
        except Exception:
            return ""
    return ""
