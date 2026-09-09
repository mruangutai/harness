# Plan amendment — panel c0 transcribed, three findings fixed (BUG-1309-mirror-build-entry)

**BLUF: `plan.yaml` now carries the full panel record (2 readers, 7 findings, 3 resolved / 4 open)
and the three mechanical fixes are in. The SCOPE-01 honesty clause did NOT fire — the
caller/contract-error path is reachable and I observed it: `open` on a feature with no `BRIEF.md`
exits 1 through `read()`'s `die()` with no `github` mapping written. `approval.status` is still
`pending`; tasks 9, decisions 9.**

## The write route the dispatch named does not work — `apply` refuses, `amend` is the verb

`plan-merge.py apply` re-proposing an EXISTING task id with a CHANGED value exits **7 CONFLICT**
(`apply_merge`, the `pitem != item` branch). Probed before touching anything:

```
CONFLICT: id='T-03' in 'tasks' carries two different values.
EXIT=7
```

Every fix therefore went through the in-vocabulary verb for changing a value under an existing id —
`plan-merge.py amend --key tasks --id T-NN --field <f> [--yaml-value] --expect-sha256 <sha> --value-file <f>`
— five amends, each `AMENDED … / APPLIED …` at exit 0. The panel went through `set-panel
--value-file`. No hand edit, no whole-file write.

## Fix 1 — LEAD-01: the registration instruction, verified at all three sites myself

My read matches the lead's on `.claude/settings.json` and adds the two the lead did not price:

| site | Bash array, in file order | new hook is |
|---|---|---|
| `.claude/settings.json` (`hooks.PreToolUse`, matcher `Bash`) | branch-create, bash-write-guard, gh-close, plan-sign | the **fifth** entry |
| `.claude/skills/harness/templates/settings.snippet.json` | branch-create, bash-write-guard, plan-sign — **no gh-close entry at all** | the **fourth** entry |
| `.omp/extensions/harness-hooks.ts` `firstBlock([...])` | gh-close, branch-create, bash-write-guard, plan-sign — **a third, different order** | the **fifth** element |

The rewritten instruction names, per site, the literal predecessor (`plan-sign-gate.sh` in all
three, as it happens) and the literal successor (**none** — merge-gate.sh is last), and states the
constraint the neighbours only encode: **merge-gate.sh runs last, after `bash-write-guard.sh`.**
`bash-write-guard.sh` is the only registered gate whose subject can also match a merge command
line (it scans the whole line for redirects/`tee`/`cp`/`mv`/`rm`), so `gh pr merge 7 > log` is
refused by both; the write-guard's reason must win, because the redirect is refused whatever the
merge verdict while merge-gate's reason names a recovery command that would not make that line
legal.

Consequence, per path, verified at source: `firstBlock(results)` is
`results.find(r => r.blocked)?.reason` over an **already fully evaluated** array
(`harness-hooks.ts:276-278`, call site `:697-702`) — every gate runs on every bash call whatever
its index, so position decides only *which deny reason the agent sees*. In the `settings.json`
path no index is read at all: the failure mode there is **absence, not order**, and the instruction
says so rather than inventing a consequence. The instruction also tells the doer to satisfy the
constraint, not the names, if a reshuffle has already moved them, and turns
`tests/unit/omp-hooks.test.ts`'s ordering assertion into the machine-checkable form
(`indexOf("merge-gate.sh")` greater than `indexOf("bash-write-guard.sh")` and
`indexOf("plan-sign-gate.sh")` — a relation, never a literal index).

## Fix 2 — SCOPE-01: one declared case, and the clause is real

Honesty clause checked by **running the path**, not by reading it. `cmd_open`'s first data
statement is `parse_brief` → `read()` → `die()`. Probe: a sync-enabled fixture with `github.repo`
pinned, `BRIEF.md` deleted, fake `gh`:

```
exit: 1
gh-sync: ERROR — …/FEAT-9001-probe/BRIEF.md does not exist
feature.json keys: ['feature_id', 'status']      # no github mapping written at all
```

Reachable, and reached **after** `main()` arms `_BUILD_ENTRY["feat_dir"]` — the only state in which
a recording bug could fire. So the clause stands and no BRIEF sub-clause is struck.

