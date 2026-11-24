# Security review distillation

**Applied one craft replacement: verify the input editor’s existing capabilities before rating a new injection or traversal path.** No diff reviewed or suite run for this dispatch.

- **SEC-1 — applied (Patterns P-02).** The c1 review established an uncontained write, but the c1 validator recorded that the same inventory editor could already change code run by the same suite. That supports non-gating hardening, not a claim that the copy is contained. Six spawns from now, the replacement changes the review order: compare what the least-privileged editor can already do under the same runner and controls before assigning severity. Tracked data alone proves no equivalence; different identities, targets, or approval requirements can change the conclusion. The c2/c3 reviews leave the hardening on the existing backlog. Sources: `review-harness-security-reviewer-c1.md` through `-c3.md`; validate c1 digest, SEC-1.
- **Committed QA checkout paths — rejected as a standalone rule.** The c3 validator treated the observed metadata as advisory; targeted inspection found no credential values. That does not establish that local paths are always harmless, or that captured output is redacted. Existing P-08 already asks what exposure changed, and G-13 keeps an unmitigated boundary distinct from its disposition. The case-specific grade adds no durable action. Sources: c2/c3 security notes and validate c3 digest, ranked item 3.

Craft counts (before → after): Patterns 15 → 15; Gotchas 15 → 15; Outcomes 10 → 10; Open 0 → 0. Repository tier unchanged. Batch `c0351e3179da2795a19551697efc9b24b6682c4e0a05e1d7f665f5a6cc328604`.

**Open questions:** none.
