# opamend-c2 — the operator's two signature conditions, applied

**Both conditions are in the artifacts and the plan is route-clean; approval stays `pending`.**
Two files changed: `plan.yaml` (five `plan-merge.py amend` calls + one `apply`) and `BRIEF.md`.
Nothing else. One cascade is recorded as OPEN (D-13) and deliberately not resolved.

## Change 1 — the CLI floor leaves the preflight entirely (D-12, T-11, T-10)

Anchors re-measured at HEAD before writing, not inherited: `.claude/skills/harness-init/SKILL.md:34`
is the bare `claude --version` probe inside the preflight fence; `:40` is
`- **CLI < 2.1.217** → below the floor for the spawn env vars. Stop; the depth setting will not take.`
Both confirmed present today (`grep -nF`, output pasted under Evidence 2).

- **D-12 rewritten** to the operator's ruling, attributed to them and dated 2026-09-09: no Claude CLI
  version check of any kind survives in the preflight — probe and floor both deleted, not made
  conditional, not downgraded to a warning. `harness-add-repo` unchanged (no provider CLI check).
  `dec: DEC-83` kept. `because` states the reason in one move — the floor's own stated reason was the
  spawn env vars, i.e. DEC-83's nesting-depth setting, a Claude Code mechanism, inside an artifact
  now isolated to fresh-checkout configuration under a provider-neutral doctrine — plus the accepted
  cost (Claude Code operators lose a live preflight check).
- **T-11 `intent`**: the `AMEND THE PREFLIGHT'S CLAUDE-CLI GATE` paragraph is replaced by
  `DELETE THE PREFLIGHT'S CLAUDE-CLI GATE ENTIRELY`, naming `:34` and `:40`, telling the doer to
  re-measure (they have moved twice), and stating that the templates and `git rev-parse` probes and
  the no-templates / not-a-git-repo / `.harness`-exists STOP bullets all stay. Every other paragraph
  byte-identical (the replacement was computed by slicing the old paragraph out of the loaded value,
  not retyped).
- **T-11 `verify`**: removed the now-false positive assertion
  `cat "$F" | tr '\n' ' ' | grep -qF 'only when running under Claude Code'`; added
  `! grep -qF 'claude --version' "$F"` and `! grep -qF '2.1.217' "$F"` directly after the existing
  STOP-prose ban. All other clauses byte-identical.
- **The `Stop; the depth setting will not take` ban KEEPS its place.** It is not redundant with the
  two new bans: a doer could delete the probe line and the version number and leave a reworded floor
  bullet ("CLI too old → Stop; the depth setting will not take"), which both new greps pass and this
  one catches. It is also still RED today, so it is a discriminating clause, not decoration.
- **T-10 `intent`** (the one other site the change falsified): the closing sentence of its preflight
  paragraph said "This is unconditional here and differs from harness-init, where D-12 keeps the
  floor as a runtime-conditional check". Amended to say harness-init no longer differs — T-11 deletes
  the probe and the floor outright, so neither onboarding artifact checks any provider CLI version.

**Search for other sites asserting the removed strings — result: none beyond the T-10 intent fix.**
Grep of `plan.yaml` + `BRIEF.md` for `2.1.217|claude --version|depth setting|running under Claude Code`
leaves exactly: T-10's verify ban `! grep -q 'claude --version'` and T-17's intent clause (both about
**harness-add-repo**, both correct and untouched); T-11's new bans and new intent; and
`plan.yaml:320`, the cycle-1 **panel finding summary** — a record of what a reader said, noted and
deliberately NOT edited. No SC in `BRIEF.md` mentions either string.

## Change 2 — SC-15, the live OMP UAT

Added after SC-14, `verify: uat`, serving REQ-09. The operator's own act is the test: open an OMP
session, type `/harness-plan`. It is discriminating and states both failure shapes and how to tell
them apart — (a) it does not resolve at all (echoed as prompt text / unknown command: the original
bug), (b) it resolves from a root other than `.omp/commands/`, distinguished by adding a marker line
to `.omp/commands/harness-plan.md` beforehand and seeing whether the door honours it. ~1 minute.
Only the operator writes PASS/FAIL.

