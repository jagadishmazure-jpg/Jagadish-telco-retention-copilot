# ADR 0002: Choose offers by uplift, not by churn score

**Status:** accepted

**Context.** Ranking by churn risk says who might leave, not who an offer would keep. High-risk
customers include people leaving the country, and offers to settled customers can backfire.

**Decision.** A T-learner (one logistic churn model per offer arm, fitted on the randomised campaign)
predicts each offer's churn reduction; the predicted net value uses the same value and cost formula as
the business. The churn model is used only to build the call queue.

**Consequences.** Offers pay for themselves on average. The model is only as good as the campaign it
learnt from; with fewer than about 2,000 customers per arm it ranked offers worse than a blanket
discount in early checks, so the campaign size is part of the design.
