# Goal-check c4 — amended plan vs the operator's stated intent — FEAT-54

## VERDICT

**YES — this plan delivers the operator's stated intent.** The c4 amendment repointed mechanism and
file locations; it carried no intent.

**10/10 settled lines carried, 0 uncarried · 0 out-of-scope re-admissions · 0 REQs changed · 0 SC
intents changed · all four retained-item rulings intact.** Every declared path resolves and is
permitted by the layout gate; every citation exists at HEAD. **Gate verdict: PASS**, with four
non-blocking findings, none repaired.

Graded at worktree HEAD `48d27cca` **plus the uncommitted working tree** — the c4 amendment is not
committed (`git status`: `plan.yaml`, `BRIEF.md` modified), so `git diff HEAD` IS the c4 delta.
`safe_load` object diff: `tasks [T-01,T-02,T-03,T-04,T-06,T-07,T-09,T-12]`,
`decisions [D-04,D-06]`, every other top-level key byte-identical; `BRIEF.md` one hunk, old
lines 135-138 (SC-09's mechanism sentence) only. The enumerated floor exactly, nothing else.

## 1. Intent carriage — 0 uncarried

Method reused from c2 (`research-FEAT-54-goalcheck-plan-c2.md:19-28`), which mapped all ten
carriers; I re-tested each carrier's survival across the c4 delta rather than re-deriving the map.

| Grilling line | Carrier | c4 touched it | Still carries |
|---|---|---|---|
| :9 fifth standalone section | REQ-01, SC-01, T-03(a), T-04, T-08 | T-03/T-04 path-only | yes |
| :10 immediate action in `## Next` | REQ-01, SC-10, T-08, T-11 | no | yes |
| :11 one `Scope:` + 1–4 `Authority:` | REQ-02, SC-02, T-01(c), T-02 §2, T-03(c), T-06(c) | path-only | yes |
| :12 logical AND | REQ-03, SC-12, T-01(f), T-02 | path-only | yes |
| :13 four bounded types, code loc is not one | REQ-04, SC-03/13, T-01(d)(e), T-03(d)(g) | path-only | yes |
| :14 typed pointer syntax | REQ-05, SC-03, D-03, T-02 §3 | T-02 verify path only | yes |
| :15 pointers resolve when written | REQ-06, SC-15, D-10, T-03(d), T-04 | path-only | yes |
| :16 historical valid / new notes five | REQ-07, SC-04/06/11, D-01, D-08, T-05..T-07, T-11 | T-06/T-07 path-only | yes |
| :17 keep 60-line cap, no per-section caps | REQ-08, SC-05/14, T-03(e)(h), T-06(h), T-07 | path-only | yes |
| :18 permanent deterministic gate, benchmark rerun at review | REQ-10, SC-09, D-04, T-09, T-12 | **substantively** | yes — see §3 |

**The dispatch's "three touched carriers" understates the c4 delta and overstates its depth.** c4
touched carriers of nine of the ten lines, but for eight of them the change is a pure path
substitution: word-stream diff of T-03's `intent` is one replacement
(`bin/test-check-domain.py` → `tests/integration/test-check-domain.py`), T-06's likewise, and
T-01's replacements are all registration mechanism — **no case letter (a)–(h) of T-01, T-03 or T-06
changed a word.** Only :18's carriers changed in substance (D-04, T-09, T-12 rewritten, SC-09's
mechanism), and :18 is still carried: the probe stays `locally_run`, out of `test_matrix`, under a
directory neither runner glob covers.

`## Not yet specified` is `None` (grilling :22) — nothing was left open, so nothing was silently
decided. The four `## Facts I verified` are untouched by the delta.

## 2. Out-of-scope re-admissions — 0

All five lines re-checked against the amended text. Corpus rewriting: T-11 still confined to this
build's non-baselined notes; the 141-path baseline is untouched (T-05 `status: done`, its verify
re-run today: `ok 141`, every path on disk, none carrying the section). 60-line cap: kept by T-04
and T-07 verbatim. Per-section caps: T-03(h)/T-06(h)/SC-14 unchanged, word for word. Token/latency
saving: claimed nowhere. Permanent release gate: `--kind all` cannot reach `tests/manual/`
(`run-unit-tests.sh:25-27`), asserted by T-12(c). **Re-admissions: 0.**

## 3. Preservation

- **PF-1e45eb3a (D-04, T-09, T-12, SC-09 retained whole).** All four survive as artifacts; D-04's
  and T-09/T-12's mechanism moved, the retained *substance* did not: `locally_run`, absent from
  `test_matrix`, probe rerunnable, registration graded. **Intact.**
