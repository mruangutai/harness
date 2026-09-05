PASS

# QA Expertise distillation — BUG-1286-test-tree-enforcement (feature close)

**BLUF: no craft entry applied.** All three relayed candidates (C1/C2/C3) were judged genuine,
craft-tier (pass the "true in a repo never seen" test), and each names a specific existing entry
it would displace — but `expertise-merge.py apply` has **no drop/replace primitive**, and craft
Patterns (15/15), Gotchas (15/15) and Outcomes (10/10) are all at the DEC-145 cap. Confirmed live
against the real files (not inferred): a same-id-different-text proposal is a hard `CONFLICT`
(exit 7, nothing applied — verified in a scratch fixture); a new-id proposal against a full section
is a hard `CAP EXCEEDED` (exit 8, nothing applied — verified three times against the *actual*
`.harness/expertise/harness-qa.md`, once per section, file byte-identical before/after each
attempt). Distillation cannot mechanically condense a full section this way; `expertise_full: true`
is the honest outcome for all three sections, per harness-distill's own escape valve.

## Candidates judged

- **C1** (probe-construction methodology: mutate production + run the real entry point, not
  hand-edit an intermediate value in a copied test) — would REPLACE `P-09` (same topic, sharper:
  P-09 says pick the right mutant, C1 adds that the *edit itself* must reach the value the
  assertion consumes). Craft: yes (general vacuity-proof discipline). Blocked by cap+no-drop.
- **C2** (a clean exit alone doesn't distinguish a real sweep from a no-op sweep; need a discovery
  count) — would REPLACE `G-07` (same topic — real-binary-against-live-data — sharpened to also
  demand a non-trivial count, not just exit 0). Craft: yes. Blocked by cap+no-drop.
- **C3** (reconciling a peer's FAIL report against your own clean run: reproduce at the shared
  merge-base before concluding regression) — would REPLACE `O-02` (judged the weakest surviving
  Outcome: its lesson — verify each route independently — is already subsumed by `P-06`'s more
  general "verify each triggering leg has its own test", making O-02 the best candidate to give up
  the slot). Craft: yes. Blocked by cap+no-drop.

No repository-tier filing: filing craft-quality lessons under the repo tier merely because the
craft tier is full is a layer violation (harness-distill's own anti-pattern — filing by convenience,
not aboutness), so I did not do it.

## Tooling gap (see `open_questions`)

`expertise-merge.py`'s `compute_union` (bin/expertise-merge.py:113-139) unconditionally keeps every
existing base entry and only ever *adds* ids the proposal introduces that are not already present;
same id + different text is an unconditional `MergeRefusal(7)`, and any union exceeding a section's
cap is an unconditional `MergeRefusal(8)` — both leave the file untouched. There is no entries-file
syntax (`DROP`, empty text, etc.) that removes a base entry. `harness-distill/SKILL.md` instructs
"condense until you are under it — distillation IS the curation step", which is not mechanically
achievable with this CLI once a section is at cap. This is a harness defect, not a workaround to
carry forward, so it is raised as an open question rather than encoded anywhere in Expertise.

## check-expertise.sh

| File | Exit |
|---|---|
| `.harness/expertise/harness-qa.md` (craft, mine) | 0 (`OK`) |
| `.harness/harness/expertise/harness-qa.md` (repo, mine) | 0 (`OK`) |
| `.harness/expertise/harness-validator-lead.md` (craft, read-only measurement) | 0 (`OK`) |
| `.harness/harness/expertise/harness-validator-lead.md` (repo, read-only measurement) | 0 (`OK`) |

No violation text on any of the four (all four print a bare `OK <path>` line).

## Entry counts (before → after — unchanged, nothing applied)

- Craft `harness-qa.md`: Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 1→1.
- Repository `harness-qa.md`: Patterns 0→0, Gotchas 8→8, Outcomes 0→0, Open 0→0.

## Worktree state

Nothing staged, nothing committed, no worktree removed. Scratch fixtures and probes lived entirely
under `/tmp/bug1286_qa_probe` and `/tmp/bug1286_qa_distill`, outside the tracked tree.
