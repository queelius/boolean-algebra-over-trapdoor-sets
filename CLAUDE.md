# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A C++20 header-only library for privacy-preserving set operations using cryptographic trapdoor functions. Part of a larger research monorepo on oblivious computing.

**Key insight**: One-way hash transformations enable equality testing and set operations on encrypted data without revealing underlying values.

## Build Commands

```bash
# Standard build with tests and examples
cmake -B build -DCTS_BUILD_TESTS=ON -DCTS_BUILD_EXAMPLES=ON
cmake --build build -j$(nproc)

# Run all tests
cd build && ctest --output-on-failure

# Run single test
./build/tests/test_trapdoor

# Build with benchmarks (requires Google Benchmark)
cmake -B build -DCTS_BUILD_BENCHMARKS=ON
cmake --build build --target bench_trapdoor

# Build with sanitizers
cmake -B build -DCTS_ENABLE_SANITIZERS=ON
```

## Architecture

### Core Types (`include/cipher_trapdoor_sets/`)

The library is built around explicit approximation - all operations return `approximate_value<T>` with false positive/negative rates.

```
cts.hpp                    # Umbrella header - includes everything
├── core/
│   ├── hash_types.hpp     # hash_value<N> with bitwise ops, key_derivation
│   └── approximate_value.hpp  # Wraps values with FPR/FNR error rates
├── trapdoor.hpp           # One-way transformation: T → hash_value<N>
├── sets/
│   ├── boolean_set.hpp    # Full Boolean algebra (AND, OR, NOT, XOR)
│   └── symmetric_difference_set.hpp  # XOR-only operations
├── operations/
│   ├── batch_ops.hpp      # Batch operations for efficiency
│   ├── cardinality.hpp    # Approximate cardinality estimation
│   ├── homomorphic.hpp    # Homomorphic operations on encrypted sets
│   ├── similarity.hpp     # Jaccard similarity, MinHash
│   └── analytics.hpp      # Statistical analytics
├── key_management.hpp     # Key generation and verification
└── serialization/
    └── binary_format.hpp  # Binary serialization
```

### Type Hierarchy

1. **`trapdoor<T, N>`** - Core type representing one-way transformed value
   - Created via `trapdoor_factory<N>` with secret key
   - Equality comparison returns `approximate_bool`

2. **`boolean_set<T, N>`** - Full Boolean algebra on trapdoor sets
   - Operations: `|` (union), `&` (intersection), `^` (XOR), `~` (complement)
   - Created via `boolean_set_factory<T, N>`

3. **`approximate_value<T>`** - Wrapper making approximation explicit
   - `value()` - the result
   - `false_positive_rate()`, `false_negative_rate()` - error bounds

### Design Principles

- **Explicit approximation**: Error rates are always visible, never hidden
- **Key compatibility**: Operations throw if trapdoors have different key fingerprints
- **Composable error**: `compose_error_rates(e1, e2) = e1 + e2 - e1*e2`

## LaTeX Paper

The research paper "Hash-Based Oblivious Sets" (HBOS) is in `paper/`:
```bash
cd paper && pdflatex main_comprehensive.tex && bibtex main_comprehensive && pdflatex main_comprehensive.tex && pdflatex main_comprehensive.tex
```

### Theoretical Framework

The paper uses the Bernoulli types framework from `bernoulli-types/papers/final/`:

- **Latent vs Observed**: Latent values (`b`, `S`) are true objects; observed values (`b̃`, `S̃`) are approximations with error rates
- **Error notation**: `α` = false positive rate, `β` = false negative rate
- **Confusion matrix**: Captures error behavior as a 2×2 stochastic matrix
- **Error composition**: Union increases FPR (`α₁ + α₂ - α₁α₂`), intersection reduces it (`α₁ · α₂`)

### Security Model

- Preimage-based privacy (not semantic security)
- Vulnerable to dictionary attacks on low-entropy inputs
- Frequency and correlation patterns are leaked
- Suitable when input domains have high entropy

## Testing

Tests are simple executables (no test framework):
- `test_trapdoor.cpp` - Core trapdoor operations
- `test_sets.cpp` - Boolean and symmetric difference sets
- `test_operations.cpp` - Batch and homomorphic operations
- `test_homomorphic.cpp` - Homomorphic property verification
- `test_core.cpp`, `test_hash_types.cpp`, `test_approximate_value.cpp` - Core types

## C++ Requirements

- C++20 (concepts, ranges)
- CMake 3.20+
- Optional: Intel TBB for parallel STL (`CTS_HAS_PARALLEL_STL` defined when available)
