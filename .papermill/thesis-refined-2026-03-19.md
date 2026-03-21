# Refined Thesis: Boolean Algebra over Trapdoor Sets

**Date**: 2026-03-19
**Source**: paper/main_comprehensive.tex, foundations/trapdoor-boolean-algebra.md, formalism/cipher-map-formalism.md
**Supersedes**: .papermill/thesis-analysis.md

---

## 1. Core Contribution (Stripped of Drift)

The authentic contribution of this paper is:

**An approximate Boolean algebra homomorphism $F$ from the powerset of the free semigroup to fixed-width bit vectors, via cryptographic hash, with precise error characterization.**

Specifically:

$$F : \bigl(\mathcal{P}(X^*),\ \cup,\ \cap,\ \complement,\ \emptyset,\ X^*\bigr) \longrightarrow \bigl(\{0,1\}^n,\ |,\ \&,\ \sim,\ 0^n,\ 1^n\bigr)$$

where $F(\{x_1, \ldots, x_k\}) = h(x_1) \mathbin{|} \cdots \mathbin{|} h(x_k)$ and $h$ is a cryptographic hash.

**What $F$ preserves exactly:**
- Union: $F(A \cup B) = F(A) \mathbin{|} F(B)$ (exact, by idempotency of OR)
- Identity elements: $F(\emptyset) = 0^n$, $F(X^*) = 1^n$ (by definition and pigeonhole)

**What $F$ preserves approximately:**
- Intersection: $F(A \cap B) \subseteq F(A) \mathbin{\&} F(B)$ (extra bits from cross-element collisions)
- Membership: $x \in_B S$ iff $h(x) \mathbin{\&} F(S) = h(x)$, with FPR $(1 - 2^{-(k+1)})^n$
- Subset: $S_1 \subseteq_B S_2$ iff $F(S_1) \mathbin{\&} F(S_2) = F(S_1)$, with FPR $(1 - (1-2^{-k_1}) 2^{-k_2})^n$

**What $F$ does not preserve:**
- Complement: $F(\complement A) = 1^n \neq \mathord{\sim} F(A)$ for any finite $A$ (by pigeonhole: the complement in $X^*$ is infinite, so its OR representation saturates all bits)

**Why $F$ is one-way:**
- Non-injectivity: infinitely many inputs per output (pigeonhole, $|X^*| = \aleph_0$, $|\{0,1\}^n| = 2^n$)
- Preimage resistance: $h$ is a cryptographic hash

---

## 2. What is Genuinely Novel

### Novel (original to this work)

1. **Free semigroup framing.** The domain algebra is explicitly $\mathcal{P}(X^*)$ -- the powerset of all finite strings over an alphabet. This is a stronger and more natural setting than "sets of elements" because: (a) it makes the complement non-preservation structurally inevitable (infinite complement vs. finite representation), and (b) it connects to the string-processing applications where the construction is most natural.

2. **Complement non-preservation proof.** The pigeonhole argument ($F(\complement A) = 1^n$ for finite $A$) is clean and original. While Bloom filter literature notes that "complement is not supported," this paper proves *why* at the algebraic level: the homomorphism breaks specifically at complement because OR of infinite hash values saturates.

3. **Size-dependent FPR formulas.** The membership FPR $\varepsilon = (1 - 2^{-(k+1)})^n$ and subset FPR $\varepsilon = (1 - (1-2^{-k_1}) 2^{-k_2})^n$ are precise closed-form expressions derived from first principles. While Bloom filter FPR analysis is well-studied, this specific formulation for the raw bit-vector OR construction (without $k$ hash functions) appears to be original.

4. **Space complexity result.** The proof that maintaining constant FPR requires $n = \mathcal{O}(2^k)$ bits is a direct consequence of the FPR formula, but the explicit statement and its implication (single-level scheme limited to $k \leq 20$) is a useful result.

5. **Two-level bin hashing.** The construction of partitioning into $2^w$ bins to reduce effective set size per bin, with precise FPR formula, is a practical extension.

### Known / related to existing results

1. **Bloom filter connection.** The bit-vector OR construction $F(S) = h(x_1) | \cdots | h(x_k)$ is essentially a Bloom filter with a single hash function ($k=1$ in Bloom filter notation). Standard Bloom filters use multiple hash functions to improve FPR at given space cost. The FPR formula $(1 - 2^{-(k+1)})^n$ is the single-hash-function specialization of the general Bloom filter FPR. This connection is not stated in the paper.