- **PF-570b9c87 (T-06 case (g), SC-04's review-time evidence).** T-06's `intent` diff is ONE path
  substitution, so case (g)'s fixture-root text and the tail paragraph are byte-identical;
  `BRIEF.md:89-101` SC-04 is outside the c4 hunk. **Intact.**
- **PF-9183266 (T-09's `exclude`).** Present in both halves: `plan.yaml:723`
  `assert k['exclude']=='.claude/worktrees/**'` and `:750`. Value verified at source —
  `test_kinds.omp_session_accessor.exclude == '.claude/worktrees/**'`, and all 8 existing kinds
  declare `exclude`. **Intact.**
- **D-10 write-time-only.** `D-10.choice`/`because` are not in the object diff; T-01(g), T-06(e1)
  and T-07's `resolve=False` clause unchanged. **Intact.**
- **SC-09 — both acceptance clauses survive UNCHANGED IN SUBSTANCE.** The leading sentence
  ("rerunnable on demand and absent from the normal suites") and
  `verify: automated  evidence: integration` are outside the hunk. Clause 1 *rerunnable on demand*:
  was "the probe is registered / zero KIND-DRIFT lines", now "`test_kinds.handoff_comprehension`
  with `status: locally_run` and `detect`/`cmd` both the probe path, asserted positively and shown
  to discriminate against a mutant config" — the same claim, and the registration carries `cmd`,
  which IS the on-demand rerun. Clause 2 *absent from the normal suites*: was "basename in neither
  `UNIT_SCRIPTS` nor `INTEGRATION_SCRIPTS`", now "under `tests/manual/`, covered by neither runner
  glob, proved by running the real runner with `--kind all` over a fixture tree." Same claim,
  and now gradable: the old mechanism named machinery that does not exist at HEAD
  (`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/`KIND-DRIFT`: 0 occurrences in `run-unit-tests.sh`, which
  selects by glob at `:25-27` and reads no test kinds). The amendment strengthens the evidence
  without widening the claim.

## 4. Per-path resolution — every declared path, one row each

Column (a) is measured, not paraphrased: each path was planted **alone** in a minimal fixture root
and `suite_layout.violations()` (`suite_layout.py:6-34`) run over it, filtered to messages naming
that path. Positive control: the four pre-amendment spellings
(`bin/test-{handoff-done-when,check-domain,check-state}.py`, `bin/probe-handoff-comprehension.py`)
and `tests/manual/test-oops.py` all come back **FORBIDDEN**, so the harness discriminates.

| Path (declared in) | (a) gate | (b) verb vs disk | (c) citations resolved |
|---|---|---|---|
| `tests/unit/test-handoff-done-when.py` (T-01 `files`/verify, T-02 verify, D-06) | allowed | "Create" · ABSENT ✔ | `test-suite-layout.py:10-14` sys.path pattern ✔ (exact), `:101-102` pins `integration.detect` to `templates/harness.json` ✔ (equal, `tests/integration/**`) |
| `.claude/skills/harness/bin/handoff_done_when.py` (T-02 `files`, T-01/T-07/T-11 intent) | allowed | "Create" · ABSENT ✔ | `plan-merge.py:66` imports yaml plainly ✔ |
| `tests/integration/test-check-domain.py` (T-03 `files`, T-04 verify) | allowed | "Extend" · EXISTS ✔ | handoff cap + missing-section fixture rows `:1137,:1140,:2889-2934` ✔ |
| `.claude/skills/harness/bin/check-domain.sh` (T-04 `files`) | allowed | "extend the RE_HANDOFF branch" · EXISTS ✔ | `RE_HANDOFF` `:1096,:1546` ✔; `_head("handoff shape (DEC-159).")` `:1562` ✔; prose site (i) "four fixed sections" `:1547` ✔; prose site (ii) cap message "It is intent, trust, / dead ends and a working set" `:1552-1553` ✔ (wrapped across two lines — a single-line grep misses it; located by content, as T-04 instructs) |
| `tests/integration/test-check-state.py` (T-06 `files`, T-07 verify) | allowed | "Extend" · EXISTS ✔ | `HANDOFF_GOOD` fixture `:2089`, shape/cap cases `:2138,:2153` ✔ |
| `.claude/skills/harness/bin/check-state.sh` (T-07 `files`, SC-04/07/08) | allowed | "extend the INV-17 pass" · EXISTS ✔ | `HANDOFF_HEADINGS` at `:1059` and read exactly twice, `:1199` (`miss`) and `:1219` (empty-body loop) ✔ — all three anchors exact, no fourth reader; SC-08's two exempt sites ✔ ("Measured at cf51dce" `:1185` + "All 74 carry the four headings…" `:1188`; "…nothing under any of them passed" `:1203`) |
| `.harness/harness.json` (T-05, T-09 `files`) | allowed | T-05 "Add two keys" · EXISTS, and **T-05 already landed** (`status: done`) — both keys present, verify re-runs green | `_panel_era_start_note` register key ✔; 8 kinds, all with `exclude` ✔; `handoff_comprehension` absent ✔ (T-09 adds it); `eval`/`ui`/`component`/`typecheck` `cmd: null` ✔ (BRIEF `## Verification gaps` true) |
| `tests/manual/probe-handoff-comprehension.py` (T-09 `files`/verify, SC-09, D-04) | **allowed** — `probe-*` is forbidden only under `bin/`; the `tests/` sweep matches `test-*.py`/`test_*.py`/`*_test.py` only (`suite_layout.py:20-28`) | "Create" · ABSENT ✔ | `tests/manual/probe-omp-session-accessor.py` exemplar EXISTS ✔ with `runner_note` ✔ and the credentials/never-in-CI docstring ✔ (but see F-02); `test-suite-layout.py:105` forbids an ACTIVE kind detecting `tests/manual` ✔; `code_grade.py:458-472` `_is_test_path` counts `locally_run` at bar 3 (`:488`) ✔; `run-unit-tests.sh --check-layout` EXISTS ✔ and exits 0 at HEAD, 2 on a planted bin test (layout suite case "planted") ✔ |
| `tests/integration/test-run-unit-tests-kinds.py` (T-12 `files`/verify) | allowed | "Create … a NEW file" · ABSENT ✔ | — |
| `tests/integration/test-run-unit-tests-layout.py` (T-12 verify + style model) | allowed | read-only, "do NOT modify" · EXISTS ✔ | `^PASS planted` emitted: **corroborated, 1 line** on a live run; `tree()` at `:15-23` builds `.harness/team-config.yaml` + copies `run-unit-tests.sh`, `harness_boundary.py`, `suite_layout.py`, `run_pool.py` + one test per kind — exactly as T-12(c) describes ✔; all four copied files EXIST ✔ |
| `.claude/skills/harness/templates/HANDOFF.md` (T-08 `files`/verify, refusal messages) | allowed | "add a fifth section" · EXISTS ✔ | header comment "Four sections, all required, ~60 lines total" `:4` ✔ (so T-08's `! grep -i 'four sections'` conjunct is RED today) |
| `.claude/skills/harness/SKILL.md` (T-08 `files`/verify) | allowed | "Rewrite it" · EXISTS ✔ | seam paragraph "Four sections, ~60 lines, shape-gated at write" `:311` ✔ verbatim |
| `.harness/harness/docs/DECISIONS.md` (T-10 `files`/verify) | allowed | "Amend DEC-159 in place" · EXISTS ✔ | "**The handoff: working memory, not summary.**" `:3698` ✔; grilling artifact `.harness/notes/grilling-handoff-done-when-2026-09-02.md` EXISTS ✔; next free id — see F-04 |
| `.harness/harness/docs/DECISIONS-INDEX.md` (T-10 `files`/verify) | allowed | "Regenerate" · EXISTS ✔ | `gen-decisions-index.py` EXISTS ✔ |
| `.harness/harness/features/FEAT-54-.../notes/` + `notes/handoff-plan.md` (T-11 `files`/verify) | allowed | "append a section" · both EXIST ✔ | baseline read with `.get(...,[])` ✔; note is NOT in the 141 ✔ |
| `notes/review-<reviewer>-*.md` (SC-04) | n/a | reviewer-authored at review · template path ✔ | pm/reviewer per-feature `notes/` convention ✔ |
| `.claude/skills/harness/templates/harness.json` (D-06, T-01) | allowed | read-only · EXISTS ✔ | `integration.detect` equals the repo value byte-for-byte ✔ |
| `tests/unit/test-*.py`, `tests/integration/test-*.py` (SC-09, D-04, D-06) | allowed | globs · both directories populated ✔ | `run-unit-tests.sh:25-27` selects exactly these two ✔ |
| `.harness/harness/features/*/notes/handoff-*.md` (REQ-07, SC-11) | n/a | corpus glob | 141 matches at the base and **0** carrying `## Done when` — re-derived today ✔ |
| `bin/test-check-{domain,state}.py`, `bin/test-handoff-done-when.py`, `bin/probe-handoff-comprehension.py` | FORBIDDEN | — | appear ONLY at `plan.yaml:139,142,148,160` (`lanes:`), the known unwritable defect — excluded by dispatch, not re-raised |

Dead-token sweep corroborated: `UNIT_SCRIPTS|INTEGRATION_SCRIPTS|KINDCHECK|KIND-DRIFT` → **0** in
both files. `check-plan-routes.py <plan>` → **exit 0, 0 violation(s), 8 DEVIATION** (baseline).

## 5. Red-capability of the eight amended `verify:` blocks

Judged against the tree the task actually starts from, and measured at HEAD where measurable.
Baseline measured today: `test-check-domain.py` rc=0 / 0 FAIL, `test-check-state.py` rc=0 / 0 FAIL,
`grep -qi 'done when'` finds nothing in either gate script.

| Task | Can it report RED before its own work? | Evidence |
|---|---|---|
| T-01 | **yes, at HEAD.** Ran it: rc=2, and `grep -q handoff_done_when` NO-MATCH on the interpreter's "no such file" message (which carries only the hyphenated `test-handoff-done-when.py`), so the verify fails today and can only pass once the test exists and fails on the module import | measured |
| T-02 | **yes, at HEAD.** rc=2 today (both files absent); green only when the test exists and passes | measured |
| T-03 | **yes, at HEAD.** Requires rc≠0 **and** `done when` in the output; the suite is rc=0 today, so the verify is red until T-03's cases exist and fail | measured |
| T-04 | **no at HEAD; yes from its real starting state.** `python3 tests/integration/test-check-domain.py` exits 0 on the untouched tree, so the block alone is non-discriminating. `depends_on: [T-03]` makes the tree it starts from red (T-03's cases fail until the gate enforces the section). **Finding F-01, low** | measured |
| T-06 | **yes, at HEAD.** Same shape as T-03; suite rc=0 today | measured |
| T-07 | **yes, at HEAD.** The `grep -qi 'done when' check-state.sh` conjunct finds nothing today, so the block is red independently of the suite; the real-corpus conjunct then requires no `Done when` line | measured |
| T-09 | **yes, at HEAD.** `probe-handoff-comprehension.py --dry-run` is rc=2 (absent) and the JSON assert `KeyError`s on `handoff_comprehension`. `--check-layout` alone is green today, but it grades the placement choice — it exits 2 iff the probe lands under `bin/` | measured |
| T-12 | **yes, at HEAD.** The new file is absent → rc=2, and the basename grep would find nothing. The `PASS planted` conjunct is green today by design (a non-weakening guard on the layout suite, not the discriminator) | measured |

## Findings — reported, not repaired

- **F-01 (low, pre-existing shape).** T-04's `verify` passes on an untouched tree (measured rc=0);
  its discrimination is inherited from `depends_on: T-03`. c4 changed only the path, so this is not
  an amendment defect. Any repair belongs to the operator's TDD-chain convention, not to this cycle.
- **F-02 (low).** `plan.yaml:730-734` tells the doer to follow
  `tests/manual/probe-omp-session-accessor.py`'s shape "… and a `--dry-run` flag". That file has no
  argument parsing at all (`grep argv|argparse` → 0 hits); the exemplar carries three of the four
  listed attributes. The task remains executable — the flag's contract is fully specified inline
  ("prints the plan of work and exits 0 WITHOUT making any model call") and T-09's verify exercises
  the file this task creates, not the exemplar.
- **F-03 (low).** REQ-07 (`BRIEF.md:41`), D-08 (`plan.yaml:204`) and T-05 (`:493`) state
  `git merge-base main HEAD` = `b7956fc4`. At HEAD `48d27cca` the merge-base is `0ec44965` — main
  advanced 13 commits past `b7956fc4`. **The data is unaffected:** 141 notes and 0 carrying the
  section at BOTH commits, and T-05's frozen list verifies green. Only the derivation sentence is
  stale, and it rots silently because the number it produces is still right.
- **F-04 (info).** D-07 (`:199`) and T-10 (`:795`) name 212 as the next free decision id "at
  `b7956fc4`"; `DEC-212` and `DEC-213` now exist, so it is 214. Not actionable — T-10 already says
  "recompute it, do not trust that number if other work has landed".

## Open questions

- **Q1 (non-blocking).** F-03: does the operator want `b7956fc4` re-worded as a pinned base sha
  rather than as an equation with `git merge-base main HEAD`? BRIEF/REQ text is approval-gated.
- **Q2 (non-blocking, harness).** `plan.yaml`'s `lanes:` block is writable by no author and read by
  no gate, so four dead surfaces cannot be corrected by the agent that owns the plan. Already
  carried up by the c4 amendment run; restated here only so it is not lost.
