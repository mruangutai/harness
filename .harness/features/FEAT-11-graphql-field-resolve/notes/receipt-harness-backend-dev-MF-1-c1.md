# Receipt — harness-backend-dev — FEAT-11 T-01 MF-1 fix cycle (c1)

## What changed

`.claude/skills/harness/bin/test-factory-gh.py`, four sites, exactly as ordered by the dispatch:

- `:400` (unknown-owner call) — owner arg `"owner"` → `"acmeuser"`, one short inline comment.
- `:411` — assertion substring `"owner" in str(unknown_exc)` → `"acmeuser" in str(unknown_exc)`.
- `:421` (organization loop call) — owner arg → `"acmeuser"`, one-line pointer comment.
- `:436` — assertion substring → `"acmeuser" in str(org_exc)`.
- `:450` (board-absent call) — owner arg → `"acmeuser"`, one-line pointer comment (trap 1).
- `:457` (approx) — expected substring `"owner project 3"` → `"acmeuser project 3"`.

(Line numbers shifted a few lines after the comments were added/trimmed; the four call sites and
their four assertions are the only behavioural change.) Nothing else touched. `factory_gh.py`
unedited — confirmed byte-identical before and after both mutant runs, sha256
`f5978a33269828704f2225ccd2af851b131e45012ef2ac6c68ccfcf4c8ca1e02`, and absent from the final
`git status --porcelain` below. No frozen D-04 strings touched, no `:320`/`:332`/`:460`/`:468`/
`:606`/`:616` sites, no `:377`/`:389` transport case.

## Baseline

`python3 .claude/skills/harness/bin/test-factory-gh.py` (unmodified tree): **118/118 checks
passed**, exit 0.

## Mutant, BEFORE the fix (factory_gh.py mutated: branch (a)/(b) raises carry `""` instead of
`owner` as the value; test-factory-gh.py still unedited at this point)

Result: **113/118 passed, 5 FAILING** — not zero, reported exactly as observed rather than rounded
to the dispatch's stated expectation:

```
FAIL  organization (exit-1 unreachable): raises GhError naming the owner
FAIL  organization (exit-0 reachable): raises GhError naming the owner
FAIL  GhError invariant holds for 'project owner not found:  — check the owner login'
FAIL  GhError invariant holds for 'organization-owned board not supported:  — run against a use'
FAIL  GhError invariant holds for 'organization-owned board not supported:  — run against a use'
```

`unknown owner: raises GhError naming the owner` (the `:407`-era check) did **not** redden — it is
vacuous exactly as MF-1 says, because `"project owner not found"` contains the literal substring
`"owner"` in its fixed prose (checked directly in Python: `True`).

The two `organization (...)` naming checks **did** redden — contrary to MF-1's framing that both
named messages are vacuous. Checked directly: `"owner" in "organization-owned board not
supported:  — run against a user-owned board"` is `False` — that message's fixed prose contains
`"owned"`, not the substring `"owner"`. So of the two messages MF-1 names as vacuous, only the
unknown-owner one actually was; the organization-message naming check already discriminated on
this literal-substring assertion before this cycle's fix. This is a partial falsification of
MF-1's static-proof claim, not of its remedy — the four-site value move is still required
regardless (it fixes the genuinely vacuous `:407` case, and `:421`/`:441` must move with it per
trap 1) — so it changes the finding's accuracy, not the fix. Surfaced as `open_questions` below
for the record, since it isn't mine to edit `runs/t01-qa-validator/digest.md`.

**The three `GhError invariant holds for ...` failures are not unrelated collateral** — read the
condition at `test-factory-gh.py:794-800` (`"—" in m and "GhError" not in m and "Traceback" not in
m and value.strip() != ""`): it is a general guard, run over every `GhError` raised anywhere in the
suite, that the value slot is non-empty. It independently caught this exact defect class (an empty
value) on both mutant runs, for every one of the three cases whose value was emptied. It does not
substitute for MF-1's fix — it says "some value is present," never "the right value is present," so
it would not catch a value swapped for a different wrong string — but it is a second, structurally
distinct signal on the same defect, not noise.