2. **Boolean error composition rules.** The AND/OR/NOT composition rules for independent Bernoulli Booleans are standard probability. They appear in reliability theory, Bayesian networks, and the Bloom filter composition literature. The paper presents them cleanly but does not claim novelty.

3. **One-wayness.** The one-wayness properties (non-injectivity + preimage resistance) are standard cryptographic hash properties, not novel.

4. **Marginal uniformity / 1/p(y) principle.** The idea of mapping elements to multiple hash representations inversely proportional to frequency originates in the author's Bernoulli types framework (separate work). It is authentically the author's idea, but it belongs to the Bernoulli types paper, not this one.

---

## 3. Connection to Cipher Map Framework

The trapdoor Boolean algebra is an **online construction cipher map** in the cipher map taxonomy (formalism/cipher-map-formalism.md, Section 2.3).

### Mapping to cipher map abstraction

| Cipher map component | Trapdoor Boolean algebra realization |
|---|---|
| **Latent function** $f$ | Set operations over $\mathcal{P}(X^*)$: membership, subset, intersection, union |
| **$\hat{f}$** (total function on bit strings) | Bitwise operations: $|$, $\&$, $\sim$ on $n$-bit vectors |
| **$\mathrm{enc}(x, k)$** | $h(x)$ = cryptographic hash of element (single encoding, $K=1$) |
| **$\mathrm{dec}(r)$** | Membership test: compare $r \mathbin{\&} F(S) = r$ (returns Bernoulli Boolean) |
| **Secret $s$** | Hash key $k$ (in $T_k(v) = H(k \| v)$) |

### The four cipher map properties

| Property | Status | Parameter value |
|---|---|---|
| **Totality** | Yes | Bitwise operations defined on all $\{0,1\}^n$ |
| **Representation uniformity** ($\delta$) | Marginal only | Hash outputs uniform under ROM; joint correlations leak |
| **Correctness** ($\eta$) | Operation-dependent | Union: $\eta = 0$ (exact). Membership: $\eta = (1-2^{-(k+1)})^n$. NOT: $\eta \to 1$ as $k \to \infty$ |
| **Composability** | Yes | Error rates compose via Bernoulli Boolean rules |

### Online vs. batch construction

This is the key distinguishing feature: the trapdoor Boolean algebra is an **online construction**. The cipher map $\hat{f}$ (bitwise operations) is defined by the hash structure alone -- no seed search is needed. The hash key is a secret, not a searched seed. This contrasts with batch constructions (HashSet, entropy map) where a seed is found to satisfy correctness constraints for all elements simultaneously.

**Consequences of online construction:**
- No construction cost beyond hashing
- Operations (union, intersection) can be performed by the untrusted machine without the key
- Space/accuracy trade-off is fixed by hash width $n$
- No tunable $\eta$ -- error rates are determined by set size and hash width

### The trusted/untrusted decomposition

- **Trusted machine**: holds hash key $k$, encodes elements as $T_k(x) = H(k \| x)$, decodes results (interprets Bernoulli Booleans)
- **Untrusted machine**: holds $F(S) = T_k(x_1) | \cdots | T_k(x_k)$ and performs bitwise operations ($|$, $\&$, membership test) without knowing $k$ or the elements

The untrusted machine never sees plaintext. It operates on opaque $n$-bit strings. Query results are Bernoulli Booleans -- plaintext approximate answers with explicit error rates. This is the "layered privacy model" the paper describes: the representation is hidden (one-way hash), but query results are observable.

---

## 4. What the Paper Should Say (Reframed Thesis)

### Title

"Boolean Algebra over Trapdoor Sets" (keep -- this is authentic and accurate).

Drop "HBOS" branding. Drop "oblivious" (misleading; the construction does not hide access patterns). Use "trapdoor" consistently.

### Central claim

The paper presents an approximate Boolean algebra homomorphism from the powerset of the free semigroup $X^*$ to fixed-width bit vectors via cryptographic hash, characterizes which algebraic operations are preserved exactly (union, identity), approximately (intersection, membership, subset), and not at all (complement), derives precise FPR formulas, establishes $\mathcal{O}(2^k)$ space complexity, and provides a two-level hashing scheme for scalability.

### Framing

This is a **cipher map for set operations** -- an online construction where the untrusted machine evaluates Boolean operations on hash-encoded sets without access to the hash key or plaintext elements. The error model is the Bernoulli Boolean framework: all operations return approximate results with explicit FPR/FNR. Union is exact; intersection introduces false positives from cross-element hash collisions; complement is not supported (inherent algebraic limitation, not an engineering gap).

