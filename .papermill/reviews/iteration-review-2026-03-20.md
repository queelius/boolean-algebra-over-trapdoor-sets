# Iteration Review: Boolean Algebra over Trapdoor Sets (Second Pass)

**Date**: 2026-03-20
**Paper**: paper/main_comprehensive.tex
**Reviewer**: Claude Opus 4.6 (1M context)
**Prior documents**: verification-2026-03-20.md, reviews/review-2026-03-19.md, proofs/proof-verification-2026-03-19.md, thesis-refined-2026-03-19.md

---

## 1. Fix Consistency Propagation

### 1.1 Intersection Superset Claim Propagation

The corrected intersection claim (lines 435--444: `H(A) \land H(B) \supseteq H(A \cap B)`) needs to be consistent throughout the paper. Checking all places where intersection is discussed:

| Location | Text | Consistent? |
|----------|------|-------------|
| Line 211 (Sec 3.1) | "Intersection: $A \cap B$ with error composition" | **OK** -- generic description, no exactness claim |
| Line 243 (Thm 2) | "$\alpha_{A \cap B} = \alpha_A \cdot \alpha_B$" | **OK** -- this is the Bernoulli Boolean composition rule (both must false-positive), not the structural bit-vector claim. Compatible with superset. |
| Line 248 (Thm 2 proof) | "a false positive requires *both* sets to report false positives" | **OK** -- standard Bernoulli interpretation |
| Line 290 (Sec 3.4.2) | "Set operations: Union and intersection return sets with composed error rates per Theorems 1--3" | **OK** -- refers to error composition, not structural exactness |
| Line 358 (Def 8) | $F(\cap) = \land$ in the homomorphism definition | **MAJOR** -- This still maps $\cap \mapsto \land$ without qualification. Definition 8 presents $F$ as a homomorphism, implying exactness. The correction at line 439 (Definition 10) states the superset relationship, but Definition 8 on line 358 still presents intersection as an exact mapping. A reader encountering Definition 8 first will think intersection is exact, only to find the correction 80 lines later. |
| Line 439 (Def 10) | "$H(A) \land H(B) \supseteq H(A \cap B)$" | **OK** -- the fix itself |
| Line 444 | "Important Note" paragraph | **OK** -- reinforces the correction |
| Line 642 (Table 1) | "Set intersection (1K each)" | **OK** -- performance table, no exactness claim |

**Severity: MAJOR.** Definition 8 (Trapdoor Homomorphism, line 358) still maps $\cap \mapsto \land$ without any caveat. This directly contradicts the corrected Definition 10 at line 439. The homomorphism definition should include a note: "Intersection is approximate; see Definition 10 for the precise relationship."

### 1.2 Variable Rename Propagation (n -> k for set size)

The rename in the Bit-Rate Remark (lines 387--396) uses `k` for set size and `m` for bit-vector length. Checking for conflicts:

| Context | Variable `k` meaning | Conflict? |
|---------|----------------------|-----------|
| Lines 277, 280 (Sec 3.4.1) | Hash key in $T_k(v) = H(k \| v)$ | **MAJOR** -- `k` is the secret hash key here |
| Line 368 (Def 8) | Set size: $S = \{x_1, \ldots, x_k\}$ | No conflict -- same meaning |
| Lines 411--412 (Sec 4.2) | Hash key in $H(k \| x)$ | **Same conflict as line 277** |
| Lines 449--484 (Sec 4.4) | Set size: "For sets of size $k$..." | No conflict -- same meaning |
| Line 509 (Remark 8) | Number of hash functions in Bloom filter FPR: $(1-e^{-kn/m})^k$ | **MINOR** -- Here `k` is the number of Bloom filter hash functions (standard Bloom notation), which is different from set size. This is within a single remark comparing to Bloom filters, so the local reuse is acceptable if confusing. |
| Line 559 (Sec 4.6) | Again `k` in Bloom filter FPR formula and also in $H(k \| v)$ for HBOS trapdoor | **MAJOR** -- In the same bullet list (line 558--559), `k` means "number of hash functions" in the Bloom filter bullet and "hash key" in the HBOS trapdoor bullet. Two different meanings of `k` separated by one line. |

**Severity: MAJOR.** The variable `k` is now overloaded three ways in the paper: (1) set size (Sec 4.4, the intended use after the rename), (2) hash key (Sec 3.4.1, Sec 4.2, Sec 4.6), and (3) Bloom filter hash count (Sec 4.6 line 558). The rename from `n` to `k` resolved the collision with hash width `n` but created a new collision with hash key `k`. The hash key should use a different symbol (e.g., `\kappa` or `\mathsf{key}`) to disambiguate.

