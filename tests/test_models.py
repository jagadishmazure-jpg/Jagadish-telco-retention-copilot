"""Churn and uplift models."""

import json

import numpy as np
from conftest import ROOT, customer

from retention.models import Logistic, Uplift, auc, features
from retention.offers import eligible


def test_logistic_learns_a_separable_signal():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(400, 2))
    y = (X[:, 0] > 0).astype(float)
    p = Logistic().fit(X, y).predict(X)
    assert ((p > 0.5) == (y == 1)).mean() > 0.95


def test_auc_known_values():
    assert auc([0.1, 0.2, 0.8, 0.9], [False, False, True, True]) == 1.0
    assert auc([0.9, 0.8, 0.2, 0.1], [False, False, True, True]) == 0.0
    assert auc([0.5, 0.5, 0.5, 0.5], [False, True, False, True]) == 0.5


def test_features_do_not_use_age_band_or_region():
    assert features(customer(age_band="18-29", region="Southfen")) == features(customer(age_band="65+", region="Westvale"))


def test_keyword_features_read_the_note():
    a = features(customer(note="Last call: moving abroad next month."), keywords=True)
    b = features(customer(), keywords=True)
    assert len(a) == len(features(customer())) + 5 and a != b


def test_training_file_has_no_hidden_truth():
    line = (ROOT / "data/train.jsonl").read_text().splitlines()[0]
    assert "_truth" not in json.loads(line)


def test_ranked_offers_are_all_eligible_and_none_is_always_there(model, q):
    for c in q[:20]:
        r = model.ranked(c)
        assert "none" in [o for o, _ in r] and all(eligible(o, c)[0] for o, _ in r)
        assert [v for _, v in r] == sorted((v for _, v in r), reverse=True)


def test_uplift_model_learns_that_discounts_help_price_sensitive_customers(model):
    pricey = customer(monthly_charge=48.0, late_payments_12m=2, tenure_months=6)
    happy = customer(monthly_charge=25.0, tenure_months=80, autopay=True)
    assert model.net_values(pricey)["loyalty_discount"] > model.net_values(happy)["loyalty_discount"]


def test_uplift_is_a_t_learner_with_one_model_per_arm(model):
    from retention.offers import NAMES

    assert set(model.arms) == set(NAMES) and isinstance(model, Uplift)
