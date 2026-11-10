# ADR 0001: Simulated customers with every potential outcome known

**Status:** accepted

**Context.** Retention policies are hard to judge on real data: you only see what happened under the
offer that was made, and real customer data cannot be published.

**Decision.** A deterministic simulator gives every customer a hidden churn driver and a churn
probability under every offer. Models learn only from a past randomised campaign (one random offer per
training customer, outcome observed), the way a real team would. Policies are then scored on held-out
customers by the true expected value of the offer they chose.

**Consequences.** Every policy, including the copilot, is scored exactly and can be compared with an
oracle. The effect sizes are invented, so the absolute values will not transfer.
