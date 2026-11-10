"""Churn and uplift models in plain numpy (L2 logistic regression), trained on the past campaign.

The uplift model is a T-learner: one churn model per offer arm, fitted on the customers who got that
offer in the randomised campaign. The predicted net value of an offer is
(p_none - p_offer) * value - cost * (1 - p_offer), using the same value formula the business uses.
"""

from __future__ import annotations

import numpy as np

from .offers import NAMES, cost, eligible
from .simulate import CONTRACTS, MARGIN, PLANS

KEYWORDS = {"kw_price": ["bill", "price", "cheaper", "charge"], "kw_network": ["signal", "dropping", "slow in", "mast"],
            "kw_device": ["battery", "handset", "phone", "screen"], "kw_service": ["hold", "complaint", "error"],
            "kw_moving": ["moving", "relocating", "leaving the country"]}


def features(c: dict, keywords: bool = False) -> list[float]:
    """Account data only. Age band and region are deliberately not used."""
    x = [c["tenure_months"] / 48, c["monthly_charge"] / 40, c["data_gb"] / 12, c["dropped_call_pct"] / 2,
         c["tickets_90d"], c["late_payments_12m"], c["device_age_months"] / 18, float(c["autopay"]),
         float(c["discount_last_12m"])]
    x += [float(c["plan"] == p) for p in PLANS[1:]] + [float(c["contract"] == k) for k in CONTRACTS[1:]]
    if keywords:
        low = c["note"].lower()
        x += [float(any(w in low for w in ws)) for ws in KEYWORDS.values()]
    return x


class Logistic:
    def __init__(self, l2: float = 1.0, iters: int = 400, lr: float = 0.5):
        self.l2, self.iters, self.lr = l2, iters, lr

    def fit(self, X: np.ndarray, y: np.ndarray) -> Logistic:
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        Z = np.c_[np.ones(len(X)), (X - self.mu) / self.sd]
        w = np.zeros(Z.shape[1])
        for _ in range(self.iters):
            p = 1 / (1 + np.exp(-Z @ w))
            g = Z.T @ (p - y) / len(y) + self.l2 * np.r_[0, w[1:]] / len(y)
            w -= self.lr * g
        self.w = w
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        Z = np.c_[np.ones(len(X)), (X - self.mu) / self.sd]
        return 1 / (1 + np.exp(-Z @ self.w))


class Uplift:
    """One churn model per offer arm (T-learner)."""

    def __init__(self, keywords: bool = False):
        self.keywords = keywords

    def fit(self, train: list[dict], campaign: list[dict]) -> Uplift:
        by_id = {c["id"]: c for c in train}
        self.arms = {}
        for o in NAMES:
            rows = [r for r in campaign if r["offer"] == o]
            X = np.array([features(by_id[r["id"]], self.keywords) for r in rows])
            y = np.array([float(r["churned"]) for r in rows])
            self.arms[o] = Logistic().fit(X, y)
        return self

    def churn(self, c: dict) -> float:
        return float(self.arms["none"].predict(np.array([features(c, self.keywords)]))[0])

    def net_values(self, c: dict) -> dict[str, float]:
        x = np.array([features(c, self.keywords)])
        p = {o: float(m.predict(x)[0]) for o, m in self.arms.items()}
        value = MARGIN * c["monthly_charge"] * 24
        return {o: round((p["none"] - p[o]) * value - cost(o, c) * (1 - p[o]), 2) for o in NAMES}

    def ranked(self, c: dict) -> list[tuple[str, float]]:
        """Eligible offers by predicted net value, best first ('none' is always eligible)."""
        nv = self.net_values(c)
        return sorted(((o, v) for o, v in nv.items() if eligible(o, c)[0]), key=lambda t: -t[1])


def auc(scores: list[float], labels: list[bool]) -> float:
    s, y = np.asarray(scores), np.asarray(labels, dtype=bool)
    order = s.argsort()
    ranks = np.empty(len(s))
    ranks[order] = np.arange(1, len(s) + 1)
    pos = y.sum()
    return float((ranks[y].sum() - pos * (pos + 1) / 2) / (pos * (len(s) - pos)))
