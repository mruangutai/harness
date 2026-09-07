# Plan fix c7 — the two approved disposition amendments are applied

**BLUF.** Both operator-approved textual amendments are in `plan.yaml` via `plan-merge.py amend`
(compare-and-swap, `--show` then `--expect-sha256 --value-file`). Nothing else moved: 9 tasks,
9 decisions, `approval.status: pending`, `panel.findings` still 7 with unchanged ids, readers,
severities and dispositions (3 resolved / 4 open). `check-plan-routes.py` exits 0.

## The two amendments

- **T-06 `intent:`** — the `THE SHARED SOURCE (D-08)` era-set bullet now specifies the SHIPPED
  comment's required content as three things: the generating command verbatim, the commit sha, and
  one further sentence written on its own line beside them, quoted VERBATIM in the task and
  followed by an explicit note that it is text the doer writes into `feature_schema.py`, not the
  plan's prose about the comment: *"When this file is vendored into another project at upgrade,
  regenerate this set THERE with the same command, from that project's feature directories."*
  Closes PF-8bfef7ee (accepted forward-only). Freezing rule, generating command, one-definition
  clause (`THE ERA SET HAS EXACTLY ONE DEFINITION … is a DEFECT`), fixture-name rules, case-name
  contract and `verify:` all unchanged; the only other edit was re-wrapping the one line the
  insertion had run on.
- **D-09 `because:`** — one appended price rider (one sentence, semicolon-separated three items).
  All prior text retained, including the closing disclosure that the orchestrator's reading is
  overturnable at signature. `choice:` untouched.

## The three price items, as verified in T-05 (line anchors, pre-amend read of T-05 at 649-953; T-06 follows T-05 so these anchors did not shift)

1. **Second verbatim deny reason** — T-05 step 6, `REPO UNPINNED` branch, `plan.yaml:766-781`;
   the verbatim reason text sits at `:776-781` and names no clearing command
   (`NO COMMAND CLEARS THIS BY ITSELF`), with the no-`open`-token rule at `:773-775`.
2. **CONFIG PAIR unpinned half** — declared at `plan.yaml:886-898` (unpinned half `:893-898`),
   case name `"T-05 unpinned repo absent build_entry denies naming the configuration fix"` at
   `:937-940` and in T-05's `verify:` name list at `:671`.
3. **Standing pin constraint** — `plan.yaml:899-901`: *every other* fixture root in
   `tests/integration/test-merge-gate.py`, allow and deny alike, pins `github.repo` to the literal
   `acme/widgets`; the pinned half itself is at `:890-892`.

## Confirmed counts — `python3 /tmp/bug1309_c7_check.py` over `yaml.safe_load`

```
safe_load: OK
tasks: 9
decisions: 9
approval.status: pending
panel.findings: 7
dispositions: {'resolved': 3, 'open': 4}
ids: ['PF-f1684ee3de7606a3e48a4bb9b545a8a9', 'PF-1aa3b36ca9f98cdaf25b30f16e72069f', 'PF-a882c9b854373d226faa38bddba8fcc7', 'PF-6030c547ed525627c274560e6edd9c05', 'PF-8bfef7ee69e3adc23a65c02cfd5debd4', 'PF-23f51fd8ee94dc42e9df11fbed42593b', 'PF-da04a39ff4551e9e99da72e940e64c99']
severities: ['med', 'med', 'med', 'low', 'low', 'low', 'low']
T-06 sentence verbatim: True
one-definition clause intact: True
D-09 overturnable sentence retained: True
```

## `check-plan-routes.py` — verbatim

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

The three `DEVIATION` lines are the expected DEC-174 carve-out output for granted paths declared
main-session-direct; only `VIOLATION` gates, and there are none.

## Open

None. The operator's acceptance of the four remaining open findings is the main session's
`sign-approval --overrule` write — no disposition was changed here.
