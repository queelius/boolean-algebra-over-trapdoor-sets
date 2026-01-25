"""Cipher Trapdoor Sets - Privacy-preserving set operations.

Core types:
- HashValue: Fixed-size byte array with bitwise operations
- BernoulliBoolean: Boolean with explicit error rates (alpha, beta)
- Trapdoor: One-way transformed value for equality testing
- TrapdoorFactory: Creates trapdoors with a secret key
- BooleanSet: Set of trapdoors with Boolean algebra

Example:
    >>> from cts import TrapdoorFactory, BooleanSet
    >>> factory = TrapdoorFactory()
    >>> s1 = BooleanSet.from_values(["alice", "bob"], factory)
    >>> s2 = BooleanSet.from_values(["bob", "carol"], factory)
    >>> union = s1 | s2  # {"alice", "bob", "carol"}
    >>> intersection = s1 & s2  # {"bob"}
"""

from .hash_value import HashValue
from .approximate import (
    BernoulliBoolean,
    compose_and,
    compose_or,
    compose_not,
    compose_xor,
    mutual_information,
)
from .trapdoor import Trapdoor, TrapdoorFactory
from .boolean_set import BooleanSet

__all__ = [
    "HashValue",
    "BernoulliBoolean",
    "compose_and",
    "compose_or",
    "compose_not",
    "compose_xor",
    "mutual_information",
    "Trapdoor",
    "TrapdoorFactory",
    "BooleanSet",
]

__version__ = "0.5.0"
