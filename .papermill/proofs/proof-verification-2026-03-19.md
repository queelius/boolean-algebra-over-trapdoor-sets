# Deep Proof Verification: Boolean Algebra over Trapdoor Sets

**Date**: 2026-03-19
**Source**: paper/main_comprehensive.tex
**Cross-references**: foundations/trapdoor-boolean-algebra.md (authentic blog post), formalism/cipher-map-formalism.md (cipher map abstraction)

---

## Methodology

For each formal claim in the paper, I state it precisely, identify assumptions (explicit and implicit), walk through the argument step-by-step, and give a verdict. Where the paper's proof is a sketch, I supply the missing steps. Where there are errors, I characterize them precisely.

Throughout: $h : X^* \to \{0,1\}^n$ is a cryptographic hash modeled as a random oracle (bits of $h(x)$ are i.i.d. Bernoulli(1/2), independent across distinct $x$). $F(S) = h(x_1) \mathbin{|} \cdots \mathbin{|} h(x_k)$ for $S = \{x_1, \ldots, x_k\}$.

---

## Claim 1: Union Error Bound (Theorem 1)

**Statement.** For sets $A$, $B$ with element-level FPR $\alpha_A, \alpha_B$ and FNR $\beta_A, \beta_B$:
$$\alpha_{A \cup B} \leq \alpha_A + \alpha_B - \alpha_A \alpha_B, \qquad \beta_{A \cup B} = \beta_A \beta_B$$

**Assumptions.** (1) $A$ and $B$ are independently constructed (error events independent). (2) "FPR of a set" means: the probability that a membership query for an element NOT in the set returns True.

**Step-by-step.**

- FPR of union: An element $x \notin A \cup B$ is falsely reported as a member of $A \cup B$ iff it is falsely reported in at least one of $A$ or $B$. Under independence:
  $$\alpha_{A \cup B} = 1 - (1 - \alpha_A)(1 - \alpha_B) = \alpha_A + \alpha_B - \alpha_A \alpha_B$$
  The paper uses "$\leq$" which is correct (it is exact under independence, and an upper bound if positive correlations exist).

