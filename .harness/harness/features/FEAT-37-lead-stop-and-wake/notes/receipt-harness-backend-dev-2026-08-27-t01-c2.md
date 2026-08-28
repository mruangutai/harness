# Receipt — harness-backend-dev — FEAT-37 T-01 — cycle 2 (send-back)

## Defect closed

`bound_cases()` in `.claude/skills/harness/bin/test-lead-stop-and-wake.py`: an `--only` value
matching no `BOUND_SITES` entry previously produced an empty `sites` list, so the loop never ran,
`results` stayed `[]`, and `main()` printed `ALL PASS` / exit 0 — grading the empty set as success,
the exact fail-open shape the task's per-site floor exists to forbid one level up from where it was
placed.

**Fix** (`bound_cases`, line ~339): when `only_path` is given and matches nothing, append a single
named result `("case_only_matched_no_site", False, "--only <path> matched no bound site; available:
<comma-joined site paths>")` and return immediately — never fall through to the empty loop. No
change to `BOUND_SITES` (still exactly two entries) and no enum-narrowing of `--only`; any unmatched
value is refused, regardless of cause.

## Assertion added — where and why

Added to `run_self_check()` (`--self-check`), after the six existing variants: calls
`bound_cases(only_path="/no/such/site/path/for/self-check.md")` directly and asserts the returned
list is non-empty and every entry's `ok` is `False`, printing `SELFCHECK PASS/FAIL variant
bound_only_unmatched`. This does **not** open a live file — the empty-match branch in `bound_cases`
returns before `bound_site_cases`/`read_text` is ever called for the bogus path — so it satisfies
`--self-check`'s "no live file" constraint while still running under a command the verify block
executes (`--self-check` is verify line 1).

## Task verify — literal output, this cycle

```
$ cd "$(git rev-parse --show-toplevel)"
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --self-check; sc=$?
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group playbook; pb=$?
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group coverage; cv=$?
$ .claude/skills/harness/bin/run-unit-tests.sh --check-kinds; ck=$?
$ echo "selfcheck=$sc playbook=$pb coverage=$cv checkkinds=$ck"
selfcheck=0 playbook=1 coverage=1 checkkinds=0
T01_PASS
```

All seven `--self-check` variants (A FAIL / B PASS / C FAIL / D FAIL / E FAIL / F FAIL, plus the
new `bound_only_unmatched` PASS) printed `SELFCHECK PASS` — the required six verdicts are
unchanged, and the new seventh variant is additive, not a substitution. `playbook=1` and
`coverage=1` both still fail against real, unshipped text (9/9 and 3/3 cases respectively, same
case names and same detail strings as cycle 1's receipt) — neither group loosened.
`task_verify: pass`.

## Discriminating pair — required evidence

**Bogus `--only` path (before the fix: exit 0 / `ALL PASS`; after the fix):**

```
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group bound --only /no/such/bogus/path.md
FAIL case_only_matched_no_site --only '/no/such/bogus/path.md' matched no bound site; available: .harness/harness/docs/DECISIONS.md, .claude/skills/harness/bin/inflight_registry.py

1 FAILURE(S): ['case_only_matched_no_site']
exit=1
```

**Valid `--only` path (must still select exactly that one site, unaffected by the fix):**

```
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group bound --only .harness/harness/docs/DECISIONS.md
reading bound site from <abs>/.harness/harness/docs/DECISIONS.md
PASS case_floor_DECISIONS.md
FAIL case_occurrence_DECISIONS.md_6869_1 ...
FAIL case_occurrence_DECISIONS.md_6870_2 ...

2 FAILURE(S): ['case_occurrence_DECISIONS.md_6869_1', 'case_occurrence_DECISIONS.md_6870_2']
exit=1
```

Same site, same two occurrence names/lines as cycle 1's receipt — the fix touches only the
zero-match branch, nothing on the matched-selection path.

## What did not change

- `run-unit-tests.sh` — diffed against cycle 1: identical one-line `UNIT_SCRIPTS` addition, no
  further edits this cycle.
- `BOUND_SITES` — still exactly `[DECISIONS_PATH, INFLIGHT_REGISTRY_PATH]`.
- No `.claude/skills/harness-team/SKILL.md`, `.claude/skills/harness/SKILL.md`,
  `inflight_registry.py`, or `.harness/harness/docs/` edits (T-03 remains struck, #903 — not
  restored, not relitigated).
- The `--only` CLI flag still accepts any string; no enum narrowing.

## Files touched

- `.claude/skills/harness/bin/test-lead-stop-and-wake.py` (bound_cases fix + self-check assertion)
- this receipt

## Digest

```yaml
VERDICT: PASS
DIGEST:
  headline: "--only with an unmatched bound site now fails named and non-zero instead of vacuously passing the empty set"
  tests_added: 1
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/test-lead-stop-and-wake.py
    - .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/receipt-harness-backend-dev-2026-08-27-t01-c2.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/receipt-harness-backend-dev-2026-08-27-t01-c2.md
```
