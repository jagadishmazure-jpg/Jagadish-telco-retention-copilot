# ADR 0002: Choose offers by uplift, not by churn score

**Status:** accepted

**Context.** Ranking by churn risk says who might leave, not who an offer would keep. High-risk
customers include people leaving the country, and offers to settled customers can backfire.

**Decision.** A T-learner (one logistic churn model per offer arm, fitted on the randomised campaign)
predicts each offer's churn reduction; the predicted net value uses the same value and cost formula as
the business. The churn model is used only to build the call queue.

**Consequences.** Offers pay for themselves on average. The model is only as good as the campaign it
learnt from; in an early check with 4,000 campaign customers (about 670 per arm) it earned less than
a blanket discount, so the campaign was grown to 12,000 (about 2,000 per arm).
