# QA Gate — DELTA c4 (cycle 4/4) — BUG-1308-expertise-replace-drop

Graded via `git show b70d57b464743034231fed3d18227a17faae2ed4:<path>` for every source/test file below.
No test authored or edited this cycle. Full command transcripts in `/tmp/unit_out.txt`, `/tmp/int_out.txt`.

## VERDICT: PASS — the VL-06 fix is load-bearing and every signed SC binds a running, asserting test.

## Suites (worktree root, `env -u HARNESS_AGENT_TYPE`)

| kind | exit | `^FAIL ` | discovered files |
|---|---|---|---|
| unit | 0 | 0 | 28 |
| integration | 0 | 0 | 46 |

`test-expertise-ops.py` (unit, exit 0) and `test-expertise-merge.py` (integration, exit 0, 8.06s)
both present in the discovered set and both printed `PASS <file>` — not a load/import/collection
error masquerading as green.

## Matrix gate (`origin/main..b70d57b4` for spec compliance; `plan.yaml` for change_type)

T-01 (core mechanism, `expertise-merge.py`, tests) = `change_type: bugfix`. Per `harness.json`
`test_matrix.bugfix`: `always: []`, `unit` required (`touches_runtime_code` fires — real runtime
code changed, not test/doc only), `integration` not strictly obligated by
`fix_confined_to_tests_and_contract_docs` (false here — the fix touches runtime code, so that
clause doesn't fire) or by `__bug_class__` (unresolvable placeholder, repo-known, never fires —
G-08). T-02 = `scaffolding`, two doc tasks = `docs`; both `always: []`. **Floor: unit only.**
qa adds `integration` regardless — a merge tool with file I/O, locking and a CLI surface
obviously warrants it, and 971 lines were added to `test-expertise-merge.py` exercising exactly
that surface. Both kinds ran, both green. `matrix_ok: true`.

## VL-06 mutation proof (disposable worktree `.claude/worktrees/qa-mutant-c4`, never the target worktree)

Copied `expertise-merge.py` at the pin, neutered `_validate_target_grammar` to a no-op, ran
`tests/unit/test-expertise-ops.py` against the mutant via `EXPERTISE_MERGE_BIN=<mutant path>`:

- `u21: add too-long id` — **RED** (mutant) / PASS (real)
- `u21: add embeds valid id` — **RED** (mutant) / PASS (real)
- `u21: replace too-long id` — **RED** (mutant) / PASS (real)
- `u21: drop too-long id` — **RED** (mutant) / PASS (real)
- `u22: well-formed add succeeds` (positive control) — **stayed GREEN under the mutant** — the
  case set is not vacuous; it fails only when the grammar guard is actually removed, and only
  for inputs the guard is meant to catch.

Confirms `_validate_target_grammar` is checked for `add`, `replace` AND `drop` at the resolver
(u21 loops all three verbs through the same Step-A gate). The CLI-level integration case
(`case_ops_target_grammar`, case25/26) exercises only `add` through the subprocess boundary — the
resolver-level unit coverage for `replace`/`drop` is the only proof for those two verbs; adequacy
note below.

## SC-01..SC-12

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | MET | integration | `case11: replace at capacity exits 0` / `stdout carries REPLACED P-07` / `Patterns still holds 15 entries` / `7th entry line is P-07` with new text — all PASS |
| SC-02 | MET | integration | `case12: drop exits 0` / `DROPPED G-03` / `- G-03: is absent` / G-01,02,04,05 still present — all PASS |
| SC-03 | MET | integration | `case13: missing target exits 10` / `MISSING TARGET` / id `P-99` / section `Patterns` / sha256 unchanged — all PASS |
| SC-04 | MET | unit (u13) + integration (case14 b/c, case20 a/b) | `case14: (b) duplicate id exits 11 / AMBIGUOUS TARGET`; `(c) two ops same target exits 11`; `case20: (a)/(b) missing/empty section exits 12 / MALFORMED OPS / index=0`, byte-identical, and a following `apply` still exits 0 — all PASS |
| SC-05 | MET | integration | `case15: atomic failure exits non-zero` / sha256 equal to pre-invocation / following apply still exits 0 — PASS |
| SC-06 | MET | integration | `case16: add-only exits 0 / ADDED,PRESERVED,APPLIED tokens / same-id-different-text still exit 7 / over-cap still exit 8` — PASS |
| SC-07 | MET | unit | `u10: compute_union returns non-empty conflicts` + `merged Patterns still carries OLD text at index 6` — PASS, run directly (not inferred) |
| SC-08 | MET | integration | `case11`/`case12`: `check-expertise.sh still accepts the written file` — both PASS |
| SC-09 | MET | integration | `case17`: real SKILL.md returns no failures; three drifted copies each redden the SPECIFIC direction the SC names and stay green on the other — all 9 sub-checks PASS |
| SC-10 | MET | integration + direct read | `DECISIONS-INDEX.md:219` carries the exact literal `replace and drop through the ops subcommand`; `test-gen-decisions-index.py` exit 0 |
| SC-11 | MET | integration | `case18`: `neither child exits during the 2.0s hold window … (2.01s observed)` — production lock (`harness_merge.acquire`) taken by the test itself, no bypass; both children exit 0 after release; census exact; P-07 carries replacement text — all PASS |
| SC-12 | MET | unit (u11 + reversal, u12) + integration (case19) | `case19`: exits 0, `DROPPED P-01`/`REPLACED P-05`, id sequence exactly `P-02..P-05`, marker only on P-05, `check-expertise.sh` still accepts — all PASS; u11/u12 present and green in unit run |

