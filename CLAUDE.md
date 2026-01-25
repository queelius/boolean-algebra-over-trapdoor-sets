# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A minimal Python library (~200 lines) for privacy-preserving set operations using cryptographic trapdoor functions. Part of a larger research monorepo on oblivious computing.

**Key insight**: One-way hash transformations enable equality testing and set operations on encrypted data without revealing underlying values.

## Quick Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run single test class or method
pytest tests/test_cts.py::TestBooleanSet -v
pytest tests/test_cts.py::TestBooleanSet::test_union -v

# Run tests with coverage
pytest --cov=cts --cov-report=term-missing tests/

# Run demo
python examples/demo.py

# Build paper (from project root)
cd paper && pdflatex main_comprehensive.tex && bibtex main_comprehensive && pdflatex main_comprehensive.tex && pdflatex main_comprehensive.tex
```

## Architecture

### Core Modules (`cts/`)

The library is built around the Bernoulli types framework - all operations return `BernoulliBoolean` with false positive/negative rates (α, β).

```
cts/
├── __init__.py          # Package exports
├── hash_value.py        # HashValue: fixed-size bytes with bitwise ops
├── approximate.py       # BernoulliBoolean + error composition + mutual_information
├── trapdoor.py          # Trapdoor + TrapdoorFactory
└── boolean_set.py       # BooleanSet with full Boolean algebra
```

### Type Hierarchy

1. **`HashValue`** - Fixed-size byte array with bitwise operations (`^`, `&`, `|`, `~`)

2. **`Trapdoor`** - One-way transformed value: `T_k(v) = H(k || v)`
   - Created via `TrapdoorFactory` with secret key
   - Equality comparison checks key compatibility

3. **`BernoulliBoolean`** - Boolean with explicit error rates (second-order)
   - `.value` - the observed result
   - `.alpha`, `.beta` - false positive/negative rates
   - `.confidence` - probability of correctness (1 - α - β)
   - `.confusion_matrix` - 2×2 latent→observed transition matrix
   - `.posterior(prior)` - Bayesian update P(latent=True | observation)

4. **`BooleanSet`** - Full Boolean algebra on trapdoor sets
   - Operations: `|` (union), `&` (intersection), `^` (XOR), `-` (difference)
   - Error rates propagate through operations
   - Cardinality tracking: `.cardinality_bounds`, `.membership_fpr()`, `.subset_fpr()`

### Error Propagation Formulas

```python
# AND: FPR decreases, FNR increases
compose_and(a1, b1, a2, b2) -> (a1*a2, b1 + b2 - b1*b2)

# OR: FPR increases, FNR decreases
compose_or(a1, b1, a2, b2) -> (a1 + a2 - a1*a2, b1*b2)

# NOT: rates swap
compose_not(a, b) -> (b, a)

# XOR: symmetric error rates
compose_xor(a1, b1, a2, b2) -> (error, error)

# Mutual information: I(latent; observed) in bits [0, 1]
mutual_information(alpha, beta, prior=0.5) -> float
```

## Theoretical Framework

The paper (`paper/main_comprehensive.tex`) uses the Bernoulli types framework:

- **Latent vs Observed**: Latent values (`b`, `S`) are true objects; observed values (`b̃`, `S̃`) are approximations with error rates
- **Error notation**: `α` = false positive rate, `β` = false negative rate
- **Confusion matrix**: Row-stochastic 2×2 matrix [[1-α, α], [β, 1-β]]
- **Error composition**: Union increases FPR (`α₁ + α₂ - α₁α₂`), intersection reduces it (`α₁ · α₂`)

### Security Model

- Preimage-based privacy (not semantic security)
- Vulnerable to dictionary attacks on low-entropy inputs
- Frequency and correlation patterns are leaked
- Suitable when input domains have high entropy

## Testing

Tests cover: `HashValue` bitwise ops, `BernoulliBoolean` error handling, `compose_*` formulas, `Trapdoor` transformations, `BooleanSet` operations with error propagation, confusion matrix/posterior/mutual information, cardinality tracking, and size-dependent FPR.

## Python Requirements

- Python 3.10+
- No external dependencies (stdlib only)
- pytest, pytest-cov for testing (dev dependencies)