New case, identical literal text in T-02's `intent:` case list and its `verify:` `for n in` list:
**`T-02 contract error records nothing`**. It asserts exit status exactly 1 and
`"build_entry" not in doc.get("github", {})` — key absence, never a falsy value. `.get` rather than
`doc["github"]` is deliberate and measured: `stage()`'s `feature.json` carries no `github` key
until a write creates one, so `doc["github"]` would `KeyError` instead of asserting.

## Fix 3 — SCOPE-02: traces widened, coverage re-derived

`T-02.traces` += REQ-07, `T-03.traces` += REQ-09. Nothing removed. Map re-derived from the amended
file (every REQ-01..REQ-10 in `BRIEF.md` is traced; no orphan):

```
REQ-01 T-02 T-04 T-08 T-09   REQ-06 T-02 T-04
REQ-02 T-03 T-07 T-08 T-09   REQ-07 T-02 T-05
REQ-03 T-01 T-02             REQ-08 T-03 T-09
REQ-04 T-01 T-02             REQ-09 T-03 T-07
REQ-05 T-01 T-02             REQ-10 T-06
```

## The panel record

`panel:` is a sibling of `approval:`, written by `set-panel`. `last_run: 2026-09-06-01-validator`,
`cycle: 0`, both readers present with `status: ran` (no skip-only fields), seven findings.

**Ids are content hashes of `reader + summary`, so every summary is the lead's digest text
UNALTERED** — extracted programmatically from the digest's fenced return block and passed verbatim
to `panel_findings.py id`. A reworded summary is a different finding, and an operator ruling naming
the old id would silently stop applying. That rule is recorded in the file as
`panel.transcription_rule`.

| ref | id | sev | reader | disposition |
|---|---|---|---|---|
| LEAD-01 | PF-f1684ee3de7606a3e48a4bb9b545a8a9 | med | should-not-exist | resolved · T-05 |
| SNE-01 | PF-1aa3b36ca9f98cdaf25b30f16e72069f | med | should-not-exist | open |
| SCOPE-01 | PF-a882c9b854373d226faa38bddba8fcc7 | med | scope | resolved · T-02 |
| SNE-04 | PF-6030c547ed525627c274560e6edd9c05 | low | should-not-exist | open |
| SNE-02 | PF-8bfef7ee69e3adc23a65c02cfd5debd4 | low | should-not-exist | open |
| SNE-03 | PF-23f51fd8ee94dc42e9df11fbed42593b | low | should-not-exist | open |
| SCOPE-02 | PF-da04a39ff4551e9e99da72e940e64c99 | low | scope | resolved · T-02 |

Severities are the readers' own values, unreassigned. **LEAD-01 is recorded under
`should-not-exist`**: the vocabulary is closed (`should-not-exist | scope | goalcheck`) and has no
`lead` member, and the finding originated in `should-not-exist`'s own cross-lane prose while that
reader was pricing T-05 — `scope`'s file set is the plan and the BRIEF, so it could not have seen
the repo file. SCOPE-02's `resolved_by` is T-02; its summary names the T-03 half, which
`resolved_by` cannot carry. SNE-01/02/03/04 stay `open` with no `resolved_by`: DEC-176 reserves
their risk acceptance for the operator's signature.

## check-plan-routes.py — verbatim

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-04 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-05: declared main-session-direct (.claude/settings.json, .claude/skills/harness/templates/settings.snippet.json, .omp/extensions/harness-hooks.ts ungranted)
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/feature_schema.py, tests/integration/test-check-state.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
DEVIATION T-07 .claude/skills/harness/bin/post-merge-sweep.sh, tests/integration/test-post-merge-sweep.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md, .claude/skills/harness/SKILL.md ungranted)
OK T-09 granted to harness-documentor
0 violation(s) across 1 plan(s)
EXIT=0
```

`DEVIATION` lines are the DEC-174 carve-out output and do not gate; only `VIOLATION` does.

## Open question — not fixed, not mine to fix

**T-05's `settings.snippet.json` bullet says "so harness-init installs it", and that is false as
written.** `harness-init` installs hooks through `merge-settings.py`'s hard-coded `HOOK_SPECS`
(seven entries), not by copying the snippet; a script absent from `HOOK_SPECS` is never installed
into a target project however the snippet reads. `plan-sign-gate.sh` is already in exactly that
position — in the snippet, absent from `HOOK_SPECS` — so `merge-gate.sh` would inherit a
**pre-existing** inconsistency rather than create a new one. Out of this dispatch's scope (it would
add `merge-settings.py` to T-05's `files:`), so T-05 is unchanged and this is raised as Q1.
