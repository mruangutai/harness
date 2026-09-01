# Scope review — FEAT-48 plan.yaml, cycle 3 (final round before signature)

Scope note: `scope` reader only. `goalcheck_path` does not exist — the plan is pre-signature, so
no goal-check has run; its absence is recorded, not treated as satisfied. Reviewed at worktree
commit `d5c23a0` (rebased onto main after FEAT-45 merged). `SEC-01` (`validate-digest.py:745`)
still rejects a placeholder `review_sha`; this artifact plus the returned yaml block below are the
full return, per dispatch — no retry attempted.

## BLUF

**I would sign this plan.** All four cycle-2 items resolve cleanly, confirmed at source with
independent re-derivation (not trust of the plan's own prose), and both of this round's
substantive changes (T-02's fourth mutant site, T-03's content-read exclusion) are correct and
their verify blocks discriminate on live evidence, not assumption. Two new findings, both narrow
and both about *disclosure precision* rather than a broken build or an unsatisfiable gate:
`severity_max: med`. Per the operator's stated bar, med-or-below is signable.

## Job 1 — cycle-2 items, dispositioned at source

| item | disposition | evidence |
|---|---|---|
| **a. T-05 DEC-heading regex** (`plan.yaml:927`) | **CONFIRMED FIXED, both directions tested** | `re.search(r"^## DEC-\d+\b[^\n]*?The suite runs in parallel.*?(?=^## DEC-|\Z)", txt, re.M\|re.S)`. Ran it myself against three fixtures: em-dash house style (`## DEC-206 — The suite runs in parallel, ...`) **matches**; a heading with the right number but wrong title **does not match** (`m is None`); an absent phrase entirely **does not match**. `[^\n]*?` cannot cross a newline, so a same-named phrase appearing only in a *different* entry's body text also does not false-positive-match. Both directions hold. |
| **b. T-03 discovery-walk skip list** (`plan.yaml:473-479`) | **CONFIRMED FIXED** | New wording is unambiguous: "There is NO general dot-directory rule... `.claude` begins with a dot and must be WALKED... `.claude/worktrees` is named as an exclusion precisely because `.claude` itself is not one." I independently re-implemented the exact rule (prune `.git`/`node_modules`/`.venv` by name at any depth, prune `.claude/worktrees` by path, walk everything else) and ran it over the live worktree: **58** files discovered, matching the plan's claim exactly and comfortably clearing the verify block's `>=50` floor. c2's MED (self-defeating reading that would zero discovery) cannot recur under this wording. |
| **c. D-09 census count** (`plan.yaml:121-126`) | **CONFIRMED ACCURATE** | "exactly TWO new `test-*.py`... `test-suite-independence.py` (T-03) and `test-run-pool.py` (T-04) — plus two non-test helpers... `isolated_bin.py` (T-01) and `run_pool.py` (T-04)." Parsed every task's `files:` list directly: T-01 → `isolated_bin.py` (new) + `test-check-domain.py` (edited); T-02 → two edited files, no new file; T-03 → `test-suite-independence.py` (new) + edited `run-unit-tests.sh`; T-04 → `run_pool.py` (new) + `test-run-pool.py` (new) + two edited files; T-06/T-05 → no new `bin/` files. Sum matches D-09's claim exactly, no drift. |
| **d. D-11's third static-scan blind spot** (`plan.yaml:169-175`, T-05 intent `~985-988`) | **Stated accurately** — T-03's taint model seeds only the literal `__file__`; a write built from a relative literal or `os.getcwd()`-joined path carries no tainted name and both halves miss it if it lands outside `bin/`. Verified against T-03's own taint rule text: nothing in it seeds anything but `__file__`. **But see Finding F2** — a related, *unnamed* fourth blind spot exists in the same neighborhood, opened by this cycle's own content-read fix, and D-11/T-05 do not disclose it even though the plan's stated philosophy ("named here so the next auditor does not read the two named blind spots as the whole gap") argues it should be. No `SC` in `BRIEF.md` claims coverage D-11 disclaims. `REQ-02`, however, does — see Finding F1. |

## Job 2 — this round's two substantive changes

**a. T-02's fourth mutant site** (`test-check-state.py:3066-3088`, `.check-state-inv32-mutant.sh`)

- **Located exactly where the plan says.** Read the live file: `_inv32_mutant_is_discriminating` spans `3066-3088` verbatim (function def at `3066`, the `finally: os.unlink(mutant)` closing the block at `3088`); the mutant path is built at line `3070` — `os.path.join(os.path.dirname(SCRIPT), ".check-state-inv32-mutant.sh")`, exactly matching the dispatch's own citation.
- **T-02's `files:` and intent reach it**: `test-check-state.py` is in T-02's `files:` list; T-02 intent names this exact site and range under "THE FOUR SITES."
- **The verify block still discriminates — reconfirmed empirically, not by reading.** I ran T-02's own verify script (unmodified) against the live, unfixed tree right now:
  `fails [] appeared ['.check-state-inv32-mutant.sh', '.mutant-check-state-t10.sh', '.mutant-check-state-t14.sh', '.mutant-feature-worktree-behind.py'] moved [] → exit 1`.
  All four basenames appear, including the new one; the block reddens today exactly as a
  positive control must, and nothing about counting "what appears" (vs. naming fixed basenames)
  weakens that.

**b. T-03's content-read exclusion clause**

- **(i) Precise enough to build the scan the counts assume.** I independently re-implemented the taint model from the clause's own text (a value expression that IS a bare `.read`/`.readline`/`.readlines`/`.read_text`/`.read_bytes`/`.load`/`.safe_load` call does not propagate taint) against `git show ea6f51f` copies of the three files, with a per-scope, source-order, with-item-aware walker. **With** the exclusion it reproduces exactly the ten named `(file, line)` sites and nothing else. **Without** it, it reproduces exactly the fifteen extraneous locations the plan describes, all in `test-check-domain.py` between `1786` and `2071` (`os.makedirs`/`open('w')` under a tempdir rooted in `fixture(manifest_text)`). The clause is implementable as specified.
- **(ii) The hole it opens — named concretely.** The exclusion is correct and necessary (`SC-03`'s live-tree zero is otherwise unreachable in any tree — confirmed by my own re-scan). But it is a blanket rule: it also un-taints any value built from a tainted file's *content*, not just from a path. A test that reads a live-checkout file's text and derives a **write target** from that text — e.g. a path *string* embedded in a manifest, config, or fixture file it reads via `.read()`/`.load()` — would no longer be flagged, even where that derived target is itself inside the live checkout. This is a fourth static-scan blind spot, in the same family as D-11's three named ones (subprocess-mediated, helper-wrapped, relative-literal/`os.getcwd()`), but **it is not named anywhere in D-11 or T-05's DECISIONS entry.** I found no evidence any of the 58 live test files currently exploits it (my re-scan of the live rule reproduces exactly the known 10/13 sites, nothing more) — see Finding F2 for severity reasoning.
- **(iii) Counts reconcile.** Re-derived independently (not merely re-reading the plan's own numbers): 25 findings without the clause at `ea6f51f` (10 real + 15 extraneous, all in the `1786–2071` range as claimed), exactly 10 with it. Matches `plan.yaml`'s own claim and the research note's re-derivation word for word. The live-tree "13, minus T-01/T-02's four fixes, plus the two FEAT-45 test files reporting zero" chain was not independently re-run (T-03 doesn't exist yet to execute), but the ten-site and fifteen-extra numbers it depends on are now independently confirmed, not merely trusted.

## Job 3 — satisfiability of every verify block, this cycle and repaired ones alike

| task | (a) what reddens it on broken work | (b) any tree where it passes? |
|---|---|---|
| **T-01** | Live `feature_schema.py` bytes/mtime move, or `case()` stops emitting the two required substrings (`"CRASHING schema module DENIES"`, `"never written"`). | **Yes.** Read `case()`'s exact print shape and today's case-3 name at source (`test-check-domain.py:1447-1490`); the crash-case substring is already present verbatim. The restore-case name intent mandates ("...never written (bytes and mtime unchanged)") satisfies the `untouched` grep by construction. Unchanged since c0/c1; not re-run end-to-end this cycle (verify block itself untouched by this cycle's diff). |
| **T-02** | A mutant basename appears in the live `bin_dir` listing during the poll window, either subprocess exits non-zero, or a tracked file's mtime moves. | **Yes — empirically reconfirmed today** (see Job 2a): current run exits 1 with all four basenames under `appeared`; post-fix, mutants land in an `isolated_bin` copy under a tempdir and none of this fires. |
| **T-03** | Live scan reports >0, `disc[0] < 50`, wrong resolved root, misses any of the ten named `ea6f51f` sites, or the file contains a literal `resolve_scan_root(x) == resolve_scan_root(x)`-shaped self-comparison. | **Yes — independently re-derived**, not merely re-read: 58 files discovered under the live rule (comfortable margin over the 50 floor); `root_above` is a pure marker-walk verified at `harness_boundary.py:84-100`; the content-read-excluded taint model, reimplemented from scratch, reproduces exactly the ten named sites at `ea6f51f`. |
| **T-04** | Any child exits non-zero unexpectedly, attribution interleaves, worker count misreports, either mutation vector is missed, empty/absent `DIR` reports clean, or `--check-kinds` disagrees after this task's own registration edits. | **Yes.** Verify block text is byte-identical to what c1 (F-05 fix) and c2 confirmed; this cycle's diff does not touch T-04's `verify:` or its foreign-`cwd` handling. Re-confirmed the load-bearing fact c2 traced (`run-unit-tests.sh` resolves its root from `BASH_SOURCE[0]`, zero `git` calls, `cd "$_ROOT"` as its first act) still holds against the current file. Not independently re-executed this cycle (`run_pool.py`/`test-run-pool.py` do not exist yet). |
| **T-06** | `run_pool.py` invocation absent/duplicated/missing the exact `--mutation-check "$BIN_DIR"` argument, the serial-loop string survives, `--check-kinds`/unknown-kind regress, or the measurements note is missing any required line, count, or the `tree condition:` line. | **Yes — reconfirmed at source today.** Grepped `run-unit-tests.sh` directly: line `64` is `for s in "${ALL_SCRIPTS[@]}"` (drift detector, untouched by T-06), line `148` is `for s in "${SCRIPTS[@]}"` (the loop T-06 replaces) — the literal substring `"${SCRIPTS[@]}"` occurs **only** at line 148 today, and the planned replacement line (`"${SCRIPTS[@]/#/$BIN_DIR/}"`) does not contain it either (character-checked, the `/#/` breaks the match before the closing brace). `--kind nope` hits the case statement's `*)` branch → exit 2, confirmed by reading the case block. |
| **T-05** | Section regex fails to locate the `## DEC-NN` heading, any of the fifteen required phrases or the 300-word floor is missing, or the generated index drifts from the committed one. | **Yes — independently tested (see Job 1a)** and `gen-decisions-index.py`'s `--stdout`/no-`--check` contract reconfirmed at source (`gen-decisions-index.py:6-10, 253-259`): unrecognized args exit 2, `--stdout` is the only accepted token, matching what T-05's verify block calls. `DECISIONS.md` today: 190/190 headings em-dash style, last is `DEC-207` — matches the plan's cited baseline exactly, so the next-free-number authoring-time approach lands at `DEC-208` as expected. |

No block in this table reddens on correct work, and none passes on broken work in any tree I could
construct or find evidence for. The standing lens (Job 0) is unchanged from c1/c2: every `REQ-01`
through `REQ-08` traces to at least one task, no task cites a REQ absent from `BRIEF.md`,
`depends_on` forms the same valid linear chain (`T-01→T-02→T-03→T-04→T-06→T-05`), and no verify
block asserts something a predecessor task deletes.

## Findings

**F1** [severity: **low**] — `BRIEF.md` `REQ-02`: "A violation of REQ-01 reintroduced anywhere in
the test tree fails a gate CI already runs..." is an unqualified universal claim. `plan.yaml` D-11
(`:169-175`) discloses that a violation via a relative-literal- or `os.getcwd()`-derived path,
landing outside `.claude/skills/harness/bin/`, is caught by **neither** the static scan nor the
runtime check — a case where `REQ-02`'s literal "anywhere" does not hold. No `SC` overclaims this
(each names its specific covered vectors), so this is a `REQ`-vs-plan wording tension, not a gate
defect. Narrow and not currently exploited by any of the 58 discovered test files. Advisory: the PM
may want to soften `REQ-02`'s wording or add an explicit caveat alongside the existing
`## Verification gaps` section, but nothing here blocks a build that will ship correctly.

**F2** [severity: **med**] — T-03's content-read exclusion (correct and necessary — without it
`SC-03`'s live-tree zero is unreachable in any tree, independently reconfirmed) opens a **fourth,
unnamed** static-scan blind spot: a write to a path derived from the *content* of a tainted-path
read (as opposed to the path itself) is never tainted, so a test that reads a live file's text and
builds a write target from that text — rather than from `__file__` or a name derived from it —
escapes the static scan even where the resulting target is genuinely inside the live checkout. This
sits in the same family as D-11's three explicitly-named blind spots (subprocess-mediated,
helper-wrapped, relative-literal/`os.getcwd()`), but is not named in D-11 or in T-05's mandated
DECISIONS entry, despite the plan's own stated discipline of naming known gaps explicitly so "the
next auditor does not read the [] named blind spots as the whole gap." Currently unexploited — my
independent re-derivation of the live-tree scan (Job 2b(iii)) finds exactly the known 10/13 sites
and nothing else — so this is a residual/future risk rather than a live defect, and it matches the
exact defect class (a guard whose completeness claim quietly narrows) this feature exists to
eliminate, which is why I am not rating it lower than med despite the empty exploit surface today.
Advisory: name it in T-05's DECISIONS.md entry alongside the third class, or in a comment on the
content-read exclusion itself, before or shortly after signature — it does not block this build.

## Open questions

- { id: Q1, question: "Should DEC-208 (T-05's entry) explicitly name the content-read-derived-path blind spot (F2) alongside the third uncovered class it already names, so the completeness disclosure stays accurate as of this build?", blocking: false }
- { id: Q2, question: "Should BRIEF.md REQ-02's wording be softened (or caveated) to match what the delivered two-mechanism coverage can actually prove, given D-11's own disclosed third blind spot?", blocking: false }

```yaml
VERDICT: PASS
DIGEST:
  headline: >-
    All four cycle-2 items hold at source, independently re-derived rather than trusted, and both
    of this round's substantive changes (T-02's fourth mutant site, T-03's content-read exclusion)
    are correct and empirically discriminating. Two new low/med advisory findings about disclosure
    completeness, neither blocking: severity_max med, no must_fix. I would sign this plan.
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "unsigned plan.yaml at d5c23a0 (FEAT-48-parallel-safe-suite worktree), cycle 3"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should DEC-208 name the content-read-derived-path blind spot (F2) alongside the third uncovered class it already names?", blocking: false }
    - { id: Q2, question: "Should BRIEF.md REQ-02's wording be softened to match what the two-mechanism coverage can actually prove, given D-11's own disclosed gap?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-planpanel-c3.md
```
