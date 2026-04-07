---
title: Crisis Commander
emoji: siren
colorFrom: red
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# Crisis Commander

An OpenEnv-style reinforcement learning environment where an agent acts as a citywide incident commander during cascading public emergencies.

This repo is designed as a strong Round 1 submission for the Meta x PyTorch OpenEnv Hackathon. The hackathon brief asks for a mini RL environment with defined tasks, graders, and reward logic. Crisis Commander goes beyond a toy workflow and turns that brief into a high-stakes, multi-objective decision system:

- multiple incident types with different resource requirements
- constrained responders across ambulances, fire engines, police units, and drones
- hospital surge planning and overflow penalties
- fairness pressure for high-vulnerability districts
- cascading events that appear mid-episode
- a grading rubric that feels like an actual judging harness, not just a raw reward sum

## Why This Can Stand Out

Most first-round environments stop at "classify", "route", or "pick next ticket". This one is harder to fake and easier to remember:

- It looks like a real public-systems simulator, not a CRUD workflow.
- The reward is explicitly multi-objective: safety, timeliness, fairness, resilience, and efficiency.
- It has a strong story judges can repeat in one sentence:
  "The agent runs a city crisis command center under cascading incidents and hospital pressure."
- It is demo-friendly. A single rollout is immediately legible to reviewers.
- It maps cleanly to real RL research themes: constrained planning, delayed rewards, fairness-aware optimization, and dynamic resource allocation.

## Core Environment Loop

Each episode starts with a scenario such as a rush-hour crash + fire, a festival blackout, or a storm-driven industrial accident.

At every step the agent can:

- dispatch a resource to an incident
- reroute an already committed resource
- pre-stage units in a likely spillover zone
- open hospital surge capacity
- request mutual aid at a budget cost
- wait for another timestep

After each action, the simulator:

1. advances the mission clock
2. spawns any scheduled cascading incidents
3. updates responder movement
4. worsens or stabilizes each active incident based on coverage
5. routes patients into hospitals
6. computes reward and grading signals

## Reward Design

The OpenEnv reward stream is tracked through a `ScoreBreakdown` with:

- `resolution_bonus`
- `stabilization_bonus`
- `foresight_bonus`
- `harm_penalty`
- `response_delay_penalty`
- `fairness_penalty`
- `capacity_penalty`
- `resource_efficiency_penalty`
- `invalid_action_penalty`

This means a policy cannot win by optimizing only one thing. Fast but unfair plans lose points. Safe but wasteful plans lose points. Greedy dispatching without surge planning loses points.

## Hackathon-Facing Grader

`crisis_commander_env/grader.py` adds a judge-style summary on top of the raw step reward:

- outcome
- timeliness
- fairness
- efficiency
- resilience

The final verdict returns labels like:

- `final-round caliber`
- `strong shortlist`
- `promising but leaky`

That makes the environment easy to benchmark and easy to present in a submission video or README.

## Scenario Bank

### `rush_hour_cascade`

The best default demo. A bus crash and warehouse fire are already live when a hazmat leak and grid failure arrive later.

### `festival_blackout`

A crowd-control heavy scenario where media-visible incidents compete with a vulnerable district blackout.

### `industrial_storm`

A resilience-focused scenario where the right answer is rarely the most obvious first dispatch.

## Repo Structure

```text
crisis_commander_env/
  __init__.py
  baselines.py
  client.py
  grader.py
  models.py
  openenv_compat.py
  scenarios.py
  simulator.py
server/
  app.py
  crisis_commander_environment.py
tests/
  test_baselines.py
  test_simulator.py
examples/
  sample_actions.json
  strategy_notes.md
openenv.yaml
pyproject.toml
README.md
```

## Quick Start

```bash
pip install -e .
python -m unittest
python -m server.app
```

Visual preview:

```text
Open index.html directly in your browser for the interactive concept demo.
```

Live browser app:

```bash
python -m pip install fastapi uvicorn pydantic huggingface_hub
python -m server.app
```

Then open:

```text
http://127.0.0.1:8000/
```

The browser UI will create a real simulator session, run the baseline policies against the Python
environment, and display live snapshots from the backend.

## Hugging Face Model Integration

The browser app now includes a real Hugging Face strategist panel backed by a live instruct model.

- Default model: `Qwen/Qwen2.5-7B-Instruct`
- Integration path: `huggingface_hub.InferenceClient`
- UI action: click `Ask HF Strategist` on the live app page

Authenticate either by exporting `HF_TOKEN` or logging in locally:

```bash
hf auth login
```

Or on PowerShell:

```powershell
$env:HF_TOKEN="your_token_here"
python -m server.app
```

The strategist endpoint sends the current simulator snapshot to Hugging Face and returns a short
operational recommendation grounded in the live mission state.

Minimal local usage:

```python
from crisis_commander_env.models import ActionType, CrisisAction
from crisis_commander_env.simulator import CrisisCommanderEnv

env = CrisisCommanderEnv()
result = env.reset(seed=7, options={"scenario_id": "rush_hour_cascade", "difficulty": "advanced"})

print(result.observation.text)

result = env.step(
    CrisisAction(
        action_type=ActionType.DISPATCH,
        resource_id="POL-1",
        incident_id="INC-1",
    )
)

print(result.reward)
print(result.info["grade"])
```

## Baselines

Two simple heuristics are included:

- `severity_first_policy`
- `fairness_aware_policy`

They exist to show that:

- the environment is rich enough to support nontrivial policies
- the scoring surface has meaningful tradeoffs
- we can compare naive and fairness-aware behavior in a submission demo

## Submission Angle

If you are submitting this to Round 1 of the Meta x PyTorch OpenEnv Hackathon running from March 25, 2026 to April 8, 2026, the strongest pitch is:

> Crisis Commander is a multi-objective urban emergency response environment for training agentic systems that must balance casualties, response latency, hospital capacity, fairness, and operational cost under cascading uncertainty.

That pitch is specific, technically credible, and much more memorable than a generic support or ticketing environment.
