"""One-way trapdoor transformation for privacy-preserving equality testing."""

from __future__ import annotations
import hashlib
import secrets
from dataclasses import dataclass
from typing import Union

from .hash_value import HashValue
from .approximate import BernoulliBoolean


@dataclass(frozen=True, slots=True)
class Trapdoor:
    """A one-way transformed value: T_k(v) = H(k || v).

    Trapdoors can be compared for equality, but the original value
    cannot be recovered without knowing the key.
    """

    hash: HashValue
    key_fingerprint: bytes  # First 8 bytes of H(key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Trapdoor):
            return NotImplemented
        if self.key_fingerprint != other.key_fingerprint:
            raise ValueError("Cannot compare trapdoors with different keys")
        return self.hash == other.hash

    def __hash__(self) -> int:
        return hash((self.hash.data, self.key_fingerprint))

    def equals(self, other: Trapdoor, fpr: float = 0.0) -> BernoulliBoolean:
        """Compare trapdoors with explicit error rates.

        Args:
            other: Another trapdoor to compare
            fpr: False positive rate (collision probability)

        Returns:
            BernoulliBoolean with the comparison result
        """
        if self.key_fingerprint != other.key_fingerprint:
            raise ValueError("Cannot compare trapdoors with different keys")
        result = self.hash == other.hash
        # FNR is 0 for hash equality (no false negatives)
        return BernoulliBoolean(result, alpha=fpr, beta=0.0)

    def __repr__(self) -> str:
        return f"Trapdoor({self.hash.hex()[:16]}...)"


class TrapdoorFactory:
    """Factory for creating trapdoors with a secret key.

    Usage:
        factory = TrapdoorFactory()  # generates random key
        t1 = factory.create("alice")
        t2 = factory.create("bob")
        print(t1 == t2)  # False
    """

    def __init__(self, key: Union[bytes, None] = None, hash_size: int = 32):
        """Initialize factory with a secret key.

        Args:
            key: Secret key bytes. If None, generates random 32-byte key.
            hash_size: Size of output hash in bytes (default: 32 for SHA-256).
        """
        self._key = key if key is not None else secrets.token_bytes(32)
        self._hash_size = hash_size
        self._fingerprint = hashlib.sha256(self._key).digest()[:8]

    @property
    def key_fingerprint(self) -> bytes:
        """Public fingerprint for key compatibility checking."""
        return self._fingerprint

    def create(self, value: Union[str, bytes]) -> Trapdoor:
        """Transform a value into a trapdoor.

        Args:
            value: The value to transform (string or bytes).

        Returns:
            A Trapdoor that hides the original value.
        """
        if isinstance(value, str):
            value = value.encode('utf-8')

        # T_k(v) = H(k || v)
        h = hashlib.sha256(self._key + value)
        hash_bytes = h.digest()[:self._hash_size]

        return Trapdoor(
            hash=HashValue(hash_bytes),
            key_fingerprint=self._fingerprint
        )

    def collision_probability(self) -> float:
        """Theoretical collision probability for this hash size.

        Based on birthday paradox: ~1/2^(n/2) for n-bit hash.
        For 256-bit hash, this is ~2^-128, essentially zero.
        """
        bits = self._hash_size * 8
        return 2.0 ** (-bits / 2)