### 1.3 Old Corollary 1 References

The FIXED comment at line 382 notes the old Corollary 1 was replaced with Remark 6. Searching for references to "Corollary 1" in the paper body: **none found** (only the comment itself at line 382). The auto-numbering via `\newtheorem` means the corollary environment was removed entirely (replaced by a `\remark`), so any `\ref` to the old label would produce an undefined reference warning. No dangling references.

**Severity: None.** Clean replacement.

---

## 2. Provenance Issues

### 2.1 Bibliography Entries with Wrong Dates

Checking the flagged entries against references.bib:

| Bib key | Paper | Bib year | Correct year | Status |
|---------|-------|----------|--------------|--------|
| `mcsherry2021exponential` | McSherry & Talwar, "The exponential mechanism" | **2021** | **2007** (FOCS 2007) | **CRITICAL** -- The original paper is "Mechanism design via differential privacy" (2007). The bib entry title "The exponential mechanism for differential privacy revisited" with year 2021 and venue "Journal of Privacy and Confidentiality" may reference a different, later paper. However, the text at line 781 says "Recent advances include the exponential mechanism~\cite{mcsherry2021exponential}" -- calling the 2007 exponential mechanism a "recent advance" is wrong regardless. This looks like a Claude fabrication: the title, venue, and year do not correspond to any known paper. |
| `brakerski2022fully` | Brakerski & Vaikuntanathan, "Fully homomorphic encryption from ring-LWE" | **2022** | **2011** (CRYPTO 2011, appeared in full 2014) | **CRITICAL** -- The bib entry has venue "Annual Cryptology Conference" which is correct (CRYPTO), but year 2022 is wrong. The paper was published at CRYPTO 2011 (proceedings) with a full journal version in 2014. Year should be 2011 or 2014. |
| `bonawitz2021practical` | Bonawitz et al., "Practical secure aggregation" | **2021** | **2017** (CCS 2017) | **CRITICAL** -- The bib entry itself contains a contradiction: `year={2021}` but `booktitle={Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security}`. The venue says 2017 but the year field says 2021. The paper was published at CCS 2017. |

Additional suspicious entries found in this pass:

| Bib key | Issue |
|---------|-------|
| `ting2020count` | "Count-HyperLogLog" by Daniel Ting, arXiv 2020. The arXiv ID `2005.14165` is actually the GPT-3 paper by Brown et al. (2020), not a cardinality estimation paper. **CRITICAL** -- fabricated arXiv ID. |
| `schoppmann2023psi` | "PSI from pseudorandom correlation generators" by Schoppmann, Gascon, Kerschbaum, 2023. Cannot verify this paper exists with these exact authors. Likely Claude-fabricated. |
| `chen2022blazing` | Appears to be a duplicate/variant of `raghuraman2022blazing` with different authors. Both entries share the identical title (a PSI paper using OKVS and subfield VOLE) but list completely different author sets. One of these is fabricated. |

**Severity: CRITICAL.** At least 4 bib entries have verifiably wrong dates or fabricated metadata. The entire related work bibliography (30+ entries added in Claude-era commits) should be audited. Entries not cited in proofs or core results should be removed.

### 2.2 Remaining "Oblivious" Terminology

Count of "oblivious" occurrences in the paper: **24 instances** across lines 46, 62, 64, 72, 79, 83, 117, 199, 201, 270, 273, 275, 277, 283, 296, 326, 543, 570, 758, 786, 832, 834, 836, 838, 843, 968, 983.

Key locations requiring change:

| Location | Usage | Recommendation |
|----------|-------|----------------|
| Line 46 | `\Oblivious` macro definition | Remove or rename to `\Trapdoor` |
| Line 62 | "Hash-Based Oblivious Sets (HBOS)" | Rename: "Hash-Based Trapdoor Sets" or "Trapdoor Boolean Algebra" |
| Line 64 | "oblivious representation" | Replace with "trapdoor representation" |
| Line 72 | Keywords: "oblivious data structures" | Replace with "trapdoor data structures" |
| Lines 199, 270, 275, 277, 283 | "Hash-Oblivious Values", "Oblivious Representation Layer" | Replace with "trapdoor" throughout |
| Line 296 | "oblivious RAM~\cite{oset}" | This is the one place "oblivious" is correctly used (referring to ORAM). Keep, but it should only appear when discussing the ORAM comparison, not as the paper's own terminology. |
| Lines 832--843, 968, 983 | C++ code: `hash_oblivious`, `ObliviousSet` | Rename to `hash_trapdoor`, `TrapdoorSet` |

