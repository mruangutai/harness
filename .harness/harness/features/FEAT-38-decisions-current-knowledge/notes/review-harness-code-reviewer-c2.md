# Review c2 — harness-code-reviewer — FEAT-38-decisions-current-knowledge

**BLUF: PASS.** All 18 T-14 citation edits classified, re-derived and semantically checked; verify
block re-run at the tip is clean (exit 0), valid for pin `48bbe7e` since the one commit above it
(`04d333d`) touches only `feature.json`. T-22/T-23 verify blocks pass. No HIGH finding. One LOW note
(pre-existing, not introduced by this diff) on Q1's joint citation.

## Scope examined

- `git -C <wt> diff 2557950 48bbe7e --stat`: 26 files, matches the dispatch's declared shape exactly.
- Full raw diff of all 13 T-14 files, hunk by hunk (`git diff 2557950 48bbe7e -- <13 paths>`).
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml` T-14 (L1048), T-22
  (L1484), T-23 (L1544), and BRIEF REQ-04/REQ-05 traced via `traces:`.
- DECISIONS.md / DECISIONS-INDEX.md at `7ebfc9e` and `48bbe7e` for DEC-100, DEC-102(index only, body
  deleted at pin), DEC-120, DEC-19 (index only, body deleted at pin), DEC-84, DEC-85, DEC-171,
  DEC-138, DEC-145, DEC-191, DEC-192 (index only, no body at either sha), DEC-203.
  DECISIONS.md itself is settled ground (prior panel); read here only as evidence for citation
  correctness, never re-graded.
- Re-ran T-14's `verify:` block verbatim at the worktree tip.
- Re-ran T-22's `verify:` block verbatim (readback-fold.md headers + `git show` mention): OK.
- T-23: `gh issue view 448` → `CLOSED NOT_PLANNED` — verify's `state == CLOSED` check passes.
- `.gitignore` / `gitignore.snippet` diff, `fleet.yaml` YAML parse (`yaml.safe_load`, OK).

## Item 1 — file-scope violation check

**No violation.** The 13 non-T-14 files in the 26-file diff are all under
`.harness/harness/features/FEAT-38-decisions-current-knowledge/` — `STATE.md`, `feature.json`,
`plan.yaml` (status flips for T-14/T-22/T-23), `notes/readback-fold.md` (T-22's declared file), and
process artifacts from tasks *outside* my lens (review-cycle-1 notes, the 2026-08-29-16 ship review,
the goalcheck research note, grilling/answers/handoff records, `uat-FEAT-38.md`). None of these is
application/tool source; all are the feature's own admin trail, which `main-session-direct` writes as
a side effect of marking tasks done regardless of a task's literal `files:` list (T-22's own
`execution_reason` establishes the notes path is broadly granted to the orchestrator tier). No
tracked source file outside the feature directory or the 13 declared T-14 paths was touched.

## Item 2 — the 18 T-14 edits, classified

13× **Case A** (am.N suffix dropped, same DEC-N): `commands/harness.md` (DEC-138 am.4),
`harness-brief/SKILL.md` (DEC-138 am.7), `harness-init/SKILL.md` (DEC-171 am.1),
`harness-wayfinding/SKILL.md` (DEC-138 am.6), `harness/SKILL.md`×3 (DEC-157 am.1; bare `(am.2)`→
`(DEC-145)`; DEC-138 am.4), `github-mirror.md`×3 (DEC-138 am.6, am.7, am.4),
`gitignore.snippet` + `.gitignore` (DEC-171 am.1 each), `fleet.yaml` (DEC-174 am.1).

4× **Case B** (deleted id → successor): `agents/harness-orchestrator.md`, `harness-team/SKILL.md`,
`omp/agents/harness-orchestrator.md` — all DEC-102→DEC-120; `harness/SKILL.md` L246 — DEC-192→DEC-191
(not in T-14's own MEASURED narrative, found by the implementer's own grep sweep — see Item 6).

1× **Case C** (pattern, citation dropped): `debug-mission.md` — "approval bypasses grow (DEC-19)" →
"approval bypasses grow." — the file T-14's own intent names by name as the pattern case.

13+4+1 = 18, matching the diff's 18 insertions/18 deletions exactly. No am.N-drop spot-checked
(DEC-145/am.2, DEC-138/am.7, DEC-171/am.1) shows any loss of the specific claim being cited — in each
case the fold consolidated the amendment's content into the flat body, so the bare `DEC-N` now says
what the citing sentence needs word for word (DEC-145's body: "the lead relays at most 3 sourced
candidates... the member accepts or rejects each with a reason... first-class" — matches
`harness/SKILL.md`'s prose almost verbatim).

## Item 3 — verify re-run

Ran the literal `verify:` block from the repo root at the worktree tip (`04d333d`):
**exit 0**, no output. Checked the precondition rather than assuming it: `git log 48bbe7e..HEAD`
shows exactly one commit, `04d333d [harness:review-pin]`, touching only
`.../feature.json` (1 line) — the verify's search roots (`.claude/skills .claude/commands
.claude/agents .omp/agents .harness/factory CLAUDE.md .gitignore`) are untouched by it, so the
exit-0 result stands for the pin `48bbe7e` unchanged.

## Item 4/5 — the semantic check (Q1–Q3)

### Q1 — DEC-102→DEC-120 (×3: `agents/harness-orchestrator.md` L46, `harness-team/SKILL.md` L15,
`omp/agents/harness-orchestrator.md` L49) — **DEFENSIBLE**

Base index: `DEC-102 ... — SUPERSEDED BY DEC-120` — the repoint is the recorded successor, exactly
T-14's own named example. But DEC-120's body (§"The orchestrator becomes a spawned agent...") is
about depth 2→3 and the org's spawn topology; it never states "hierarchical works, the flat fallback
is not needed" in those or equivalent words. Tracing the quote to its origin, `SPEC.md:1397-1400`
attributes that *specific* clause to **DEC-100 alone** ("Verified (DEC-100): hierarchical works. The
flat fallback is not needed.") and attributes the *separate* depth-encoding clause to DEC-120. So the
joint `(DEC-100, DEC-120)` citation over-attributes the flat-fallback claim to DEC-120 — **but this
imprecision is pre-existing**: the original `(DEC-100, DEC-102)` had the identical shape (DEC-102 was
about the depth-2 shape, not the flat-fallback finding, either). T-14's mandate was narrowly "cite the
successor for a deleted id," which it did correctly; auditing whether the *original* joint citation
ever supported its claim is outside what T-14 was asked to fix. **Not a regression this diff
introduced.** LOW, non-gating, and I'd frame it as backlog: the joint citation should probably read
`(DEC-100)` alone for the flat-fallback clause, with DEC-120 cited separately for the depth-topology
context if that context is meant to be flagged too.

### Q2 — DEC-192→DEC-191 (`harness/SKILL.md` ~L246) — **CORRECT**

DEC-192's strike ruling names DEC-203 as the *content* successor ("DEC-203 carries its six
column-named values forward, unchanged in substance") — the naively "mechanical" choice. The
implementer instead cited **DEC-191**, which is only a `refs:` neighbor of DEC-192, not its recorded
successor. Reading both bodies at the pin settles it: DEC-191's body is *exactly* "The
execution-state file may carry eleven top-level keys and no others... `additionalProperties: false`
at the top level" — a verbatim match for the citing sentence, "There is no `phase:` key (DEC-191),
and the schema declares `additionalProperties: false`." DEC-203's body is entirely about GitHub
ticket/board lifecycle (open-until-Done, who writes the Done station, the parent-child rule) — it
never mentions the feature-state schema's key set or `additionalProperties` at all. Had the sweep
followed the mechanical successor, it would have produced exactly the class of defect this dispatch
was built to catch: a citation resolving to a live heading that supports the wrong claim. **Ruling on
the general question:** a citation must go to whichever decision supports the specific assertion
being made, never mechanically to a struck entry's recorded successor when that successor's content
doesn't cover the claim — the "successor" concept describes which entry inherits an id's *overall*
ruling in the graph, not which entry backs any one sentence that happened to cite it. This edit
applied that correctly.

### Q3 — DEC-19 dropped (`debug-mission.md` L21) — **CORRECT** on both counts

DEC-19's body at `7ebfc9e` ("`check-domain.sh` is the one deliberate exception to files-only
delivery") is about the domain-hook write-safety mechanism — it never discusses "approval bypasses"
or a "second, lighter lane." T-14's own intent names this file as the pattern case, so the drop is
literally the specified behavior. It is also the *better* outcome on the merits: DEC-19's two
recorded successors, DEC-84 (`delete: false` removed) and DEC-85 (serialization is the write-safety
mechanism), are read in full above and neither one discusses approval bypasses or process lanes
either — repointing to DEC-85 per the generic "cite the successor" rule would have produced a live
heading supporting the wrong claim, same defect class as Q2's naive path. Dropping the citation and
keeping the pattern stated in prose (already done — the sentence stands on its own without the
parenthetical) loses no provenance that was ever real: the citation was decorative, not load-bearing,
even before the fold.

## Item 6 — sweep for an uncounted repoint

Did not trust the "18" count from the dispatch narrative; derived the classification independently
from the raw diff (Item 2). The DEC-192→DEC-191 edit is exactly the "found by grep, not narrated"
case T-14's intent anticipates ("Re-derive every one by grep before editing"). No 18th-plus edit
exists beyond what's listed; the diff's insertion/deletion counts (18/18) and my per-file tally
reconcile exactly.

## Stage 2 (quality) — brief, since stage 1 passed

- No rewritten sentence reads wrong or self-contradictory; each am.N-drop was spot-checked against
  its now-flat DECISIONS.md body (Item 2) and reads correctly.
- `.gitignore` vs `gitignore.snippet`: the two files carry different surrounding prose pre-existing
  this diff (confirmed via `diff`), but the specific edited line — `(DEC-171 am.1)` → `(DEC-171)` —
  was applied identically in both, which is the byte-consistency this dispatch asked me to check.
- `fleet.yaml` parses as valid YAML post-edit (`yaml.safe_load`, no error).

## Open questions

None blocking. One backlog-shaped observation from Q1 (not a defect of this diff, see above).

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-14's 18 citation edits are correctly classified and semantically sound; T-22/T-23 verify clean; no HIGH finding"
  severity_max: low
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: "2557950..48bbe7e"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
```
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-code-reviewer-c2.md
