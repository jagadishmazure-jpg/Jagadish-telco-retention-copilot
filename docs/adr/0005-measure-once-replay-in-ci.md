# ADR 0005: Measure the copilot once, replay the scoring in CI

**Status:** accepted

**Context.** Three copilot configurations over the call queue take over an hour on CPU. CI should not
need model weights.

**Decision.** Copilot replies are measured once with `scripts/run_copilot.py` and committed. CI rebuilds
the customers, campaign and queue from the simulator, refits the uplift models, re-scores every policy,
checks the hash manifest, and fails if any number differs from `results/` or from the docs.

**Consequences.** Every number is reproducible offline. Re-measuring the model itself needs
`scripts/fetch_models.sh` and about an hour of CPU.
