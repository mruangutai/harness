# Goal-check — FEAT-31, gc1, at review_sha fcb8984

**Path note:** the dispatch named `notes/goalcheck-gc1.md`; `check-domain.sh` denies that path to
`harness-pm` and permits `notes/research-FEAT-*.md`. The guard is right, so the artifact lives here.

## BLUF — the goal is NOT met, and everything outstanding is the operator's

**12 of 14 criteria are met. Two are not, and neither is routable to a squad.** SC-10 (`verify: uat`)
and SC-15's behaviour half (`verify: uat`) require the operator. `gates.uat` is
`blocking_when_uat_criteria_exist` (`.harness/harness.json` `gates`, verified this run), so those two
block the ship independently of the qa gate and the review panel. Nothing here is a build defect:
the code, the config, the gates and the decision entry all landed in the reviewed tree.

**Grading basis, independent of qa.** Suites re-run at review_sha (working tree == fcb8984 except
`STATE.md`/`feature.json` bookkeeping): `--kind unit` exit 0 (187 PASS lines), `--kind integration`
exit 0, `--check-kinds` exit 0. `test-context-watch.py` 76/76, `test-context-watch-cli.py` 10/10,
`test-context-watch-hook.py` 20/20, `test-check-state.py`, `test-check-domain.py`,
`test-validate-feature-json.py` all exit 0. All content grades read `git show fcb8984:<path>`.

## Where I differ from qa

- **SC-09: qa said `not_met` at `ed62d74`; I grade it MET at fcb8984.** T-19 landed. DEC-159 at
  `DECISIONS.md:4004-4010` now states the mid-flight rule ("determines the nearest seam ... where no
  seam is reachable it writes a mid-phase handoff"), the false clause is rewritten in place ("the
  watchdog is no longer only a post-hoc audit", :3989), and the deferred **turn-count** nudge is
  explicitly separated from the **context-size** warning that shipped (:3994-3997). No `am.N` block
  inside the entry; `grep "mid-flight|mid-phase|nearest seam"` over the whole file returns hits only
  inside DEC-159 — one statement, one home.
- **SC-03/REQ-05 re-derived at a grown corpus.** `context-watch.py` with no argument printed **109**
  rows; my own independent glob of `~/.claude/projects/*/*/subagents/agent-*.meta.json` filtered on
  `agentType == harness-orchestrator` counted **109** of 2055. Exact agreement; the mechanism, not
  the constant, is what holds.
- **SC-01's live half re-derived by me, not inherited.**
  `verify-context-watch-live.py a0f553774aa86ca61` -> tool and independent recomputation both
  `current=186503 peak=186503 entries=190`, PASS. Independence checked at source: `importlib` in that
  script is used only to load a mutant **of itself** (:374-375); `context-watch.py` is reached solely
  by `subprocess.run` (:220).
- **SC-04 threshold re-derived:** 37 rows print `overage=`, the tool exits 1 with the warning naming
  current and threshold and "this advises only".

## SC-15 — the behaviour half does not discharge on the evidence offered

The live orchestrator's own report is **confounded, not merely imperfect**. `notes/handoff-build.md`
`## Next` names T-05 (eng-lead) and T-09 (product-lead) "as two separate runs in one message"; the
successor's first dispatch was T-05 to `harness-eng-lead` (`feature.json runs` `t05-eng`, then
`t09-product`). But the successor **also received a main-session dispatch naming T-05 and T-09**, so
the observation cannot discriminate the handoff from the prompt — and SC-15's premise is a successor
"given only the feature directory". The timing divergence (sequenced, not batched) is the lesser
issue. Composite: gate half **met** (`test-check-state.py` `(t10-b)` rejects an emptied `## Next`,
`(t10-red)` mutant differential 1 vs 0); behaviour half **not_met**; criterion **partially_met**.

## New finding, not among #663-#669 — for the operator

**DEC-159's enforcement paragraph still says `check-domain.sh` denies a handoff note ">40 lines"**
(`DECISIONS.md:3986`), while the same entry states the ~60 cap and both gates enforce 60
(`check-domain.sh:952`, `check-state.sh:664`). A falsified clause standing in the authority — the
DEC-188 shape, pre-existing, not introduced by this feature. Not filed as an issue (searched). It
does not fail SC-09, whose subject is the mid-flight case and the watchdog clause.

## What T-17's non-observability means for SC-13

SC-13's declared method is `automated / integration` and it is discharged by
`test-context-watch-hook.py` (20/20, exit 2, stderr channel, both directions, guarded red proof) plus
`H/I/J`. The hook **is** registered at review_sha (`.claude/settings.json:60`). What cannot be shown
pre-merge is delivery into a live orchestrator's context — hooks resolve via `CLAUDE_PROJECT_DIR` to
the main checkout. That is a limit on live evidence, not an unmet criterion: SC-13 never asked for a
live firing, and Q-HOOKCTX is closed. First live firing is a post-merge observation.

## REQ coverage

All ten REQs are cited by `traces:` in `plan.yaml` (REQ-01..REQ-10, each appearing on at least two
tasks). No dropped requirement.

## Outstanding, with owners

| Item | Owner |
|---|---|
| SC-10 — run the tool with no argument and with a live orchestrator named; answer all four questions from the output alone | operator (UAT) |
| SC-15 behaviour half — a successor given **only** the feature directory, no dispatch naming its tasks; grade its first dispatch against `## Next` | operator (UAT) |
| DEC-159:3986 ">40 lines" stale against the 60 both gates enforce | operator (docs) |
