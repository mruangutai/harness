# QA — matrix conformance, SC-12 receipt, frozen-constants question — FEAT-04 @ 363b539

## BLUF

PASS. Matrix conformance holds (floor met, nothing dropped below it). SC-12 confirmed by the
correct check (a runner-emitted `MISCONFIGURED` line, not a substring match) — 0 hits, exit 0,
`PASS test-gen-decisions-index.py` present. The frozen 171-raw/170-distinct constants in
`test_row_per_distinct_dec_matches_authority` are PLAN-mandated documentation of a measured
divergence, not an implementer shortcut, and they currently agree with the authority's live count —
gate is green, not red. Residual brittleness (next appended DEC reddens the literal-comparison
half only) is real, already fired once this feature (DEC-170), and is backlog, not a FEAT-04 fix.

## Phase 1 — expected coverage, derived before reading code

From BRIEF/PLAN alone: only T-01/T-02 are `change_type: logic` (matrix `always: [unit]`); T-03–T-10
are `docs`/main-session (`always: []`). Six named unit tests were PLAN-mandated (T-01) covering
SC-01, SC-02, SC-03, SC-04 (+orphan MF-5), SC-06, SC-11. SC-05/07/08/09/10/12 rest on `inspection`
receipts — BRIEF's own "Verification gaps — DEC-163" section already discloses this (only
`test_kinds.unit` has a `cmd`) and audits correctly against `.harness/harness.json`, verified
directly (only `unit.cmd` is non-null; five other kinds `cmd: null`).

**Phase 1 gap, already disclosed, not newly found:** no `eval` runner exists, so the feature's
actual behavioral claim — an agent given the index greps it instead of reading the authority
whole — is unproven by anything shipped. BRIEF says so itself (DEC-163 section) and defers it to
a post-ship cache-read measure. Recorded as a coverage gap per protocol; not this run's finding.

## 1. Matrix conformance (walked T-01..T-10 against `harness.json` `test_matrix`)

| Task | change_type | Required (floor) | State |
|---|---|---|---|
| T-01 | logic | unit | satisfied — 6 named tests, all `ok`, direct run and via runner |
| T-02 | logic | unit | satisfied — same suite exercises the generator directly |
| T-03..T-08 | docs | none | N/A by matrix; inspection receipts per BRIEF (SC-05/07/08) |
| T-09, T-10 | docs (main-session) | none | N/A by matrix; inspection receipts (SC-09/10) |

No task demanded a kind never produced. `matrix_ok: true`.

Diff also carries unrelated fixes (`bash-write-guard.sh`, `check-domain.sh`, both with their own
`test-bash-write-guard.py`/`test-check-domain.py`, both `PASS` in the runner output) — not FEAT-04
scope per PLAN's task table, already covered, not a gap.

## 2. SC-12 receipt — the check that was actually run

