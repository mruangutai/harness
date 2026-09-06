# Code Review — BUG-440-digest-verdict-reconciliation — cycle 1

**BLUF: FAIL.** Spec compliance (Stage 1) is clean — all four REQs, all five REQ-03 cases, D-07,
PF-b884d6ee, and SC-07's byte-for-byte regex citation are correctly implemented and traced. The
gate is a genuine `high` code-quality finding: the new test function
`case_bug440_digest_verdict_reconciliation` grades **1** against a test-code bar of 3
(`code-grade.py`, cyclomatic 28 / cognitive 17 / ABC 67.1, driver `cyclomatic+abc`). That is
`must_fix`; nothing else found gates.

**Pin note:** `git rev-parse HEAD` == `2964cddbbfe465d1268cb12a248861d8a28e31a6` (matches pin), but
`git status --porcelain` shows `feature.json` and `plan.yaml` for this feature modified in the
working tree (2 lines each — live bookkeeping, presumably a concurrent peer). Everything below was
read via `git show <sha>:<path>` / `git diff <base>..<sha>`, never the working tree, so this review
is unaffected by the dirty state.

## Stage 1 — spec compliance

Range reviewed: `772790be52774eafe2971f9c44400e18b2d54275..2964cddbbfe465d1268cb12a248861d8a28e31a6`
(merge-base of `origin/main`). Diff stat: 19 files, +1693/-7. Outside the declared code scope, every
touched file is BUG-440's own planning/tracking bookkeeping under
`.harness/harness/features/BUG-440-digest-verdict-reconciliation/` (BRIEF, plan.yaml, STATE.md,
notes/, observations/) — expected harness workflow byproduct, not scope creep. No file outside the
declared scope touches production or test code.

- **REQ-01** (`check-state.sh:1541-1550`): finding appended to `bad` (blocking), never `warn`.
  Message names all five things: feature (`os.path.basename(_feat_dir)`), run id (`_rid`), digest
  verdict (`_dm.group(1)!r`), feature.json verdict (`_rv!r`), digest.md path
  (`os.path.relpath(dg, H)`), feature.json path (`os.path.relpath(.../feature.json, H)`). Verified
  clean.
- **REQ-02**: equal values → the `if _dm.group(1) != _rv:` guard never appends; no `warn`/info path
  exists in this arm at all. Verified clean.
- **REQ-03**, all five cases traced from code, not the test:
  - (a) non-lead host / (b) not-complete: both gated by the pre-existing `if complete and _host in
    LEADS:` at check-state.sh:1520 — INV-37 code is unreachable outside it. Verified clean.
  - (c) missing digest.md: first `if not os.path.isfile(dg):` branch, unchanged, INV-37 code
    unreached. Verified clean.
  - (d) `validate("lead", ...)` fails: the new region is `else:` on `if _errs:` at
    check-state.sh:1533/1541 — confirmed by reading indentation, not the outer `if/elif/else` at
    :1523/:1526/:1531. A failing digest gets exactly its existing contract-violation line and
    nothing stacks. Verified clean.
  - (e) unclaimed run directory: membership is `if _rid in _recorded:` (check-state.sh:1544) — an
    explicit `in` test, not a `.get()` chain that would compare `None == None`. Verified clean.
- **REQ-04**: grepped the whole new region (check-state.sh:1516-1557) for
  `open\(|os\.(rename|remove|replace|mkdir|makedirs)|shutil\.|\.write\(` — the only hit is the
  pre-existing read-mode `open(dg, ...)`. No write, rename, or mkdir anywhere in the region. Verified
  clean.
- **D-07** (`check-state.sh:604, 654-655, 1550-1553`): `run_verdicts` is `dict[feat_dir][rid] ->
  list`, built with `.setdefault(..., []).append(...)` (never overwritten). The comparison loop is
  `for _rv in dict.fromkeys(_recorded[_rid]):` — collapses byte-identical duplicates, compares each
  distinct value, one finding per distinct contradiction. The `runs` 3-tuple at
  check-state.sh:645-651 is untouched (still `(id, squad, verdict)`), and the INV-7/INV-22 unpacks
  still expect three. Verified clean.
