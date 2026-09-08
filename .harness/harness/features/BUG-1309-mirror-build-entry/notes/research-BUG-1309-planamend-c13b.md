# Plan amendment c13b — gating the R-3 remedy (Q2 of research-BUG-1309-planamend-c13.md)

**Q2 is CLOSED in the plan.** The non-era `recovery-required` notice's `recover-terminal` horn — the
R-3 remedy, whose command is derived from `feature_schema.recovery_command_for` — now has a named
case in `T-04.verify`'s asserted list and its acceptance stated as behaviour in `T-04.intent`. Two
compare-and-swap amendments, nothing else touched.

## The new case name, byte for byte

```
T-04 recovery-required non-era recover-terminal horn names the derived command
```

## What was swapped

| field | expect-sha256 (pre) | sha256 (landed) | lines now |
|---|---|---|---|
| `T-04.verify` | `26fe51e15aefac9021f2370001cb0bd9eafd92e9dbad648e645025afcf721111` | `c39b03e51ce1f861ed7b827bb2c1f647ae0a7ab1ac792231617395f74d565eb8` | header 774, body 775-780 |
| `T-04.intent` | `33c6baef73df02ac8699b8e3d356bdf3c7751bc3d5c6fbcc7b58243da678952b` | `b3c16793d9c86f2b9bc8e3e91d217dc69f81cc4636db592ec582d60a3498a900` | header 781, body 782-975 |

Note the `--show` sha is computed over the **raw indented block lines** in the file
(`plan-merge.py:1581`), while `--show`'s printed body is dedented; the dedented body is what
`--value-file` takes. Extracting the base via `yaml.safe_load` gives that same dedented string
(verified equal), so the base for a large field can be extracted mechanically instead of retyped.

## Case count — the dispatch said six existing, there were FIVE

`T-04.verify` asserted **five** `T-04 …` names before this amendment, not six. **Six** after the
append; the original five are unchanged and in their original order, and the delta over the whole
block is exactly the appended quoted name (proved by string-subtracting the name and comparing to
the pre-swap value). `T-04.intent` took two pure insertions, zero removals: a 4-line paragraph after
the "Keep that fixture on that horn" sentence, and the new 18-line case bullet immediately after the
unnamed `open`-horn case.

## The file-target finding — the case belongs in `tests/integration/test-gh-sync.py`

The dispatch named `tests/unit/test-gh-sync-build-entry.py`. That target is **unsatisfiable together
with the verify append**, confirmed at source:

- `T-04.verify` greps the integration runner's format `ok    <name>` (`tests/integration/test-gh-sync.py:733-739`);
  the unit runner prints `PASS <name>` (`tests/unit/test-gh-sync-build-entry.py:34-37`). A name in
  that `for` loop can never match a case hosted in the unit file.
- `T-04.files` is `['.claude/skills/harness/bin/gh-sync.py', 'tests/integration/test-gh-sync.py']` —
  the unit file is T-11's.
- The five existing `T-04 …` cases are in the integration file at `:3602-3627`; the unit file's
  naming convention is `BE-NN`.

So the host is the integration file, in that same block. `T-04.intent`'s existing "Tests, in
tests/integration/test-gh-sync.py" line already agrees, so the amendment introduced no second
spelling.

## The horn condition, stated not pinned

`recovery_command_for` (`feature_schema.py:324-338`) returns `recover-terminal` for: era-exempt
basename, unreadable `plan.yaml`, `plan.status` in `{review, done}`, or any task `status: done`;
otherwise `open`. The new case's intent names the *condition* (`status` `review`/`done`, or any task
`status: done`) and leaves the fixture shape to the implementer, and requires the assertion to read
the classifier's answer rather than a second hardcoded command string — agreement with the
classifier is the property under test (that pinning is what produced PANEL-3 / ruling R-3).

## Left alone, deliberately

- The **`open`-horn half** of the same notice is still specified by an **unnamed** case bullet and is
  therefore still ungated. Out of this amendment's scope; the intent now says explicitly that it is
  not renamed, re-fixtured or "fixed". Raised as `Q3` (non-blocking) rather than widening the swap.
- `BRIEF.md`, `approval:`, every station verb, every other task, everything under
  `.claude/skills/harness/bin/` and under `tests/`.

## Checks run

- `yaml.safe_load` parses: 13 tasks, 15 decisions.
- Lines 1-23 (`approval:` is lines 3-23, last line `reason: resolved by disclosure …`) are byte
  identical to `HEAD`; the earliest `git diff -U0` hunk in the file starts at old line 202. Approval
  bytes unchanged.
- `check-plan-routes.py <plan>` → `0 violation(s)`, exit 0 (the `DEVIATION` lines are the standing
  DEC-174 main-session carve-outs, unchanged by this amendment).
- No test was written or edited (DEC-174): the case name and its acceptance are in the plan; the
  main session implements it.