Deleted the superseded gap bullet ("REQ-09's *actually reachable through OMP* has no criterion of any
method that requires the OBSERVATION …") in full, through "stays with the operator as an open
question at signature." It would now assert a falsehood about the project's own plan.

**Minimum correction to the preceding gap bullet**, which SC-15 also falsified: its title became
**No AUTOMATED gate proves a door is DISCOVERED by a provider**, and its final sentences now read
"gated by SC-15 (`uat`), which is required and blocks the ship decision, but which no runner can take
over: `.omp/config.yml` cannot be exercised by a test in this repository." The previous wording
"recorded in the UAT notes, not gated" is what changed; the SC-13 sentence is untouched. The other
five gap bullets are byte-identical.

## `notes/uat-FEAT-56.md` — spent, LEFT UNTOUCHED

It is a record of a prior cycle, not the live script for this revision. Three independent signals:
`covers: SC-09 (the only verify: uat criterion)` and SC-09 is STRUCK; `review_sha: 62debeaf` predates
the replan; and its setup reads `git show 62debeaf:.claude/skills/harness-init/SKILL.md` as a
419-line blob with Track B still in it and quotes line anchors from that blob (U-01 cites "lines
153–186 `### 2. Land harness.json, then register the repository`"), a document this plan deletes.
Adding an SC-15 step to it would graft a live step onto a stale pin. The live UAT for this revision —
covering SC-11, SC-12 and now SC-15 — is written fresh at ship time against the real `review_sha`.

## Change 3 — the cascade, recorded OPEN as D-13 (no task, no file edits)

`cli_min_version: "2.1.217"` survives at `.harness/harness.json:3`, `.harness/team-config.yaml:11`,
`.agents/skills/harness/templates/harness.json:4`, `templates/team-config.yaml:21`,
`templates/examples/harness.kaya-ai.json:4`, and as reasoning in `BUILD.md` and in **DEC-83, a signed
decision**. D-13 records the open question — with no onboarding step reading it, is the key still
meaningful for Claude Code runs or is it dead config — points at DEC-83, and marks it explicitly as
the operator's to decide. **pm's recommendation, one sentence:** keep the key and amend DEC-83 to say
it is a documented Claude Code compatibility floor that no gate enforces, rather than deleting a
value six files and a signed decision still reference.

## Evidence

**1 — plan integrity.**
```
$ env -u HARNESS_AGENT_TYPE python3 -c "import yaml;d=yaml.safe_load(open('.../plan.yaml'));print(len(d['tasks']),[x['id'] for x in d['decisions']],d['approval'])"
17 ['D-01', 'D-02', 'D-03', 'D-04', 'D-05', 'D-06', 'D-07', 'D-08', 'D-09', 'D-10', 'D-11', 'D-12', 'D-13'] {'status': 'pending'}
```

**2 — T-11's amended `verify` run VERBATIM from the worktree root, observed RED.** The file run is
byte-identical to the stored value (checked by reloading `plan.yaml` and comparing: `IDENTICAL`).
```
$ bash /tmp/feat56/t11_verify.txt; echo "EXIT=$?"
EXIT=1
```
The whole chain short-circuits at clause 2 (`! grep -q 'Track A'`), so the two NEW clauses were also
run in isolation against the live file — this is the proof that they discriminate, not the chain's
exit code (O-04):
```
$ F=.claude/skills/harness-init/SKILL.md
$ ! grep -qF 'claude --version' "$F"; echo "no-probe-clause EXIT=$?"
no-probe-clause EXIT=1
$ ! grep -qF '2.1.217' "$F"; echo "no-floor-clause EXIT=$?"
no-floor-clause EXIT=1
$ grep -nF 'claude --version' "$F"; grep -nF '2.1.217' "$F"
34:claude --version
40:- **CLI < 2.1.217** → below the floor for the spawn env vars. Stop; the depth setting will not take.
```
Both new clauses are RED today and both anchors re-confirmed at `:34` and `:40`.

**3 — SC-15 in full and the remaining `## Verification gaps`:** `BRIEF.md:256-268` and `:270-299`.
The superseded bullet is gone; five gap bullets remain, four byte-identical and one minimally
corrected as described above.

**4 — other sites asserting the removed strings:** the T-10 intent sentence (fixed); `none` beyond it.
`plan.yaml:320` panel finding noted, not edited.

**5 — routes.**
```
$ env -u HARNESS_AGENT_TYPE python3 .../check-plan-routes.py .../plan.yaml
... OK T-01..T-17 ...
0 violation(s) across 1 plan(s)
EXIT=0
```

## Open questions

- **Q1 (non-blocking):** the `cli_min_version` cascade — D-13. The operator's, at signature.
- **Q2 (non-blocking):** `plan.yaml:320`'s cycle-1 panel finding text now describes a state the plan
  no longer holds. It is a record of what a reader said and was left alone; if the panel record
  should carry a `disposition` noting the operator superseded it, that is the main session's write
  into `approval.rulings`, not pm's.
