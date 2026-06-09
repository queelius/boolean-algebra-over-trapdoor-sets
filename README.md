# Boolean Algebra over Trapdoor Sets

Source for the paper *Boolean Algebra over Trapdoor Sets: A Practical Framework
for Privacy-Preserving Set Operations with Probabilistic Guarantees* (Alexander
Towell), part of the trapdoor-computing series.

This is a paper-only repository. The earlier standalone `cts` Python library was
removed on 2026-06-04; the reference implementation now lives as the
`TrapdoorSet` type in the shared `trapdoor-maps` library.

## Subject

The paper characterizes the **trapdoor set**: a set whose elements are opaque,
deterministic (K=1) trapdoors, supporting a collision-bounded generalized Boolean algebra (union,
intersection, and difference exact up to hash collision; no false negatives; no
complement) while
answering membership as a plaintext `bool` by byte-equality.

The trapdoor set sits at the leaky-but-exact end of an opacity/exactness axis.
It never decodes (recovers no plaintext); what it exposes is the **equality
predicate** among ciphertexts, the deterministic-encryption and
searchable-encryption leakage profile. The homophony parameter `K(x)` is the
dial: `K=1` opens that channel and gives this collision-bounded algebra; `K>1` closes it and
yields the opaque set-indicator (an `element -> Bool` trapdoor map). In exchange
for the leak, set operations are exact rather than error-accruing.

The manuscript is being reframed around this value-type framing; see `CLAUDE.md`
for status and the reframe checklist.

## Implementation

The reference implementation is the `TrapdoorSet` type in `trapdoor-maps`
(`~/github/trapdoor-computing/src/cipher-maps`, package `trapdoor_maps`), the
library that backs the trapdoor-computing papers' empirical claims. Design spec:
`~/github/trapdoor-computing/src/cipher-maps/docs/superpowers/specs/2026-06-04-trapdoor-set-design.md`.

## Build

No Makefile. Build the PDF with:

```bash
cd paper
pdflatex main_comprehensive.tex && bibtex main_comprehensive && \
  pdflatex main_comprehensive.tex && pdflatex main_comprehensive.tex
```

## License

MIT (see `LICENSE`).
