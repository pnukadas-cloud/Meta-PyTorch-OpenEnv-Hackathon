# Strategy Notes

`rush_hour_cascade` is the best demo scenario for the hackathon because it proves three things at once:

1. The agent must reason about cascading incidents instead of solving a single static task.
2. The reward function mixes public safety, fairness, and infrastructure resilience.
3. The action space is broad enough to reward planning, not just greedy dispatching.

Suggested baseline story for a demo:

1. Dispatch perimeter control and medical response to the central bus crash.
2. Cover the warehouse fire early so it does not become the hidden losing condition.
3. Use mutual aid or pre-staging before the hazmat event appears.
4. Expand a hospital only when the incoming patient wave justifies the spend.

