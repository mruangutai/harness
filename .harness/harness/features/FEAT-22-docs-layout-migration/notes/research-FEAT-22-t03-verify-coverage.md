# research — FEAT-22 — T-03 verify coverage, send-back 4

BLUF: the send-back's core claim is confirmed and closed with **five runnable assertions** in T-03's
`verify:` (plan.yaml:363-380). Each was run against a token-swap-only rewrite of
`harness_boundary.py` and reds it, while today's verify passes that same rewrite — measured, not
argued. Q1 is closed by measurement: **zero `^FAIL test-` lines in both suites** at the pin. All
three advisories folded. `BRIEF.md` untouched — nothing in Job 1 turns on a criterion's wording.

Base re-confirmed before and after: `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`.

## The gap, restated as a measurement

Applying only token substitutions to `harness_boundary.py` (`docs/harness/**` → `.harness/*/docs/**`,
`docs/harness/<link>` → `.harness/harness/docs/<link>`, `docs/harness/SPEC.md` →
`.harness/harness/docs/SPEC.md`, `<harness>/docs/harness/guide.md` →
`<harness>/.harness/harness/docs/guide.md`) and dropping every semantic requirement:

- T-03's pre-existing positive migrated-regex grep: **exit 0 (passes)**
- T-03's pre-existing whole-file legacy-absence grep: **no match (passes)**

So the exact build the intent forbids passed the gate. That is the finding, reproduced.

## The five assertions, and what each proved

Extracted from the plan by `yaml.safe_load` and executed — the proof attaches to the shipped string,
not to a prototype. Each grep was given its own file descriptor; an earlier run that piped one
process substitution through the whole block was invalid (the first grep consumes the stream) and
was discarded.

| Site | Assertion (plan.yaml) | vs token-swap build | vs pin file | vs correctly-fixed build |
|---|---|---|---|---|
| `:84` | `grep -qi 'redundant'` (:364-365) | exit 1 — **reds it** | exit 1 — non-vacuous | exit 0 |
| `:221` | negative `grep -qE 'holds no.*entry anywhere'` (:366-369) | matches — **reds it** | matches — discriminating | no match, passes |
| `:111` | positive `grep -qF -- '-> ../../../.claude'` (:370-371) | exit 1 — **reds it** | exit 1 — non-vacuous | exit 0 |
| `:111` | negative `grep -qF -- '-> ../../.claude'` (:372-375) | matches — **reds it** | matches (1 occurrence, unique) | no match, passes |
| `:315` | awk window around the unique `guide.md` anchor must contain `.harness/*/docs/**` (:376-380) | exit 1 — **reds it** | exit 1 — non-vacuous | exit 0 |

Why the `:111` negative is safe: `-> ../../../.claude` does **not** contain the substring
`-> ../../.claude` (tested directly), so the correct fix does not trip its own guard. The bare
two-climb chain occurs exactly once in the file today, so no legitimate second site is caught.

Why the `:315` check is window-scoped, not whole-file: after T-03 the literal `.harness/*/docs/**`
exists at `:90` as the list entry, so a whole-file grep would be vacuous. The window is anchored on
the `guide.md` occurrence (unique, asserted) and spans eight lines above to three below — content-
anchored, so it survives renumbering. The `:90` entry sits 200+ lines away and cannot satisfy it.

## `:221` is negative-only, and that is the ceiling

The positive handle the intent implies — "TARGET-keyed" — is **already present at `:220` today**, so
asserting it would be vacuous and would pass a build that changed nothing. The shipped assertion
therefore forces the falsified claim OUT but cannot force the replacement prose to be right. That
half rests on the intent plus a human reading the diff. Stated rather than dressed up as coverage.

## Intent tightened alongside every assertion

Each pinned token is now named to the builder, because `intent:` is the whole dispatch and a verify
token the builder was never told about reds a semantically-correct build: `:84` must use the word
*redundant*; `:111` gets the literal `../../../.claude` **and** the segment-count reason (two-segment
base needs two climbs to escape, the three-segment destination needs three); `:221` names the
forbidden phrase; `:315` must name `.harness/*/docs/**` as the grantor inside the guide.md paragraph
and keep `guide.md` to one occurrence.

## Q1 — settled by measurement, at the pin

Runner actually used: `.claude/skills/harness/bin/run-unit-tests.sh` (there is no `bin/` at the repo
root; the dispatch's path was a guess).

| Suite | `^FAIL test-` | `^PASS test-` | exit |
|---|---|---|---|
| `--kind unit` | **0** | 15 | 0 |
| `--kind integration` | **0** | 12 | 0 |

Both green at `0f12f14`, with one unrelated modified tracked file in the tree
(`.harness/logs/2026-08-15.md`) and untracked feature notes. T-05's expected-FAIL pin stands on a
verified premise; nothing was patched around.

## Advisories — all three folded

- **A1** (T-01 red windows, :243-256): corrected. `test-layout-migration.py` is red on **[T-02, T-03)**
  via case 1's real-root exit-0 assertion (`test-layout-migration.py:131`, read at the pin), and T-05
  only adds cases to it. The `[T-03, T-05)` sentence now covers only the other four, and the 4-integration/
  1-unit split is stated. Suite membership verified against `run-unit-tests.sh:17-18`.
- **A2** (T-09 stray files, :937-947): hardened with a **prefix allow-list** over the commit's file
  list plus a `-ge 28` floor. An allow-list beats a count here — it catches the live case (a stray
  `.harness/logs/` edit riding `git add -u`) and cannot red a correct build the way an exact count
  would. 28 is the enumerated cluster; it is a floor, not an equality.
- **A3** (T-01 pre-move suite capture, intent + verify :194-195): PRE-MOVE now records both suites'
  PASS/FAIL lines and exit codes as a verbatim capture, giving SC-07/SC-08 a recorded "before". The
  verify asserts the section exists; it does not assert zero FAILs, because the note is a capture,
  not a gate.

## Open, non-blocking

`test-check-domain.py`'s comment at `:785-788` carries the **same false-claim shape** as `:221` — it
argues no `docs/harness/**` entry exists anywhere in team-config.yaml, which T-02 falsifies. T-05's
intent (:568-576) directs the rewrite, but no assertion enforces it and the reviewer's sweep covered
`harness_boundary.py`, not the test files. Same class, outside this send-back's four sites; raised
rather than silently fixed.

## Gates run after the edit

- `yaml.safe_load` over the whole plan: loads; every edited field's tail intact.
- `check-plan-routes.py`: exit 0, 0 violations (routing untouched).
- `approval.status`: `pending`, unchanged. `BRIEF.md` not opened for edit.