### What to strip

1. **"HBOS" branding and "Hash-Based Oblivious Sets"**: Replace with "trapdoor Boolean algebra" or "cipher map over Boolean sets." The term "oblivious" has a specific meaning in cryptography (ORAM, oblivious transfer) that implies access-pattern hiding. This construction does not hide access patterns.

2. **All ORAM references**: Remove the citation to Wang et al. 2014 ("Oblivious data structures") and the comparison to ORAM in Remark 5. The construction is not related to ORAM.

3. **Expanded applications section (Sec 7)**: PSI, deduplication, analytics, federated learning are Claude-generated padding. Replace with the authentic motivating example (if any) from the blog post, or omit entirely.

4. **Expanded related work (Sec 8)**: The Claude-generated literature survey with 30+ references (many with incorrect years) should be stripped. Replace with: (a) Bloom filter references (the direct ancestor), (b) the Bernoulli types paper (error framework), (c) a brief note on FHE/MPC as the "exact but expensive" alternatives.

5. **Security game (Sec 4.2)**: The $\mathcal{G}_{OW}$ game is a standard formalism that adds nothing beyond restating preimage resistance. Remove or reduce to a sentence.

6. **C++ Appendix A**: The code does not match the authentic C++ implementation and contains bugs (wrong FPR formula in operator&&). Either use the authentic trapdoor<X,N>/trapdoor_set<X,N> code from 549091a, or omit.

7. **Performance benchmarks (Table 1, Figure 3)**: Entirely projected, no actual data. Remove.

8. **Bit-Rate Formula (Corollary 1)**: Contains an error. Remove or correct.

9. **Composition Accumulation (Corollary 2)**: Imprecise. Either make precise (specify operation, fix error term) or remove.

### What to add

1. **Explicit Bloom filter connection**: State that the construction is equivalent to a single-hash-function Bloom filter, and discuss how multi-hash-function Bloom filters achieve better FPR at the same space cost. This contextualizes the contribution honestly.

2. **Cipher map framing**: Explicitly connect to the cipher map framework (Definition 1.1 from formalism/cipher-map-formalism.md). Identify this as an online construction cipher map. State the four properties and parameter values.

3. **Intersection approximation**: In the homomorphism definition (current Definition 5), explicitly state that intersection is approximate: $F(A \cap B) \subseteq F(A) \mathbin{\&} F(B)$.

4. **Complement analysis for finite approximation**: While $F(\complement A) \neq \mathord{\sim} F(A)$, the paper should quantify how good/bad $\mathord{\sim} F(A)$ is as an approximation for small $|A|$. The formalism document notes that NOT is most accurate for small sets. This is the useful direction (small sets are where the construction works).

---

## 5. Novelty Assessment

| Contribution | Novelty | Notes |
|---|---|---|
| Free semigroup Boolean algebra framing | **Novel** | Natural setting for the construction; makes complement non-preservation structural |
| Complement non-preservation proof | **Novel** | Clean pigeonhole argument at algebraic level |
| Membership FPR $(1-2^{-(k+1)})^n$ | **Likely novel** for this specific construction | Related to single-hash Bloom filter analysis |
| Subset FPR formula | **Novel** | Not standard in Bloom filter literature |
| $n = O(2^k)$ space complexity | **Novel statement** | Consequence of FPR formula; explicit statement is new |
| Two-level hashing scheme | **Novel engineering** | Practical extension; standard bin-hashing idea applied to this context |
| Bernoulli Boolean error composition | **Known** | Standard probability; clean presentation |
| One-way hash properties | **Known** | Textbook material |
| 1/p(y) marginal uniformity | **Author's own** (from Bernoulli types) | Authentic but belongs to the companion paper |
| Online cipher map classification | **Novel framing** (from cipher map formalism) | Distinguishes this from batch constructions |

### Bottom line

The paper has a genuine, if modest, novel contribution: the characterization of which Boolean algebra operations survive the hash homomorphism and which do not, with precise error formulas. The complement non-preservation proof is the most distinctive result -- it explains at the algebraic level why Bloom filters (and this construction) cannot support complement. The FPR formulas are useful closed-form results. The space complexity and two-level scheme are practical contributions.

The contribution is strongest when positioned as: "a systematic algebraic analysis of the Boolean operations available under hash-based set encoding, with precise error formulas." It is weakest when positioned as: "a new privacy-preserving computation framework" (which overpromises relative to FHE/MPC and conflicts with established terminology).
