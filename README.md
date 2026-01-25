# Cipher Trapdoor Sets (CTS)

A minimal Python library for privacy-preserving set operations using cryptographic trapdoor functions. Implements the core algorithms from the accompanying research paper.

## Key Insight

**One-way hash transformations enable equality testing and set operations on encrypted data without revealing underlying values.**

## Installation

```bash
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Quick Start

```python
from cts import TrapdoorFactory, BooleanSet

# Create a factory with a secret key
factory = TrapdoorFactory()

# Create privacy-preserving sets from plaintext values
alice_contacts = BooleanSet.from_values(["bob", "carol", "dave"], factory)
bob_contacts = BooleanSet.from_values(["alice", "carol", "eve"], factory)

# Set operations - work on encrypted data
common = alice_contacts & bob_contacts  # Intersection
all_contacts = alice_contacts | bob_contacts  # Union

# Membership testing with explicit error bounds
carol = factory.create("carol")
result = alice_contacts.contains(carol)
print(f"Contains carol: {result.value} (confidence: {result.confidence:.2%})")
```

## Core Concepts

### Trapdoors
One-way cryptographic transformations: `T_k(v) = H(k || v)`

```python
factory = TrapdoorFactory(key=b'secret')
t1 = factory.create("alice")
t2 = factory.create("alice")
print(t1 == t2)  # True - same value, same key
```

### Bernoulli Booleans
All operations return `BernoulliBoolean` with explicit error rates (α = FPR, β = FNR):

```python
result = set.contains(trapdoor)
print(f"Value: {result.value}")
print(f"False positive rate: {result.alpha}")
print(f"Confidence: {result.confidence}")

# Bayesian posterior given prior probability
prior = 0.01  # rare event
posterior = result.posterior(prior)
```

### Error Propagation
Set operations compose error rates mathematically:

| Operation | FPR (α) | FNR (β) |
|-----------|---------|---------|
| AND (∩)   | α₁·α₂   | β₁ + β₂ - β₁·β₂ |
| OR (∪)    | α₁ + α₂ - α₁·α₂ | β₁·β₂ |
| NOT       | β       | α (rates swap) |

### Boolean Sets
Full Boolean algebra on trapdoor sets:

```python
s1 | s2   # Union - FPR increases
s1 & s2   # Intersection - FPR decreases
s1 ^ s2   # Symmetric difference
s1 - s2   # Difference
```

## API Reference

### `HashValue`
Fixed-size byte array with bitwise operations (`^`, `&`, `|`, `~`).

### `BernoulliBoolean`
A boolean with explicit error rates (second-order Bernoulli type):
- `.value` - the observed result
- `.alpha` - false positive rate
- `.beta` - false negative rate
- `.confidence` - probability of correctness (1 - α - β)
- `.confusion_matrix` - 2×2 transition matrix [[1-α, α], [β, 1-β]]
- `.posterior(prior)` - Bayesian update P(latent=True | observation)

### `TrapdoorFactory`
Creates trapdoors from a secret key:
- `TrapdoorFactory(key=None)` - generates random key if not provided
- `.create(value)` - transform string/bytes to trapdoor
- `.key_fingerprint` - public fingerprint for compatibility checking

### `BooleanSet`
Privacy-preserving set with Boolean operations:
- `BooleanSet.from_values(values, factory)` - create from plaintexts
- `.contains(trapdoor)` - membership test returning `BernoulliBoolean`
- `|`, `&`, `^`, `-` - set operations with error propagation

## Running Tests

```bash
pytest tests/ -v
```

## Demo

```bash
python examples/demo.py
```

## Security Model

- **Preimage-based privacy**: Cannot recover original values without the key
- **Dictionary attacks**: Vulnerable if input domain has low entropy
- **Pattern leakage**: Frequency and correlation patterns may leak information
- **Suitable for**: High-entropy inputs where dictionary attacks are infeasible

## Research Paper

See `paper/main_comprehensive.tex` for the full theoretical treatment, including:
- Formal security analysis
- Error propagation proofs
- Relationship to Bernoulli types

## License

MIT License
