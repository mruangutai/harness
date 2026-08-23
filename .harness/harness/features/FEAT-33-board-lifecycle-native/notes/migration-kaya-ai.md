# Migration report — board 2, mruangutai/kaya-ai

Date: 2026-08-23. Board **2** (`mruangutai/kaya-ai`). Run from the harness worktree, reaching
kaya-ai over the API — `factory_config.product_config` reads a served repo's config from the
REMOTE at default branch, never from a checkout. The kaya-ai checkout was not touched and
`factory/issue-334` was not moved.

## Outcome

**29 findings → 11 real findings → 0 findings.** `audit` exits **0**.

Unlike board 3, this board genuinely reaches zero: nothing here needed a human.

| | count |
|---|---|
| first audit | 29 |
| **of those, FALSE** | **18** |
| real, after the #783 fix | 11 |
| fixed by `reconcile --apply` | 11 |
| **remaining** | **0** |

## THIS RUN FOUND A DEFECT AND STOPPED. That is the headline.

The first audit reported 29 findings, **18 of them false**. Example:

```
STATUS: .../FEAT-26-pr-linkage-recorded records status 'Done' but its parent #732 reads None
```

`#732` is a **`mruangutai/harness`** issue — `gh issue view 732 --repo mruangutai/kaya-ai` returns
"Could not resolve to an issue". The STATUS class was walking this checkout's own features and
comparing their parents against **kaya-ai's** board. Every harness feature produced a finding.

**Board 3 could not expose it**, because there the features on disk ARE the audited repo. T-11's
run was clean. Only a second repository shows it — which is precisely why the plan ordered the live
runs after the fake-`gh` tests.

`reconcile --apply` was NOT run against the broken class. The task stopped, the defect was filed as
**#783**, and T-15 was reopened.

**Nine mutation-proved assertions in these files could not see it.** No fixture audited a
repository whose features were not the ones on disk. The guard now exists, and building it cost
more than the fix: it required teaching the fake `gh` a network endpoint it had never needed.

**The fix is a self-skip, and the alternative was declined on evidence.** Scoping STATUS to
features whose recorded repo matches the audited one was *invented, not available* — no
`feature.json` carries a `github.repo` field, and a served repo's config is read remotely, so there
is no local directory to filter. STATUS now runs only for this checkout's own repo and prints one
honest line otherwise.

**`reconcile` shared the leak** and inherited the fix, both calling `_audit_findings`. Proved with
a dry-run-only fixture rather than assumed.

## The discriminating pair

| board | before fix | after fix |
|---|---|---|
| 2 (foreign) | 29, incl. 18 false STATUS | 11, one skip line, **no false STATUS** |
| 3 (own) | 2 | **2** — STATUS still runs |

A fix that silenced STATUS everywhere would look identical on board 2 and wrong on board 3.

## The 11 real findings, all fixed

**Six STATION** — closed issues sitting at `Building` that should read `Done`: #297, #296, #152,
#83, #49, #31.

**Five LABEL** — `not_planned` with no `abandoned` label: #214, #154, #105, #75, #2.

## What was correctly NOT a finding

**kaya-ai's 82 untriaged `Backlog` items produced zero findings**, as the plan required. Only closed
issues at the wrong station, closed issues with a null reason, and `not_planned` issues without the
label are findings. Had open Backlog items been reported, this task was instructed to stop.

No DECLARATION finding: T-01's six-key declaration is correct on kaya-ai's master.
No REASON finding. No WORKFLOW finding — all three required workflows are enabled on board 2.

## Final audit

```
board_lifecycle: workflow detection matches by NAME only -- ProjectV2Workflow exposes neither trigger nor action, so a workflow the operator renamed is reported MISSING rather than assumed present
board_lifecycle: STATUS: skipped -- auditing 'mruangutai/kaya-ai', not this checkout's own repo ('mruangutai/harness'); this checkout's on-disk features are never that repo's
board_lifecycle: 0 finding(s)
```

## How this is verified, stated plainly

The tool's **logic** is proven by T-04 through T-06 and T-15's unit tests against a fake `gh`. What
this task adds is the **live outcome**, which no runner in this repository can reach. It is carried
by the captures beside this file and by **SC-11, which the operator runs**. SC-11 stays `not_met`
until they do.

`grep -q "0 findings"` on this file would be satisfied by typing the string, so the verify has been
corrected to assert the live audit's exit status instead.