- **PF-b884d6ee**: read indentation directly — `runs.append((...))` and
  `run_verdicts.setdefault(...)` are both at 8 spaces inside `for entry in (...)`, outside any `if`.
  `code_reviewing_runs.append(entry)` sits at 12 spaces inside `if _squad == "validator" and
  entry.get("code_grade") != "n_a":` (check-state.sh:668-669), several lines below and structurally
  separate. Verified clean.
- **SC-07**: `validate-digest.py:1155-1160` is
  `anchors = list(re.finditer(r"^\s*VERDICT:", text, re.M))` / `if anchors: text =
  text[anchors[-1].start():]` / `m = re.search(r"^\s*VERDICT:\s*(\S+)", text, re.M)`. New code
  (check-state.sh:1546-1548) uses the identical two regex patterns and identical `re.M` flag,
  restructured as a ternary rather than an if-block (variable names differ, patterns do not — the
  citing comment at :1545 names the lines). `_dtext` is read once (:1532) and reused, no second
  `open()` of `dg`. No literal `PASS`/`FAIL`/`BLOCKED`/`ESCALATE` token anywhere in
  check-state.sh:1516-1557 (grepped). Verified clean.
- **Key identity (item 9, the highest-value check asked for)**: `os.path.dirname(fy)` (recording
  site, fy from `glob.glob(os.path.join(H, "*", "features", "*", "feature.json"))`) and
  `os.path.dirname(os.path.dirname(rundir))` (read site, rundir from `glob.glob(os.path.join(H, "*",
  "features", "*", "runs", "*", "state.yaml"))`) both derive from the SAME `H` variable
  (`check-state.sh:68`, set once) via `os.path.join` over the same wildcard-expanded directory-name
  segments. Simulated with `H` variants including a trailing slash and relative `..` components — the
  two derivations produced byte-identical strings in every case, because both are pure string
  algebra over identical inputs, never `os.path.realpath`/`normpath`. **Not vacuous.** A symlinked or
  relative `H` affects both derivations identically since they share the same `H` string and the same
  glob-matched component names.
- **Four `feature.json` corrections** — all match the BRIEF's disclosed measurement exactly:
  - `FEAT-07-verify-teeth-batch-probe`, run `goalcheck-product`: `FAIL` → `ESCALATE`.
  - `FEAT-22-docs-layout-migration`, run `2026-08-16-15-distill-product`: `INCOMPLETE` → `PASS`.
  - `FEAT-22-docs-layout-migration`, run `2026-08-16-15-distill-validator`: `INCOMPLETE` → `PASS`.
  - `FEAT-25-claim-feature-root`, run `2026-08-19-6-distill-validator`: `PASS` → `FAIL`.
  Confirmed the run ids named in each diff hunk match the disclosure exactly. **Unverifiable in this
  checkout**: all four `runs/<id>/digest.md` paths are missing from this worktree (run directories
  are untracked/per-checkout) — could not independently confirm the new value equals the digest text.
  Do not treat this as confirmed agreement; it is the disclosure's own self-reported measurement,
  unverified by me.
- **Test wiring**: `case_bug440_digest_verdict_reconciliation` (test-check-state.py:4618) covers all
  seven fixture runs (M, E, N, I, G, X, O) plus a second clean tree, each asserted separately
  (`mismatch_ok`, `no_new`, `existing`, `before == after`, `clean_ok`) rather than by one file-global
  count. Wired at `ok_bug440 = case_bug440_digest_verdict_reconciliation()` (:4853) and present in the
  final gating `and` conjunction (:4867, `... and ok_bug1305 and ok_bug440 and ok_i33 ...`) — a case
  omitted from that conjunction would not gate; this one is present. Verified clean.

## Stage 2 — code quality

**`code-grade.py --base 772790be... --head 2964cddb...`** (the pinned range) reports:

```
case_bug440_digest_verdict_reconciliation  test-check-state.py:4618
  CYCLOMATIC: 28  COGNITIVE: 17  ABC: 67.1  GRADE: 1  DRIVER: cyclomatic+abc  BAR: 3  RESULT: FAIL  SEVERITY: high
case_bug440_digest_verdict_reconciliation.digest  :4628  GRADE 5  PASS
case_bug440_digest_verdict_reconciliation.build    :4649  GRADE 4  PASS
```

