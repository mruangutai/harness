# Efficiency angle — FEAT-45 plan surface

**BLUF:** The DAG is over-serialized. 8 of 10 tasks carry a `depends_on` edge that is
narrative-only — nothing in the dependent's `intent`/`verify` reads the predecessor's file.
Dropping the false edges (keeping the two content-real chains, T-08→T-07 and
T-10→{T-02,T-03,T-04}, plus one shared-file edge, T-10→T-09) collapses the plan from
**5 waves to 2 waves**.

## Current DAG (as written)

```
W1: T-01
W2: T-02
W3: T-03, T-05, T-06
W4: T-04, T-07, T-09
W5: T-08, T-10
```
5 waves.

## Edge-by-edge ruling

- **T-02 `[T-01]` — FALSE.** T-01 appends two DEC entries to `DECISIONS.md`/`-INDEX.md`. T-02's
  intent (author `plan-panel.yaml`, matching `review.yaml`'s vocabulary) and verify (structural
  YAML assertions + a `check-domain.sh --resolve` probe) never cite a DEC number or read either
  file T-01 touches. **Saves 1 step**: T-01 and T-02 can share wave 1.

- **T-03 `[T-02]` — FALSE.** T-03 edits `SKILL.md` to *describe* the plan-panel team (filename,
  generic "spawned non-harness subagent" framing) — all of it derivable from the plan's own
  decisions (D-01..D-04), not from reading T-02's actual `plan-panel.yaml` content (step ids,
  personas). Verify never opens `plan-panel.yaml`. **Saves 1 step.**

- **T-04 `[T-03]` — FALSE.** T-04 edits only the `**Target state:**` bullet of
  `harness-plan.md`; its verify checks tokens (`plan-panel`, `DEC-176`, `approval.rulings`,
  `simplify`) against that file alone. Nothing in T-04's intent or verify reads `SKILL.md`.
  **Saves 1 step** (independent of T-03's own drop).

- **T-05 `[T-02]` — FALSE.** T-05 defines the `panel`/`rulings` schema shape in the plan template
  and `harness-spec-driven/SKILL.md`, fully spelled out from D-05/D-06/D-07 in T-05's own intent
  block. It does not read `plan-panel.yaml`. **Saves 1 step.**

- **T-06 `[T-02]` — FALSE.** T-06 adds a doctrine section to `harness-validator-lead.md`
  restating the shape/severity contract already fixed by D-03/D-06 — no grep or read of
  `plan-panel.yaml`'s content (step ids, prompts). **Saves 1 step.**

- **T-07 `[T-05]` — FALSE.** INV-32's four checks (panel shape, per-finding severity gating,
  rulings attribution, stale-ruling) are fully re-specified in T-07's own intent, verbatim from
  the decisions — `check-state.sh` reads a project's *real* `plan.yaml`, never the *template*
  T-05 edits. **Saves 1 step.**

- **T-09 `[T-05]` — FALSE.** `panel_findings.py`'s hash algorithm (lowercase+collapse-whitespace,
  sha256, `PF-`+8 hex) is fully specified in T-09's intent directly from D-05. It never reads
  `templates/plan.yaml` or `harness-spec-driven/SKILL.md`. **Saves 1 step.**

- **T-08 `[T-07]` — REAL, keep.** `test-check-state.py`'s `inv32-red` case locates the literal
  marker lines `# INV-32 BEGIN (FEAT-45 T-07)` / `# INV-32 END (FEAT-45 T-07)` inside
  `check-state.sh`, copies the file, and slices out the region T-07 wrote — a genuine read of
  T-07's produced content, not just its existence.

- **T-10 `[T-02, T-03, T-04, T-06, T-09]`** — mixed:
  - **`T-02` REAL.** `test-plan-panel.py` case 1 does `harness_yaml.load_file('plan-panel.yaml')`
    and asserts literal prompt substrings and step personas; cases 2/3/4/6 re-open the same file.
  - **`T-03` REAL.** Case 1 also asserts the goalcheck question string appears in `SKILL.md`;
    case 2 resolves the `notes/research-<FEAT>-goalcheck-plan-c0.md` path `SKILL.md` names.
  - **`T-04` REAL.** Case 7 regex-slices the `**Target state:**` bullet of `harness-plan.md` and
    asserts `plan-panel` and `simplify` both appear.
  - **`T-06` FALSE.** None of `test-plan-panel.py`'s seven cases open, grep, or otherwise
    reference `harness-validator-lead.md` (in either `.omp/agents/` or `.claude/agents/`) — the
    doctrine content T-06 adds (`unrated`, `plan-panel`, `never CONTENT`) is checked only by
    T-06's own verify block, never by T-10's. **Saves 1 step.**
  - **`T-09` FALSE for content, but REQUIRED for a different reason — keep it, mislabeled.**
    `test-plan-panel.py` never opens `panel_findings.py` or `test-panel-findings.py`, and T-10's
    verify never greps for `test-panel-findings.py` in the suite's output. But T-09 and T-10 BOTH
    append an entry to the same `UNIT_SCRIPTS` array in `run-unit-tests.sh`, and plan-level tasks
    (unlike team steps) have no `mutates_repo` primitive (only team-step YAML carries that key —
    confirmed in T-02's own intent, line ~282) — `depends_on` is the *only* thing serializing this
    write. So the edge is accidentally-labeled: it reads as a content dependency but is load-bearing
    only as a write-conflict lock. **Recommend to pm:** keep the edge, but change its cited reason
    from "T-10 needs T-09's output" to "shared-file serialization on `run-unit-tests.sh`" so a
    future reader doesn't drop it as a false content edge — which it would otherwise correctly look like.
  - **T-07/T-08 correctly absent** from T-10's `depends_on` — `test-plan-panel.py` grades
    doctrine/wiring files only; it never touches `check-state.sh` or `test-check-state.py`.

## Cost

Before: **5 waves**. After (drop the 8 false edges above, keep T-08→T-07 and the four T-10 edges
including the relabeled T-09 one): **2 waves** — `{T-01,T-02,T-03,T-04,T-05,T-06,T-07,T-09}` then
`{T-08,T-10}`. **3 sequential steps saved.**

## Repeated work: `run-unit-tests.sh --kind unit` in T-09 and T-10 verify

Measured once, read-only, on this checkout: **wall 20.3s** (`time bash
.claude/skills/harness/bin/run-unit-tests.sh --kind unit`). Not negligible in absolute terms, but
each task registers a *different* new test file (`test-panel-findings.py` vs.
`test-plan-panel.py`) and each verify's own full-suite run is that task's own proof its
registration didn't drift — this is the KIND-DRIFT boundary check DEC-174 exists for, not
duplication of the same claim. Because T-10→T-09 must stay serialized anyway (shared-file write
above), the two 20s runs are on the critical path regardless of wave restructuring — that cost is
inherent to two tasks touching one shared array file, not fixable by DAG reshaping. Not flagged as
a finding to act on.

## plan.yaml / BRIEF.md / .claude untouched

`git status --porcelain` on `plan.yaml`, `BRIEF.md`, and `.claude/` at review_sha
1d3e5db5d17d9e7cf484b38e3796cf8ed5468bb1 returns empty — no modifications made by this pass.