**Severity: MAJOR.** The "oblivious" terminology throughout the paper will mislead cryptography reviewers into expecting ORAM-style access-pattern hiding. The paper explicitly acknowledges (Remark 5, line 294) that HBOS does NOT hide access patterns. The terminology conflicts with the paper's own security claims. Systematic replacement with "trapdoor" is required.

### 2.3 ORAM References

The `\cite{oset}` reference (Wang et al. 2014, "Oblivious data structures") appears only at line 296, in Remark 5 (The Concession). This is the correct and only appropriate place for an ORAM reference -- it is used as a contrast point ("a fully oblivious system would hide even the pattern of true/false results (as in oblivious RAM)"). No ORAM references appear elsewhere.

**Severity: MINOR.** The ORAM reference at line 296 is appropriate for the comparison. However, it should be clearer that this is a *contrast* -- perhaps: "Unlike oblivious RAM~\cite{oset}, which hides access patterns, HBOS does not hide query result patterns."

---

## 3. Remaining Technical Issues

### 3.1 XOR/Symmetric Difference Composition

The paper claims (line 440): "Symmetric difference: $H(A) \oplus H(B) = H(A \triangle B)$ (exact for disjoint sets)."

This is correct for disjoint sets but the qualification "(exact for disjoint sets)" underscores a problem: for non-disjoint sets, XOR cancels shared elements. If $x \in A \cap B$, then $h(x)$ appears in both $F(A)$ and $F(B)$, and XOR cancels it. So $F(A) \oplus F(B)$ loses information about $A \cap B$. The paper correctly restricts to disjoint sets.

The XOR composition formula from the Python library (`compose_xor`) is flagged as a "Python heuristic" by the proof verification. The formula:
```
p_correct = p1_correct * p2_correct + (a1 + b1) * (a2 + b2)
error = (1 - p_correct) / 2
```
is an approximation, not a derivation. The paper **wisely does not include** XOR composition as a theorem. However, Theorem 3 (Boolean Error Composition, line 253) only covers NOT, AND, OR -- it does not cover XOR. Since the paper discusses XOR/symmetric difference as a primary operation (lines 219--225), a reader may expect an error composition rule for XOR.

**Severity: MINOR.** The paper avoids stating the XOR composition as a theorem, which is correct since the exact derivation is more complex (depends on prior probabilities). A brief remark noting that XOR error composition is prior-dependent would be helpful.

### 3.2 Two-Level FPR: Expected vs. Worst Case

The Two-Level FPR theorem (line 527) states:
$$\varepsilon(k,w,q) = \left(1 - 2^{-(k/2^w + 1)}\right)^{q-w}$$

This uses the **expected** bin size $k/2^w$. The proof verification (Claim 12) notes that actual bin sizes follow a multinomial distribution, and the maximum bin size is $\Theta(k/2^w + \log(2^w)/\log\log(2^w))$ by standard balls-into-bins results.

For the paper's example ($w=8$, $q=256$, $k=1000$): expected bin size $\approx 3.9$, worst-case bin size $\approx 8$--$10$. The FPR difference is enormous in relative terms: $\approx 2^{-248}$ (expected) vs. $\approx 2^{-127}$ (worst case), though both are astronomically small.

The paper does not note this distinction.

**Severity: MINOR.** The expected-case formula is the standard presentation (matching Bloom filter analysis). A one-sentence note acknowledging "this uses expected bin size; a worst-case bound replaces $k/2^w$ with the maximum bin load" would be sufficient.

### 3.3 Composition Accumulation Corollary (line 266)

The Corollary states: "For $n$ operations each with symmetric error rate $\varepsilon$, the accumulated error is bounded by $n\varepsilon - O(\varepsilon^2)$ for small $\varepsilon$."

Three problems identified in proof verification:
1. Does not specify which operation (only applies to FPR under OR chains, or FNR under AND chains, not both)
2. Error term should be $O(n^2\varepsilon^2)$, not $O(\varepsilon^2)$ -- the suppressed factor depends on $n$
3. States "symmetric error rate" ($\alpha = \beta = \varepsilon$) but HBOS has $\alpha > 0, \beta = 0$ (asymmetric)

Additionally, this corollary uses `n` for number of operations -- after the Fix 1 rename, the paper uses `k` for set size, but `n` still means hash width in most of the paper. Here `n` means "number of composed operations," which is yet a third meaning for `n`.

**Severity: MAJOR.** The corollary is underspecified, has the wrong error term, and uses conflicting variable names. It should be either made precise or removed.

### 3.4 Intersection FPR Bound in Definition 10

The intersection fix (line 439) states: "Each extra 1-bit arises with probability at most $|A \setminus B| \cdot |B \setminus A| / 2^n$ per bit position."

