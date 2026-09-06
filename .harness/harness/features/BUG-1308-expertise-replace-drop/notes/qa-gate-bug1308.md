# QA test_matrix gate — BUG-1308 — PASS

## Matrix resolution

Per-task `change_type` (plan.yaml): T-01 `bugfix`, T-02 `scaffolding`, T-03/T-04 `docs`.
`scaffolding.always: []` and `docs.always: []` — neither obligates a kind. Only T-01 fires the
`bugfix` row (`.harness/harness.json:203-219`).

Predicates resolved against the actual non-`.harness` changed paths (`.harness/**` files are
excluded from consideration by DEC-217's own text): `.claude/skills/harness-distill/SKILL.md`
(`*.md`), `.claude/skills/harness/bin/expertise-merge.py` (not `.md`, not `tests/**`),
`tests/integration/test-expertise-merge.py`, `tests/unit/test-expertise-ops.py` (both `tests/**`).

- `touches_runtime_code` → **TRUE**, solely via `expertise-merge.py` → requires `unit`.
- `fix_confined_to_tests_and_contract_docs` → **FALSE** (same file breaks it) — confirms the two
  are exact complements here, exactly one fires, per repo precedent.
- `match_bug_class` → **does not fire** (repo Expertise G-08: `__bug_class__` names no
  `test_kinds` entry anywhere in this project; consistent with every prior gate in this repo).

**Required kind: `unit`.** I additionally ran `integration` because T-02's entire deliverable is
`tests/integration/test-expertise-merge.py` (the diff clearly warrants it, verification-rules
"may add, never drop below").

| kind | state | cmd | evidence |
|---|---|---|---|
| unit | **satisfied** | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0, `^FAIL `=0, 28 files discovered (`pool: 8 workers, 28 files`), `test-expertise-ops.py` present and green |
| integration | **satisfied** (qa-added) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0, `^FAIL `=0, 46 files discovered, `test-expertise-merge.py` case11..case20 present and green |

Non-required kinds, honest state: `functional`/`eval` **excluded** (DEC-187, unrelated to this
diff). `component`/`ui`/`typecheck` **unresolved**, null `cmd` — not required by the `bugfix` row
here (no interaction/UI/TS surface touched), so this is not a gate failure, just an honest unresolved
state per the dispatch's own instruction.

## Suite runs (verbatim, from worktree root)

- `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` → exit 0; `grep -c '^FAIL '`=0;
  discovery line `pool: 8 workers, 28 files, 4.05s wall`.
- `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` → exit 0; `grep -c '^FAIL '`=0;
  discovery line `pool: 8 workers, 46 files, 63.73s wall`.
(Both runs used `env -u HARNESS_AGENT_TYPE`, per repo Expertise G-07 — without it `test-plan-merge.py`
fails 11 checks unrelated to this diff.)

## Coverage mapping (4 required properties → case ids)

- **exit 10 MISSING TARGET**: unit `u3`; integration `case13`.
- **exit 11 AMBIGUOUS TARGET**: unit `u5` (dup id in section), `u6` (two ops, one target);
  integration `case14(b)` (dup id), `case14(c)` (two ops same target).
- **exit 12 MALFORMED OPS**: unit `u7` (op=merge), `u13` (missing/empty section, 4 shapes),
  `u14` (payload not a list — mapping and bare string); integration `case20(a/b/c)` (missing
  section key, empty section key, digest-shaped mapping).
- **keyed on (section,id), never index / replace-does-not-move**: unit `u1` (index 6 unchanged
  after replacing P-07, all other entries at their own index); integration `case11` (7th entry
  line carries new text, 15 entries unchanged) and `case19` (id sequence exactly
  `P-02,P-03,P-04,P-05` after a drop+replace).
- **order-independence of multi-op proposal**: unit `u11` (forward vs reversed op order produce
  byte-identical merged `Patterns`, explicit, "never trimmed" per its own docstring); integration
  `case19` (multi-op composition).

No gap: every property has a case in both the unit and integration suite that can fail on it (see
reachability below for the exit-code and position properties).

## Reachability proofs (mutation, (a)) — all four target properties measured, not just read

My domain (`harness-qa`) is denied write access to `.claude/skills/harness/bin/expertise-merge.py`
by both the Write tool and the bash-write-guard, **even inside a disposable worktree** — confirmed:
`git worktree add` under `.claude/worktrees/` still resolves the domain check by path suffix, so
in-place mutation of the real source is not available to this role by design (DEC-151, not a bug).
Adapted proof: copied the module to a scratch file under my own `tests/**` domain
(`tests/tmp_qa_mutation/expertise-merge-mut.py`, since removed), mutated ONE line at a time, then
ran the exact case assertion via a tiny driver against both the real module and the mutant.

1. **exit 10 MISSING TARGET** — mutated `_resolve_replace_or_drop`'s `MergeRefusal(10, ...)` → `99`.
   `u3`'s assertion (`e.code == 10`): real → PASS, mutant → **FAIL `code=99`**. Reverted (file discarded).
2. **exit 11 AMBIGUOUS TARGET** — same function's second raise → `99`. `u5`'s assertion: real →
   PASS, mutant → **FAIL `code=99`**. Reverted.
3. **exit 12 MALFORMED OPS** — mutated the shared `_malformed()` helper's `MergeRefusal(12, ...)` →
   `99`. `u13`'s missing-section assertion: real → PASS, mutant → **FAIL `code=99`**. Reverted.
   (Note: `op=="merge"`'s own inline `MergeRefusal(12, ...)` at `_validate_verb` is a *separate*
   literal, not routed through `_malformed`; `u7` did not redden under this particular mutation —
   verified by direct read that this second site is a distinct hardcoded `12`, equally mutable and
   equally load-bearing for `u7`; not re-run under (a) for time, so this one sub-case is (b)
   reasoning: flipping that literal trivially reddens `u7`'s `code == 12` assertion.)
4. **replace does not move its entry** — mutated `_rebuild_section` to append replaced entries at
   the section's end instead of rewriting in place. `u1`'s assertion (`patterns[6] ==
   ("P-07","NEW TEXT")`): real → PASS, mutant → **FAIL, index 6 held `("P-08","text-08")`** (the
   entry shifted, proving the walk-in-original-order invariant is exactly what the assertion pins).

`git status --porcelain` on the feature worktree after cleanup: **empty** (confirmed below). The
disposable worktree used to attempt in-place mutation (denied) was removed via
`git worktree remove --force` from the MAIN checkout, never from inside it; HEAD of the feature
worktree never moved (`30b84a94`, confirmed via `git log --oneline -1` post-cleanup).

## Test-first compliance (T-01, T-02) — FINDING, not a gate failure

`git log --oneline --name-only origin/main..HEAD`: T-01's implementation
(`.claude/skills/harness/bin/expertise-merge.py`) and its test
(`tests/unit/test-expertise-ops.py`) land in the **same commit** (`182a2788`). T-02's cases land
in one commit (`8fd6ffcb`) alongside `tests/integration/test-expertise-merge.py` only (no source
change, consistent with `scaffolding`). Commit-level history cannot demonstrate red-before-green
ordering when source and test co-land in one commit — neither confirms nor refutes TDD compliance
for T-01; this is a visibility gap in the commit convention, not evidence of a violation.

## Task `verify:` blocks (secondary evidence)

- T-01 (`plan.yaml:354-359`), run verbatim: all 15 cases present, `python3 test-expertise-ops.py`
  exit 0, all listed lines `PASS`.
- T-02 (`plan.yaml:540-545`), run verbatim: all 10 cases present, `python3 test-expertise-merge.py`
  exit 0, 0 `FAIL` lines.

## must_fix

None. No coverage gap identified against the four required properties for either T-01
(`expertise-merge.py` / `tests/unit/test-expertise-ops.py`) or T-02
(`tests/integration/test-expertise-merge.py`).