Ran `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` directly, captured
combined stdout+stderr. **Check performed:** `grep -n 'MISCONFIGURED' <captured output>` → 0
matches (not a grep for `SKIP` or a loose look at `test-gh-sync.py`'s own printed case names like
`ok    gh missing -> SKIP, exit 0`, which are that file's test labels, not runner-emitted lines).
Confirmed the runner's actual emission site: `run-unit-tests.sh:19` —
`"MISCONFIGURED: $f is not in run-unit-tests.sh's explicit script list"` — a distinct string that
did not appear anywhere in the captured output. Exit code: 0. `PASS test-gen-decisions-index.py`
present at output line 137. **SC-12 satisfied**, on the correct discriminator.

Also ran `test-gen-decisions-index.py` directly (not just via the runner): exit 0, all six `ok`.

## 3. The frozen-constants question

**Which pair does the test assert, and does it agree with the authority at 363b539?**
`test-gen-decisions-index.py:115,119` hardcodes `raw != 171` / `distinct != 170` → FAIL. Measured
directly against the committed `docs/harness/DECISIONS.md` at 363b539 (same fence-toggle the
generator uses): **raw = 171, distinct = 170** — they agree. The gate is green, not red. This
is consistent with DEC-170 having landed since the `f723194` baseline (170 raw / 169 distinct per
`feature.yaml:112`); the pair in circulation that's live now is 171/170, matching both the test and
the authority, not the 169/170 BRIEF SC-01 cites (that citation is baseline-dated, historical, not
a live requirement — SC-01's *operative* requirement is the runtime comparison, see below).

**Is this consistent with SC-01's run-time-counting requirement?** Yes. SC-01's operative clause —
row count equals live-heading count, "counted at run time rather than against a frozen number" — is
satisfied by a *separate* assertion in the same test: `len(rows) != len(distinct)` at
`test-gen-decisions-index.py:139-141`, where `distinct` is computed at runtime via
`fence_guarded_dec_headings()` (`:34-49`), never hardcoded. The two literal constants (171, 170) are
an *additional* assertion, explicitly mandated by `PLAN.md:134-136`: "Assert both numbers explicitly
— expected 169, and 170 for the raw count — so the divergence is documented by the test rather than
rediscovered." (PLAN's own literals are stale relative to DEC-170 having landed since — the test was
correctly updated, per `observations/harness-backend-dev.md`'s note on the re-pin, PLAN's task text
was not, but PLAN prose isn't a live contract here — the approved instruction, "assert both numbers
explicitly," is what's binding, and the test does.) So the frozen constants are plan-mandated, not
an implementer shortcut, and they coexist with — never substitute for — the runtime floor.

**FEAT-04 fix or backlog?** Backlog. It's explicitly instructed by the signed PLAN, not a shortcut
taken against it. Changing the mechanism (e.g., dropping the frozen pair, or auto-deriving it) would
be a PLAN deviation needing its own decision/approval, out of this run's scope. The residual —
appending DEC-171 reddens the two literal-comparison lines even though the generator's actual
correctness (rows == runtime-computed distinct count) is untouched — is real and already
materialized once this feature: `observations/harness-backend-dev.md` records a "T-11" follow-up
that re-pinned both literals (170→171, 169→170) after DEC-170 landed, alongside adding the 30-word
cap logic. That confirms the coupling is a recurring, manual step, not a one-time cost.

## Findings already on record (per dispatch) — not re-litigated here

DEC-102 index row supersession clause gap; `bash-write-guard.sh` heredoc/compound-line misparse;
orchestrator playbook cost-append vs. placeholder duplicate-key; `.harness/**/*.md` as an
undocumented `check-docs.sh` scan surface; a code/receipt-only member having no per-feature
writable artifact beyond observations.

## SC evidence for pm's goal-check

| SC | Method | Anchor |
|---|---|---|
| SC-01 | unit | `test-gen-decisions-index.py:104-147` (runtime compare `:139-141`; frozen-pair check `:115,119` — see §3) |
| SC-02 | unit | `test-gen-decisions-index.py:338-404` — absence `:356`, presence floor `:370-398` |
| SC-03 | unit | `test-gen-decisions-index.py:350-352` (header token) |
| SC-04 | unit | `:150-213` (preserve-by-DEC), `:216-286` (ok-stale), `:407-451` (orphan, MF-5) |
| SC-05 | inspection | run directly: `gen-decisions-index.py && git diff --exit-code docs/harness/DECISIONS-INDEX.md` → exit 0, `git status --porcelain` clean on that path |
| SC-06 | unit | `test-gen-decisions-index.py:289-335` |
| SC-07 | inspection | run directly: `check-docs.sh` → exit 0, "checked 45 superseded pattern(s) across 101 file(s)" |
| SC-08 | audit-only | `.harness/features/FEAT-04-decisions-index/observations/harness-documentor.md:118-138` — not QA's to run (no reviewer can plant; code reviewer's receipt) |
| SC-09 | inspection | run directly: presence `CLAUDE.md:36,43` (2 hits); both widened absence greps → 0 hits |
| SC-10 | inspection | run directly: 4 trigger markers; `floor` hit at `.claude/skills/harness-handoff/SKILL.md:64` |
| SC-11 | unit | same test as SC-02, `:381-397` (30-word cap over the ` :: ` segment) |
| SC-12 | inspection | run directly: exit 0, `PASS test-gen-decisions-index.py` present, 0 `MISCONFIGURED` lines (see §2 for the exact check) |

## Open question

Q1 (non-blocking): appending a new top-level `## DEC-NN` to `DECISIONS.md` requires manually
bumping the two frozen literals in `test-gen-decisions-index.py` (currently 171/170) or the unit
gate reddens for a reason unrelated to generator correctness. This already happened once this
feature (DEC-170). PLAN's "REQ-09 has mechanical teeth" section documents the ruling-writing
obligation on future features but not this literal-bump obligation — worth adding there so a future
feature doesn't rediscover it as a mystery red gate.