This bound is loosely stated. The probability that a specific bit position $j$ has an extra 1-bit (set by cross-element collisions) requires: (a) at least one element of $A \setminus B$ sets bit $j$, AND (b) at least one element of $B \setminus A$ sets bit $j$. For random oracle bits, (a) has probability $1 - 2^{-|A \setminus B|}$ and (b) has probability $1 - 2^{-|B \setminus A|}$. The product is $(1 - 2^{-|A\setminus B|})(1 - 2^{-|B\setminus A|})$. The stated bound $|A\setminus B| \cdot |B\setminus A| / 2^n$ conflates bit-level collision probability with hash-level collision probability (the $2^n$ should be $2$ for per-bit analysis under the OR construction, or $2^n$ for full-hash collision).

**Severity: MINOR.** The bound is presented within a definition, not a theorem, and is described as a bound ("at most"). The qualitative point (cross-element collisions cause extra 1-bits) is correct. The quantitative bound needs tightening if this is ever promoted to a theorem.

---

## 4. Paper Quality Assessment

### 4.1 Top 3 Improvements for Publishability

**1. Strip Claude-drifted content and fix bibliography (CRITICAL)**

The single most impactful change. The paper's authentic core (Boolean algebra homomorphism, complement non-preservation, FPR analysis, two-level hashing) is solid. But the Claude-generated padding (HBOS branding, expanded applications section, 30+ suspect bibliography entries, fabricated benchmarks, C++ appendix with bugs) undermines credibility. A reviewer will flag the wrong bibliography dates, the "projected" benchmarks, and the misuse of "oblivious" -- and may dismiss the genuine contributions.

Action items:
- Remove or fix all bibliography entries with wrong dates/fabricated metadata
- Remove the applications section (Sec 7) or replace with 1--2 concrete examples from the authentic blog post
- Remove projected benchmarks (Table 1 footnote is honest, but "projected" benchmarks in a submitted paper signal incomplete work)
- Remove the C++ appendix or replace with authentic code
- Replace "HBOS" and "oblivious" with "trapdoor" throughout

**2. Resolve variable overloading (MAJOR)**

The paper uses `k` for three things (set size, hash key, Bloom filter hash count) and `n` for three things (hash width, number of composed operations, and historically set size before the rename). This will confuse reviewers and makes formulas ambiguous.

Action items:
- Use `k` consistently for set size (already done in most places)
- Use `\kappa` or `\mathsf{key}` for the hash key (currently `k` in $T_k(v) = H(k \| v)$)
- Use `m` consistently for bit-vector width (already done in Definition 8; reconcile with `n` used in Theorems 4--7)
- Remove or fix the Composition Accumulation corollary where `n` means "number of operations"

**3. Add the explicit Bloom filter connection and honest positioning (MAJOR)**

The construction $F(S) = h(x_1) | \cdots | h(x_k)$ is equivalent to a single-hash-function Bloom filter. Standard Bloom filters use $k$ independent hash functions to achieve FPR $(1-e^{-kn/m})^k$ at the same space cost. The paper mentions Bloom filters as a point of comparison (Sec 4.6, line 558) but never explicitly states that its core construction IS a single-hash Bloom filter.

A venue reviewer familiar with probabilistic data structures will immediately recognize this. Stating the connection upfront -- and then explaining what this paper adds beyond standard Bloom filter analysis (the free semigroup framing, the complement non-preservation proof, the precise FPR for subset testing) -- is essential for credibility.

### 4.2 Self-Containedness

The paper is mostly self-contained for the Boolean algebra and FPR results. It relies on two external references by the same author (`bernoulli-types` and `oblivious-computing`, both listed as "Working paper, 2024") for:
- The Bernoulli Boolean framework (Definitions 2--3)
- The error composition rules (Theorem 3 -- though this is also proved in the paper)
- The 1/p(y) principle (Section 4.7)
- The unified hash construction (Section 4.6)

The Bernoulli Boolean concepts used here (FPR, FNR, confusion matrix) are standard enough that the paper can stand alone. The 1/p(y) principle section (Sec 4.7) is the least self-contained -- it relies heavily on the Bernoulli types framework and could be trimmed or moved to an appendix without loss.

**Severity: MINOR.** The paper is reasonably self-contained for the core results. The dependency on unpublished companion papers should be noted as a limitation for venue submission.

### 4.3 Suggested Target Venue

Given the authentic contribution (algebraic analysis of hash-based set encoding, precise FPR formulas, complement non-preservation proof):

