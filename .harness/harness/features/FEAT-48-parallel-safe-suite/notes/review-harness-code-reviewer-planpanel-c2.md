# Scope review — FEAT-48 plan.yaml, cycle 2 (scope reader half)

Scope note: I am the `scope` reader for this panel only. The independent `should-not-exist`
reader (`fable-advisor`) ran in parallel under the main session, not under this lead — this
record covers my half. `goalcheck_path` does not exist (pre-signature plan); its absence is
recorded, not treated as satisfied.

## BLUF

**Do not sign yet.** All five cycle-1 findings (G-01, G-02, G-03, VL-02, the D-11 overclaim) and
`PM-01` are genuinely dispositioned as claimed, confirmed at source. But the job-2 mandate — hunt
the `PM-01` class in every `verify:` block — surfaces a **new high-severity unsatisfiable-as-
written conjunct in T-05**: its section regex requires the DEC heading to read
`## DEC-NNN The suite runs in parallel` with a plain space, but **every one of the 188 existing
`## DEC-` headings in `DECISIONS.md` uses an em-dash separator** (`## DEC-NNN — Title`, 188/188,
verified by grep). A documentor following the file's own universal convention writes a heading
the regex cannot match, and `T-05`'s own verify reddens on a substantively correct entry — the
same failure shape that let `PM-01` survive two cycles. A second, lower-stakes ambiguity in
`T-03`'s discovery walk is also newly flagged (med): as literally worded it could be read to
prune `.claude` itself, which would zero out discovery.

## Job 1 — cycle-1 fix dispositions, reconfirmed at source

| id | disposition | evidence |
|---|---|---|
| **G-01** | **CONFIRMED FIXED, both sides** | FEAT-48 `BRIEF.md`'s constraint section and `plan.yaml` D-09 (`:112-134`) now claim only "no edit to their logic," name the import as the one exception, and state the correction is FEAT-47's to make. Read FEAT-47 `plan.yaml` T-03 intent directly (`FEAT-47/plan.yaml:391-421`): it now says verbatim "THERE IS NO CLIMB TO REPOINT, and the root needs no edit at all," correctly names `root_above`, and separately instructs repointing only the `sys.path` import climb (`BIN_DIR` derivation) — exactly the narrower claim FEAT-48 makes. D-09's "no edit" framing is true as written on **both** sides today. |
| **G-02** | **DISMISSAL HOLDS, judged on merits** | T-06's `notes/measurements-parallel-suite.md` check (`plan.yaml:756-780`) is shape-only; a hand-typed note with well-formed fabricated numbers passes. No cheaper mechanical authenticity check exists without new design (crypto-signing or embedding an invocation log), and the gap is disclosed twice — `plan.yaml` T-06 intent and `BRIEF.md` `## Verification gaps` — where the human signer reads it. Concur: no edit warranted. |
| **G-03** | **CONFIRMED FIXED** | T-04 intent step 3, `plan.yaml:712-725`: "REGISTRATION, IN THIS TASK AND NOT THE NEXT ONE" — adds `test-run-pool.py` to `INTEGRATION_SCRIPTS` and to `test_kinds.integration.detect` in the same task that creates the file; T-04's `files:` list includes `.harness/harness.json` (`:507`); T-04 verify asserts `ck.returncode == 0` (`:777`). T-06 intent (`:781-836`) opens directly with "1. run-unit-tests.sh — replace the serial for loop... and NOTHING else," makes no registration claim, and T-06's `files:` no longer lists `harness.json`. |
| **VL-02** | **CONFIRMED FIXED** | D-11's "THE RESIDUAL TRADE" paragraph (`plan.yaml:173-179`) states the real operating condition (an in-run bin/ edit trips it) and requires T-06 to record it. T-06 verify (`:773`) parses `tree = re.findall(r"^tree condition: \S.*$", t, re.M)` and the exit gate (`:777-780`) requires `len(tree) == 1`; T-06 intent (`:825-836`) mandates the exact line and forbids an unrecorded answer. |
| **D-11 overclaim** | **CONFIRMED FIXED, and accurate** | The "every vector including the two the scan is blind to" sentence is gone. `plan.yaml:153-172` ("WHAT IT COVERS AND WHAT IT DOES NOT") now states: inside DIR, vector-agnostic, sees new-untracked-file creation; outside DIR, nothing — caught only by T-03's static scan with its two named blind spots — "and no criterion here claims they are" complete. I checked this against `SC-10` in `BRIEF.md`: every coverage claim SC-10 makes (edit vector, subprocess vector, creation vector, `__pycache__` exclusion, empty/absent-DIR refusal) is scoped to DIR = `bin/`; no SC or REQ in `BRIEF.md` asserts coverage D-11 disclaims. |
| **PM-01** | **CONFIRMED FIXED, verify is satisfiable** | Read `run-unit-tests.sh` at source: line 64 is `for s in "${ALL_SCRIPTS[@]}"` (the drift detector, unedited by T-06), line 148 is `for s in "${SCRIPTS[@]}"` (the serial loop T-06 replaces). `plan.yaml:760` now checks the literal substring `'"${SCRIPTS[@]}"'`, which appears **only** at line 148 today (confirmed by grep: no other line contains that exact quoted substring — `"${ALL_SCRIPTS[@]}"` does not contain it, since `${` is immediately followed by `ALL_SCRIPTS` not `SCRIPTS`). Post-fix, line 148 becomes `python3 "$BIN_DIR/run_pool.py" --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]/#/$BIN_DIR/}"` (`plan.yaml:793`), which also does not contain the substring (the `/#/$BIN_DIR/` breaks it before the closing brace). `serial` is `True` pre-fix, `False` post-fix — correctly discriminating, and line 64 survives untouched as the intent requires (`:803`, explicit callout). |

