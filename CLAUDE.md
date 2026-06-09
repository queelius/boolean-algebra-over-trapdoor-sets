# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is (now)

**Paper-only.** Source for the paper *Boolean Algebra over Trapdoor Sets: A
Practical Framework for Privacy-Preserving Set Operations with Probabilistic
Guarantees* (`paper/main_comprehensive.tex`, IEEEtran conference, ~11 pages).

The standalone `cts` Python library (and its `tests/`, `examples/`,
`pyproject.toml`) was **removed on 2026-06-04**. The reference implementation
moved to the `TrapdoorSet` type in the shared `trapdoor-maps` library
(`~/github/trapdoor-computing/src/cipher-maps`, package `trapdoor_maps`). Do not
re-add a Python package here; this repo holds the manuscript and its review
history (`.papermill/`) only.

## The paper's subject and planned framing

The object is the **trapdoor set**: a set of opaque, deterministic (K=1)
trapdoors with a collision-bounded generalized Boolean algebra
(union/intersection/difference exact up to hash collision, FNR = 0, no complement)
whose membership test returns a plaintext `bool` by byte-equality.

The spine of the (planned) reframe:

- **It never decodes.** Membership-by-equality (`c == s` for some element) uses
  no seed and recovers no plaintext. What it exposes is the **equality
  predicate** among ciphertexts: the deterministic-encryption / searchable-
  symmetric-encryption (SSE) leakage profile, a different axis from decoding.
- **K(x) is the opacity/exactness dial.** `K=1` opens the equality channel and
  gives the collision-bounded untrusted-side algebra (this paper's object); `K>1`
  (homophonic) closes it and yields the opaque set-indicator (`element -> Bool`
  trapdoor map, as in `trapdoor-maps` `examples/document-search/`). This makes
  the paper a statement about `K` and connects it to the representation-
  uniformity (delta) machinery in the rest of the ecosystem.
- **The trade-off is the contribution:** opening the equality channel buys an
  collision-bounded algebra; the opaque cipher-Bool partition instead pays correctness error
  eta for opacity.

**Status:** the committed PDF still uses the older HBTS / "privacy-preserving
sets" framing. The reframe has not landed yet. The design spec for the
implementation the reframe will cite:
`~/github/trapdoor-computing/src/cipher-maps/docs/superpowers/specs/2026-06-04-trapdoor-set-design.md`.

## Build

No Makefile. Build the PDF with:

```bash
cd paper
pdflatex main_comprehensive.tex && bibtex main_comprehensive && \
  pdflatex main_comprehensive.tex && pdflatex main_comprehensive.tex
```

## Reframe checklist (phase 2, drawn from `.papermill/reviews/2026-05-23/review.md`)

- Connect to the cipher-maps four-property framework; cite the working
  `TrapdoorSet`; present the opaque set-indicator (K>1) as the contrasting end.
  Clears review finding M1.
- Add the SSE citations the review asked for (Curtmola et al. 2006); recast
  Theorem 8 (privacy) as QIF / equality-pattern leakage, not random-oracle
  preimage.
- Adopt the honest collision-bound FPR `|S| * 2^(-8 * n_bytes)`; drop the old
  bit-vector formula `(1 - 2^-(k+1))^n`, which never matched the actual
  set-of-hashes implementation.
- Drop HBOS / "oblivious" branding (still present in `CITATION.cff`, along with
  a stale `oblivious-computing` repo URL); fix `CITATION.cff` while there.
- The `cts` retirement is already done (bare delete, 2026-06-04).

## Provenance

In the standalone repo, commits up to `549091a` (pre-July-2024) are authentic;
later commits carry Claude drift (HBOS/ORAM terminology, padded applications,
performance superlatives). That cutoff is not directly visible in this subtree's
`git log`. Never import ORAM / FHE / simulation-based vocabulary (see the parent
monorepo `CLAUDE.md`, "Provenance and Authenticity").

## Pointers

- `~/github/trapdoor-computing/src/cipher-maps/` (the `TrapdoorSet`
  implementation and its design spec).
- `~/github/trapdoor-computing/formalism/cipher-map-formalism.md` (four
  properties, composition theorem, two-scale confidentiality, section 4A).
- Parent monorepo `CLAUDE.md` (framework source of truth; "untrusted never
  decodes").
