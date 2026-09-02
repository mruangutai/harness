# FEAT-53 metrics dashboard — plan signature review, pass 2

**Your five rulings are applied and hold up under a second adversarial reading. The plan is not
signable yet, for two reasons that both need one word from you.** The new panel found one high
finding, and the cycle-time question you sent to the backlog turns out to gate the signature rather
than follow it.

Nothing you confirmed as drafted was reopened. `D-20` (the client build) and `D-08`/`T-18` (the
TanStack Charts alpha, Shape B built this increment) are byte-unchanged, and both panel readers
re-walked them without raising anything new.

**How this briefing was assembled.** I spawned no reporting round. I read three run digests off
disk — `runs/2026-09-01-07-product/digest.md` (the remediation), `runs/2026-09-01-08-validator/digest.md`
(the cycle-2 panel) and `runs/2026-09-01-09-product/digest.md` (the panel record) — plus the
findings prose in the panel digest and the plan itself. Everything from the earlier phases stands as
written in the first briefing, `notes/ship-review-2026-09-01-plan.md`; I have not re-narrated it
here. Where I state something as measured, I measured it myself against `plan.yaml` on disk.

---

## What your rulings changed

**DEC-1, the framework — done.** `D-03` now reads *"The server is a real web framework — Flask, one
WSGI application object in dashboard/serve.py"* and rejects FastAPI plus uvicorn, a Node server and
the stdlib `ThreadingHTTPServer` **by name, with a reason each**, in its own `because:`
(`plan.yaml:52-53`). Flask was picked because the whole KPI core is Python — a Node server would
mean porting six modules or paying an interpreter start per request against a 3.6s budget — and
because `send_from_directory` supplies the traversal-safe join and the mimetype lookup the `/assets`
route was going to hand-write. `T-12`'s prerequisite gate names Flask and `python3 -m pip install
flask`; the loopback-only bind, the read-only guarantee, port 8971, `--check`, the Content-Type
table and the 8.0s ceiling all survived the rewrite intact.

One judgement inside that, recorded so you can overrule it: **Flask is a dashboard-only
prerequisite, not a ninth platform prerequisite.** Nothing in `bin/` outside `bin/dashboard/`
imports it, so declaring it platform-wide would make every onboarded project install a framework the
factory never calls. `T-22` installs it in *this* repository's CI job, and says in as many words that
this is a claim about this repository only.

**DEC-4 / `PF-328f8f3c` — done.** New `D-21` makes "post-instrumentation" computable rather than
rhetorical: `.harness/metrics/instrumented_at` holds one RFC3339 instant, a feature's start is its
`approval.date` or the author date of the first commit adding its directory, and a measured zero
requires both to exist with start ≥ epoch. Everything else is null plus one of `D-19`'s specific
sentences. `SC-17` asserts both branches separately.

**DEC-4 / `PF-7408d83a` — done.** `T-21` mounts the charts inside the panels and `T-22` makes that
assertion reachable from `run-unit-tests.sh` and CI. The gate executes a real render and grades
per-case status, after the first draft was sent back for being green on a skipped test.

**DEC-5, the prototype — ready for you.** The designer found the prototype still carried the retired
two-term aggregate, and it was fixed rather than noted, because what you open at the gate is the
prototype. It now renders a measured `0` beside `— unavailable · this feature predates touchpoint
instrumentation` **on identical input** — neither feature has a touchpoints file, only their start
dates differ. 37/37 smoke checks, a clean build and a dev server, all executed. It is at
`notes/prototypes/FEAT-53/`. This gate is still open: nobody but you can close it.

---

## What needs your decision now

### 1. One high panel finding — the ordering gap that would undo DEC-4

`T-16` builds and commits the production `dist/` bundle and depends only on `[T-12, T-15]`, while
`T-21` — the task that mounts the chart — depends on `[T-14, T-15]`. They become ready at the same
point of the graph, in different lanes, and **no task after `T-21` ever rebuilds the bundle.** So the
bytes a user actually receives from `serve.py` can be the ones built before the chart was mounted,
reproducing exactly the failure you ruled must be fixed — while `T-21`'s and `T-22`'s render
assertions stay green, because they exercise source through the test renderer and never the built
artifact.

The remedy is one line: add `T-21` (or `T-22`) to `T-16`'s `depends_on`. I did not apply it. A panel
finding never opens its own pre-signature fix cycle (DEC-207), and only you resolve or overrule one.
**Say "fix it" and it is one pm dispatch.**

### 2. Cycle-time origin — `B-6` gates the signature after all

You accepted `B-6` as a backlog issue. Working the plan showed why it cannot wait: the grilling
(line 26) and `REQ-03` both say cycle time runs **from BRIEF approval**, while `D-14`, `T-06` and now
`D-21` measure **from `plan.yaml` approval.date**. You are about to sign a BRIEF whose `REQ-03` the
plan knowingly does not implement.

- **Option A — match your words.** Nothing records a BRIEF approval date machine-readably today, so
  `D-14`, `T-06`, `D-21` and the trend record all change and a new dated field has to be captured.
- **Option B — keep `approval.date`,** buildable as it stands, and **reword `REQ-03`** so the BRIEF
  states what will actually be measured. Nobody reworded it to close the gap quietly; pm was
  explicitly told not to.

Either way this is one decision and it is yours. `B-6` then becomes redundant and should be struck.

### 3. Four lower findings — accept as backlog, or fix now

Same convention as last time: **strike a row by ID and it dies; anything not struck becomes a backlog
issue labelled `Dashboard`.** The ten rows you already accepted (`B-1`..`B-10`) stand as accepted.

| ID | Sev | Finding | If you fix it now |
|---|---|---|---|
| B-11 | med | `D-21`'s runtime files have no git disposition. `.harness/metrics/` matches no ignore rule, so the first `record()` call dirties the tree — the exact deadlock class `.harness/.pyyaml-bootstrap` is ignored to prevent. And with the epoch uncommitted, a **second clone** loses it, writes a later one, and a feature starting after that reports a measured zero — the fabricated zero you ruled out. `D-21`'s risk note covers worktree loss, which is genuinely safe; it does not cover a clone. | An ignore rule plus a stated disposition. The ignore file is `main-session-direct`, so it is your hands or mine, not a squad's |
| B-12 | med | The ~250 lines of stale `#` comments that a tool defect spliced into `plan.yaml` (see below) **contradict the live YAML twice** — they claim no task touches `tests.yml` for Flask (`T-22` does, `:1168`), and they quote a weaker `T-21` verify than the one that shipped. A reader trusting them would undo both fixes | Not removable by any sanctioned verb today. Needs the tool fix first |
| B-13 | med | `SC-17` declares `evidence: integration`, but its "aggregate reports the not-tracked count by name" clause is asserted only in a unit-registered script. A coverage matrix reads it as covered; an integration-only run — which is what CI splits out — asserts nothing for that clause. Same shape as the already-backlogged `B-4`, on a criterion authored this cycle | One evidence-kind correction |
| B-14 | low | `T-12`'s 8.0s ceiling is vacuous where it runs mechanically: CI checks out shallow and single-ref, so the timed case has no feature branches and a depth-1 history — it measures the fast unavailable branches, not the real cost, while every PR pays a whole-repo grader run forever. `D-09` stakes its no-cache deferral on that ceiling staying falsifiable | Scope the timing case to a run with real history, or make it report-only |