## Job 2 — every `verify:` block, both questions

| task | (a) what reddens it | (b) any tree where it passes? |
|---|---|---|
| **T-01** | live `feature_schema.py` bytes/mtime move, or the `case()` helper stops printing `ok    schema/...CRASHING schema module DENIES...` / `ok    schema/...never written...` (verified `case()`'s exact print shape at `test-check-domain.py:1447-1453`). | **Yes.** Traced the exact case-name strings the intent mandates (`plan.yaml:270-272`, "the case name must contain the words 'never written'") against `verify`'s `crash`/`untouched` string search — the mandated case names satisfy both greps by construction. Pre-fix red confirmed by research note (`bytes_equal True mtime_equal False`, since the live-tree restore still rewrites mtime). |
| **T-02** | a mutant basename appears in the live `bin_dir` listing during the poll window, or either file's subprocess exits non-zero. | **Yes.** Post-fix, mutants land in an `isolated_bin` copy under a tempdir per T-01/T-02's shared helper; the live `bin_dir` poll set is untouched. Pre-fix red is the documented positive control (research note: `appeared` names all three mutants). |
| **T-03** | live scan finds >0, `disc[0] < 50`, wrong resolved root, or misses any of the 10 named `ea6f51f` sites; `resolve_scan_root` self-comparison line present. | **Yes, but the discovery-walk wording is ambiguous — new finding, MED (below).** The rule set is empirically pre-validated: `notes/research-FEAT-48-independence-invariant.md` proves the taint/sink model finds exactly the 10 named sites with 0 false positives against `ea6f51f` (measured, reference implementation included). `git show ea6f51f:` resolves for all three named files (confirmed). Under the *correct* reading of the skip rule the live discovery count is 56 (measured with a walk matching the intended semantics), safely above the 50 floor. |
| **T-04** | any child exits non-zero unexpectedly, attribution interleaves, worker count misreports, either mutation vector is missed, empty/absent DIR reports clean, or `--check-kinds` disagrees after the same-task registration. | **Yes.** Specifically chased the job-2 hint on `os.chdir(d)` + foreign cwd: read `run-unit-tests.sh:10-16` — it resolves its root via `BASH_SOURCE[0]` (an absolute path fixed before the test's `chdir`) and `harness_boundary.resolve_root`, pure arithmetic off the script's own location, with **zero** `git` calls anywhere in the file (grepped) and `cd "$_ROOT"` as its first act — so the verify block's foreign-cwd invocation of `run-unit-tests.sh --check-kinds` (`plan.yaml:594`) is unaffected by the tempdir cwd. Not a defect; confirmed dismissed. Conjunct-by-conjunct comparison against T-04's own "ON THIS TASK'S VERIFY BLOCK" claim (`:653-661`) found no dropped property — attribution, propagation, worker-count reporting, both mutation vectors, empty-dir refusal and `--check-kinds` are each present in the block exactly as claimed; the *cap-enforcement* error path (`HARNESS_TEST_WORKERS=0`/non-integer → exit 2) is explicitly and correctly deferred to `test-run-pool.py`'s own case (d), not claimed as independently reconstructed by this task's intent — no overclaim found. |
| **T-06** | `run_pool.py` invocation absent/duplicated or missing `--mutation-check "$BIN_DIR"`; serial-loop string survives; `--check-kinds`/unknown-kind regress; measurements note missing any of the 10 `run` lines, control/post-fix counts, wall time, or the `tree condition:` line. | **Yes**, confirmed via source read of `run-unit-tests.sh`'s case statement (`:38-52`): `--kind nope` hits the `*)` branch, exit 2, satisfying `bad.returncode == 2`. `PM-01`'s replacement (above) is satisfiable and discriminating. `tree condition:` regex requires the single instructed line only; no plausible second match in the same note. |
| **T-05** | **NEW HIGH FINDING — see below.** | **No, not under this repository's established convention** — see finding. |

### New finding — T-05, HIGH: section regex cannot match the file's own heading convention

**`plan.yaml:865`**: `m = re.search(r"^## DEC-\d+ The suite runs in parallel.*?(?=^## DEC-|\Z)", txt, re.M | re.S)`.

Every one of the 188 existing `## DEC-` headings in `.harness/harness/docs/DECISIONS.md` follows
`## DEC-NN — Title` (em-dash separator) — verified with `grep -c '^## DEC-[0-9]* —'` = 188 and
`grep -c '^## DEC-[0-9]* [^—]'` = 0, zero exceptions across the entire file, including the four
most recent entries (DEC-201 through DEC-205). `plan.yaml:889` tells the author only "The heading
is: The suite runs in parallel, and no test mutates state another test can see" — it does not
name a separator, so a documentor following the file's own 100%-consistent house style writes
`## DEC-206 — The suite runs in parallel, ...`. I ran the actual regex against both spellings:
it matches the no-dash form and **fails to match the em-dash form** (verified with `re.search`
in a throwaway script). Consequence: an author who writes the heading in the only style this
file has ever used gets `m is None`, `sec = ""`, every phrase in `need` reported missing, and
`sys.exit(1)` on a substantively complete, correctly-worded entry — the identical failure shape
`PM-01` was raised for (an implementer following the plan text produces a red gate). The only way
to pass this verify block is to write a `DECISIONS.md` heading that is inconsistent with every
other entry in the file DEC-205 itself declares authoritative ("This file states current truth,"
`DECISIONS.md:6256`) — which a documentor is unlikely to knowingly do, and which a later drive-by
style pass would "fix," silently re-breaking `SC-09`. Severity high: it blocks this task's own
verify under normal, house-style-compliant authorship, and there is no readily-visible reason in
the plan text to expect the author to deviate from convention.

### New finding — T-03, MED: discovery-walk wording admits a self-defeating reading

**`plan.yaml:452-453`**: "skip `.git`, `.claude/worktrees`, `node_modules`, `.venv` and any
directory beginning with a dot other than the root itself." Read literally as a per-directory
pruning rule applied throughout the walk (not just at the four named paths), this excludes
**every** dot-prefixed directory anywhere in the tree, including `.claude` itself — which is not
the root and does begin with a dot. Since `.claude/skills/harness/bin/` is where every one of the
56 `test-*.py` files in this repository lives (measured: a walk that prunes all dot-directories
including `.claude` discovers **0** files; a walk that treats `.claude/worktrees` as the only
`.claude`-rooted exclusion discovers **56**), the literal reading makes `disc[0] >= 50`
categorically unreachable and none of the 10 historical sites discoverable — the whole invariant
would scan nothing. The correct reading is recoverable by internal consistency (naming
`.claude/worktrees` specifically would be pointless if `.claude` were already excluded by the
general dot-rule), and — unlike the T-05 finding — this one is **self-correcting**: the same
verify block's `disc[0] >= 50` and named-site assertions would loudly catch the wrong build
rather than silently pass it. Rated med rather than high because the failure is loud, not silent,
but it is a real ambiguity worth tightening before build to avoid a wasted implementation pass.

## Standing lens — re-derived, not inherited

Traces: REQ-01..REQ-08 each map to at least one task (T-01/T-02/T-04→REQ-01, T-03→REQ-02/07,
T-04→REQ-03/04/05/07, T-06→REQ-03/05/06, T-05→REQ-08); no task cites a REQ absent from `BRIEF.md`;
no orphans. `depends_on` edges: `T-01→T-02→T-03→T-04→T-06→T-05`, a valid linear chain matching
file order (`T-05.depends_on: [T-06]` confirmed at `plan.yaml`). No verify block asserts
something a predecessor task deletes. D-09's prose is internally consistent with the task set: it
correctly describes T-04/run_pool.py as the pool half and cites `run-unit-tests.sh:147-157` as
the replaced range, matching T-06's actual edit.

## Open questions

- { id: Q1, question: "T-05: should the verify regex be widened to `## DEC-\\d+.*?The suite runs in parallel` (or otherwise tolerate the em-dash) before build, given 188/188 existing headings use it?", blocking: true }
- { id: Q2, question: "T-03: should the intent's skip-list sentence be rewritten to state explicitly that only `.claude/worktrees` (not all of `.claude`) is excluded under the dot-directory rule, to remove the self-defeating reading before an implementer has to reverse-engineer the correct one?", blocking: false }

```yaml
VERDICT: FAIL
DIGEST:
  headline: >-
    Cycle-1's five fixes and PM-01 all hold, confirmed at source — but the job-2 sweep of every
    verify: block finds a new high-severity unsatisfiable-as-written conjunct in T-05 (its DEC
    heading regex cannot match the em-dash convention used by all 188 existing DECISIONS.md
    entries) plus a med ambiguity in T-03's discovery-walk wording that could zero out discovery
    if misread, though that one is self-correcting.
  severity_max: high
  findings: 2
  must_fix:
    - "T-05 (high, plan.yaml:865): the section regex '^## DEC-\\d+ The suite runs in parallel'
      requires no separator between the DEC number and title; every one of the 188 existing
      DECISIONS.md headings uses an em-dash ('## DEC-NN — Title'), so an author following the
      file's own universal convention writes a heading this regex cannot match, and the verify
      block reddens on a substantively correct entry."
  spec_violations: []
  reviewed: "unsigned plan.yaml at HEAD of FEAT-48-parallel-safe-suite worktree, cycle 2"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "T-05: widen the DEC-heading regex to tolerate the em-dash separator every existing entry uses?", blocking: true }
    - { id: Q2, question: "T-03: reword the skip-list sentence so it cannot be read as pruning .claude itself?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-planpanel-c2.md
```
