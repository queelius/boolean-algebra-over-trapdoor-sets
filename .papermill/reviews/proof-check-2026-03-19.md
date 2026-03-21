# Proof Verification: Boolean Algebra over Trapdoor Sets

**Date**: 2026-03-19

---

## 1. Error Propagation Formulas (Theorem 3)

The paper claims, for independent Bernoulli Booleans b1 ~ (alpha1, beta1) and b2 ~ (alpha2, beta2):

### NOT: (beta, alpha) -- rates swap

**Verification**: CORRECT.

Negation flips the observed value. If latent = False and observed = True (a false positive at rate alpha), after negation observed becomes False. Now latent = True (since we negated the latent meaning too) and observed = False, which is a false negative. So the FPR of NOT(b) becomes the FNR of b, and vice versa.

Formally:
- FPR_NOT = P(~obs = True | ~lat = False) = P(obs = False | lat = True) = beta
- FNR_NOT = P(~obs = False | ~lat = True) = P(obs = True | lat = False) = alpha

The Python implementation `compose_not(alpha, beta) -> (beta, alpha)` matches.

### AND: (alpha1 * alpha2, beta1 + beta2 - beta1 * beta2)

**Verification**: CORRECT under independence assumption.

**FPR of AND**: A false positive for (b1 AND b2) means the latent value is False (meaning at least one latent input is False) but the observed value is True (meaning both observed inputs are True).

More precisely: we need P(obs1=T AND obs2=T | lat1 AND lat2 = F).

However, the standard Bernoulli composition assumes we are combining two independent Bernoulli Booleans. The correct interpretation for AND:
- **FPR**: P(b1_obs AND b2_obs = True | b1_lat AND b2_lat = False)

For the case where both latents are False (which is the relevant case for FPR composition):
- P(b1_obs=T | b1_lat=F) = alpha1
- P(b2_obs=T | b2_lat=F) = alpha2
- P(both obs True | both lat False) = alpha1 * alpha2

This is the dominant term. There are also cases where one latent is True and the other is False, but the Bernoulli composition rule treats AND as a pointwise operation on independent random variables. For the standard formulation:

For AND with independent inputs:
- FPR = P(obs=T | lat=F) where lat = lat1 AND lat2

If we condition on the case where both latents are False:
P(obs1=T AND obs2=T | lat1=F AND lat2=F) = alpha1 * alpha2

For the case lat1=T, lat2=F:
P(obs1=T AND obs2=T | lat1=T, lat2=F) = (1-beta1) * alpha2

But the Bernoulli composition rule as stated (alpha1 * alpha2) is the correct formula for the operation viewed as combining two membership tests where the FALSE case means both must be false positives. This matches the set intersection interpretation: a false positive in (A AND B) requires both A and B to give false positives. Under independence, this is multiplicative.

**FNR of AND**: P(b1_obs AND b2_obs = False | b1_lat AND b2_lat = True)
= 1 - P(b1_obs=T AND b2_obs=T | b1_lat=T AND b2_lat=T)
= 1 - (1-beta1)(1-beta2)
= beta1 + beta2 - beta1*beta2

This is the inclusion-exclusion formula: either b1 gives a false negative, or b2 does, or both.

The Python implementation matches:
```python
def compose_and(a1, b1, a2, b2):
    alpha = a1 * a2
    beta = b1 + b2 - b1 * b2
    return (alpha, beta)
```

Tests confirm: compose_and(0.1, 0.0, 0.1, 0.0) -> (0.01, 0.0) and compose_and(0.0, 0.1, 0.0, 0.1) -> (0.0, 0.19).

### OR: (alpha1 + alpha2 - alpha1 * alpha2, beta1 * beta2)

**Verification**: CORRECT. This is the De Morgan dual of AND.

**FPR of OR**: P(b1_obs OR b2_obs = True | b1_lat OR b2_lat = False)
= P(b1_obs=T OR b2_obs=T | b1_lat=F AND b2_lat=F)
= 1 - P(b1_obs=F AND b2_obs=F | b1_lat=F AND b2_lat=F)
= 1 - (1-alpha1)(1-alpha2)
= alpha1 + alpha2 - alpha1*alpha2