---

## Harness defects found this pass

Not about this feature. Each cost real time here.

1. **`plan-merge.py apply` splices a proposal's trailing comment block into `plan.yaml`** and **no
   verb can remove it** — `_trim_tail` treats trailing comments as document, `apply` never deletes,
   and the shape gate blocks every editor including yours. `safe_load` is unaffected and no gate
   flags it, but `B-12` is the consequence: unremovable stale prose inside an approval-gated
   artifact.
2. **A feature worktree vendors `.claude/skills`,** so a `bin/` verb added after the worktree
   branched is unreachable in-tree: this checkout's `plan-merge.py` exits 2 with `invalid choice:
   set-panel`. pm ran the main checkout's copy by absolute path — same tool, same lock, same single
   write route. Any skill telling an agent to run a `bin/` tool from inside a worktree shares this.
3. **BUG-1080 reproduces on the return path.** `validate-digest.py` rejects every `code_grade` value
   for a plan-phase feature with no `review_sha`, so the scope reader could not terminal-yield at
   all; its verdict and artifact were recovered from disk. The plan-phase exemption exists on the
   input path and is missing on the yield path.

Two smaller ones, for the record: `set-panel` refuses a `panel:`-wrapped value file with a message
naming missing keys rather than the wrapper; and the two superseded validator digests from cycle 1
(`01-validator`, `05-validator`) still fail the lead digest contract in `check-state.sh`, because a
digest is immutable once written.

---

## Budgets, honestly

**Eleven runs against an informational budget of 20; six rework cycles against a hard 10.** Two of
this pass's cycles were real rework and both earned their place: pm's own goal-check failed its own
cycle-1 work and closed five defects before anything left the squad, and the panel then found a sixth
that no gate in the plan could see, because it is a property of the task graph rather than of any
file. The remaining four trace to the FEAT-51→53 renumbering and the write-route defect, as recorded
in the first briefing.

The one thing I will not dress up: **two readers is a thin panel for a 22-task plan.** The evidence
that they read rather than skimmed is that each found a defect the other missed while both
independently found the same contradiction. That is convergence, not coverage.

## What I need from you

1. The high finding — **fix, or overrule.**
2. Cycle-time origin — **Option A or Option B**, and if B, `REQ-03` gets reworded before you sign.
3. `B-11`..`B-14` — **strike any, or accept all as backlog.**
4. **Open the prototype** (`notes/prototypes/FEAT-53/`) — DEC-5 is still open and only you can close it.

Then the main session signs `BRIEF.md` and `plan.yaml`, and the build phase starts.
