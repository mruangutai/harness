# QA verify-method adequacy audit — FEAT-05 PyYAML file parsers

Reviewer: harness-qa · review_sha pinned `340e18a` · diffed `37a8a66..340e18a` (18 commits)

**PATH NOTE, read first:** the dispatch named
`.harness/features/FEAT-05-pyyaml-file-parsers/notes/review-harness-qa-c0.md`. My write
grant (`team-config.yaml`) permits `.harness/features/*/notes/qa-*.md`, not
`review-harness-qa-*.md`; `check-domain.sh` denied the named path. Written instead to
`notes/qa-c0.md` per the hook's own instruction ("do not work around this hook"). Same
routing-wall class PLAN.md already logs three recurrences of (FEAT-03 Q13, FEAT-04
T-09, this feature's own T-10/T-11) — now a fourth, on the dispatch side rather than
the plan side. Non-blocking, flagged in `open_questions`.

## BLUF

**T-07's conversion of `check-state.sh` is 70% incomplete, it is not merely a leftover
regex, and it reproduces live: I triggered a real fail-open with the exact defect class
this feature exists to close.** Only 3 of the 10 census-named call sites (the
`runs:`/`val()` loop — issue #11's fix) were actually converted to `harness_yaml`. The
other 7 — `phase:` (INV-17), `state.yaml`'s `status:`/`cost:`/`host:` (INV-11/15/16),
and `feature.yaml`'s `github:` block (issue-mirror invariants) — are byte-for-byte the
pre-change raw-text regex. Confirmed by diffing the pre-change file's regex line numbers
against the current ones: `37a8a66:237→340e18a:268`, `293→324`, `297→328`, `302→333`,
`316→347`, `394→425`, `398→429`, `399→430` — every one shifted by a uniform **+31**
lines (the import + `_selfdir`/`PYTHONPATH` preamble added earlier in the file) with
**identical regex source text**. Not a reconstruction — measured directly with `git
show 37a8a66:... | grep -n` against the working tree.

**Reproduced live, not hypothesized:** a `state.yaml` with `status: "complete"` (quoted
— legal YAML, resolves identically to bare `complete` under any real parser) and no
`cost:` block should trip INV-11 ("an unmetered completed run is a hole"). It does not —
`complete = bool(re.search(r"^status:\s*complete", txt, re.M))` requires the bare word
immediately after the colon, so the quoted form makes `complete` false and the check is
silently skipped. Control case (bare `status: complete`, no cost) correctly violates;
the quoted case, fixture-identical otherwise, produces **zero** violations. This is
issue #11's exact defect class — a legal YAML variant silently voiding an invariant,
exit 0, no message — alive in the script whose Problem statement anchors the whole
feature, in a build that shipped after that defect class was supposedly closed.
A second, milder case: `parent: "40"` (quoted) in a `github:` block makes
`has_parent = re.search(r"^\s*parent:\s*\d+", blk, re.M)` fail to match (bare-digits
only), so INV-21 wrongly fires a false-positive "no numeric parent recorded" note
against a feature that has one — `gh-sync.py`'s own `load_recorded` docstring names
this exact regex shape as a defect it fixed in *that* file, one file over.

REQ-01 ("no hand-rolled YAML key/value regex is left behind") and SC-03 ("reaches
PyYAML on every one of its .yaml read paths") are false for `check-state.sh`. This is
invisible to every gate because T-07, alone among the four conversion tasks that carry a
regex-count discriminator (T-04 → 0 remaining, T-06 → 5 named markdown lines, T-12 → 7
at named lines, T-14 → 5 at named lines), has **no such assertion in its own `verify:`
line** — only unit-test pass, unchanged exit code, and a run-inventory diff, none of
which touch `phase:`/`state.yaml`/`github:`. SC-02 and SC-13 both pass *because* nothing
downstream of the unconverted fields is exercised by an invariant that would move on
this repo's real data — passing while the criterion (full conversion, and the
invariants it protects) fails. T-17's receipt-row count (`≥14 rows`) is a third green
signal with the same blind spot: the seven unconverted sites produce no
`harness_yaml`-parsed-value consumers, so they contribute zero rows and the count
passes precisely because the conversion didn't happen there.

**No decision defers this.** I checked PLAN.md's Decisions, the handoff, and every
receipt under `notes/` for a ruling that scopes `check-state.sh`'s conversion down to
just the `runs:`/`val()` loop. None exists. Commit `60b266c`'s own message states
"check-state.sh reads feature.yaml with a real parser (T-07/T-08)" without
qualification. PLAN T-07 enumerates all ten sites by line number and names exactly two
carve-outs (the 7 markdown/`CHECKPOINT_KEYS` survivors D-05 documents, and D-09's
deliberately-deferred `review_sha` fail-open) — neither covers `phase:`, `state.yaml`'s
block, or `github:`. This reads as unfinished work reported as complete, not a scoping
decision.

Two further gaps, both matching the requested defect class:

- **T-13/T-15's byte-level equivalence proof (11/11, 12/12 payload shapes, exit code +
  stderr bytes) exists only as a narrative log line in `.harness/logs/2026-08-03.md` and
  a commit message — never as a script or receipt under `notes/`.** Nothing a reviewer
  can re-run; the "verify" for these tasks (unchanged test file + a regex-count grep) is
  the durable evidence, and neither one is the byte-comparison PLAN.md text demands.
- **`bash-write-guard.sh`'s bootstrap escape (`require_or_bootstrap`, wired at line 78)
  has zero test coverage.** `test-bash-write-guard.py` never hides PyYAML for this hook —
  every case fires with the real interpreter. The exact regression this feature already
  shipped once (both hooks discarding `require_or_bootstrap`'s return value, commit
  `0775862`) is now regression-tested for `check-domain.sh` only.
- **T-07's SC-13 verify demands two durable listing artifacts ("both listings are then
  real artifacts the reviewer cites"); only the baseline (`receipt-baseline-run-inventory.md`)
  exists.** I regenerated the post-change listing myself via `harness_yaml.load_file` — it
  matches the baseline for all 5 features (FEAT-05 legitimately grew a 4th run since the
  baseline was taken) — so the underlying claim holds, but the artifact SC-13's own text
  requires was never produced.

## Lead-by-lead

**1. T-13/T-15 equivalence.** Not durable — confirmed above. `git log` on
`notes/**` for the T-13/T-15 commits (`78c86d2`, `6935bda`) shows no receipt written; the
11/11/12/12 payload-shape claim lives only in `.harness/logs/2026-08-03.md` (an operator
log, not feature evidence) and in commit message prose. `test-check-domain.py`
(11/11) and `test-bash-write-guard.py` (36/36) staying green is real evidence of
*functional* equivalence but not of the byte-identical-stderr claim PLAN.md T-13
demands. **Severity: med** — the underlying work plausibly happened (timings are
concrete and consistent across three independent log entries), but it is not
reviewable.

**2. T-02 test 5 fixture provenance.** **Refuted — the fixture is accurate.** I
extracted the pre-change `collect()` regex verbatim from `37a8a66`'s `check-domain.sh`
and ran it directly against the current `.harness/team-config.yaml` for
`harness-backend-dev`, `harness-dev-ops`, `harness-pm`; all three matched
`COLLECT_FIXTURE` in `test-harness-yaml.py:31-` exactly. Not a hand-transcription risk.

**3. SC-14 corpus gate.** **Adequate.** The negative fixtures in
`test-harness-yaml-corpus.py` call the *same* `scan()` function used against the real
repo (test 1: `scan(REPO)`), just pointed at a temp root containing `.harness/probe.yaml`
— not a separate code path. Commit `60b266c`'s message additionally records a genuine
RED→GREEN run against the real `team-config.yaml:18` defect before/after repair. SC-14's
"shown RED against a malformed fixture" is satisfied both by the standing negative cases
and by that one-time proof.

**4. Dead-identity-path generalization.** `test-harness-yaml.py`'s
`test_bootstrap_marker_lifecycle` (lines 238-254) exercises **only**
`payload={"session_id": ...}` — confirmed dead in production by
`receipt-main-session-q4-session-identity.md` (21 fires, `session_id` and
`transcript_path` absent every time; `CLAUDE_CODE_SESSION_ID` is the live entry). But
this gap is **closed at the integration level**: `test-check-domain.py:204-266` fires
the real hook binary as a subprocess with `CLAUDE_CODE_SESSION_ID` set (and
`CLAUDE_CODE_BRIDGE_SESSION_ID` explicitly popped), with an explanatory comment naming
exactly why the module-level test doesn't suffice. This is disclosed self-correction,
not a live gap, **for `check-domain.sh`**. It is *not* closed for `bash-write-guard.sh`
(see BLUF, third bullet) — same mechanism, same production-dead entry risk, no
subprocess-level test at all.

## Every synthetic-payload/env test, and whether the shape is observed in production

| Test | Input shape | Observed in production? |
|---|---|---|
| `test-harness-yaml.py::test_bootstrap_marker_lifecycle` | `payload={"session_id": ...}` | **No** — dead entry (receipt above) |
| `test-check-domain.py` SC-08/09/D-14a block | real hook subprocess, `CLAUDE_CODE_SESSION_ID` env var, `CLAUDE_CODE_BRIDGE_SESSION_ID` popped | **Yes** — matches the 21-fire probe exactly |
| `test-bash-write-guard.py` (all cases) | real hook subprocess, **no** PyYAML-hidden case, no session-id manipulation | N/A — bootstrap path never exercised, so the question doesn't arise; this is the coverage gap itself |
| `test-check-domain.py` main-path cases | real hook subprocess, `agent_type` in payload | **Yes** — the payload shape T-09/Q4 receipts confirm (`['agent_type', 'tool_input', 'tool_name']`) |

## Test-matrix floor (`logic` → `always: [unit]`)

11 of 17 tasks are `change_type: logic`. All 11 have named unit tests specified in
PLAN.md **except one is missing entirely**:

- **T-04 (`upgrade-config.py`) — MISSING.** The task requires creating
  `.claude/skills/harness/bin/test-upgrade-config.py` with three named tests and adding
  it to `run-unit-tests.sh`'s `SCRIPTS` array. **Neither exists.** `ls
  .claude/skills/harness/bin/test-*.py` and `run-unit-tests.sh`'s `SCRIPTS` array both
  confirm the file was never created, in any commit in the diff range. `upgrade-config.py`
  itself *was* converted (`harness_yaml.load_str` at `:99`/`:124`), so there is
  production code with **zero** regression coverage — the exact shape the matrix exists
  to prevent. `run-unit-tests.sh` exits 0 / 11 suites, not the 12 the plan implies.
  **State: missing (FAIL) for T-04's `logic` requirement.**
- **T-06, T-07, T-12, T-14, T-17** — all have their named tests present and running
  (confirmed by grep against the diff and a live `run-unit-tests.sh` pass). T-07's tests
  (case_e/case_f) cover only the part of the script that was actually converted (see
  BLUF) — adequate for what they assert, silent on the 7 unconverted call sites.
  T-02/T-03 (harness_yaml.py itself) — 9/9 tests present and green.

## Suite run — real numbers

`CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh`, run 3 times:

```
exit=0, exit=0, exit=0 (no flake across 3 runs)
11 suites, 11 PASS, 0 FAIL, 0 skip, 0 MISCONFIGURED lines
```

`SCRIPTS` array (11 entries) has no drift against the actual `test-*.py` file set — but
see T-04 above: the array is *consistent with itself*, it is just missing an entry the
plan mandated.

`check-state.sh` → exit 0, 0 violations, 40 notes (`feature.yaml` records
`baseline_exit: 0 / baseline_violations: 0` — matches; 1 extra INV-8 note is this run's
own bookkeeping, consistent with SC-02).

`check-docs.sh` → exit 0. `gen-decisions-index.py --check` → exit 0. Both green, per
DEC-174's premise these are not evidence of correctness beyond their own narrow scope —
confirmed true here, since neither would ever see the check-state.sh gap.

## SC-05/SC-06 paired-assertion check

Both satisfied **in one invocation context**, not split across setups:
- `test-check-domain.py` T-12 section's SC-05 pair: one `fixture()` manifest, one fire
  for `allowed/`, one for `forbidden/`, asserted together.
- `test-bash-write-guard.py::run_t14`: same shape, one `FIXTURE_MANIFEST`, `ok`/`no`
  fired against it, asserted as a single pair (`T14.append(("SC-06 pair: ...", ok.returncode
  == 0 and no.returncode == 2, ...))`).

Neither is discharged in two separate setups. Adequate.

## SC evidence map

| SC | State | Test |
|---|---|---|
| SC-01 | met | `test-check-state.py::case_e` (invariant-level, RED/GREEN per commit `60b266c` message) |
| SC-02 | met | live `check-state.sh` run above, matches `feature.yaml` baseline |
| SC-03 | **NOT met for check-state.sh** | census answer key is stale against actual code — see BLUF |
| SC-04 | met for the 5 converted scripts; moot/unverifiable for check-state.sh's unconverted fields | `test_exactly_one_guarded_import_in_the_tree` |
| SC-05 | met | `test-check-domain.py` paired assertion |
| SC-06 | met | `test-bash-write-guard.py::run_t14` paired assertion |
| SC-07 | met | grep counts verified live (0 "six", 1 "seven prerequisites", 3 "No such file") |
| SC-08 | met at unit level, per D-14a/b fix | `test-check-domain.py` `systemMessage` assertion (post-fix) |
| SC-09 | met | `uat-bootstrap-escape-expiry.md`, U-05, genuine session boundary, user-run |
| SC-10 | met for converted consumers | `receipt-harness-backend-dev-typed-value-sweep.md` + sweep script |
| SC-11 | met (refutation) | `test-gh-sync.py` audited, no mislabeled invocation found |
| SC-12 | met | live run above: 11 suites (not the stale "9" baseline text), 0 FAIL, 0 skip |
| SC-13 | **substance holds, artifact missing** | I regenerated the post-change listing (matches baseline); PLAN's required second file does not exist |
| SC-14 | met | `test-harness-yaml-corpus.py`, negative fixtures confirmed non-decorative |

## Coverage gaps (Phase 1 expectations with no test)

- Phase 1 (BRIEF/PLAN only) expected: every named script's YAML reads fully routed
  through the shared parser, with a discriminating absence-check per script. **Missing
  for `check-state.sh`'s `phase:`/`state.yaml` block/`github:` block.**
- Expected: regression coverage for `upgrade-config.py`. **Entirely missing** (T-04).
- Expected: symmetric bootstrap-escape coverage for both hooks named in REQ-04/REQ-05.
  **Missing for `bash-write-guard.sh`.**
- Expected: a reproducible byte-equivalence artifact for T-13/T-15. **Missing**, only
  narrative.

## Findings, with severity

1. **[critical]** `check-state.sh:268,324,328,347,425,429,430` — `phase:`,
   `state.yaml` `status:`/`cost:`/`host:`, and `feature.yaml`'s `github:` block are
   unconverted raw-text regex (measured old→new line mapping above, +31 uniform
   offset, identical source), contradicting T-07's explicit instruction to convert
   census items `237 293 297 316 394 398 399`. REQ-01 and SC-03 are false for this
   script. **Reproduced as a live fail-open**: `status: "complete"` (quoted) with no
   `cost:` block silently passes INV-11 where the bare form correctly violates —
   issue #11's own defect class, alive in the script that closed issue #11. A second
   reproduction: `parent: "40"` (quoted) false-positives INV-21. State that would
   satisfy every current verify command while this is true: exactly the state
   observed — `run-unit-tests.sh` exit 0, `check-state.sh` exit 0/0 violations on
   this repo's real (unquoted) data, run-inventory diff clean — because none of
   those signals depend on the unconverted fields or exercise a quoted value.
2. **[high]** T-04's `test-upgrade-config.py` and its `SCRIPTS` registration were never
   created. `upgrade-config.py`'s conversion ships with zero regression tests.
3. **[med]** `bash-write-guard.sh`'s bootstrap-escape path (`require_or_bootstrap`) has
   no test coverage — the exact class of bug (`0775862`) that already shipped once for
   both hooks is now caught only for `check-domain.sh`.
4. **[med]** T-13/T-15's byte-level equivalence proof is not a durable, reviewable
   artifact — narrative-log-only.
5. **[low]** SC-13's "both listings" requirement is unmet as a paperwork matter; the
   underlying claim is true (verified independently by re-running the comparison).

## Test-first audit

Where git history is checkable (T-02 RED before T-03 GREEN, T-07's case_e/f described as
RED-before-fix in the commit message), test-first was followed for the parts that were
actually built. It cannot vouch for the unconverted parts of T-07 because no test was
ever written against them in either order — they were simply not touched.

---

VERDICT: FAIL

DIGEST:
  headline: T-07's check-state.sh conversion is 70% incomplete and I reproduced a live fail-open from it (quoted `status: "complete"` silently skips INV-11) — issue #11's own defect class, alive in the script that closed issue #11; plus a missing T-04 test file and an untested bash-write-guard.sh bootstrap escape.
  suite: pass
  failures: 0
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh", named_tests: 11 }
    - { kind: unit, state: missing, cmd: "test-upgrade-config.py (never created, T-04)", named_tests: 0 }
  coverage_gaps:
    - "check-state.sh: phase:/state.yaml status:-cost:-host:/feature.yaml github: block still raw regex, never routed through harness_yaml"
    - "upgrade-config.py: no test file exists despite T-04 mandating one"
    - "bash-write-guard.sh: bootstrap-escape (require_or_bootstrap) path never exercised by any test"
    - "T-13/T-15: byte-level equivalence proof exists only as log/commit-message narrative, not a durable artifact"
  sc_evidence:
    - { id: SC-01, test: ".claude/skills/harness/bin/test-check-state.py:145 (case_e)" }
    - { id: SC-02, test: "live run: CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh" }
    - { id: SC-03, test: "NOT MET for check-state.sh — see finding 1" }
    - { id: SC-04, test: ".claude/skills/harness/bin/test-harness-yaml.py:test_exactly_one_guarded_import_in_the_tree" }
    - { id: SC-05, test: ".claude/skills/harness/bin/test-check-domain.py (SC-05 paired assertion, T-12 section)" }
    - { id: SC-06, test: ".claude/skills/harness/bin/test-bash-write-guard.py:143 (run_t14)" }
    - { id: SC-07, test: "live greps against .claude/skills/harness-init/SKILL.md" }
    - { id: SC-08, test: ".claude/skills/harness/bin/test-check-domain.py:262 (systemMessage assertion, post D-14b)" }
    - { id: SC-09, test: ".harness/features/FEAT-05-pyyaml-file-parsers/notes/uat-bootstrap-escape-expiry.md (U-05)" }
    - { id: SC-10, test: ".harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-typed-value-sweep.md" }
    - { id: SC-11, test: ".claude/skills/harness/bin/test-gh-sync.py (label audit)" }
    - { id: SC-12, test: "live run: run-unit-tests.sh, 11/11 PASS, exit 0" }
    - { id: SC-13, test: "substance verified independently; PLAN's required second artifact absent" }
    - { id: SC-14, test: ".claude/skills/harness/bin/test-harness-yaml-corpus.py" }
  open_questions:
    - { id: Q1, question: "Dispatch named notes/review-harness-qa-c0.md; harness-qa's write grant only permits notes/qa-*.md. Written to notes/qa-c0.md instead. Fourth recurrence of the routing-wall class PLAN.md already logs three of (FEAT-03 Q13, FEAT-04 T-09, this feature's T-10/T-11) — this time on the dispatcher side. Route to the harness owner for the naming-convention fix, not to a builder.", blocking: false }
  files_touched: [".harness/features/FEAT-05-pyyaml-file-parsers/notes/qa-c0.md"]
  expertise_update: []

artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog/.harness/features/FEAT-05-pyyaml-file-parsers/notes/qa-c0.md