Restored `factory_gh.py`, verified byte-identical (sha256 matches, above).

## Applied the four-site fix to test-factory-gh.py

`python3 .claude/skills/harness/bin/test-factory-gh.py`: **118/118 checks passed**, exit 0 — green,
no behaviour change.

## Mutant, AFTER the fix (same factory_gh.py mutation, test-factory-gh.py now carries the fix)

Result: **112/118 passed, 6 FAILING**. Exactly **three** SC-10 naming checks reddened, verbatim:

```
FAIL  unknown owner: raises GhError naming the owner
FAIL  organization (exit-1 unreachable): raises GhError naming the owner
FAIL  organization (exit-0 reachable): raises GhError naming the owner
```

Matches the dispatch's prediction exactly: the unknown-owner check fires once, the organization
check fires twice (once per label in the `("exit-1 unreachable", "exit-0 reachable")` loop). The
other three failures are the same `GhError invariant holds for ...` checks described above.

Restored `factory_gh.py` again, byte-verified identical (same sha256 as above).

## `git status --porcelain` after the final restore (verbatim)

```
 M .claude/skills/harness/bin/test-factory-gh.py
 M .harness/features/FEAT-11-graphql-field-resolve/DESIGN.md
 M .harness/features/FEAT-11-graphql-field-resolve/feature.yaml
 M .harness/features/FEAT-11-graphql-field-resolve/observations/harness-visual-designer.md
 M .harness/logs/2026-08-10.md
?? .harness/features/FEAT-11-graphql-field-resolve/notes/qa-c0.md
?? .harness/features/FEAT-12-end-copy-distribution/
```

`factory_gh.py` does not appear. The `DESIGN.md`, `feature.yaml`, `observations/*`, `logs/*`,
`notes/qa-c0.md` and `FEAT-12-end-copy-distribution/` entries were already present/modified before
this cycle started (confirmed against `git status --porcelain` run at the start of this session)
and were not touched by this cycle.

## T-01 verify block — cross-checked against `plan.yaml` programmatically

Loaded `plan.yaml` `tasks[0]["verify"]` via `harness_yaml.load_plan(...)`, wrote the loaded string
and the dispatch's quoted block to two files, and ran `diff` between them: **exit 0, no output** —
byte-identical, no mismatch. Then executed the loaded string itself (not a retyped copy) with
`bash -c "$(cat <loaded file>)"`:

```
$ bash -c "$(cat loaded_verify.txt)"
PASS
```

## Both test kinds, run separately, real per-kind counts

- `run-unit-tests.sh --kind unit`: exit 0. **10/10 scripts PASS**, per-script counts: 13, 15, 10,
  33, 118 (`test-factory-gh.py`), 56, 30, 172, 77, 45.
- `run-unit-tests.sh --kind integration`: exit 0. **12/12 scripts PASS**
  (`test-validate-digest.py`, `test-gh-sync.py`, `test-check-state.py`, `test-check-expertise.py`,
  `test-gen-decisions-index.py`, `test-bash-write-guard.py`, `test-check-domain.py`,
  `test-harness-yaml.py`, `test-upgrade-config.py`, `test-check-plan-routes.py`,
  `test-merge-settings.py`, `test-factory-integration.py`), including `test-factory-integration.py`
  **97/97**.

## Constraints honoured

No live `gh` calls (all fixture/fake-driven). `check-domain.sh`, `bash-write-guard.sh`,
`validate-digest.py`, `check-state.sh`, `run-unit-tests.sh` untouched.
`test-factory-decompose.py` / `test-factory-claim.py` / `test-factory-land.py` untouched — sha256
pins confirmed matching in the verify block above. No commit made, no push.
