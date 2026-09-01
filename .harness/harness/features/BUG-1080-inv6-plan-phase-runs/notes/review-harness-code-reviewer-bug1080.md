# Code review — BUG-1080 — review_sha a2fb6c0b (base 9f2a0702)

Worktree confirmed: `.claude/worktrees/harness/BUG-1080-inv6-plan-phase-runs`, `git diff HEAD a2fb6c0b`
empty for the reviewed files; HEAD (`7851902`) is one commit past the pin, touching only
`feature.json`/`review_sha`/`notes/` (the pin itself), never the reviewed source. Diff matches the
contract exactly: `check-state.sh` (+28/-3), `feature-schema.json` (+3/-1), `test-check-state.py`
(+132/-1).

## Stage 1 — spec compliance

The fix delivers exactly what issue #1080's "Proposed fix" scoped: a `feature-schema.json` addition,
the INV-6 predicate, and tests — `check-state.sh:419-461`, `feature-schema.json:61`,
`test-check-state.py:3308-3506`. Fail-closed default confirmed correct and load-bearing (traced by
hand: `entry.get("code_grade", "")` on a missing key yields `""`, `.strip().lower() != "n_a"` is
`True`, so absence is always treated as "reviewed code" — matches D-23's `agent`-key precedent in
spirit but inverts the polarity deliberately, as the diff's own comment states). `runs` stays a
3-tuple; every consumer (`INV-7:463`, `INV-22:520,522`, dedup loop `:531`) still unpacks three
elements — verified by `grep -n "runs\b"` against the file directly (not the structural summary,
which returned stale/spliced content for this exact range across two separate tool calls this
session — see note at bottom). No scope creep: the diff touches only the three contracted files.

**Omission — HIGH, and this is the finding the dispatch's item 4 asks for an explicit verdict on.**
The exemption is real, tested, and reachable *in code*, but I traced every route by which a
`code_grade: "n_a"` value could ever land inside a `runs[]` entry and found **none, currently**:

- Repo-wide grep for `code_grade` outside this diff and its own prior art (`code-grade.py`,
  `validate-digest.py`'s unrelated reviewer-digest field, DECISIONS.md's DEC-207) returns zero hits
  in any skill, playbook, or agent instruction that tells an orchestrator to set the key on a
  `runs[]` entry.
- `.claude/skills/harness/SKILL.md` (the orchestrator playbook) step "6. Adjust and record" — the
  *only* documented instruction that appends to `feature.json`'s `runs:` list — says "update
  `feature.json`'s DATA: the runs list, and `cycles_used`... Values, never narrative." Nothing
  names `code_grade`. This file is untouched by the diff (`git diff 9f2a0702 a2fb6c0b --
  SKILL.md` empty) and was last edited under FEAT-45, before BUG-1080 existed.
- `feature-json-merge.py append-run` (the sole structured writer, confirmed via repo grep — no
  other caller) takes a free-form JSON object; it neither infers nor defaults `code_grade`.
  Whoever builds that JSON must know to add it, and nothing tells them to.
- DEC-207 (unchanged, pre-existing) only ever discusses `code_grade: n_a` as a **reviewer digest**
  field (`validate-digest.py`'s schema) — a different document from `feature.json`'s `runs[]`. No
  code path bridges the two (grepped for a digest-to-run-entry copy; none exists).
  `plan-panel.yaml`'s own recording step (harness/SKILL.md "The plan phase," step 3) transcribes
  the panel digest into **`plan.yaml`'s `panel` key**, never into `feature.json`.
  - The build handoff (`notes/handoff-build.md`) itself concedes half of this: "FEAT-46's
    `feature.json` still records two validator runs without `code_grade: n_a`... backfill is the
    main session's, after this merges." That sentence is scoped to the *retroactive* FEAT-46
    backfill (correctly out of this dispatch's non-goals). It says nothing about the *forward*
    case — the very next feature whose plan-phase panel runs, under the orchestrator's unchanged
    step-6 instruction, will append a `squad: validator` run with no `code_grade` key, exactly as
    FEAT-46 did, and INV-6 will fire exactly as it did before this fix (issue #1080's own text:
    "every future plan-phase panel hits this... not specific to FEAT-46").

**Verdict on item 4: the exemption is schema-legal and gate-correct, but is dead code in practice
today** — no producer sets it, and none is created by this diff. The live defect (issue #1080: "the
gate is red right now, blocking every flow in the repository") recurs on the next plan-phase panel
unless `.claude/skills/harness/SKILL.md`'s record-step (or the plan-panel team's own recording
instruction) is updated to stamp `code_grade: "n_a"` on that run's entry. This is the
`check-decision-anchors.py` shape the dispatch named: a capability that ships and nothing invokes.
Not a defect in the reviewed code — a missing companion change, one directory outside this diff's
contracted three files.

## Stage 2 — code quality

**Item 2 — fail-closed test, verified by hand-trace (I have no write grant to run a live mutant;
traced the interpreter semantics directly instead):**
`str(entry.get("code_grade", "")).strip().lower() != "n_a"`.

| input | gate treats as | schema (`"enum": ["n_a"]`, exact match) | direction |
|---|---|---|---|
| missing key | code-reviewing (pin required) | N/A (key absent, schema silent) | fail-closed, correct |
| `null`/`~` | code-reviewing (`str(None)` = `"None"`) | **schema-invalid** (not `type: string`) | fail-closed, correct |
| `0`, `[]`, `{}` | code-reviewing | schema-invalid | fail-closed, correct |
| `"N_A"` / `" n_a "` | **exempt** (case/whitespace folded) | **schema-invalid** (exact-string enum, no fold) | **gate is more lenient than schema** |
| `"n_a"` | exempt | schema-valid | agree |

The one divergent direction: `check-state.sh`'s case-insensitive, whitespace-tolerant comparison
accepts a strict superset of what the schema allows, so a hand-typed `code_grade: "N_A"` would be
exempted by INV-6 while being rejected by schema validation. Low practical severity, not med/high:
`feature-json-merge.py append-run` → `feature_json_write.write_feature_json` schema-validates
**before** the atomic write and refuses invalid documents (confirmed: `_apply` →
`feature_json_write.write_feature_json`, doc-string: "schema-validates the candidate text... before
the atomic replace"), and the `check-domain.sh` PreToolUse hook denies a raw `Write`/`Edit` with the
same violation at `sys.exit(2)` (blocking). Reaching the gap requires bypassing both — a raw
filesystem write outside every governed writer. Real, but narrow. Not blocking; recorded as a
should-fix (tighten the comparison to `.strip() != "n_a"`, dropping `.lower()`, or leave the
lenience but note it is intentional — currently unstated either way).

**Item 3 — `_squad` conjunct.** Not duplicated: the diff factors squad extraction into one
`_squad = str(entry.get("squad", "")).strip()` (`:432`), reused by the tuple append (`:433-435`) and
by the sole `_squad == "validator"` test that builds `code_reviewing_runs` (`:445-446`). The old
`any(sq == "validator" for _, sq, _ in runs)` at the INV-6 site is gone entirely, replaced by
`if code_reviewing_runs and (...)`. One test site, not two — an improvement over what the dispatch
worried about, not a new hazard.

**Item 5 — `feature_schema.py`/D-23 positional rule.** Correctly needs no `code_grade` counterpart.
`RUNS_AGENT_EXEMPT` exists because `agent`'s absence is deliberately benign and a grandfather list is
needed to let old entries through while still enforcing the key going forward. `code_grade`'s
absence is *never* benign (fail-closed = "reviewed code," true of every historical entry), so there
is no legacy corpus to grandfather and no positional enforcement to add. `test-validate-feature-json.py`
run clean (67/67 PASS) confirms no regression here.

**Item 6 — naming collision.** `code_grade` now names two unrelated things: `validate-digest.py`'s
reviewer-digest field (`pass`/`fail`/`grade_2`/`n_a`, DEC-207/FEAT-43) and `feature-schema.json`'s
new `runs[]` field (closed single-value `n_a` enum, BUG-1080). Grepped for any code path that reads
one and writes the other — none exists; the two are structurally separate documents
(`runs/*/digest.md` vs `feature.json`) with no automated bridge. So this is a **maintenance/human-
confusion hazard (med)**, not a live code defect: the closed enum actually protects against the worst
outcome (a stray `"pass"`/`"fail"` copied from a digest into a run entry is schema-refused at write
time, not silently accepted). Worth a should-fix rename (e.g. `plan_only: true` or
`reviewed_code: false`) to remove the collision, but not blocking.

**Grading.** `code-grade.py --base 9f2a0702 --head a2fb6c0b`: 7 gated functions (the new
`_inv6_feature` fixture helper and the 6 `case_inv6_*` cases), all grade 4-5 against bar 3.
`code_grade: pass` for all seven — none gated, no `grade_2_reasons` needed.

**Test suite.** `test-check-state.py`: ran clean, all ok including exit-code-unchanged guard, exit 0.
`test-validate-feature-json.py`: 67/67 PASS, exit 0. Discrimination for the 6 new cases verified by
hand-trace against the exact predicate (I could not execute a live mutant — no write grant outside
my two permitted paths) and cross-checked against the build handoff's claim: the
`entry.get("code_grade", "")` → `entry.get("code_grade", "n_a")` mutant is caught by
`case_inv6_code_run_still_fires` and `case_inv6_unknown_grade_fails_closed` plus the two pre-existing
regression guards `case_e`/`case_h` (both use a validator run entry with no `code_grade` key at all)
— 4 cases, matching the claim exactly by inspection of each assertion's fixture.

## Tooling note

`_grep`/`_read` against `test-check-state.py` (this worktree) returned content that silently spliced
over a real ~230-line span (the six `case_inv6_*` definitions, lines ~3288-3410) with no elision
marker, across two separate tool calls. `sed -n`/`grep -n` via bash against the identical path
showed the true content. Recorded here since I have no write grant to the issue-report channel;
future readers of this file who re-run `_read`/`_grep` against this same range should verify with
`sed`/`grep` directly if the returned content looks discontinuous.

## must_fix

1. **(HIGH, omission)** No documented producer sets `code_grade: "n_a"` on the plan-phase panel's
   `runs[]` entry. Update `.claude/skills/harness/SKILL.md`'s orchestrator record-step (or the
   plan-panel team's own recording instruction) to stamp it, or the fix is inert for every feature
   after this one and issue #1080 reopens on the next plan-phase panel.

## should_fix (non-blocking)

- `check-state.sh:446` — tighten `.strip().lower()` to `.strip()` so the gate's acceptance set
  matches the schema's exactly, or document the intentional lenience.
- Resolve the `code_grade` naming collision with `validate-digest.py`'s unrelated reviewer-digest
  field — different token, same repo, two meanings.