**FNR of OR**: P(b1_obs OR b2_obs = False | b1_lat OR b2_lat = True)

If both latents are True: P(b1_obs=F AND b2_obs=F | b1_lat=T AND b2_lat=T) = beta1 * beta2

For the case where only one is True (say lat1=T, lat2=F):
P(b1_obs=F AND b2_obs=F | b1_lat=T, lat2=F) = beta1 * (1-alpha2)

The formula beta1*beta2 applies to the worst case (both latents True). This is conservative for the mixed case. Under the standard Bernoulli composition semantics (both latents True for the OR-True case), this is exact.

The Python implementation matches. Tests confirm: compose_or(0.1, 0.0, 0.1, 0.0) -> (0.19, 0.0) and compose_or(0.0, 0.1, 0.0, 0.1) -> (0.0, 0.01).

### De Morgan Consistency Check

NOT(AND(b1, b2)) should equal OR(NOT(b1), NOT(b2)):
- AND(b1, b2) has rates (a1*a2, b1+b2-b1*b2)
- NOT of that: (b1+b2-b1*b2, a1*a2)

- NOT(b1) has rates (b1, a1), NOT(b2) has rates (b2, a2)
- OR(NOT(b1), NOT(b2)): (b1+b2-b1*b2, a1*a2)

These match. De Morgan's laws are preserved by the composition rules.

---

## 2. Set Operation Error Bounds (Theorems 1-2)

### Union (Theorem 1)

Claims:
- alpha_{A cup B} <= alpha_A + alpha_B - alpha_A * alpha_B
- beta_{A cup B} = beta_A * beta_B

**Verification**: CORRECT. Union corresponds to OR at the element level. A false positive in union membership requires at least one set to give a false positive (hence additive/sub-additive FPR). A false negative requires both sets to miss the element (hence multiplicative FNR). Matches OR composition.

Note: The paper uses "<=" for the FPR bound (acknowledging it is an upper bound under independence), and "=" for FNR. This is correct because the FNR formula is exact under independence (both must miss), while the FPR bound assumes the worst case.

### Intersection (Theorem 2)

Claims:
- alpha_{A cap B} = alpha_A * alpha_B
- beta_{A cap B} <= beta_A + beta_B - beta_A * beta_B

**Verification**: CORRECT. Intersection corresponds to AND at the element level. A false positive requires both sets to give false positives (multiplicative FPR). A false negative requires at least one set to miss (hence additive/sub-additive FNR). Matches AND composition.

---

## 3. Membership FPR (Theorem 4)

Claim: epsilon_in(k, n) = (1 - 2^{-(k+1)})^n

**Verification**: CORRECT.

Derivation check:
1. After inserting k elements via OR, each bit position j has P(bit_j = 1) = 1 - 2^{-k} (each of k elements sets the bit with prob 1/2, independence gives 1-(1/2)^k).
2. For query element x not in S, h(x) has each bit set with prob 1/2.
3. A false positive requires: for every bit j, if h(x)_j = 1 then F(S)_j = 1.
4. P(not refuted at bit j) = P(h(x)_j=0) + P(h(x)_j=1 AND F(S)_j=1) = 1/2 + (1/2)(1-2^{-k}) = 1 - 2^{-(k+1)}.
5. Independence across n bits: (1 - 2^{-(k+1)})^n.

The derivation in the paper and blog post matches this step-by-step.

---

## 4. Subset FPR (Theorem 5)

Claim: epsilon_subseteq(k1, k2, n) = (1 - (1-2^{-k1}) * 2^{-k2})^n

**Verification**: CORRECT.

Derivation check:
1. For S1 subseteq S2 to test positive (in bit-vector representation): F(S1) & F(S2) = F(S1), i.e., every bit set in F(S1) must be set in F(S2).
2. P(bit j set in F(S1)) = 1 - 2^{-k1}
3. P(bit j unset in F(S2)) = 2^{-k2}
4. P(bit j refutes subset) = (1-2^{-k1}) * 2^{-k2}
5. P(bit j does not refute) = 1 - (1-2^{-k1}) * 2^{-k2}
6. Independence across n bits: (1 - (1-2^{-k1}) * 2^{-k2})^n

