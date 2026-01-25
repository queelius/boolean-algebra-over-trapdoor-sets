"""Bernoulli Boolean types with explicit error rates.

Implements the Bernoulli types framework from:
bernoulli-types/papers/final/paper1_bernoulli_theory.tex
"""

from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BernoulliBoolean:
    """A boolean with false positive/negative rates (alpha, beta).

    Implements the Bernoulli types framework from:
    bernoulli-types/papers/final/paper1_bernoulli_theory.tex Section 2

    This is a second-order Bernoulli Boolean (allows alpha != beta).
    First-order is a special case where alpha = beta.

    Terminology:
    - Latent value: the true boolean we're approximating
    - Observed value: .value (what we computed)
    - Confusion matrix: [[1-alpha, alpha], [beta, 1-beta]]

    Error model:
    - alpha (FPR): P(observed=True | latent=False)
    - beta (FNR): P(observed=False | latent=True)
    - confidence: 1 - alpha - beta
    """

    value: bool
    alpha: float = 0.0  # False positive rate
    beta: float = 0.0   # False negative rate

    def __post_init__(self):
        if not (0 <= self.alpha <= 1 and 0 <= self.beta <= 1):
            raise ValueError("Error rates must be in [0, 1]")

    @property
    def confidence(self) -> float:
        """Probability of correct result: 1 - alpha - beta."""
        return max(0.0, 1.0 - self.alpha - self.beta)

    @property
    def confusion_matrix(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return 2x2 confusion matrix Q where Q[i,j] = P(observe j | latent i).

        Row 0: latent=False -> [1-alpha, alpha]
        Row 1: latent=True  -> [beta, 1-beta]

        This is a row-stochastic matrix (rows sum to 1).
        """
        return ((1 - self.alpha, self.alpha), (self.beta, 1 - self.beta))

    def posterior(self, prior: float) -> float:
        """P(latent=True | observation) using Bayes' theorem.

        Args:
            prior: P(latent=True) before observing

        Returns:
            P(latent=True | observed value) - updated probability

        Example:
            For a rare disease test with 1% prevalence and 5% FPR:
            >>> bb = BernoulliBoolean(True, alpha=0.05, beta=0.0)
            >>> bb.posterior(0.01)  # ~17% chance of actually having disease
        """
        if not (0 <= prior <= 1):
            raise ValueError("Prior must be in [0, 1]")
        if self.value:
            # P(true | obs=true) = P(obs=true|true)*P(true) / P(obs=true)
            p_obs_true = (1 - self.beta) * prior + self.alpha * (1 - prior)
            return (1 - self.beta) * prior / p_obs_true if p_obs_true > 0 else prior
        else:
            # P(true | obs=false) = P(obs=false|true)*P(true) / P(obs=false)
            p_obs_false = self.beta * prior + (1 - self.alpha) * (1 - prior)
            return self.beta * prior / p_obs_false if p_obs_false > 0 else prior

    def __bool__(self) -> bool:
        """Returns the observed value (for approximate booleans)."""
        return bool(self.value)




def _binary_entropy(p: float) -> float:
    """Binary entropy H_2(p) = -p*log2(p) - (1-p)*log2(1-p)."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def mutual_information(alpha: float, beta: float, prior: float = 0.5) -> float:
    """I(latent; observed) - information revealed by observation.

    Computes the mutual information between the latent boolean and its
    observed approximation, given error rates and prior probability.

    Uses: I(X;Y) = H(Y) - H(Y|X)

    Args:
        alpha: False positive rate P(obs=True | latent=False)
        beta: False negative rate P(obs=False | latent=True)
        prior: P(latent=True), default 0.5 (maximum entropy prior)

    Returns:
        Mutual information in bits. Range [0, 1] where:
        - 0 means observation reveals nothing (alpha=beta=0.5)
        - 1 means observation perfectly reveals latent (alpha=beta=0)

    Example:
        >>> mutual_information(0.0, 0.0)  # Perfect observation
        1.0
        >>> mutual_information(0.5, 0.5)  # Useless observation
        0.0
    """
    if not (0 <= alpha <= 1 and 0 <= beta <= 1 and 0 <= prior <= 1):
        raise ValueError("All parameters must be in [0, 1]")

    # P(observed=true) = P(obs=T|lat=T)*P(lat=T) + P(obs=T|lat=F)*P(lat=F)
    p_obs_true = (1 - beta) * prior + alpha * (1 - prior)

    # H(observed)
    h_obs = _binary_entropy(p_obs_true)

    # H(observed | latent) = P(lat=T)*H(obs|lat=T) + P(lat=F)*H(obs|lat=F)
    # H(obs|lat=T) = H_2(beta), H(obs|lat=F) = H_2(alpha)
    h_obs_given_latent = prior * _binary_entropy(beta) + (1 - prior) * _binary_entropy(alpha)

    return max(0.0, h_obs - h_obs_given_latent)


def compose_and(a1: float, b1: float, a2: float, b2: float) -> tuple[float, float]:
    """Error rates for AND operation.

    AND: True only if both inputs are True
    - FPR decreases: both must be false positives
    - FNR increases: either can be a false negative
    """
    alpha = a1 * a2
    beta = b1 + b2 - b1 * b2
    return (alpha, beta)


def compose_or(a1: float, b1: float, a2: float, b2: float) -> tuple[float, float]:
    """Error rates for OR operation.

    OR: True if either input is True
    - FPR increases: either can be a false positive
    - FNR decreases: both must be false negatives
    """
    alpha = a1 + a2 - a1 * a2
    beta = b1 * b2
    return (alpha, beta)


def compose_not(alpha: float, beta: float) -> tuple[float, float]:
    """Error rates for NOT operation.

    NOT: Swaps true/false, so rates swap too.
    """
    return (beta, alpha)


def compose_xor(a1: float, b1: float, a2: float, b2: float) -> tuple[float, float]:
    """Error rates for XOR operation.

    XOR = (A AND NOT B) OR (NOT A AND B)
    Using independence assumption.
    """
    # P(error) = P(exactly one input wrong)
    p1_correct = 1 - a1 - b1
    p2_correct = 1 - a2 - b2
    # XOR is correct when both correct or both wrong
    p_correct = p1_correct * p2_correct + (a1 + b1) * (a2 + b2)
    # Symmetric error rates for XOR
    error = (1 - p_correct) / 2
    return (error, error)
