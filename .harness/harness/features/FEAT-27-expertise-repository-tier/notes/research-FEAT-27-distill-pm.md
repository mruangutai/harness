# Distillation — harness-pm — FEAT-27

**Nine ops applied, both tiers clean, no entry deleted.** Craft file 123 -> 130 lines (budget 150);
repository file created at 18 lines (budget 40). `check-expertise.sh` exits 0 over both, with one
advisory (see below) I ruled on and kept.

Written here, not at the dispatch-named `notes/distill-harness-pm.md`: `check-domain.sh` denies that
path for me and grants `notes/research-*.md` (the #216 shape — the guard is right, the dispatch name
was not).

## Ops

Craft — `.harness/expertise/harness-pm.md` (read-modify-write; every prior entry survives)

| op | target | source | why |
|---|---|---|---|
| replace | P-05 | self | grades each clause against its own subject — a trailing gloss whose subject excludes the case does not broaden the criterion, the mirror of the leading-claim rule already there |
| replace | P-07 | self | a sanctioned alternative set commits only to its weakest member; the old P-07's disambiguation-by-sibling-scoping is the same family, sharper here |
| replace | P-10 | **relay C3** | body anchoring is blind to renumbering — assert the identifier separately |
| replace | P-11 | **relay C2** | an SC grades the delivered state, not the regression suite; zero-case declared evidence is coverage debt routed to qa, not an unmet criterion |
| replace | P-14 | self | a handed-down *premise* changes the unit of work, not just a number; generalises the old count-only rule |
| replace | G-11 | self | anchors for a verbatim-move check come from the move commit's removed lines, not the baseline the brief quotes |
| add | O-07 | self | a prior commit is a free mutant when the change is one script |
| add | O-08 | self | a binary-override seam converts an unprovable "the mutant reddens" into a two-command proof |
| add | O-09 | self | dangling symlink, not a zeroed mode, for an unreadable-path fixture |

Repository — `.harness/harness/expertise/harness-pm.md` (**created**), 3 Gotchas: the write guard
denies shell file operations whatever the target; it reads the command line, so a variable-spelled
path is refused where the literal is allowed; `check-plan-routes.py`'s 50-line machine-field budget
excludes `intent:`, so a long `files:` list starves `verify:`.

## Counts

| Section | Craft before | Craft after | Repo before | Repo after |
|---|---|---|---|---|
| Patterns | 15/15 | 15/15 | — | 0/15 |
| Gotchas | 15/15 | 15/15 | — | 3/15 |
| Outcomes | 6/10 | 9/10 | — | 0/10 |
| Open | 0/5 | 0/5 | — | 0/5 |

## Rejections

- **C1** (a gap committed at REQ level, operationalized by no criterion, is a third thing) —
  rejected. Patterns is at cap and nothing surviving is weaker than it; its routing half (escalate
  rather than adopt a narrower reading) is already P-06. Died at a full section, correctly.
- Sizing a coverage gap by what a guard *uniquely* catches — same fate, no weaker entry to displace.
- "Enumerate before totalling" — covered by P-04.
- A short absence-anchor matching an unrelated entry — covered by G-04's rule that the anchor label
  must be asserted unique; only the failure direction differs (false FAIL vs false PASS).
- Concurrent writers on my own signed artifacts — the Edit tool already forces the re-read, so the
  residual lesson is thin.
- The two-layer path table itself — preloaded by `harness-distill` at exactly the moment it applies.

## Stale-entry check

No surviving entry is contradicted by this feature's evidence. Two were **incomplete**, not false,
and were replaced rather than dropped: P-10 (body anchoring, proven blind to renumbering — craft
`harness-documentor.md` keeps P-02/P-10/G-03/G-04/G-05 while the repository file renumbers the same
five) and P-14. `check-expertise.sh` flags P-01's `.harness/harness/features/` exemplar as a
repository-layer candidate; ruled craft — the rule is about non-discriminating verifies anywhere and
the path is a live exemplar pointer, which the distill rules explicitly permit.

Nothing staged or committed.
