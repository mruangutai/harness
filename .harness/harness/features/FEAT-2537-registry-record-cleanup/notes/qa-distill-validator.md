# QA distill — FEAT-2537-registry-record-cleanup

**BLUF:** I accepted both relayed candidates (C-QA1 and C-QA2) as craft Outcomes and one item from my own log as a repository Gotcha. Each displaced an entry I judged weaker, so every section count is unchanged. I rejected the other five log bullets because existing entries already cover them. This was distillation only: I reviewed no diff, ran no suite, and committed nothing.

## Candidates
| Source | Decision | Reason |
|---|---|---|
| C-QA1: raw-bytes letter gap | **Accepted.** It replaces craft O-04 | This is a sharper successor to O-04. At r-3 I followed O-04's route-up step but rated the text-mode read low because bytes measured identical today. The c1 ruling judged that read the one real letter miss (the CRLF writer passed 200/200), and it cost a completion round. The new entry keeps O-04's general scope (literal wording stricter than the assertion, routed upward). It adds grading against the letter, not present equivalence, and running the mutant the weaker assertion admits. It does not overlap P-08 (element identity) or O-05 (don't call an undiscriminated test useless). |
| C-QA2: delta I classified myself | **Accepted.** It replaces craft O-08 | At r-2 my probe found the live-claim fold, and I called it in-class myself. The c0 ruling confirmed that the signoff's "bytes identical" claim was false for row-carrying envelopes, so the stop clause had fired. The rule is distinct from O-04, which covers criterion wording, not delta classification. O-08 (mutate the real call site, not a passthrough accessor) is largely covered by O-06 and O-10, which makes it the weakest Outcome. |
| Log: full bin/ copy for the module swap | Rejected | The verification-rules skill already classifies ModuleNotFoundError as misconfiguration, not FAIL. The fact is also specific to one test's harness. |
| Log: shape-matrix probe found a surviving mutant | Rejected | P-05 (probe each field: missing, wrong type, out-of-domain) plus Build the Lever already cover it. |
| Log: INV-26 reads the live board at the pin | **Accepted (repository tier).** It replaces repo G-11 | It recurs on every validate run at a pin that predates station commits: INV-26 exited 1 at the pin and 0 at the tip. G-11 is generic advice to preserve output, so it was the weakest repository gotcha. |
| Log: CRLF text-mode read | Folded into C-QA1 | — |
| Log: stderr-noise mutant misses the missing-file row | Rejected | P-06 and G-10 cover it: a mutant at one site doesn't reach rows that bypass that site. |
| Log: CRLF one-factor control | Rejected | It is an instance of P-09. |

## Ops applied
- Craft batch `3d2ce5f197b4b164c0e0b631bbeaabfeab80b82fa2b3ff77c58e04a1ac2997d9`: REPLACED O-04 and REPLACED O-08 (Outcomes).
  - Counts before→after: Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 0→0.
- Repository (harness) batch `e5afc9a56c6783b3e297f3d28816b5d6721f33f7e7d9cefae36be9bbfd52f739`: REPLACED G-11 (Gotchas).
  - Counts before→after: Patterns 0→0, Gotchas 15→15, Outcomes 0→0, Open 0→0.
- Receipt (both batches): `FD/notes/expertise-receipt-b43237d22c53b3ae1ff21f86ceee7e9835d5d3e5cb7cf54428307209ce0201c4.json`

## Open questions
None.
