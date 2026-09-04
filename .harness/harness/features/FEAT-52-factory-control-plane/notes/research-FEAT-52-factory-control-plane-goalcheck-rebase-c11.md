# Goal-check — FEAT-52 factory-control-plane — post-rebase, graded at `HEAD d2bfb4bd`

## BLUF

**FAIL — one new blocker, three carried.** The decision collision is **CLOSED**: the branch is now
43 commits ahead of and 0 behind `origin/main` (`origin/main` is an ancestor), main's `DEC-213 —
Harness's own tests live under tests/**` survives at `DECISIONS.md:6645`, FEAT-52's entry is
renumbered to `DEC-214` at `:6689`, there is no duplicate heading, and
`gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` is byte-clean — the `@line` rot that
failed the previous check is gone.

The rebase that closed the collision opened a bigger one. `DEC-213` makes the test directory the
kind, and FEAT-52's two test files are still under `bin/`:

```
run-unit-tests.sh --check-layout  -> exit 2
MISCONFIGURED: test-shaped file remains under bin: .claude/skills/harness/bin/test-anchor-directions.py
MISCONFIGURED: test-shaped file remains under bin: .claude/skills/harness/bin/test-check-instruction-paths.py
```

The layout delegation runs **before any test** (`run-unit-tests.sh:33-42`), so at HEAD **no kind
runs at all** — unit, integration or all. Five criteria (SC-03, SC-04, SC-05, SC-06, SC-11) name
those two files as their carriers, and the qa gate cannot pass for any change type while the tree is
MISCONFIGURED. Both suites are green when invoked by hand (`test-check-instruction-paths.py` 16 PASS,
`test-anchor-directions.py` 7 ok with `HARNESS_REVIEW_SHA=d2bfb4bd`) — the defect is location, not
content.

## Criterion verdicts at `d2bfb4bd`

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated/integration* | `tests/integration/test-inject-expertise.py` case4b — 21 ok, exit 0 |
| SC-02 | met | automated/integration* | same file, case4c + case14 — exit 0 |
| SC-03 | **not_met** | automated/unit | carrier `bin/test-check-instruction-paths.py:59` is run by **no** runner (B1) |
| SC-04 | **not_met** | automated/unit | carrier `bin/test-anchor-directions.py` run by no runner (B1); also mandated `git show <review_sha>:` pin is off-branch (B5). Passes 7/7 when fired by hand at HEAD |
| SC-05 | **not_met** | automated/unit | carrier unrunnable (B1); assertion itself green (`:40`, inline `:1:`, fenced `:3:`, `2 violation(s)`) |
| SC-06 | **not_met** | automated/unit | unchanged from c10. Sole assertion is `os.path.isfile(debug_path)` at `bin/test-check-instruction-paths.py:64`; no `product_cwd` fixture and no placeholder-stripped `not os.path.exists(...)` half exists anywhere in the file (grep `product_cwd` → 0 hits) |
| SC-07 | met | inspection | `.harness/team-config.yaml` zero-line diff `origin/main..HEAD`; the `.omp/agents/*.md` additions only re-anchor pre-existing writable claims — no new path, no `tools:` change |
| SC-08 | met | automated | `case_workflow_gate` — real `tests.yml` plus both mandated mutants asserted false |
| SC-09 | **partial** | inspection | Contract present (`harness-handoff/SKILL.md:62,63,65`), entry present (`DECISIONS.md:6689`), collision closed. **The index row's ruling is unwritten** — `DECISIONS-INDEX.md:214` reads `⚠ RULING PENDING`, so `test-gen-decisions-index.py::test_committed_index_is_complete_and_within_budget` **FAILS** ("1 row(s) unwritten … Offending: DEC-214"), exit 1, and T-13's signed `verify:` is red (B4) |
| SC-10 | met | automated/integration | `test-inflight-registry.py` — 126 ok, exit 0 (`case_35_feature_root_cli`, `_ambiguous_feature_root_case`) |
| SC-11 | **not_met** | automated/unit | carrier unrunnable (B1); row `SC-11 S2 write observations` green at HEAD by hand; pin off-branch (B5) |
| SC-12 | **not_met** | automated/unit | unchanged from c10. `test-inject-expertise.py:249-251` asserts only `HARNESS_PATH_DRIFT: none` and `1 unanchored path(s)`; the criterion's `<file>:<line>` detail line (`.omp/agents/harness-qa.md:1`, which the case's own stub checker prints at `:237`) is asserted nowhere |
| SC-13 | met | automated/integration | `test-dispatch-guard.py` case_17 — 48 ok, exit 0 |
| SC-14 | met | inspection | Four per-file findings at HEAD: `harness-product-lead.md:92`, `harness-eng-lead.md:110`, `harness-validator-lead.md:138` (no shell / dispatch-line anchor / `VERDICT: BLOCKED`), `harness-orchestrator.md:157` (emit duty), plus `harness-handoff/SKILL.md:65`. Graded at HEAD because the mandated pin is off-branch (B5) |
| SC-15 | met | automated/integration | `test-check-domain.py` `SC-15 PAIR` — 301 ok, exit 0 |

