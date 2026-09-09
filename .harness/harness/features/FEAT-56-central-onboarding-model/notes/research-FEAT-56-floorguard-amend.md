# research — FEAT-56 floor-guard amend (durability of the CLI-floor deletion)

**Closed.** The operator's ruling — the Claude CLI 2.1.217 floor leaves `harness-init`'s preflight
entirely — now has a permanent guard. T-17's split test asserts both strings ABSENT from
`.claude/skills/harness-init/SKILL.md`, per file and per token, and the pair was observed RED
against today's tree. No new task, no new decision, no production file, `approval:` untouched.

## What changed — two halves, one change

- `plan.yaml` T-17 `intent`, via `plan-merge.py amend --expect-sha256` (the only write route).
  The existing CLI-probe bullet was widened from one file to two, keeping its bullet class: it now
  reads "The CLI-probe strings are absent from BOTH cut skills … one assertion per token naming its
  token", covering `harness-add-repo` (`claude --version`) and `harness-init`
  (`claude --version`, `2.1.217`). Its RED-CAPABILITY paragraph gained the two measured counts at
  the same pin. T-17's `verify:`, `files:`, `traces:`, `depends_on:` are untouched, and `verify:`
  remains a literal `|` block (loads with 5 newlines).
- `BRIEF.md` SC-14: `claude --version` and `2.1.217` appended to the `harness-init/SKILL.md`
  `matches none of` list only. Its `harness-add-repo` list, command-door clauses,
  `verify:`/`evidence:` are unchanged.

## Why the guard was needed

T-11's verify (`! grep -qF 'claude --version'`, `! grep -qF '2.1.217'`) is a **build gate that stops
existing the moment T-11 is done**. T-17's case named `harness-add-repo` only, and SC-14's
`harness-init` token list omitted both strings — so a later edit re-adding the STOP reddened
nothing. Same failure class this feature already fixed once: an assertion that can only ever pass.

## Measurement at the pin `12f74ea8` (unchanged pin)

`git show 12f74ea8:.claude/skills/harness-init/SKILL.md | grep -cF …` →
`claude --version` **1**, `2.1.217` **1** (controls: `Track B` 2, `factory/fleet.yaml` 2).
SC-14's trailing RED statement was extended in the same clause shape and remains true: the enlarged
token list is still fully falsified at that commit.

## Red-capability — observed, not asserted

T-17's `verify:` was run verbatim from the worktree root first; it died at
`test-onboarding-split.py: [Errno 2] No such file or directory` (exit 2) because T-17 is unbuilt.
That is **not** evidence, so the amended clause set was run directly against
`.claude/skills/harness-init/SKILL.md` at HEAD in the per-file-per-token shape the intent specifies:

```
RAN 2 assertions
FAIL .claude/skills/harness-init/SKILL.md: must not match the string 'claude --version'
FAIL .claude/skills/harness-init/SKILL.md: must not match the string '2.1.217'
FAILS 2 / exit=1
```

Positive control — same harness against a temp copy with the two lines cut (the post-T-11 shape):
`RAN 2, FAILS 0, exit=0`. The clauses discriminate in both directions; they are not ever-red either.
(`harness-add-repo/SKILL.md` does not exist yet — T-13 unbuilt — so the harness SKIPs it explicitly
rather than letting a missing predecessor short-circuit the new clauses.)

**A future edit re-adding the floor STOP to `.claude/skills/harness-init/SKILL.md` trips
`tests/integration/test-onboarding-split.py`'s CLI-probe case — one named assertion per token.**

## No conflict, re-checked at source

`test-hooks-install.py::case_commands_verbatim_in_skill` pins the two `git config … core.hooksPath`
strings (`:63-65`), not the CLI probe. Recorded in T-17's item 3 so the next reader does not
re-litigate it.

## Gates

- 17 tasks, D-01..D-13, `approval: {'status': 'pending'}` — unchanged.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`, exit 0.
- `git status` shows no production file modified.

## Open questions

None blocking. The bullet was widened rather than split into a new case so the count of case classes
in T-17 is unchanged — a reversible shape choice, recorded here rather than raised.
