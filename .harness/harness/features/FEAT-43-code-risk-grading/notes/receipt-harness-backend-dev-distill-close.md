# Receipt — harness-backend-dev — FEAT-43 feature-close distillation

## BLUF

Craft Patterns and craft Gotchas are BOTH at hard cap (15/15) and I found no mechanical way to
displace an existing entry through `expertise-merge.py` — it is provably additive-only. All three
lead-relayed candidates (C1/C2/C3) are judged ACCEPTED on merit but could not be applied to those
two capped craft sections; I recorded their repo-specific residue in the repository tier instead
(which had headroom) and escalate the tooling gap as a blocking open question. One self-derived
Outcome was applied to craft (room existed there).

## The tooling gap, empirically confirmed

`compute_union` in `expertise-merge.py` unconditionally copies every existing `(section, id)` pair
into the merged result before considering the proposal (`merged_list = list(base_entries)`), so:

- a proposal reusing an existing id with different text always raises exit 7 (CONFLICT), file
  byte-identical afterward — no override path exists.
- a proposal adding any new id once the section is at its cap always raises exit 8 (CAP
  EXCEEDED), file byte-identical afterward.

I verified both empirically against a scratch copy of my own craft file before concluding this
(not from reading source alone): same-id-different-text on `P-16` → `EXIT=7`, file unchanged.
There is no `--drop`/`--replace` flag, and `.claude/skills/harness/bin/expertise-merge.py` is
byte-identical to `.agents/skills/harness/bin/expertise-merge.py`. `DECISIONS.md` DEC-145 itself
flags "Displacement-at-cap remains untested (no section was full)" — this is the first real
contact with that gap. I messaged my lead (`Feat43EngineeringDistill`) to check for a sanctioned
resolution and waited ~2.5 min combined; no reply arrived. Given my dispatch's absolute
constraint — "NEVER write or Edit an Expertise file directly" — I did not work around the gap with
a direct edit. `open_questions` below carries this up.

## Candidate judgments

**C1** (own log, 2026-08-29/30 — complexity-gate helper decomposition). ACCEPTED on merit: a
sharp, generalizable insight (decomposition drops cyclomatic AND cognitive scores together under
sonar-style nesting penalties) that would have displaced craft Pattern P-16 (the weakest of the 15
— a fairly generic "reuse, don't reimplement" rule already partially covered by its own logic).
NOT applied to craft (section at cap, tool cannot displace — see above). Its repo-specific residue
(the actual tool name and its measured thresholds) was captured as a NEW repository-tier Pattern
instead, where there was headroom.

**C2** (cycle-29 digest — substring-containment assertion). ACCEPTED on merit: sharp, general,
distinct from existing Gotcha G-11 (wrong stream) — a count-string substring test is contained in
its own regression output ("1 file(s)" ⊂ "41 file(s)"). Would have displaced craft Gotcha G-08
(narrowest existing entry — a domain-manifest-fixture tip, useful but the least broadly applicable
of the 15). NOT applied — Gotchas also at cap, same tool limitation. No repo-specific residue
exists (the lesson is pure assertion-writing practice, not tied to a repo tool), so nothing was
added to the repository tier for C2 — inventing one would be padding.

**C3** (cycle-29 digest — shared-helper-only fixtures blind to call-site regressions). ACCEPTED on
merit: distinct from P-10 (mutation scoping) — this is about guard *design* (AST property over
parsed nodes, no exclusion list to rot) rather than mutation-test scoping. Would have displaced
craft Gotcha G-06 (self-referential grep-scan concern, the narrowest/most idiosyncratic of the 15).
NOT applied — same cap/tool limitation. No repo-specific residue; nothing added to repository tier.

**Self-derived (own log, C25 entry — pinned-commit-ancestor check)**: ACCEPTED and APPLIED as
craft Outcome O-04. Outcomes had headroom (3/10 before). Passes six-spawns test: recognizing that
HEAD moving away from a pinned base mid-task is not necessarily a problem, provided the pinned
commit is still an ancestor, generalizes to any long-running git-based task.

**Self-derived (own log — "no-exemption ruling" for code_grade.py's own codebase)**: ACCEPTED and
APPLIED as repository-tier Gotcha G-04 (had headroom, 3/15 before). This is a genuine one-repo
policy fact (this specific gate enforces no allowlist escape hatch for its own guarded functions),
not a generalizable craft claim.

## Counts by source

| | Relay-sourced | Self-derived |
|---|---|---|
| Accepted (judged sound) | 3 (C1, C2, C3) | 2 |
| Applied | 0 (blocked by tooling cap) | 2 |
| Rejected | 0 | 0 |

Rejection reasons: none — every candidate judged sound. The 3 relay-sourced candidates were
accepted-but-blocked, which is distinct from rejected; no candidate died on merit.

## Per-section counts, before → after

**Craft** (`.harness/expertise/harness-backend-dev.md`):
- Patterns: 15 → 15 (unchanged — cap, tool cannot displace)
- Gotchas: 15 → 15 (unchanged — cap, tool cannot displace)
- Outcomes: 3 → 4 (+O-04)
- Open: 0 → 0

**Repository tier** (`.harness/harness/expertise/harness-backend-dev.md`):
- Patterns: 0 → 1 (+P-01)
- Gotchas: 3 → 4 (+G-04)
- Outcomes: 0 → 0
- Open: 0 → 0

## Verification

```
$ python3 .agents/skills/harness/bin/expertise-merge.py apply --file .harness/expertise/harness-backend-dev.md --entries /tmp/craft-entries.md
ADDED O-04
PRESERVED P-01 ... PRESERVED O-03
APPLIED .harness/expertise/harness-backend-dev.md
EXIT=0

$ python3 .agents/skills/harness/bin/expertise-merge.py apply --file .harness/harness/expertise/harness-backend-dev.md --entries /tmp/repo-entries.md
ADDED P-01
ADDED G-04
PRESERVED G-01
PRESERVED G-02
PRESERVED G-03
APPLIED .harness/harness/expertise/harness-backend-dev.md
EXIT=0

$ .agents/skills/harness/bin/check-expertise.sh .harness/expertise/harness-backend-dev.md .harness/harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-backend-dev.md
ADVISORY .harness/expertise/harness-backend-dev.md:25: G-08 names 'team-config' — repository-layer candidate; rule on it (issue 340)
OK   .harness/harness/expertise/harness-backend-dev.md
EXIT=0
```

The G-08 advisory is pre-existing (not touched by this distillation) and is advisory, not
blocking, per `check-expertise.sh`'s own contract.

`git status --porcelain` confirms only my two Expertise files were modified by me; the other
modified/untracked files in the working tree belong to sibling distillers running concurrently
(`harness-dev-ops`, `harness-security-reviewer`, `harness-ui-reviewer`, `harness-qa`,
`harness-code-reviewer`), not touched by this run.