\* SC-01, SC-02 and SC-12 declare `evidence: unit`, but their carrier
`test-inject-expertise.py` lives in `tests/integration/` — under `DEC-213` the directory **is** the
kind, so the declared label is false at HEAD. Substance is proven; the label is not. See Q1.

Suites run by me at HEAD (tracked tree clean apart from my own notes/observations,
`HARNESS_AGENT_TYPE` unset): `test-inject-expertise.py` 21 ok, `test-dispatch-guard.py` 48 ok,
`test-inflight-registry.py` 126 ok, `test-check-domain.py` 301 ok, `test-suite-layout.py` 20 PASS —
all exit 0. `test-gen-decisions-index.py` **exit 1**, one FAIL. `run-unit-tests.sh --check-layout`
**exit 2**. `check-state.sh` exit 1, but both VIOLATIONs are FEAT-51's; FEAT-52 carries notes only
(five unrecorded run dirs).

## Blockers, criterion-level

- **B1 (new, dominant)** — `bin/test-anchor-directions.py` and `bin/test-check-instruction-paths.py`
  violate `DEC-213`; `suite_layout.violations('.')` returns exactly those two, and the runner exits
  2 before running anything. Kills SC-03, SC-04, SC-05, SC-06, SC-11 and the qa gate for every kind.
- **B2** — SC-06's discriminating half still absent (`:64`).
- **B3** — SC-12's `<file>:<line>` assertion still absent (`:249-251`).
- **B4** — `DEC-214`'s index ruling unwritten; the generator does not emit the `' :: <ruling>'` tail,
  so regeneration alone will never satisfy it. `test-gen-decisions-index.py` red.
- **B5** — `feature.json review_sha = 49df4bee` is **not an ancestor of HEAD** (the rebase rewrote
  it; the object survives only in this checkout's store). Every criterion whose method is
  `git show <review_sha>:<path>` — SC-04, SC-11, SC-14 — grades a commit that will never merge, and
  fails outright in CI or a fresh clone.

## REQ coverage

REQ-01 → T-03/T-14 (`inject-expertise.sh` control-plane block; proven). REQ-02 → T-04..T-08, T-10,
T-11 — the five canonical sites are correctly anchored at HEAD (`test-anchor-directions.py` 7/7 by
hand), but its family-5 half is still the one SC-06 cannot prove. REQ-03 → SC-07. REQ-04 → T-02,
T-12 (checker + enforced `integration` step; the checker's own suite is currently outside every
runner). REQ-05 → case4c. REQ-06 → T-01, T-09, T-15. **No requirement is unimplemented** — all five
blockers are evidence, location and record defects.

## Next action — one remediation cycle, main-session-direct (DEC-174), then re-pin

1. Move both test files into `tests/unit/` (their criteria declare `unit`, and `unit`/`integration`
   is the only discoverable pair), fix their `HERE`-relative `CHECK`/`REPO_ROOT` constants for the
   new depth, and confirm `run-unit-tests.sh --check-layout` exits 0.
2. Restore SC-06's deleted half in `test-check-instruction-paths.py`: the `product_cwd`
   product-shaped temp checkout, and the placeholder-stripped
   `not os.path.exists(<product_cwd>/.agents/skills/harness-systematic-debugging/SKILL.md)`
   assertion. Keep the split shape that satisfied `code-grade.py`.
3. Add the `<file>:<line>` assertion to `test-inject-expertise.py::case4d` — assert
   `.omp/agents/harness-qa.md:1` appears in the drifted context, not merely the count line.
4. Write `DEC-214`'s ruling text after `' :: '` on `DECISIONS-INDEX.md:214` **by hand** (the
   generator preserves hand-written rulings by DEC number; it never produces them), then re-run
   `gen-decisions-index.py --stdout | diff -` and `test-gen-decisions-index.py`.
5. Re-pin `review_sha` to the resulting HEAD and re-take **SC-03, SC-04, SC-05, SC-06, SC-09,
   SC-11, SC-12, SC-14** only.

Advisory, not gating, not covered by any SC: `dispatch-guard.sh:175-176` carries the
`AmbiguousWorktree` refusal branch, and `test-dispatch-guard.py` still has no case for it — the
resolver side is covered (`test-inflight-registry.py:1041`), the guard side is not. Worth folding
into step 3.

## Open questions

- **Q1 (blocking the grade, operator)** — SC-01, SC-02 and SC-12 declare `evidence: unit` while
  their carrier is `tests/integration/test-inject-expertise.py`, a main-side file whose location
  FEAT-52 did not choose. Re-label those three to `integration` by BRIEF amendment, or move the
  file? Amending a signed criterion is not a pm write, and I will not soften the label silently.
- **Q2 (non-blocking, harness owner)** — carried from c10 and now demonstrated twice: a rebase onto
  `main` can falsify criteria that were graded met, and nothing in the review/ship path re-takes
  grades after history moves. B1 is a rule that arrived from main; B5 is a pin the rebase orphaned.
- **Q3 (non-blocking, harness owner)** — `DECISIONS-INDEX.md` completeness is gated only by
  `test-gen-decisions-index.py`, which is not reachable while the tree is MISCONFIGURED (B1). Two
  record gates in series, both currently dark.
