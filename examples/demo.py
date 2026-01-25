#!/usr/bin/env python3
"""Demonstration of cipher trapdoor sets.

Shows privacy-preserving set operations with explicit error tracking.
"""

from cts import TrapdoorFactory, BooleanSet


def main():
    print("=== Cipher Trapdoor Sets Demo ===\n")

    # Create a factory with a secret key
    factory = TrapdoorFactory()
    print(f"Created factory with key fingerprint: {factory.key_fingerprint.hex()}\n")

    # Create sets from plaintext values
    # In practice, the plaintexts would never be seen together
    alice_contacts = BooleanSet.from_values(
        ["bob", "carol", "dave"], factory, alpha=0.01
    )
    bob_contacts = BooleanSet.from_values(
        ["alice", "carol", "eve"], factory, alpha=0.01
    )

    print(f"Alice's contacts: {alice_contacts}")
    print(f"Bob's contacts:   {bob_contacts}\n")

    # Set operations with error propagation
    print("--- Set Operations ---")

    # Union: contacts known by either party
    union = alice_contacts | bob_contacts
    print(f"Union (either):        {union}")
    print(f"  FPR increased: {alice_contacts.alpha:.4f} + {bob_contacts.alpha:.4f} -> {union.alpha:.4f}")

    # Intersection: contacts known by both
    intersection = alice_contacts & bob_contacts
    print(f"Intersection (both):   {intersection}")
    print(f"  FPR decreased: {alice_contacts.alpha:.4f} * {bob_contacts.alpha:.4f} -> {intersection.alpha:.4f}")

    # Symmetric difference: contacts known by exactly one party
    xor = alice_contacts ^ bob_contacts
    print(f"Symmetric diff (XOR):  {xor}\n")

    # Membership testing
    print("--- Membership Tests ---")
    carol = factory.create("carol")
    frank = factory.create("frank")

    result = alice_contacts.contains(carol)
    print(f"Carol in Alice's contacts: {result.value} (confidence: {result.confidence:.2%})")

    result = alice_contacts.contains(frank)
    print(f"Frank in Alice's contacts: {result.value} (confidence: {result.confidence:.2%})\n")

    # Privacy property: the trapdoor reveals nothing about the original value
    print("--- Privacy Property ---")
    print(f"Trapdoor for 'carol': {factory.create('carol')}")
    print(f"Trapdoor for 'frank': {factory.create('frank')}")
    print("(Without the key, these reveal nothing about 'carol' or 'frank')")


if __name__ == "__main__":
    main()