**Primary recommendation**: Workshop paper at a privacy/security venue (e.g., PETS workshop, Theory of Cryptography Conference workshop, or a workshop on approximate computation). The contribution is genuine but modest -- a workshop paper is the right scope.

**Alternative**: Short paper / poster at IEEE S&P or CCS. The complement non-preservation result is a clean, citable observation. The FPR analysis is useful reference material.

**Not recommended in current form**: Full paper at a top venue (S&P, CCS, CRYPTO, EUROCRYPT). The contribution needs the Bloom filter connection stated honestly, the bibliography fixed, and the benchmarks either completed or removed. The "HBOS framework" framing overpromises relative to the actual contribution.

---

## 5. Summary of Findings

### CRITICAL

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| C1 | Fabricated bibliography entries | references.bib | `mcsherry2021exponential` (wrong year/possibly fabricated), `brakerski2022fully` (wrong year), `bonawitz2021practical` (contradictory dates), `ting2020count` (fabricated arXiv ID pointing to GPT-3 paper), `chen2022blazing` (duplicate title, different authors from `raghuraman2022blazing`), `schoppmann2023psi` (unverifiable) |

### MAJOR

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| M1 | Definition 8 still claims exact intersection | Line 358 | Homomorphism maps $\cap \mapsto \land$ without caveat, contradicting the fix at line 439 |
| M2 | Variable `k` overloaded (set size vs hash key) | Lines 277, 280, 411, 412, 559 | The rename from `n` to `k` for set size created a collision with hash key `k` in $T_k(v) = H(k \| v)$ |
| M3 | "Oblivious" terminology throughout | 24 occurrences | Misleads cryptography reviewers; conflicts with paper's own security claims |
| M4 | Composition Accumulation corollary imprecise | Line 266 | Unspecified operation, wrong error term ($O(\varepsilon^2)$ should be $O(n^2\varepsilon^2)$), variable `n` overloaded |
| M5 | Bloom filter connection unstated | Throughout | Core construction is a single-hash Bloom filter; not acknowledging this undermines credibility |

### MINOR

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| m1 | Two-level FPR uses expected bin size | Line 527 | Should note expected vs. worst-case distinction |
| m2 | XOR error composition absent | Sec 3.1, line 219 | Paper discusses XOR as primary operation but provides no error composition rule |
| m3 | ORAM reference could be clearer contrast | Line 296 | Rephrase to emphasize HBOS is NOT oblivious in the ORAM sense |
| m4 | Intersection FPR bound loosely stated | Line 439 | Quantitative bound mixes bit-level and hash-level probabilities |
| m5 | `\Oblivious` macro unused in paper body | Line 46 | Dead code; remove |
| m6 | Bloom filter FPR formula reuses `k` | Line 558 | `k` here means Bloom filter hash count, not set size |

### SUGGESTION

| # | Issue | Description |
|---|-------|-------------|
| S1 | Reframe as cipher map | Connect to the cipher map formalism from the parent repo; this is an "online construction cipher map" |
| S2 | Quantify complement approximation | While $F(\complement A) \neq \sim F(A)$, quantify how good $\sim F(A)$ is for small $|A|$ |
| S3 | Target workshop venue | The authentic contribution fits a workshop paper or short paper; the full-paper framing overpromises |
| S4 | Strip projected benchmarks | Table 1 and Figure 3 add no value and signal incomplete work |
| S5 | Fix author affiliation | Paper uses SIUE/atowell@siue.edu; verify if this is current vs lex@metafunctor.com |

---

## 6. Comparison with Previous Review

Changes since the 2026-03-19 review:

| Issue from review | Status after fixes | This iteration |
|-------------------|--------------------|----------------|
| Bit-Rate Corollary wrong approximation | **FIXED** (replaced with correct Remark) | Propagation clean; no dangling refs |
| C++ `operator&&` bug | **FIXED** (product + inclusion-exclusion) | Matches Theorem 3 and Python code |
| Intersection claimed exact | **PARTIALLY FIXED** (Def 10 corrected) | Def 8 still claims exact homomorphism (M1) |
| Variable naming collision | **PARTIALLY FIXED** (n->k for set size) | New collision: k = set size vs k = hash key (M2) |
| "Oblivious" terminology | **NOT FIXED** | 24 occurrences remain (M3) |
| Bibliography dates | **NOT FIXED** | At least 4 critical entries with wrong/fabricated data (C1) |
| Bloom filter connection | **NOT ADDRESSED** | Still missing (M5) |

**Overall assessment**: The three targeted fixes are mathematically correct and internally consistent. However, the paper still has critical provenance issues (fabricated bibliography) and major terminology/variable problems that must be resolved before submission to any venue.
