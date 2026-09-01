# QA gate — BUG-1080 cycle 1 (panel-c1)

**Verdict driver: BLOCKED-worthy finding found, but scoped as advisory** — see Q-C below. All
four named commands are measured clean; the schema cases are non-vacuous for two of three, and
one pair is empirically vacuous as written. The producer test is a whole-file substring match
that does not bind to the instruction; a real (if narrow) evasion mutant leaves it green.

## 1–4. Exact run results

1. **`test-check-state.py`**: exit 0. **164 ok / 0 FAIL** (author's claim confirmed exactly).
   **13 INV-6 cases executed**: 9 new `case_inv6_*` (all invoked from `ok_i6_plan`, all defined
   functions are called — no orphan) + 4 pre-existing INV-6-relevant cases (e, h, i, j).
   `INV-6's exemption has a documented producer` — **ok**.
2. **`test-validate-feature-json.py`**: **65/65 PASS**, `ALL PASS`. The three new cases
   (`accepted_runs_item_code_grade_n_a`, `rejected_runs_item_code_grade_other_value`,
   `rejected_runs_item_code_grade_case_variant`, lines 23–25 of output) run and pass, and are
   present in `main()`'s call list (lines 714–716) — not defined-but-uncalled.
3. **`check-state.sh`** over the real tree: exit 0, **0 `VIOLATION` lines**. Not an empty sweep:
   43 distinct `FEAT-*`/`BUG-*` IDs appear in its output (`note`/`INV-32` lines name them), and
   BUG-1080's own feature is among the referenced set (15 mentions). A substantial, non-trivial
   corpus, clean.
4. **`run-unit-tests.sh`**: exit 0, **zero literal `FAIL` result lines** (checked with an anchored
   regex, not a bare substring — the raw log has 31 lines containing the substring "FAIL" but
   every one is inside a descriptive test name like "a FAILING invocation" or "ship FAILED", never
   a standalone result token). 1064 `PASS` script-summary lines.
   ⚠️ **My first run of this command genuinely failed** (`test-check-state.py` and
   `test-hooks-install.py` both reported `FAIL`) because it executed concurrently with my own
   Q-B mutant of `SKILL.md`, which was sitting in place on disk mid-suite-run. That was
   self-inflicted contamination, not a real defect — confirmed by rerunning clean (`git status`
   verified clean first) with an identical exit 0 / zero-FAIL result. Flagging it here so the
   discrepancy in run counts across my two attempts is not mistaken for flakiness.

## Q-A — Is the HIGH genuinely closed?

**Yes, as a documentation fix it is real, not merely asserted — with one caveat.** SKILL.md step 6
now names the key and states the cost of omission at the exact point a run-writer would consult
it (line 65, inside "Adjust and record"). There is no tool-level producer (no code stamps the
key automatically), but none is required: the only writer of `runs:` entries is the agent
following SKILL.md's prose, same as every other `runs:` field (`id`, `squad`, `verdict`, `agent`)
— none of those are code-stamped either. Holding `code_grade` to a higher bar than its siblings
would be scope creep past what the finding asked for. The exemption is REAL in the sense that a
compliant writer following the doc produces a schema-valid, gate-exempt document (verified
directly, `test-validate-feature-json.py`'s `accepted_runs_item_code_grade_n_a` and
`check-state.sh`'s live behavior on CASE-01 in Q-C below both confirm the value round-trips
clean). It remains a *behavioral* fix, contingent on the writer reading and following the doc —
inherent to a documentation-only remedy, and correctly scoped for a HIGH about discoverability.

## Q-B — Does `case_inv6_producer_is_documented` discriminate?

**Weakly. It catches deletion, not evasion.** The assertion is a bare substring test,
`"code_grade: n_a" in <entire SKILL.md text>` (line 3450). I built two mutants directly against
the shipped `SKILL.md` (restored via `git checkout --`, confirmed byte-identical after, worktree
`git status --porcelain` clean throughout):

- **Mutant 1 (deletion)**: replaced the literal string with `code_grade: not_applicable`
  everywhere. Case went **RED** as claimed. The test does catch the literal string vanishing.
- **Mutant 2 (adversarial — the one the dispatch asked for)**: removed the *instructional*
  sentence entirely from step 6 (replaced with an unrelated line, "Update the runs list to
  reflect what happened."), then appended an inert HTML comment near the end of the file:
  `<!-- historical example, not an instruction: an old run once carried code_grade: n_a -->`.
  Case stayed **GREEN**.

So the assertion binds to "the literal string appears somewhere in the file," not to "an
instruction exists that tells a writer to stamp the key." A rewrite that moved, watered down, or
orphaned the instruction — while leaving any trace of the string anywhere, including a comment,
a changelog entry, or a different section entirely — would pass this test while regressing the
actual finding. This is a real gap, but a narrow one: it requires a *specific* kind of future
regression (string survives, instruction doesn't) to go undetected, and the current text is fine.
Not blocking on its own; worth a follow-up to anchor the assertion to step 6's paragraph instead
of the whole document.

## Q-C — Can a document be schema-invalid AND gate-exempt (or the reverse) now?

Built 10 real `feature.json` files on disk (not YAML-in-fixture) under a scratch harness tree,
ran both `validate-feature-json.py <file>` and `check-state.sh` (pointed at the scratch tree via
`HARNESS_PROJECT_DIR` + a copied `team-config.yaml` marker) against each:

| # | `code_grade` value | schema (`validate-feature-json.py`) | gate (`check-state.sh` INV-6) | cell |
|---|---|---|---|---|
| 1 | `"n_a"` | **valid** (exit 0) | **exempt** (silent) | safe — the intended cell |
| 2 | `"N_A"` | invalid (`'N_A' is not one of ['n_a']`) | **liable** (fires) | safe |
| 3 | `" n_a "` (quoted, padded) | invalid | liable (fires) | safe |
| 4 | `"n_a "` (trailing space) | invalid | liable (fires) | safe |
| 5 | `"graded"` | invalid | liable (fires) | safe |
| 6 | `null` | invalid (`None is not of type 'string'`) | liable (fires) | safe |
| 7 | `true` | invalid | liable (fires) | safe |
| 8 | `0` | invalid | liable (fires) | safe |
| 9 | key absent | **valid** (key is optional, not required) | liable (fires) | correct by design — absence means code review (FEAT-31-style default), not a mismatch |
| 10 | `n_a` **unquoted, trailing spaces, file is valid YAML but not valid JSON** | **invalid** (`not valid JSON: Expecting value: line 1 column 1`) | **exempt** (silent — no INV-6 violation for this feature anywhere in output) | **⚠️ DANGEROUS — schema-invalid AND gate-exempt** |

**Case 10 is the real finding.** `check-state.sh` parses every `feature.json` through
`harness_yaml` (a tolerant YAML superset parser, per its own module docstring), which reads bare
`n_a` with trailing whitespace as the Python string `"n_a"` — already stripped by ordinary YAML
scalar parsing, before check-state.sh's own (deliberately non-stripping) exact-match runs.
`validate-feature-json.py`'s CLI enforces strict JSON for a `.json`-suffixed path and rejects the
same bytes outright at the parse stage. The two layers disagree in the dangerous direction: a
malformed `feature.json` that would fail schema validation can still be silently read as exempt by
the read-time gate. This directly contradicts the remedy's own comment at
`check-state.sh:444-447` ("A document must never be schema-invalid and gate-exempt at the same
time: any deviation fails BOTH") — that claim holds only for well-formed-JSON documents; it does
not hold for the parser-divergence axis.

**Scoped, not escalated to blocking**: this is not something the `.strip()`/`.lower()` removal
introduced — it is a pre-existing property of `check-state.sh` using a YAML-tolerant reader for a
JSON-named file, present before BUG-1080 and orthogonal to this diff. It is also **largely
guarded in the normal path**: `check-domain.sh`'s write hook (`check-domain.sh:1133-1150`) calls
the *same* `feature_schema.problems_for_text` on every write to `feature.json` and denies a write
that fails it — so a compliant agent writing through the normal tool path cannot land case-10's
content on disk in the first place. The gap is real only for content that reaches disk
out-of-band: a pre-existing malformed file, a git merge, a manual edit, or (per that same file's
own commented incident history) a hook that fails open. Recommend a backlog item to make
`check-state.sh`'s `code_grade` read strict-JSON-parse-equivalent, or to have it flag
non-strict-JSON `feature.json` files directly, rather than treating this as a BUG-1080 blocker.

## Q-D — Are the three new schema cases non-vacuous?

Ran each against two mutant copies of `feature-schema.json`'s `code_grade` enum (never touched
in place; module `SCHEMA_PATH` monkey-patched to a scratch file per mutant, `_schema_cache`
cleared before each probe) — widened to `["n_a", "graded", "N_A"]`, then the `enum` key removed
entirely (permits any string):

- **`accepted_runs_item_code_grade_n_a` — non-vacuous.** Stays accepted under both widening
  mutants (expected — widening a permitted-value set cannot un-accept an already-permitted
  value). Reddened when independently *narrowed* to `["graded"]` (excludes `n_a`):
  `'n_a' is not one of ['graded']`. The case does discriminate on the enum containing `n_a`.
- **`rejected_runs_item_code_grade_other_value` — VACUOUS.** Under both the widened and the
  no-enum mutant, the fixture (`code_grade: "graded"`, no `agent` key) still returns
  `problems != []`, so the case's `check(..., problems != [], ...)` still reports "ok" — but the
  problems list under both mutants no longer contains any `code_grade`-related message. The lone
  remaining entry is the unrelated FEAT-31 positional-`agent` rule
  (`runs[0] is missing a non-empty 'agent'`), which fires unconditionally because this fixture
  (unlike the `accepted_n_a` fixture, which does include `"agent"`) never supplies one. The case
  is satisfied by an incidental confound, not by the enum it claims to test — a schema rewrite
  that dropped the `code_grade` enum constraint entirely would not redden this case.
- **`rejected_runs_item_code_grade_case_variant` — VACUOUS, same mechanism and same fixture
  shape** (`code_grade: "N_A"`, no `agent`). Identical confound: the agent-missing problem alone
  keeps `problems != []` true under both mutants.

**Fix is small and precise**: give these two fixtures an `agent` key (matching `accepted_n_a`'s
fixture), or assert on the specific `code_grade`-mentioning message rather than "any problem at
all." As written, two of the three new schema cases would not catch a broken or deleted
`code_grade` enum.

## Q-E — Anything the remedy broke that cycle 0 had passed?

None found. Full `run-unit-tests.sh` clean rerun (§4) covers this — no regressions across the
1064-script sweep, and the diff (`git diff --stat a2fb6c0b..e9b11035`, 4 files, +100/-3) touches
only additive test cases, the SKILL.md paragraph, and the exact-match tightening already ruled
correct in cycle 0. `check-state.sh`'s clean 43-feature sweep (§3) is itself a regression check
across the whole corpus, not just BUG-1080's own feature.

## Matrix-gate verdict

`gates.review` is `advisory_unless_high`. Neither open finding here is a HIGH: Q-B is a narrow
test-discrimination gap on an already-correct doc; Q-C's dangerous cell is pre-existing,
orthogonal to this diff, and guarded at write time; Q-D's vacuity is a two-line test fixture fix,
not a regression risk (the enum itself is independently exercised and correct — the `graded`/`N_A`
*values* ARE rejected today, as the Q-C live matrix directly confirms; only the *unit test's*
assertion is loose). None of the three blocks HIGH-severity re-open of the original finding.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Remedy holds — 164/0 + 65/0 + clean 43-feature sweep + clean full suite, all measured; two non-blocking gaps found (weak producer-test binding, two vacuous schema-rejection cases) plus one pre-existing, write-time-guarded parser-divergence risk (schema-invalid-but-gate-exempt on non-strict-JSON feature.json)"
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/test-check-state.py", named_tests: 164 }
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/test-validate-feature-json.py", named_tests: 65 }
    - { kind: integration, state: satisfied, cmd: "bash .claude/skills/harness/bin/check-state.sh", named_tests: 1 }
    - { kind: integration, state: satisfied, cmd: "bash .claude/skills/harness/bin/run-unit-tests.sh", named_tests: 1064 }
  coverage_gaps:
    - "case_inv6_producer_is_documented binds to string-presence anywhere in SKILL.md, not to the step-6 instruction specifically (Q-B, demonstrated with a real adversarial mutant)"
    - "rejected_runs_item_code_grade_other_value and rejected_runs_item_code_grade_case_variant are vacuous re: the code_grade enum specifically — pass under both a widened and a removed enum because an incidental agent-missing confound in the fixture keeps problems != [] true regardless (Q-D)"
  sc_evidence:
    - { id: "cycle-0 HIGH (code_grade producer)", test: ".claude/skills/harness/bin/test-check-state.py:3432 case_inv6_producer_is_documented; SKILL.md:65" }
    - { id: "cycle-0 Q2 (exact-match value test)", test: ".claude/skills/harness/bin/check-state.sh:444-448; test-check-state.py:3408 case_inv6_case_variant_is_not_exempt" }
    - { id: "cycle-0 Q3 (message names the remedy)", test: ".claude/skills/harness/bin/test-check-state.py:3420 case_inv6_message_names_the_remedy" }
  open_questions:
    - { id: Q1, question: "Anchor case_inv6_producer_is_documented to the step-6 paragraph (or its containing list item) rather than the whole SKILL.md text, so an instruction that moves or is deleted-but-string-survives-elsewhere reddens it.", blocking: false }
    - { id: Q2, question: "Add an 'agent' key to the other_value and case_variant fixtures in test-validate-feature-json.py (or assert on the specific code_grade message) so a broken/removed enum constraint reddens them — currently both stay green under a widened OR fully-removed enum.", blocking: false }
    - { id: Q3, question: "Backlog: check-state.sh reads feature.json through a YAML-tolerant parser and can therefore silently INV-6-exempt a document that validate-feature-json.py would reject as not-valid-JSON (demonstrated, case 10 in Q-C's matrix). Write-time guarded by check-domain.sh today; not reachable through normal agent writes, only through out-of-band disk changes (merge, manual edit, hook bypass).", blocking: false }
  files_touched: []
  expertise_update: []
artifact: ".harness/harness/features/BUG-1080-inv6-plan-phase-runs/notes/qa-bug1080-c1.md"
```
