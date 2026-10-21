"""Small, dependency-light statistics helpers for A/B test analysis.

Everything here uses only numpy and scipy so the logic is easy to read and
explain. Each function returns plain floats / dicts rather than custom objects.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def srm_check(observed_counts, expected_ratios=None):
    """Sample Ratio Mismatch check (chi-square goodness of fit).

    Tests whether the observed group sizes are consistent with the intended
    traffic split. A small p-value (commonly < 0.01) means the randomization
    or logging may be broken, so downstream results deserve extra scrutiny.

    Parameters
    ----------
    observed_counts : sequence of int
        Number of units observed in each group.
    expected_ratios : sequence of float, optional
        Intended allocation (e.g. [0.5, 0.5]). Defaults to an equal split.

    Returns
    -------
    dict with keys ``chi2`` and ``p_value``.
    """
    observed = np.asarray(observed_counts, dtype=float)
    if expected_ratios is None:
        expected_ratios = np.full(len(observed), 1 / len(observed))
    ratios = np.asarray(expected_ratios, dtype=float)
    ratios = ratios / ratios.sum()
    expected = observed.sum() * ratios
    chi2, p_value = stats.chisquare(observed, expected)
    return {"chi2": float(chi2), "p_value": float(p_value)}


def two_proportion_ztest(successes_a, n_a, successes_b, n_b, alpha=0.05):
    """Two-sided z-test for a difference in proportions (B minus A).

    The test statistic uses the pooled standard error (correct under the null
    hypothesis of equal proportions). The confidence interval uses the
    unpooled standard error (correct for estimating the true difference).

    Returns
    -------
    dict with keys ``p_a``, ``p_b``, ``diff``, ``relative_lift``, ``z``,
    ``p_value``, ``ci_low``, ``ci_high``.
    """
    p_a = successes_a / n_a
    p_b = successes_b / n_b
    diff = p_b - p_a

    p_pool = (successes_a + successes_b) / (n_a + n_b)
    se_pooled = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = diff / se_pooled
    p_value = 2 * stats.norm.sf(abs(z))

    se_unpooled = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    z_crit = stats.norm.ppf(1 - alpha / 2)

    return {
        "p_a": float(p_a),
        "p_b": float(p_b),
        "diff": float(diff),
        "relative_lift": float(diff / p_a),
        "z": float(z),
        "p_value": float(p_value),
        "ci_low": float(diff - z_crit * se_unpooled),
        "ci_high": float(diff + z_crit * se_unpooled),
    }


def bootstrap_mean_diff(a, b, n_boot=5000, seed=42, chunk=200):
    """Bootstrap distribution of mean(b) - mean(a).

    Resamples each group independently with replacement. Works for binary
    outcomes (giving a difference in rates) and for continuous ones.
    Resamples are drawn in chunks so memory stays bounded for large groups.
    """
    rng = np.random.default_rng(seed)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diffs = np.empty(n_boot)
    for start in range(0, n_boot, chunk):
        stop = min(start + chunk, n_boot)
        k = stop - start
        mean_a = a[rng.integers(0, len(a), size=(k, len(a)))].mean(axis=1)
        mean_b = b[rng.integers(0, len(b), size=(k, len(b)))].mean(axis=1)
        diffs[start:stop] = mean_b - mean_a
    return diffs


def mann_whitney(a, b):
    """Two-sided Mann-Whitney U test, appropriate for skewed engagement data
    where a t-test on means would be dominated by heavy users."""
    u, p_value = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {"u": float(u), "p_value": float(p_value)}


def mde_two_proportions(p_base, n_per_group, alpha=0.05, power=0.80):
    """Minimum detectable absolute difference for a two-sided two-proportion
    test with equal group sizes (normal approximation)."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    se = np.sqrt(2 * p_base * (1 - p_base) / n_per_group)
    return float((z_alpha + z_beta) * se)


def sample_size_two_proportions(p_base, mde_abs, alpha=0.05, power=0.80):
    """Users needed per group to detect an absolute change of ``mde_abs``
    from baseline ``p_base`` (normal approximation, equal groups)."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = 2 * p_base * (1 - p_base) * ((z_alpha + z_beta) / mde_abs) ** 2
    return int(np.ceil(n))