- FNR of union: An element $x \in A \cup B$ is falsely reported as absent iff it is missed by every set it belongs to. If $x \in A \cap B$, the FNR is $\beta_A \beta_B$ (both must miss it). If $x \in A \setminus B$, the FNR is $\beta_A$ (only A's FNR matters). The formula $\beta_{A \cup B} = \beta_A \beta_B$ applies to the case where the element is in both sets. For elements in only one set, the FNR of the union inherits the single set's FNR.

  The paper's use of "=" is correct for the case where both sets contain the element (the standard Bernoulli composition interpretation: "union reports True" means "at least one reports True", and FNR is the probability all fail to report True). For elements in only one set, the formula is conservative (overestimates FNR if $\beta_A \beta_B < \beta_A$, which holds when $\beta_B < 1$). So $\beta_A \beta_B$ is actually a *lower bound* on FNR for single-set elements, not an upper bound.

  However, in the context of hash-based sets where $\beta = 0$ (no false negatives), this subtlety vanishes: $\beta_{A \cup B} = 0 \cdot 0 = 0$.

**Verdict: CORRECT** for the standard Bernoulli composition interpretation. The FPR formula is exact under independence. The FNR formula is exact when both sets contain the element.

---

## Claim 2: Intersection Error Bound (Theorem 2)

**Statement.** For sets $A$, $B$ with FPR $\alpha_A, \alpha_B$ and FNR $\beta_A, \beta_B$:
$$\alpha_{A \cap B} = \alpha_A \alpha_B, \qquad \beta_{A \cap B} \leq \beta_A + \beta_B - \beta_A \beta_B$$

**Assumptions.** Same as Claim 1.

**Step-by-step.**

- FPR of intersection: An element $x \notin A \cap B$ is falsely reported as a member iff *both* sets falsely report it. Under independence: $\alpha_{A \cap B} = \alpha_A \alpha_B$.

  Subtlety: if $x \in A \setminus B$, then $A$ correctly reports it (not a false positive from $A$), and $B$ falsely reports it with rate $\alpha_B$. The "false positive" for $A \cap B$ in this case requires $B$ to false-positive, giving rate $\alpha_B$, not $\alpha_A \alpha_B$. The formula $\alpha_A \alpha_B$ applies to the case $x \notin A$ AND $x \notin B$, which is the standard Bernoulli composition interpretation (both latents are False).

  For the hash-based set construction, both $A$ and $B$ membership queries are independently approximate, and the intersection test is AND of two Bernoulli Booleans. The formula is correct under this interpretation.

- FNR of intersection: An element $x \in A \cap B$ is missed iff *at least one* set misses it. Under independence:
  $$\beta_{A \cap B} = 1 - (1-\beta_A)(1-\beta_B) = \beta_A + \beta_B - \beta_A \beta_B$$

**Proof in paper.** The paper gives a one-line sketch: "a false positive requires both sets to report false positives (independent events). A false negative occurs if either set reports a false negative."

**Verdict: CORRECT** under the standard Bernoulli composition (AND of two independent Bernoulli Booleans).

---

## Claim 3: Boolean Error Composition (Theorem 3)

**Statement.** For independent approximate Booleans $\tilde{b}_1, \tilde{b}_2$ with rates $(\alpha_1, \beta_1)$, $(\alpha_2, \beta_2)$:
- $\neg\tilde{b}$: rates $(\beta, \alpha)$
- $\tilde{b}_1 \wedge \tilde{b}_2$: rates $(\alpha_1\alpha_2,\ \beta_1 + \beta_2 - \beta_1\beta_2)$
- $\tilde{b}_1 \vee \tilde{b}_2$: rates $(\alpha_1 + \alpha_2 - \alpha_1\alpha_2,\ \beta_1\beta_2)$

**Step-by-step.**

### NOT: $(\beta, \alpha)$

Negation flips the observed value. Consider the four conditional probabilities:
- $P(\widetilde{\neg b} = T \mid \neg b_{\text{lat}} = F) = P(\tilde{b} = F \mid b_{\text{lat}} = T) = \beta$
- $P(\widetilde{\neg b} = F \mid \neg b_{\text{lat}} = T) = P(\tilde{b} = T \mid b_{\text{lat}} = F) = \alpha$

So $\alpha_{\neg} = \beta$, $\beta_{\neg} = \alpha$. Correct.

### AND: $(\alpha_1\alpha_2,\ \beta_1 + \beta_2 - \beta_1\beta_2)$

FPR: $P(\tilde{b}_1 \wedge \tilde{b}_2 = T \mid b_{1,\text{lat}} \wedge b_{2,\text{lat}} = F)$.

Under the Bernoulli composition convention, we evaluate this for the case where both latent values are False (the defining case for FPR of a combined Boolean):
$$P(\tilde{b}_1 = T \mid b_1 = F) \cdot P(\tilde{b}_2 = T \mid b_2 = F) = \alpha_1 \alpha_2$$

FNR: $P(\tilde{b}_1 \wedge \tilde{b}_2 = F \mid b_1 = T \wedge b_2 = T)$:
$$= 1 - P(\tilde{b}_1 = T \mid b_1 = T) \cdot P(\tilde{b}_2 = T \mid b_2 = T) = 1 - (1-\beta_1)(1-\beta_2) = \beta_1 + \beta_2 - \beta_1\beta_2$$

### OR: $(\alpha_1 + \alpha_2 - \alpha_1\alpha_2,\ \beta_1\beta_2)$

FPR: $P(\tilde{b}_1 \vee \tilde{b}_2 = T \mid b_1 = F \wedge b_2 = F)$:
$$= 1 - P(\tilde{b}_1 = F \mid b_1 = F) \cdot P(\tilde{b}_2 = F \mid b_2 = F) = 1 - (1-\alpha_1)(1-\alpha_2) = \alpha_1 + \alpha_2 - \alpha_1\alpha_2$$

FNR: $P(\tilde{b}_1 \vee \tilde{b}_2 = F \mid b_1 = T \wedge b_2 = T)$:
$$= P(\tilde{b}_1 = F \mid b_1 = T) \cdot P(\tilde{b}_2 = F \mid b_2 = T) = \beta_1 \beta_2$$

### De Morgan consistency check

$\neg(\tilde{b}_1 \wedge \tilde{b}_2)$ has rates: NOT of $(\alpha_1\alpha_2, \beta_1+\beta_2-\beta_1\beta_2)$ = $(\beta_1+\beta_2-\beta_1\beta_2, \alpha_1\alpha_2)$.

$\neg\tilde{b}_1 \vee \neg\tilde{b}_2$ has rates: OR of $(\beta_1, \alpha_1)$ and $(\beta_2, \alpha_2)$ = $(\beta_1+\beta_2-\beta_1\beta_2, \alpha_1\alpha_2)$.

These match. De Morgan's laws are preserved.

**Verdict: CORRECT** under independence. All three composition rules verified algebraically and cross-checked via De Morgan.

---

## Claim 4: Composition Accumulation (Corollary 2)

**Statement.** "For $n$ operations each with symmetric error rate $\varepsilon$, the accumulated error is bounded by $n\varepsilon - O(\varepsilon^2)$ for small $\varepsilon$."

**Analysis.** The corollary does not specify which operation is being composed. There are two cases:

- **OR chain (FPR accumulation):** $\alpha_n = 1 - (1-\varepsilon)^n \approx n\varepsilon - \binom{n}{2}\varepsilon^2 + \cdots$ for small $\varepsilon$. The leading term is $n\varepsilon$ and the next is $-O(n^2\varepsilon^2)$, not $-O(\varepsilon^2)$. So the formula is correct only if we absorb the $n$-dependence into the $O(\cdot)$.

- **AND chain (FPR accumulation):** $\alpha_n = \varepsilon^n$, which *decreases* exponentially. The stated formula does not apply.

- **AND chain (FNR accumulation):** $\beta_n = 1 - (1-\varepsilon)^n \approx n\varepsilon$ for small $\varepsilon$. Same form as OR-FPR.

The corollary is vague about:
1. Which operation (only applies to the "inclusive-exclusion" direction: FPR under OR, or FNR under AND).
2. The $O(\varepsilon^2)$ should be $O(n^2\varepsilon^2)$ -- the suppressed factor depends on $n$.
3. "Symmetric error rate" implies $\alpha = \beta = \varepsilon$, but the HBOS construction has $\alpha > 0, \beta = 0$, which is asymmetric.

**Verdict: IMPRECISE.** The leading-order approximation $n\varepsilon$ is correct for the appropriate composition direction, but the corollary is underspecified and the error term is wrong (should depend on $n$).

---

## Claim 5: Membership FPR (Theorem 4)

**Statement.** For a set $S$ of size $k$ represented as $n$-bit OR of hashes:
$$\varepsilon_{\in}(k, n) = (1 - 2^{-(k+1)})^n$$

**Assumptions.** (1) $h$ is a random oracle with i.i.d. uniform bits. (2) $x \notin S$ and $x$ is drawn independently of $S$. (3) Bit positions are independent.

**Step-by-step.**

1. After $k$ insertions via OR, each bit position $j$ of $F(S)$ satisfies:
   $$P(F(S)_j = 1) = 1 - P(\text{all } k \text{ elements have bit } j = 0) = 1 - (1/2)^k = 1 - 2^{-k}$$
   This uses the random oracle model: each element's bit $j$ is i.i.d. Bernoulli(1/2).

2. For a query element $x \notin S$, $h(x)$ is independent of $F(S)$ (random oracle). Each bit $h(x)_j$ is i.i.d. Bernoulli(1/2).

3. A false positive requires: for every bit $j$, $h(x)_j = 1 \Rightarrow F(S)_j = 1$. Equivalently, the event "bit $j$ does not refute membership" has probability:
   $$P(\text{not refuted at } j) = P(h(x)_j = 0) + P(h(x)_j = 1 \wedge F(S)_j = 1)$$
   $$= \frac{1}{2} + \frac{1}{2}(1 - 2^{-k}) = 1 - \frac{1}{2} \cdot 2^{-k} = 1 - 2^{-(k+1)}$$

4. By independence across bit positions:
   $$\varepsilon_{\in} = \prod_{j=1}^n (1 - 2^{-(k+1)}) = (1 - 2^{-(k+1)})^n$$

**Cross-check with authentic blog post.** The derivation in foundations/trapdoor-boolean-algebra.md (lines 343-377) matches exactly.

**Cross-check with cipher map formalism.** formalism/cipher-map-formalism.md (line 274) states the same formula: $\varepsilon_\in = (1 - 2^{-(k+1)})^n$.

**Verdict: CORRECT.** The derivation is rigorous under the random oracle model.

---

## Claim 6: Subset FPR (Theorem 5)

**Statement.** For sets $S_1, S_2$ of sizes $k_1, k_2$:
$$\varepsilon_{\subseteq}(k_1, k_2, n) = (1 - (1 - 2^{-k_1}) \cdot 2^{-k_2})^n$$

**Assumptions.** Same as Claim 5, plus: $S_1 \not\subseteq S_2$ (the subset relation is false in truth), and $S_1, S_2$ are independently constructed.

**Step-by-step.**

1. The subset test in the bit domain is: $F(S_1) \mathbin{\&} F(S_2) = F(S_1)$, i.e., every bit set in $F(S_1)$ is also set in $F(S_2)$.

2. Bit $j$ "refutes" the subset if $F(S_1)_j = 1$ and $F(S_2)_j = 0$.
   - $P(F(S_1)_j = 1) = 1 - 2^{-k_1}$
   - $P(F(S_2)_j = 0) = 2^{-k_2}$
   - By independence (different sets, random oracle): $P(\text{refuted at } j) = (1 - 2^{-k_1}) \cdot 2^{-k_2}$

3. $P(\text{not refuted at } j) = 1 - (1 - 2^{-k_1}) \cdot 2^{-k_2}$

4. Over $n$ independent bits: $\varepsilon_{\subseteq} = (1 - (1 - 2^{-k_1}) \cdot 2^{-k_2})^n$

**Cross-check with blog post.** foundations/trapdoor-boolean-algebra.md lines 434-459 derive the same formula.

**Verdict: CORRECT.**

---

## Claim 7: Space Complexity (Theorem 6 in paper, labeled Theorem 7 in review)

**Statement.** To maintain a fixed FPR $\varepsilon$ for membership queries on a set of size $k$: $n = \mathcal{O}(2^k)$.

**Step-by-step.**

From Claim 5: $\varepsilon = (1 - 2^{-(k+1)})^n$.

Solving for $n$:
$$n = \frac{\ln \varepsilon}{\ln(1 - 2^{-(k+1)})}$$

For small $x > 0$: $\ln(1 - x) \approx -x$. With $x = 2^{-(k+1)}$:
$$n \approx \frac{\ln \varepsilon}{-2^{-(k+1)}} = -\ln(\varepsilon) \cdot 2^{k+1} = 2 \cdot |\ln \varepsilon| \cdot 2^k$$

So $n = \Theta(2^k)$ for fixed $\varepsilon$, confirming $n = \mathcal{O}(2^k)$.

**Cross-check with blog post.** foundations/trapdoor-boolean-algebra.md lines 393-405 derive the same result.

**Verdict: CORRECT.** The exponential space requirement is the key practical limitation motivating the two-level scheme.

---

## Claim 8: Complement Non-Preservation (Theorem 6 in paper)

**Statement.** $F(\neg_A x) \neq \neg_B F(x)$ for finite sets $x$.

**Step-by-step.**

1. $\neg_A x = X^* \setminus x$, which is countably infinite (since $X^*$ is countably infinite and $x$ is finite).

2. $F(\neg_A x) = \bigvee_{y \in X^* \setminus x} h(y)$.

   Since $X^* \setminus x$ is countably infinite and $h$ is a random oracle over $\{0,1\}^n$ (a finite set), by the pigeonhole principle, infinitely many elements of $X^* \setminus x$ hash to each of the $2^n$ possible hash values. In particular, for each bit position $j$, there exist elements $y \in X^* \setminus x$ with $h(y)_j = 1$. Therefore:
   $$F(\neg_A x) = 1^n$$

3. $\neg_B F(x) = \mathord{\sim}(h(x_1) \mathbin{|} \cdots \mathbin{|} h(x_k))$ for $x = \{x_1, \ldots, x_k\}$.

   For finite $k$, $F(x)$ is the OR of $k$ independent uniform $n$-bit strings. $P(F(x)_j = 0) = 2^{-k} > 0$. So with high probability (certainty when at least one bit is 0), $F(x) \neq 1^n$, meaning $\neg_B F(x) \neq 0^n$.

   Since $\neg_B F(x) \neq 0^n$ but could equal $0^n$ only if $F(x) = 1^n$, and since $F(\neg_A x) = 1^n$, we need $\neg_B F(x) = 1^n$ for equality. But $\neg_B F(x) = 1^n$ iff $F(x) = 0^n$, which happens only for the empty set. For any non-empty finite set, $F(x) \neq 0^n$ with overwhelming probability, so $\neg_B F(x) \neq 1^n = F(\neg_A x)$.

4. Therefore $F(\neg_A x) = 1^n \neq \neg_B F(x)$ for any non-empty finite set $x$.

**Note on the paper's proof text.** The paper's proof (lines 491-496) is correct in substance but slightly sloppy in notation. It writes $F(\neg_A x) = 0^n | h(y_1) | h(y_2) | \cdots = 1^n$ -- the "$0^n |$" prefix is unnecessary (OR with zero is identity) but not wrong.

**Cross-check with blog post.** foundations/trapdoor-boolean-algebra.md lines 225-252 give the same proof with a concrete example ($x = \{a, b, ab\}$).

**Note on the blog post errata (from cipher-map-formalism.md).** The blog post says "asymptotically as $|x| \to \infty$ the third property holds." The formalism document corrects this: as $|x| \to \infty$, $F(x) \to 1^n$, so $\neg_B F(x) \to 0^n$, while $F(\neg_A x) = 1^n$. The discrepancy is *maximal* for large sets, not minimal. The paper does not reproduce this particular erroneous claim.

**Verdict: CORRECT.** Sound proof. The complement non-preservation is a genuine structural result, not an approximation limitation.

---

## Claim 9: One-Wayness of Trapdoor Homomorphism (Theorem 4 in Section 4.1)

**Statement.** $F$ is one-way for two reasons: (1) non-injectivity by pigeonhole, (2) preimage resistance of $H$.

**Analysis.** Both properties are standard:

1. **Non-injectivity.** $X^*$ is countably infinite, $\{0,1\}^n$ has $2^n$ elements. By pigeonhole, infinitely many inputs map to each output. So even if you could invert the hash, you could not determine *which* preimage was used.

2. **Preimage resistance.** By the ROM assumption, finding any $x$ such that $H(x) = y$ for given $y$ requires $O(2^n)$ operations.

**Verdict: CORRECT but TRIVIAL.** These are standard properties of cryptographic hash functions. The paper does not claim novelty here.

---

## Claim 10: Privacy Preservation (Theorem in Section 4.2)

**Statement.** In the one-wayness game $\mathcal{G}_{OW}$: $\Pr[\mathcal{A} \text{ wins}] \leq 2^{-n} + \text{negl}(n)$.

**Analysis.** In the ROM, $H(k \| x)$ is uniform over $\{0,1\}^n$ and independent of $x$ (since the adversary does not know $k$). The adversary's probability of guessing $x$ is at most $1/|X|$ where $X$ is the domain (for uniform $x$). The game is stated with "random $x \in \{0,1\}^*$" which is not well-defined (there is no uniform distribution on $\{0,1\}^*$). The intended meaning is that $x$ is drawn from some efficiently samplable distribution, and the adversary's advantage is bounded by hash collision/preimage probabilities.

The stated bound $2^{-n} + \text{negl}(n)$ is conservative (it follows from the ROM directly).

**Verdict: CORRECT** in substance, but the game definition is slightly informal (uniform distribution on $\{0,1\}^*$ is undefined). This is a standard formalism issue and does not affect the result.

---

## Claim 11: Bit-Rate Formula (Corollary 1)

**Statement.**
$$b(n, \varepsilon) = \frac{\log_2 \varepsilon}{n \cdot \alpha(n)}$$
where $\alpha(n) = 1 - 2^{-(n+1)}$ is the "per-bit occupancy probability after $n$ insertions."

**Analysis.** There are multiple problems:

### Problem 1: Variable naming collision

The corollary uses $n$ for both "number of elements" (set size, called $k$ elsewhere) and "hash width" (called $n$ or $m$ elsewhere). Comparing with Theorem 4 where $\varepsilon = (1 - 2^{-(k+1)})^n$: $k$ = set size, $n$ = hash width. In the corollary, $\alpha(n)$ should be $\alpha(k) = 1 - 2^{-(k+1)}$ where $k$ is the set size.

### Problem 2: Incorrect approximation step

The corollary claims: "For $\alpha(n)$ close to 1, $\log_2(\alpha(n)) \approx \alpha(n) - 1 \approx -\alpha(n)$ for small deviations."

This is wrong. The correct approximation for $\alpha$ close to 1 is:
$$\log_2(\alpha) = \frac{\ln(\alpha)}{\ln 2} \approx \frac{\alpha - 1}{\ln 2}$$

So $\log_2(1 - 2^{-(k+1)}) \approx -2^{-(k+1)} / \ln 2$.

The corollary writes "$\log_2(\alpha(n)) \approx \alpha(n) - 1 \approx -\alpha(n)$" which conflates two different approximations and drops the $\ln 2$ factor.

### Problem 3: The resulting formula is dimensionally wrong

The bit-rate (bits per element) should be $m/k$ where $m$ is hash width and $k$ is set size. From Theorem 4:
$$m = \frac{\log_2 \varepsilon}{\log_2(1 - 2^{-(k+1)})} \approx \frac{\log_2 \varepsilon \cdot \ln 2}{-2^{-(k+1)}} = -\ln(\varepsilon) \cdot 2^{k+1}$$

So bit-rate = $m/k \approx -\ln(\varepsilon) \cdot 2^{k+1} / k$, which is *exponential* in $k$.

The corollary writes $b = \log_2(\varepsilon) / (n \cdot \alpha(n))$. With the variable naming corrected ($n \to k$, $\alpha(k) = 1 - 2^{-(k+1)} \approx 1$), this becomes $b \approx \log_2(\varepsilon) / k$, which is $O(1/k)$ -- *inverse linear* in set size. This is grossly wrong. The actual bit-rate is $O(2^k / k)$.

### Root cause

The approximation "$\log_2(\alpha) \approx -\alpha$" is the error. Since $\alpha = 1 - 2^{-(k+1)} \approx 1$, we have $\log_2(\alpha) \approx -2^{-(k+1)}/\ln 2 \approx 0$, not $\approx -1$. The formula should be:

$$b(k, \varepsilon) = \frac{m}{k} = \frac{\log_2(\varepsilon)}{k \cdot \log_2(1 - 2^{-(k+1)})} \approx \frac{-\log_2(\varepsilon) \cdot \ln 2 \cdot 2^{k+1}}{k}$$

**Verdict: ERROR.** The formula is wrong due to a flawed approximation and variable naming confusion. The correct bit-rate is exponential in set size, not $O(1/k)$.

---

## Claim 12: Two-Level FPR (Theorem in Section 4.5)

**Statement.** The membership FPR for the two-level scheme with $k$ elements, $2^w$ bins, and $q$-bit hash is:
$$\varepsilon(k, w, q) = (1 - 2^{-(k/2^w + 1)})^{q-w}$$

**Assumptions.** (1) Elements distribute uniformly across $2^w$ bins (first $w$ bits of hash = bin index). (2) Expected elements per bin: $k/2^w$. (3) Within each bin, the single-level FPR formula applies with effective set size $k/2^w$ and hash width $q - w$.

**Step-by-step.**

1. With $2^w$ bins and $k$ elements hashed uniformly, the expected bin size is $k/2^w$.

2. A membership query for $x$ first identifies bin $j$ (first $w$ bits of $h(x)$). A false positive occurs when the remaining $q - w$ bits of $h(x)$ pass the single-level membership test against the $k/2^w$ elements (on average) in bin $j$.

3. Applying the single-level formula with $k' = k/2^w$ and $n' = q - w$:
   $$\varepsilon = (1 - 2^{-(k' + 1)})^{n'} = (1 - 2^{-(k/2^w + 1)})^{q-w}$$

**Issue: Using expected bin size instead of worst-case.**

The formula uses the *expected* bin size $k/2^w$. The actual bin sizes follow a multinomial distribution. The maximum bin size is $\Theta(k/2^w + \log(2^w)/\log\log(2^w))$ by standard balls-into-bins results. For a rigorous worst-case bound, one should use the maximum bin size. This makes the FPR slightly worse than stated.

Numerically, for the example in the paper ($w = 8$, $q = 256$, $k = 1000$): expected bin size $\approx 3.9$, maximum bin size $\approx 8$-$10$. The FPR difference: $(1 - 2^{-4.9})^{248} \approx 2^{-248}$ vs $(1 - 2^{-9})^{248} \approx 2^{-127}$. So the worst-case FPR is significantly larger, though still astronomically small.

**Cross-check with blog post.** foundations/trapdoor-boolean-algebra.md lines 489-508 state the same formula.

**Verdict: CORRECT as an expected-case formula.** The paper should note that this uses expected bin size. A worst-case bound requires replacing $k/2^w$ with the maximum bin load, which is a standard modification.

---

## Claim 13: Uniformity from Inverse-Frequency (Theorem in Section 4.7)

**Statement.** With $|\text{Valid}(y)| = c / \text{freq}(y)$:
$$P[\text{Output} = y] = |\text{Valid}(y)| / 2^m = \text{constant}$$

**Step-by-step.**

$$P[\text{Output} = y] = \text{freq}(y) \cdot \frac{|\text{Valid}(y)|}{2^m} = \text{freq}(y) \cdot \frac{c / \text{freq}(y)}{2^m} = \frac{c}{2^m}$$

This is independent of $y$, hence uniform.

**Assumptions.** (1) Each input $x$ with $f(x) = y$ is encoded uniformly at random among $\text{Valid}(y)$. (2) $c$ must be chosen so that $\sum_y |\text{Valid}(y)| \leq 2^m$ (the encoding regions fit in the hash space).

**Verdict: CORRECT.** This is the 1/p(y) principle from the Bernoulli types framework. The proof is straightforward.

---

## Claim 14: Confusion Matrix (Definition 3)

**Statement.** $Q = \begin{pmatrix} 1-\alpha & \alpha \\ \beta & 1-\beta \end{pmatrix}$ where $Q_{ij} = P(\text{obs} = j \mid \text{lat} = i)$.

**Verification.**
- Row 0 (latent = False): $P(\text{obs}=F \mid \text{lat}=F) = 1-\alpha$, $P(\text{obs}=T \mid \text{lat}=F) = \alpha$. Correct.
- Row 1 (latent = True): $P(\text{obs}=F \mid \text{lat}=T) = \beta$, $P(\text{obs}=T \mid \text{lat}=T) = 1-\beta$. Correct.
- Rows sum to 1 (row-stochastic). Correct.

Properties:
- Identity ($\alpha = \beta = 0$): $Q = I$. Perfect observation. Correct.
- Rank-1 ($\alpha + \beta = 1$): Both rows are $(1-\alpha, \alpha)$, so all rows identical. Output independent of input. Correct.
- Rank-2 ($\alpha + \beta < 1$): Rows are linearly independent. Information preserved. Correct.

**Verdict: CORRECT.** Standard confusion matrix formulation.

---

## Claim 15: XOR Composition (Python library only, not in paper)

**Statement** (from cts/approximate.py):
```python
p_correct = p1_correct * p2_correct + (a1 + b1) * (a2 + b2)
error = (1 - p_correct) / 2
return (error, error)
```

**Analysis.**

XOR is True when exactly one input is True. Let's compute the exact error rates.

Let $p_i = \alpha_i + \beta_i$ = total error rate of input $i$, and $q_i = 1 - p_i$ = correctness rate.

XOR output is correct when:
- Both inputs are correct (both right, XOR of latent = XOR of observed): probability $q_1 q_2$
- Both inputs are wrong: this is more subtle. If $b_1$ has a false positive (latent=F, obs=T) and $b_2$ has a false negative (latent=T, obs=F), the XOR of observed values is $T \oplus F = T$, while XOR of latent values is $F \oplus T = T$. So the XOR is correct. But if both have false positives, XOR of observed is $T \oplus T = F$, while XOR of latent is $F \oplus F = F$. Also correct. And if both have false negatives: observed $F \oplus F = F$, latent $T \oplus T = F$. Correct.

So when both are wrong, the XOR is *always* correct regardless of which type of error. The probability of both being wrong is: this requires specifying the error type for each input, which depends on the latent values.

The code computes $P(\text{both wrong}) = (\alpha_1 + \beta_1)(\alpha_2 + \beta_2)$. This treats the total error probability as a single number, which is only valid if we average over latent values. More precisely, $P(\text{input } i \text{ wrong}) = \alpha_i(1-\pi_i) + \beta_i \pi_i$ where $\pi_i = P(\text{latent}_i = T)$. The code implicitly assumes $\alpha_i + \beta_i$ is the total error rate regardless of prior, which requires $\alpha_i(1-\pi_i) + \beta_i \pi_i = \alpha_i + \beta_i$ only when priors cancel out appropriately. This is an approximation.

The symmetric split $(1 - p_{\text{correct}})/2$ for both $\alpha$ and $\beta$ assumes the XOR error is equally likely to be a false positive or false negative. This is reasonable as a rough bound but not tight.

**Verdict: ROUGH APPROXIMATION.** The formula is a heuristic, not a derivation. It gives symmetric error rates that are reasonable for engineering purposes but not mathematically tight. The paper wisely does not include this as a theorem.

---

## Claim 16: C++ Appendix operator&& (Appendix A)

**Statement** (lines 860-868 of paper):
```cpp
approximate operator&&(const approximate& other) const {
    return approximate(
      value_ && other.value_,
      min(false_positive_rate_, other.false_positive_rate_),
      false_negative_rate_ + other.false_negative_rate_);
}
```

**Analysis.** The FPR of AND should be $\alpha_1 \cdot \alpha_2$ (multiplicative, per Theorem 3). The code uses `min(alpha1, alpha2)`, which is wrong.

- For $\alpha_1 = \alpha_2 = 0.1$: code gives $\min(0.1, 0.1) = 0.1$, correct answer is $0.01$.
- For $\alpha_1 = 0.5, \alpha_2 = 0.01$: code gives $\min(0.5, 0.01) = 0.01$, correct answer is $0.005$.

The `min` is always an upper bound on the product (since $\min(a,b) \geq a \cdot b$ for $a, b \in [0,1]$), so it is conservative but loose.

The FNR formula `b1 + b2` is also wrong -- it should be `b1 + b2 - b1*b2`. Without the correction term, it overapproximates.

**Verdict: BUG.** Two errors: FPR uses `min` instead of product, FNR omits the `-b1*b2` correction. The Python implementation (compose_and) is correct. This is a Claude-generated code listing that does not match the authentic C++ implementation.

---

## Claim 17: Intersection Preservation (implicit in Definition 5 and Section 4.1)

**Statement** (implicit). $F(A \cap B) = F(A) \mathbin{\&} F(B)$.

**Analysis.** The paper presents this as an exact homomorphism property in Definition 5 (the "Trapdoor Homomorphism"), but it is actually approximate.

$F(A) \mathbin{\&} F(B)$ retains all bit positions set in both $F(A)$ and $F(B)$. A bit can be set in both even if no element of $A \cap B$ hashed to that position -- it suffices for some element of $A \setminus B$ to set that bit, and independently some element of $B \setminus A$ to set the same bit. These are "cross-element collisions."

Formally: $F(A \cap B) \subseteq F(A) \mathbin{\&} F(B)$ (bitwise: every bit set in $F(A \cap B)$ is set in $F(A) \mathbin{\&} F(B)$), but the reverse inclusion may fail. So $F(A) \mathbin{\&} F(B)$ may have extra bits, meaning it encodes a "superset" of $A \cap B$ in terms of the bit representation.

The paper acknowledges this implicitly via the error propagation theorems but does not state it clearly in Section 4.1. The cipher map formalism document (formalism/cipher-map-formalism.md line 259) explicitly corrects this: "F(A cap B) subseteq F(A) & F(B), with equality only when there are no cross-element collisions."

**Verdict: APPROXIMATE, not exact.** The homomorphism is exact for union, approximate for intersection. The paper's presentation in Definition 5 is misleading by listing $F(\cap) = \mathbin{\&}$ without qualification. However, the error bounds in Theorems 1-2 do account for this.

---

## Claim 18: Union Preservation (implicit in Definition 5)

**Statement.** $F(A \cup B) = F(A) \mathbin{|} F(B)$.

**Step-by-step.**

$F(A \cup B) = \bigvee_{x \in A \cup B} h(x) = (\bigvee_{x \in A} h(x)) \mathbin{|} (\bigvee_{x \in B} h(x)) = F(A) \mathbin{|} F(B)$

This uses: OR is associative, commutative, and idempotent. The third equality follows because the union of two sets contains exactly the elements in either set, and OR-ing hash values is idempotent ($h(x) \mathbin{|} h(x) = h(x)$), so duplicates in $A \cap B$ do not matter.

**Cross-check with blog post.** foundations/trapdoor-boolean-algebra.md lines 175-213 ("Proof of Second Property") gives the same argument with a concrete example.

**Verdict: EXACTLY CORRECT.** Union is the one operation that is preserved exactly (not approximately) by $F$.

---

## Independence Assumptions: Summary

Many claims above depend on independence assumptions that deserve explicit acknowledgment:

1. **Bit independence within a hash.** The ROM assumption gives this: bits of $h(x)$ are i.i.d. Bernoulli(1/2). This is the standard assumption for hash-based data structures.

2. **Independence across elements.** Different elements' hashes are independent under ROM. This is used in the FPR derivations.

3. **Independence across sets.** Theorems 1-3 assume errors in $A$ and $B$ are independent. This holds when $A$ and $B$ are constructed independently (different elements, different hash evaluations). It may fail if $A$ and $B$ share elements or if the same hash function is used in a correlated way.

4. **Independence across operations.** The composition accumulation (Corollary 2) assumes errors at each step are independent. For chained Boolean operations on the same bit vector, this is a reasonable approximation but not exact (the bit vector is a shared state).

---

## Summary Table

| # | Claim | Location | Verdict | Notes |
|---|-------|----------|---------|-------|
| 1 | Union error bound | Thm 1 | **CORRECT** | Under independence |
| 2 | Intersection error bound | Thm 2 | **CORRECT** | Under independence |
| 3 | Boolean error composition (NOT/AND/OR) | Thm 3 | **CORRECT** | Verified + De Morgan check |
| 4 | Composition accumulation | Cor 2 | **IMPRECISE** | Unspecified operation; error term should depend on $n$ |
| 5 | Membership FPR | Thm 4 | **CORRECT** | Core result, verified step-by-step |
| 6 | Subset FPR | Thm 5 | **CORRECT** | Verified step-by-step |
| 7 | Space complexity $n = O(2^k)$ | Thm 6/7 | **CORRECT** | Follows from Thm 4 |
| 8 | Complement non-preservation | Thm 6 | **CORRECT** | Pigeonhole argument, sound |
| 9 | One-wayness | Thm (4.1) | **CORRECT** | Trivial, standard |
| 10 | Privacy game | Thm (4.2) | **CORRECT** | Standard ROM argument |
| 11 | Bit-Rate Formula | Cor 1 | **ERROR** | Wrong approximation, variable collision, wrong asymptotics |
| 12 | Two-level FPR | Thm (4.5) | **CORRECT** (expected case) | Should note: uses expected bin size, not worst-case |
| 13 | Uniformity from 1/p(y) | Thm (4.7) | **CORRECT** | Straightforward |
| 14 | Confusion matrix | Def 3 | **CORRECT** | Standard formulation |
| 15 | XOR composition (Python) | cts/approximate.py | **ROUGH APPROX** | Heuristic, not in paper |
| 16 | C++ operator&& | Appendix A | **BUG** | min instead of product; missing -b1*b2 |
| 17 | Intersection = exact | Def 5 (implicit) | **APPROXIMATE** | $F(A \cap B) \subseteq F(A) \& F(B)$, not equality |
| 18 | Union = exact | Def 5 (implicit) | **CORRECT** | Genuinely exact |

### Critical Issues

1. **Bit-Rate Formula (Cor 1)**: Must be corrected or removed. The formula gives $O(1/k)$ bit-rate when the true bit-rate is $O(2^k/k)$.

2. **C++ Appendix**: Contains bugs. Either fix or remove (the authentic C++ code from 549091a is different).

3. **Intersection approximation**: The paper should explicitly state that $F(A \cap B) \subseteq F(A) \& F(B)$ (approximate, not exact) in Definition 5 or immediately after.

### Minor Issues

4. **Composition Accumulation**: Should specify it applies to OR/union chains (FPR) or AND/intersection chains (FNR), and the error term should be $O(n^2\varepsilon^2)$, not $O(\varepsilon^2)$.

5. **Two-level FPR**: Should note the expected vs. worst-case bin size distinction.

6. **Privacy game**: $x$ drawn uniformly from $\{0,1\}^*$ is ill-defined; should be "from a distribution $D$ with sufficient min-entropy."
