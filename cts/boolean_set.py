"""Privacy-preserving sets with Boolean algebra operations."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Union

from .trapdoor import Trapdoor, TrapdoorFactory
from .approximate import BernoulliBoolean, compose_or, compose_and


@dataclass
class BooleanSet:
    """A set of trapdoors supporting Boolean algebra operations.

    Operations:
    - Union (|): combines sets, FPR increases
    - Intersection (&): common elements, FPR decreases
    - Symmetric difference (^): XOR operation
    - Membership test: returns BernoulliBoolean

    Error tracking:
    - alpha (FPR): probability of false membership
    - beta (FNR): probability of missed membership (0 for hash sets)

    Cardinality tracking:
    - _low_k, _high_k: bounds on set cardinality
    - Used for size-dependent FPR calculation
    """

    _elements: set[Trapdoor] = field(default_factory=set)
    _key_fingerprint: bytes = field(default=b'')
    alpha: float = 0.0  # False positive rate
    beta: float = 0.0   # False negative rate (always 0 for hash sets)
    _low_k: int = 0     # Lower bound on cardinality
    _high_k: int = 0    # Upper bound on cardinality

    def __post_init__(self):
        if self._elements:
            fingerprints = {t.key_fingerprint for t in self._elements}
            if len(fingerprints) > 1:
                raise ValueError("All trapdoors must have the same key")
            self._key_fingerprint = next(iter(fingerprints))
            # Initialize cardinality bounds if not set
            if self._low_k == 0 and self._high_k == 0:
                self._low_k = len(self._elements)
                self._high_k = len(self._elements)

    @classmethod
    def from_values(
        cls,
        values: Iterable[Union[str, bytes]],
        factory: TrapdoorFactory,
        alpha: float = 0.0
    ) -> BooleanSet:
        """Create a set from plaintext values.

        Args:
            values: Strings or bytes to add to the set.
            factory: TrapdoorFactory for transforming values.
            alpha: Initial false positive rate.
        """
        elements = {factory.create(v) for v in values}
        k = len(elements)
        return cls(
            _elements=elements,
            _key_fingerprint=factory.key_fingerprint,
            alpha=alpha,
            _low_k=k,
            _high_k=k
        )

    def __len__(self) -> int:
        return len(self._elements)

    def __iter__(self) -> Iterator[Trapdoor]:
        return iter(self._elements)

    def __contains__(self, item: Trapdoor) -> bool:
        """Raw membership test (use .contains() for approximate result)."""
        if item.key_fingerprint != self._key_fingerprint:
            raise ValueError("Trapdoor has incompatible key")
        return item in self._elements

    @property
    def cardinality_bounds(self) -> tuple[int, int]:
        """Return bounds on set cardinality (low, high).

        These bounds track the possible range of the latent set size.
        Used for size-dependent FPR calculations.
        """
        return (self._low_k, self._high_k)

    def membership_fpr(self, n_bits: int = 256) -> float:
        """Calculate size-dependent FPR for membership queries.

        The FPR depends on set size k: (1 - 2^{-(k+1)})^n

        Args:
            n_bits: Hash size in bits (default 256 for SHA-256).

        Returns:
            False positive rate for membership queries.
        """
        k = self._high_k  # Use upper bound for conservative estimate
        if k == 0:
            return 0.0
        # (1 - 2^{-(k+1)})^n
        return (1 - 2**(-(k+1)))**n_bits

    def subset_fpr(self, other: 'BooleanSet', n_bits: int = 256) -> float:
        """Calculate FPR for subset test (self ⊆ other).

        FPR is: (1 - (1 - 2^{-k1}) * 2^{-k2})^n

        Args:
            other: The superset candidate.
            n_bits: Hash size in bits.

        Returns:
            False positive rate for the subset test.
        """
        self._check_compatible(other)
        k1 = self._high_k  # Use upper bounds for conservative estimate
        k2 = other._high_k
        if k1 == 0 or k2 == 0:
            return 0.0
        # (1 - (1 - 2^{-k1}) * 2^{-k2})^n
        return (1 - (1 - 2**(-k1)) * 2**(-k2))**n_bits

    def contains(self, item: Trapdoor) -> BernoulliBoolean:
        """Membership test with explicit error rates.

        Returns:
            BernoulliBoolean indicating membership with error bounds.
        """
        if item.key_fingerprint != self._key_fingerprint:
            raise ValueError("Trapdoor has incompatible key")
        result = item in self._elements
        return BernoulliBoolean(result, alpha=self.alpha, beta=self.beta)

    def add(self, item: Trapdoor) -> None:
        """Add a trapdoor to the set."""
        if self._key_fingerprint and item.key_fingerprint != self._key_fingerprint:
            raise ValueError("Trapdoor has incompatible key")
        if not self._key_fingerprint:
            self._key_fingerprint = item.key_fingerprint
        was_present = item in self._elements
        self._elements.add(item)
        # Update cardinality bounds
        if not was_present:
            # Definitely added
            self._low_k += 1
            self._high_k += 1
        # If was_present, cardinality unchanged

    def __or__(self, other: BooleanSet) -> BooleanSet:
        """Union: S1 | S2 - elements in either set.

        FPR increases (either can give false positive).
        Cardinality: max(k1, k2) <= |union| <= k1 + k2
        """
        self._check_compatible(other)
        new_alpha, new_beta = compose_or(
            self.alpha, self.beta, other.alpha, other.beta
        )
        new_elements = self._elements | other._elements
        return BooleanSet(
            _elements=new_elements,
            _key_fingerprint=self._key_fingerprint,
            alpha=new_alpha,
            beta=new_beta,
            _low_k=max(self._low_k, other._low_k),
            _high_k=self._high_k + other._high_k
        )

    def __and__(self, other: BooleanSet) -> BooleanSet:
        """Intersection: S1 & S2 - elements in both sets.

        FPR decreases (both must give false positive).
        Cardinality: 0 <= |intersection| <= min(k1, k2)
        """
        self._check_compatible(other)
        new_alpha, new_beta = compose_and(
            self.alpha, self.beta, other.alpha, other.beta
        )
        new_elements = self._elements & other._elements
        return BooleanSet(
            _elements=new_elements,
            _key_fingerprint=self._key_fingerprint,
            alpha=new_alpha,
            beta=new_beta,
            _low_k=0,  # Could be empty
            _high_k=min(self._high_k, other._high_k)
        )

    def __xor__(self, other: BooleanSet) -> BooleanSet:
        """Symmetric difference: S1 ^ S2 - elements in exactly one set.

        Cardinality: |k1 - k2| <= |xor| <= k1 + k2
        (lower bound: if one is subset of other; upper: if disjoint)
        """
        self._check_compatible(other)
        # For symmetric difference, error analysis is more complex
        # Use conservative estimate
        new_alpha = self.alpha + other.alpha
        new_beta = self.beta + other.beta
        new_elements = self._elements ^ other._elements
        return BooleanSet(
            _elements=new_elements,
            _key_fingerprint=self._key_fingerprint,
            alpha=min(new_alpha, 1.0),
            beta=min(new_beta, 1.0),
            _low_k=abs(self._low_k - other._high_k),  # Conservative lower
            _high_k=self._high_k + other._high_k
        )

    def __sub__(self, other: BooleanSet) -> BooleanSet:
        """Difference: S1 - S2 - elements in S1 but not S2.

        Cardinality: max(0, k1 - k2) <= |diff| <= k1
        """
        self._check_compatible(other)
        new_elements = self._elements - other._elements
        return BooleanSet(
            _elements=new_elements,
            _key_fingerprint=self._key_fingerprint,
            alpha=self.alpha,
            beta=self.beta + other.alpha,  # Other's FP becomes our FN
            _low_k=max(0, self._low_k - other._high_k),
            _high_k=self._high_k
        )

    def _check_compatible(self, other: BooleanSet) -> None:
        """Verify sets have compatible keys."""
        if self._key_fingerprint != other._key_fingerprint:
            raise ValueError("Sets have incompatible keys")

    def __repr__(self) -> str:
        return f"BooleanSet({len(self)} elements, alpha={self.alpha:.4f})"
