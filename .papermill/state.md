---
title: "Boolean Algebra over Trapdoor Sets: A Practical Framework for Privacy-Preserving Set Operations with Probabilistic Guarantees"
stage: draft
format: latex
authors:
  - name: "Alexander Towell"
    email: "lex@metafunctor.com"
    orcid: "0000-0001-6443-9897"

thesis:
  claim: "Cryptographic hash functions combined with probabilistic data structures (HBOS) enable microsecond-scale privacy-preserving set operations with explicitly managed error rates, achieving 1000-10000x speedup over homomorphic encryption."
  novelty: "Layered privacy model separating oblivious representation (hash-hidden values) from Bernoulli query results (plaintext approximate answers with explicit error rates), with systematic error propagation through composed Boolean set operations."
  refined: "An approximate Boolean algebra homomorphism F maps the powerset algebra over a free semigroup (P(X*), cup, cap, complement) to a bit-vector algebra ({0,1}^n, |, &, ~) via cryptographic hash. F preserves union and intersection exactly but NOT complement. Membership testing yields Bernoulli Booleans with FPR = (1 - 2^{-(k+1)})^n and FNR = 0. The construction is a cipher map: encoding (hash with secret key) is a batch cipher map, Boolean operations are online cipher maps, and error composition rules give the correctness bounds. Space complexity is O(2^k) for single-level; two-level hashing achieves practical FPR for large sets."

prior_art:
  last_survey: null
  key_references:
    - "Gentry 2009 - Fully homomorphic encryption using ideal lattices"
    - "Yao 1982 - Protocols for secure computations"
    - "Dwork et al. 2006 - Calibrating noise to sensitivity in private data analysis"
    - "Bloom 1970 - Space/time trade-offs in hash coding with allowable errors"
    - "Flajolet et al. 2007 - HyperLogLog: near-optimal cardinality estimation"
    - "Freedman et al. 2004 - Efficient private matching and set intersection"
    - "Bellare et al. 2012 - Foundations of garbled circuits"
  gaps: "FHE and MPC are too slow for practical deployment; existing probabilistic data structures lack systematic cryptographic privacy guarantees and formal error propagation through composed operations."

experiments:
  - label: "Performance benchmarks"
    status: "design-only"
    note: "Microsecond-scale claims (0.4-2.1us) based on algorithm complexity analysis and microbenchmark design; comprehensive validated measurements ongoing."
  - label: "Scalability analysis"
    status: "design-only"
    note: "Size-dependent FPR analysis and two-level hashing scalability."
  - label: "Security evaluation"
    status: "design-only"
    note: "Dictionary attack resistance, frequency analysis, correlation leakage."
  - label: "Application validation"
    status: "design-only"
    note: "Private set intersection, secure deduplication, federated learning aggregation."

venue:
  target: null
  candidates: []

review_history:
  - date: "2026-03-19"
    reviewer: "papermill"
    verdict: "significant-revision"
    files:
      - ".papermill/thesis-analysis.md"
      - ".papermill/reviews/review-2026-03-19.md"
      - ".papermill/reviews/proof-check-2026-03-19.md"
    key_findings:
      - "Authentic core (pre-July-2024) is mathematically sound: Boolean algebra homomorphism, FPR derivations, complement non-preservation, two-level hashing, Bernoulli error composition"
      - "Significant Claude drift in post-549091a commits: HBOS branding, ORAM terminology, expanded applications, C++ appendix rewrite, generated literature survey with incorrect citations"
      - "Error propagation formulas (AND, OR, NOT) verified correct under independence"
      - "Size-dependent FPR formulas (membership, subset) verified correct"
      - "Bit-Rate Formula (Corollary 1) has an approximation error and confusing variable naming"
      - "C++ operator&& in Appendix A has a BUG: uses min(fpr1,fpr2) instead of fpr1*fpr2"
      - "Python library (cts/) passes all 59 tests; implementation matches paper formulas"
      - "Terminology issue: 'oblivious' conflicts with ORAM meaning; should use 'trapdoor' or 'hash-hidden'"
      - "Several bibliography entries have wrong years (McSherry 2021 should be 2007, Brakerski 2022 should be 2011)"
      - "Paper does not connect to cipher map formalism from parent repo"
    action_items:
      - "Strip Claude-generated padding (applications, related work, C++ appendix)"
      - "Replace HBOS/oblivious terminology with trapdoor/cipher-map terminology"
      - "Fix Corollary 1 (Bit-Rate Formula) approximation"
      - "Fix Corollary 2 to specify it applies only to OR/union chains"
      - "Fix C++ operator&& in Appendix A or remove Appendix A"
      - "Audit bibliography for incorrect years and fabricated entries"
      - "Connect to cipher map framework (batch cipher map = hash construction, online cipher map = Boolean operations)"
      - "Run actual benchmarks or remove performance claims"

related_papers:
  - path: ~/github/trapdoor-computing/papers/cipher-maps-unified
    rel: companion
    label: "Cipher maps unified formalism"
  - path: ~/github/bernoulli/papers/bernoulli_sets
    rel: foundation
    label: "Bernoulli set model (error propagation framework)"
  - path: ~/github/trapdoor-computing/papers/algebraic-cipher-types
    rel: sibling
    label: "Algebraic cipher types"
  - path: ~/github/trapdoor-computing/papers/crypto-perf-hash
    rel: sibling
    label: "Crypto performance hashing"
---

## Notes

Initialized by papermill on 2026-03-19.

Provenance: Pre-July-2024 commits (up to 549091a) are authentic. Later commits are Claude-drifted with ORAM formalism and expanded application sections.

The paper uses IEEE conference format (IEEEtran, 10pt). The tex file in `paper/main_comprehensive.tex` is the sole authored document (~987 lines). A Python implementation exists alongside (`cts/` package) with tests (`tests/`).

## Overview

Presents Hash-Based Oblivious Sets (HBOS), a framework for privacy-preserving set operations combining cryptographic hashing with probabilistic data structures. The core abstraction is a layered privacy model: values are hidden behind one-way hash transformations (oblivious representation), while operations return Bernoulli Booleans -- plaintext approximate results with explicit false positive rate (alpha) and false negative rate (beta). Error rates propagate systematically through composed Boolean operations (AND, OR, NOT, XOR) using Bernoulli type composition rules. The paper covers Boolean algebra framework, size-dependent FPR analysis, two-level hashing for scalability, privacy-space trade-offs, cardinality estimation, and applications to private set intersection, secure deduplication, and federated learning.

## Structure

1. Introduction (motivating example, contributions)
2. Background and Threat Model (hash functions, approximate data structures, threat model)
3. System Design (core abstractions, error propagation, layered privacy, architecture)
4. Mathematical Foundations (Boolean algebra framework, security analysis, approximate algebraic properties, size-dependent FPR, two-level hashing, unified hash construction, privacy-space trade-off, cardinality estimation)
5. Implementation
6. Evaluation (benchmarks, scalability, security, limitations, comparison)
7. Applications (PSI, deduplication, analytics, federated learning)
8. Related Work (FHE, MPC, PSI, approximate data structures, differential privacy)
9. Conclusion (current limitations)
10. Appendix: Implementation Details (C++ data structures, optimization, key management, concepts, parallel execution)
