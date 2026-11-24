# Security Expertise distillation

**Two craft rules replaced weaker entries; one candidate was already covered.** No security diff was reviewed and no suite was run. No security observations log was present.

1. **Accepted → Patterns P-04 (`replace`).** The cycle-1 parent-symlink finding adds a reusable check for delete confinement: verify ancestor resolution and bind enumeration and unlink to the same directory handle. P-14 covers implicit creation, not unlink. This displaces narrower invariant-detector exemption guidance. The cycle-1 digest kept the finding advisory because the local-write precondition and low-impact stamp loss did not warrant gating, not because the parent path was confined.
2. **Accepted → Gotchas G-07 (`replace`).** The cycle-1 diagnostic finding adds a check for operator-facing output even when no gate parses it. Escaping controls in untrusted fields protects the integrity of the displayed record. This displaces a severity-token reminder already governed by the reviewer contract.
3. **Rejected as already held.** Cycle 2's pinned blob equality is an instance of O-01's identity evidence applied to O-07's per-cycle surface census. The test-only round does not justify a separate recipe.

**Tool receipt:** `notes/expertise-receipt-0231fabc532604cd2df8ba60fcc07748bb213fd71e3bb2b010df784558a3b2bd.json` (relative to this feature directory). Batch `667aaa0e6c44224ce7a7aa4c6249e1a3ffb1f6f0519dca55c59bb4db26cff982`. Counts before → after: Patterns 15 → 15; Gotchas 15 → 15; Outcomes 10 → 10; Open 0 → 0.

**Open questions:** None.