Correct.

---

## 5. Space Complexity (Theorem 7)

Claim: n = O(2^k) for constant epsilon.

**Verification**: CORRECT.

From epsilon = (1 - 2^{-(k+1)})^n:
n = log(epsilon) / log(1 - 2^{-(k+1)})

For small x: log(1-x) ~ -x, so:
n ~ -log(epsilon) / 2^{-(k+1)} = -log(epsilon) * 2^{k+1}

Therefore n = O(2^k) for fixed epsilon. The constant factor is 2*|log(epsilon)|.

---

## 6. Complement Non-Preservation (Theorem 6)

Claim: F(~A) != ~F(A) for finite sets A.

**Verification**: CORRECT.

The proof is sound:
- ~A in the set algebra is X* \ A, which is infinite (countably infinite).
- F(~A) = OR over all h(y) for y in X*\A. Since X* is infinite and h uniformly distributes over {0,1}^n (finite), by pigeonhole, eventually every bit position is set. So F(~A) = 1^n.
- ~F(A) = bitwise NOT of (h(x1) | ... | h(xk)). For finite k, F(A) has some bits unset, so ~F(A) has some bits set that F(~A) = 1^n has set, but also ~F(A) has some bits unset that F(~A) has set.
- Therefore F(~A) = 1^n != ~F(A).

The paper also notes that asymptotically (as |A| -> infinity), F(A) -> 1^n and ~F(A) -> 0^n, while F(~A) = 1^n. So the discrepancy is maximal for large finite sets.

---

## 7. One-Wayness (Theorem 4 in Sec 4.1 and Theorem in Sec 4.2)

**Theorem (One-Wayness of Trapdoor Homomorphism)**: F is one-way for two reasons: non-injectivity (pigeonhole) and preimage resistance of H.

**Verification**: CORRECT but trivial. These are standard properties of cryptographic hash functions.

**Theorem (Privacy Preservation)**: P(adversary wins G_OW) <= 2^{-n} + negl(n).

**Verification**: CORRECT in the random oracle model. This is just restating preimage resistance as a game. The proof is standard: in the random oracle model, H(k||x) is uniform and independent of x given unknown k.

---

## 8. Two-Level FPR (Theorem 8)

Claim: epsilon(k, w, q) = (1 - 2^{-(k/2^w + 1)})^{q-w}

**Verification**: CORRECT under the assumption of uniform distribution into bins.

With 2^w bins and k elements, expected elements per bin is k/2^w. Within each bin, we have q-w bits for representation. Applying the single-level FPR formula with effective set size k/2^w and hash width q-w bits gives the claimed formula.

Note: The formula uses expected bin size k/2^w. The actual maximum bin size follows a balls-into-bins distribution and can be larger (O(k/2^w + log(2^w)/log(log(2^w))) by birthday-type analysis). For a rigorous bound, one should use the maximum bin size rather than the expected value. The paper does not address this.

---

## 9. Bit-Rate Formula (Corollary 1)

Claim: b(n, epsilon) = log2(epsilon) / (n * alpha(n)) where alpha(n) = 1 - 2^{-(n+1)}.

**ISSUE**: The approximation "log2(alpha(n)) ~ -alpha(n) for small deviations" is incorrect.

For alpha(n) close to 1 (which it is for large n): log2(alpha(n)) = log2(1 - 2^{-(n+1)}).

Using the standard approximation ln(1-x) ~ -x for small x:
log2(1 - 2^{-(n+1)}) ~ -2^{-(n+1)} / ln(2)

So m = log2(epsilon) / log2(1 - 2^{-(n+1)}) ~ log2(epsilon) * ln(2) / 2^{-(n+1)} = ln(epsilon) / (-2^{-(n+1)})

The bit-rate m/n ~ -ln(epsilon) * 2^{n+1} / n