- **F-01 (high, must_fix, code_grade: fail)** — `tests/integration/test-check-state.py:4618`,
  `case_bug440_digest_verdict_reconciliation`, cyclomatic 28 / cognitive 17 / ABC 67.1, grade 1
  against the test-code bar of 3, driver `cyclomatic+abc`. Concrete cost: the function inlines two
  full fixture-tree builds (7 runs, then 1 run) plus five chained boolean aggregates
  (`inv37`, `mismatch`, `no_new`, `existing`, `mismatch_ok`, `mixed_ok` — each a comprehension or
  generator over `out.splitlines()`) in one body. A future editor adding an eighth fixture run or a
  seventh assertion has no natural seam to extend without growing this further; the two extracted
  helpers (`digest`, `build`) already show the pattern that was not applied to the assertion half.
  This gates the build per `harness-code-risk-grading` (grade 1 in test code is high regardless of
  cause) — not a judgment that the assertions themselves are wrong.

- **F-02 (info, non-gating)** — `test-check-state.py:4667` (`entries = {name: "PASS" for name in
  (...)}`) constructs a dict whose values are silently discarded: `_bug1305_invariant_feature`
  (:4538-4540) does `for name in names: ... verdict: PASS` — it only ever iterates dict *keys* and
  always hardcodes `verdict: PASS`, regardless of what a caller's dict maps each name to. In this
  fixture the discarded values happen to already be `"PASS"`, so nothing is wrong today, but the dict
  shape signals per-run configurability that isn't there: a future editor extending this exact test
  to probe an *unequal* feature.json verdict for one of the non-M runs would change the dict value,
  observe no effect, and not know why. Concrete failure scenario if unaddressed: someone "fixes" a
  perceived gap by editing `entries["N"] = "FAIL"` expecting run N's feature.json verdict to change —
  it silently stays `PASS` and the intended new case is never actually exercised. Worth renaming to a
  plain list/tuple, or teaching the helper to read per-name verdicts, whichever this repo's authors
  prefer — not gating.

- **F-03 (info, non-gating)** — `check-state.sh:1541-1557`: the new INV-37 block sits in the `else:`
  arm on `if _errs:`, which is *outside* the `try/except Exception` at :1531-1535 that shields the
  digest read/`validate()` call. If the tail-anchor regex work ever raised (it practically cannot —
  `_dtext` is already a plain `str` from a successful `.read()`, and both patterns are static), the
  whole `check-state.sh` sweep would crash rather than report one more violation and continue. This
  is a loud failure, not a silent one — the opposite of the fail-open pattern this review specifically
  hunts for — so it is not gating, but it is inconsistent with the file's general practice one line
  above of wrapping digest-file handling in a guard.

**Fail-open hunt (explicit, per protocol):** every lookup/guard in the new region was traced for a
miss-sails-through case. `_recorded = run_verdicts.get(_feat_dir, {})` misses → empty dict → `_rid in
_recorded` is `False` → silent, which is REQ-03(e)'s *specified* behaviour, not a defect. `if _dm:`
false → silent, which the plan explicitly authorizes since `validate()` already guarantees a legal,
parseable token in this arm. Neither is a fail-open defect; both are the deliberately silent cases
the spec calls for.

**Verified clean, no consequence (not filed as findings):** the `dict.fromkeys` dedup behaviour on a
synthetic 2-row duplicate-id fixture was not itself exercised by the new test (not required by any
REQ/SC — D-07's disposition rests on code inspection, which checked out); the six-substring
`mismatch_ok` check for case M includes a bare `"M"` token that is redundant with the stronger
`"runs/M"` filter already applied to build `mismatch` — weak but not exploitable since the filter
already constrains the line; `case_bug1305_run_identity_invariant` (unchanged, out of scope) was not
re-graded.

## Verdict

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Spec compliance is fully clean (all REQ/SC/D-07/PF-b884d6ee traced from code); the new test function grades 1 against a test-code bar of 3 — must_fix."
  severity_max: high
  findings: 3
  must_fix: ["F-01: case_bug440_digest_verdict_reconciliation (test-check-state.py:4618) grades 1 (cyclomatic 28, cognitive 17, ABC 67.1) against BAR 3 — RESULT FAIL"]
  spec_violations: []
  code_grade: fail
  reviewed: "772790be52774eafe2971f9c44400e18b2d54275..2964cddbbfe465d1268cb12a248861d8a28e31a6"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/review-harness-code-reviewer-c1.md
```