All 12 criteria are MET by a named, executed case whose assertion matches its text — none inferred.

## Adequacy — what the suite does NOT bind

1. **CLI-level (subprocess) coverage of the VL-06 grammar gate is `add`-only** (case25/26). `replace`
   and `drop` are proven at the resolver (unit `u21`, mutation-confirmed above) but never through
   the actual CLI/JSON-file boundary. Same code path (Step A precedes verb dispatch), so risk is
   low, but it is a **coverage gap**, not exercised end-to-end for two of the three verbs. Backlog
   (`chore`, low): add a CLI-level `replace`/`drop` grammar case mirroring case25/26.
2. **No case exercises a unicode-digit id.** `ENTRY_RE`'s `\d` is not `re.ASCII`-scoped, so e.g.
   `P-١` (U+0661) round-trips through `_validate_target_grammar` and is *accepted*, verified live:
   `ENTRY_RE.match("- P-١: x").group(1) == "P-١"`. This is *consistent* with `parse_expertise`
   using the same regex to read entries back — not a falsified requirement — but no test pins
   whether that's the intended acceptance boundary. Backlog (`enhancement`, low): decide and pin
   whether non-ASCII digit ids should be accepted or explicitly rejected.
3. **No case exercises the same id string used as `target` in two distinct sections** (e.g. `P-01`
   in both `Patterns` and `Gotchas`). Verified live by direct call: `resolve_ops` scopes
   `_base_matches` by `(section, target)`, so a `replace` targeting `Gotchas`/`P-01` correctly
   leaves `Patterns`/`P-01` untouched — no cross-section bleed, no data loss. Untested but not
   defective. Backlog (`chore`, low): add a regression case pinning this scoping explicitly.

None of the three rises to `must_fix` — each was checked by execution against the real pin and
produced correct, non-lossy behavior; they are coverage gaps, not shipped defects.

## Confirmations

- Graded via `git show b70d57b4:<path>` for `expertise-merge.py`, `tests/unit/test-expertise-ops.py`,
  `tests/integration/test-expertise-merge.py`, `BRIEF.md`.
- No test written or edited this cycle. Mutation proof ran against a copy in a disposable worktree
  (`.claude/worktrees/qa-mutant-c4`), created and removed via the sanctioned `git worktree add`/
  `remove` flow (absolute path under `.claude/worktrees/`, per bash-write-guard) — never against the
  target worktree or the main checkout.

```
$ git status --porcelain   # target worktree, after the mutation worktree was removed
(empty)
```

```yaml
VERDICT: PASS
DIGEST:
  headline: "All 12 SCs bind an executing test; VL-06 fix confirmed load-bearing across add/replace/drop by mutation; both suites green (unit 28 files/0 fail, integration 46 files/0 fail)."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 28 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 46 }
  coverage_gaps:
    - "CLI-level (subprocess) VL-06 grammar case covers only `add`; `replace`/`drop` proven at resolver level (unit) but not through the CLI boundary — backlog/chore/low"
    - "No case pins acceptance or rejection of unicode-digit ids in target grammar (ENTRY_RE is not re.ASCII-scoped) — backlog/enhancement/low"
    - "No case pins same-id-different-section scoping explicitly, though verified correct live by direct call — backlog/chore/low"
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-expertise-merge.py:case_replace_at_capacity (case11)" }
    - { id: SC-02, test: "tests/integration/test-expertise-merge.py:case_removal (case12)" }
    - { id: SC-03, test: "tests/integration/test-expertise-merge.py:case_missing_target (case13)" }
    - { id: SC-04, test: "tests/unit/test-expertise-ops.py:case_u13; tests/integration/test-expertise-merge.py:case_ambiguous_target(b/c), case_malformed_ops_cli(a/b) (case14, case20)" }
    - { id: SC-05, test: "tests/integration/test-expertise-merge.py:case_atomic_failure (case15)" }
    - { id: SC-06, test: "tests/integration/test-expertise-merge.py:case_add_only_compatibility (case16)" }
    - { id: SC-07, test: "tests/unit/test-expertise-ops.py:case_u10" }
    - { id: SC-08, test: "tests/integration/test-expertise-merge.py:case_replace_at_capacity, case_removal (case11, case12)" }
    - { id: SC-09, test: "tests/integration/test-expertise-merge.py:case_contract_drift (case17)" }
    - { id: SC-10, test: ".harness/harness/docs/DECISIONS-INDEX.md:219; tests/integration/test-gen-decisions-index.py" }
    - { id: SC-11, test: "tests/integration/test-expertise-merge.py:case_concurrent_writers (case18)" }
    - { id: SC-12, test: "tests/unit/test-expertise-ops.py:case_u11,case_u12; tests/integration/test-expertise-merge.py:case_multi_op_composition (case19)" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-qa-c4.md
```
