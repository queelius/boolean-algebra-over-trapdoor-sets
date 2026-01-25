"""Fixed-size hash values with bitwise operations."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HashValue:
    """Fixed-size byte array supporting bitwise Boolean operations."""

    data: bytes

    def __post_init__(self):
        if not isinstance(self.data, bytes):
            object.__setattr__(self, 'data', bytes(self.data))

    @classmethod
    def from_hex(cls, hex_str: str) -> HashValue:
        return cls(bytes.fromhex(hex_str))

    def hex(self) -> str:
        return self.data.hex()

    def __len__(self) -> int:
        return len(self.data)

    def __xor__(self, other: HashValue) -> HashValue:
        """XOR operation."""
        if len(self) != len(other):
            raise ValueError("Hash lengths must match")
        return HashValue(bytes(a ^ b for a, b in zip(self.data, other.data)))

    def __and__(self, other: HashValue) -> HashValue:
        """AND operation."""
        if len(self) != len(other):
            raise ValueError("Hash lengths must match")
        return HashValue(bytes(a & b for a, b in zip(self.data, other.data)))

    def __or__(self, other: HashValue) -> HashValue:
        """OR operation."""
        if len(self) != len(other):
            raise ValueError("Hash lengths must match")
        return HashValue(bytes(a | b for a, b in zip(self.data, other.data)))

    def __invert__(self) -> HashValue:
        """NOT operation (bitwise complement)."""
        return HashValue(bytes(~b & 0xFF for b in self.data))

    def __repr__(self) -> str:
        if len(self.data) <= 8:
            return f"HashValue({self.hex()})"
        return f"HashValue({self.hex()[:16]}...)"
