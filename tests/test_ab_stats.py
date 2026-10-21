import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ab_stats import (  # noqa: E402
    bootstrap_mean_diff,
    mde_two_proportions,
    sample_size_two_proportions,
    srm_check,
    two_proportion_ztest,
)


def test_srm_balanced_groups_pass():
    result = srm_check([5000, 5000])
    assert result["chi2"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)


def test_srm_detects_large_imbalance():
    assert srm_check([5000, 5600])["p_value"] < 0.001


def test_ztest_hand_computed_example():
    # 100/1000 vs 130/1000 -> pooled p = 0.115
    r = two_proportion_ztest(100, 1000, 130, 1000)
    se = np.sqrt(0.115 * 0.885 * (2 / 1000))
    assert r["diff"] == pytest.approx(0.03)
    assert r["z"] == pytest.approx(0.03 / se)
    assert r["ci_low"] < r["diff"] < r["ci_high"]


def test_ztest_is_antisymmetric():
    r1 = two_proportion_ztest(100, 1000, 130, 1000)
    r2 = two_proportion_ztest(130, 1000, 100, 1000)
    assert r1["z"] == pytest.approx(-r2["z"])
    assert r1["p_value"] == pytest.approx(r2["p_value"])


def test_sample_size_and_mde_are_inverses():
    n = sample_size_two_proportions(0.19, 0.01)
    assert mde_two_proportions(0.19, n) == pytest.approx(0.01, rel=1e-3)


def test_bootstrap_centres_on_observed_difference():
    rng = np.random.default_rng(0)
    a = rng.binomial(1, 0.20, 5000)
    b = rng.binomial(1, 0.25, 5000)
    diffs = bootstrap_mean_diff(a, b, n_boot=500, seed=1)
    assert diffs.mean() == pytest.approx(b.mean() - a.mean(), abs=0.003)
