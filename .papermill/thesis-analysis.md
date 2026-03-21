# Thesis Analysis: Boolean Algebra over Trapdoor Sets

## Main Claim

The paper presents Hash-Based Oblivious Sets (HBOS), a framework for privacy-preserving set operations that combines cryptographic hash functions with probabilistic data structures. The central claim is that by embracing approximate operations with explicitly managed error rates (Bernoulli Booleans), one can achieve microsecond-scale privacy-preserving set operations -- 1000-10000x faster than FHE/MPC -- with privacy bounded by hash collision probabilities.

## Core Contribution

The paper's actual contribution is an **approximate Boolean algebra homomorphism** from the powerset algebra over a free semigroup to the algebra of fixed-width bit vectors:

```
F : (P(X*), cup, cap, complement, emptyset, X*) -> ({0,1}^n, |, &, ~, 0^n, 1^n)
```

where F(S) = h(x1) | h(x2) | ... | h(xk) for a cryptographic hash h.

This homomorphism is:
- **One-way**: by both non-injectivity (pigeonhole) and preimage resistance of h
- **Structure-preserving for union and intersection**: F(A cup B) = F(A) | F(B), F(A cap B) = F(A) & F(B)
- **NOT structure-preserving for complement**: F(~A) != ~F(A), because ~A is infinite and F(~A) = 1^n while ~F(A) has unset bits

## What Is Novel

The authentic core (pre-July-2024, from the blog post index.md) introduces:

1. **Free semigroup framing**: The domain algebra is explicitly over X* (the free semigroup on alphabet X), not just finite sets. This makes the complement non-preservation structurally clear rather than ad hoc.

2. **Size-dependent FPR analysis**: Membership FPR = (1 - 2^{-(k+1)})^n where k is set size and n is bit width. This is a precise Bloom-filter-like analysis applied to the raw bit-vector representation.

3. **Space complexity result**: Maintaining constant FPR requires n = O(2^k), limiting single-level schemes to small sets (k <= 20).

4. **Two-level hashing**: Partitioning elements into 2^w bins to reduce effective set size per bin, achieving practical FPR for large sets.

5. **Bernoulli Boolean error propagation**: Systematic composition rules for (alpha, beta) through AND, OR, NOT. These are the standard independence-assumption formulas, but the paper frames them cleanly within the Bernoulli types framework.

## Connection to Cipher Map Properties

The four cipher map properties map to HBOS as follows:

| Cipher Map Property | HBOS Realization |
|---|---|
| **Totality** | F is defined for all S in P(X*); h is defined for all x in X*. Every input produces an n-bit output. |
| **Representation Uniformity** | Hash outputs are uniformly distributed (random oracle model). The paper discusses the 1/p(y) principle (Sec 5.6) for achieving uniform output distributions. |
| **Correctness (eta-bounded)** | Operations return Bernoulli Booleans with explicit (alpha, beta). Membership has FPR = (1-2^{-(k+1)})^n, FNR = 0. This is the "eta" bound. |
| **Composability** | Error rates compose through Boolean operations: AND(alpha1*alpha2, beta1+beta2-beta1*beta2), OR(alpha1+alpha2-alpha1*alpha2, beta1*beta2), NOT(beta, alpha). |

The hash construction is a **batch cipher map** (encoding phase: transform all values offline with the secret key). The Boolean operations on bit vectors are **online cipher maps** (operate on encoded data without the key). The key distinction is that operations happen entirely in the hash domain -- the untrusted machine never sees plaintext.

## Layered Privacy Model

The paper explicitly separates two layers:
- **Oblivious representation**: Hash values hide the underlying data (preimage resistance)
- **Bernoulli query results**: Operations return plaintext approximate answers with explicit error rates

This is the correct framing for the trapdoor computing paradigm. The paper explicitly acknowledges it does NOT hide access patterns (unlike ORAM), and frames this as a deliberate trade-off for performance.

## Provenance Assessment

The authentic intellectual content traces clearly to the June 2023 blog post (trapdoor_bool_algebra/index.md at commit 549091a). The key ideas -- the free semigroup Boolean algebra, the approximate homomorphism F, the FPR derivations, the complement non-preservation proof, the two-level hashing -- all originate there. The current paper (main_comprehensive.tex) is a Claude-era rewrite that reorganizes this content into IEEE format and adds significant expansions (see review for details).