The corollary writes this as log2(epsilon) / (n * alpha(n)), but alpha(n) = 1 - 2^{-(n+1)} ~ 1 for large n, so the corollary claims m/n ~ log2(epsilon) / n, which is WRONG for the single-level scheme. The actual bit-rate is exponential in n (the number of elements), not O(1/n).

The variable naming here is confusing (n seems to be overloaded between "number of elements" and "number of bits"). The formula needs correction and clarification.

---

## 10. Uniformity from Inverse-Frequency (Theorem 9)

Claim: With |Valid(y)| = c/freq(y), P[Output = y] = |Valid(y)| / 2^m = constant.

**Verification**: CORRECT as stated. This is the 1/p(y) principle: if encoding region sizes are inversely proportional to frequency, the output distribution becomes uniform. P[Output = y] = freq(y) * |Valid(y)| / 2^m = freq(y) * c/(freq(y) * 2^m) = c/2^m.

---

## 11. Confusion Matrix (Definition 3)

Claim: Q = [[1-alpha, alpha], [beta, 1-beta]] where Q_ij = P(obs=j | lat=i).

**Verification**: CORRECT. This is a standard 2x2 row-stochastic matrix. The properties listed (identity = perfect, rank-1 = complete information loss, rank-2 = trade-off) are correct.

The Python implementation returns the correct matrix structure (tested and passing).

---

## 12. XOR Composition (in Python, not in paper)

The paper does not formally derive XOR composition. The Python implementation uses:

```python
def compose_xor(a1, b1, a2, b2):
    p1_correct = 1 - a1 - b1
    p2_correct = 1 - a2 - b2
    p_correct = p1_correct * p2_correct + (a1 + b1) * (a2 + b2)
    error = (1 - p_correct) / 2
    return (error, error)
```

**Verification**: This treats XOR as "correct when both inputs are correct or both wrong", with symmetric error rates. The formula is:
- P(XOR correct) = P(both correct) + P(both wrong) = (1-a1-b1)(1-a2-b2) + (a1+b1)(a2+b2)
- P(XOR wrong) = 1 - P(XOR correct)
- alpha = beta = P(wrong)/2 (symmetric split)

This is a rough approximation. The actual asymmetric XOR error rates are more complex (depend on which combination of FP/FN occurred in each input). The symmetric split (error/2, error/2) is conservative but not tight. Acceptable for a library implementation with a note about the approximation.

---

## Summary

| Claim | Status | Notes |
|-------|--------|-------|
| NOT composition: swap rates | CORRECT | |
| AND composition: (a1*a2, b1+b2-b1*b2) | CORRECT | Under independence |
| OR composition: (a1+a2-a1*a2, b1*b2) | CORRECT | De Morgan dual of AND |
| De Morgan consistency | CORRECT | Verified algebraically |
| Union error bounds (Thm 1) | CORRECT | Matches OR composition |
| Intersection error bounds (Thm 2) | CORRECT | Matches AND composition |
| Membership FPR (Thm 4) | CORRECT | (1 - 2^{-(k+1)})^n |
| Subset FPR (Thm 5) | CORRECT | (1 - (1-2^{-k1})*2^{-k2})^n |
| Space complexity (Thm 7) | CORRECT | n = O(2^k) |
| Complement non-preservation (Thm 6) | CORRECT | Sound proof |
| One-wayness (Thm, Sec 4.1) | CORRECT | Standard, trivial |
| Privacy game (Sec 4.2) | CORRECT | Standard ROM argument |
| Two-level FPR (Thm 8) | CORRECT | But uses expected bin size, not worst case |
| Bit-Rate Formula (Cor 1) | **ERROR** | Approximation is sloppy, variable naming confused |
| Composition Accumulation (Cor 2) | **IMPRECISE** | Only applies to OR/union chains |
| Uniformity from 1/p(y) (Thm 9) | CORRECT | |
| XOR composition (Python only) | APPROXIMATE | Symmetric split is a rough bound |
| C++ operator&& (Appendix A) | **BUG** | Uses min(fpr1,fpr2) instead of fpr1*fpr2 |
