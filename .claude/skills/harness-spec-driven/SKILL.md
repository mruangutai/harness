---
name: harness-spec-driven
description: Planning discipline for the product manager — every task fully specified with paths, intent, verification and traceability; no placeholders; perspectives separated from decisions. Loaded by harness-pm.
user-invocable: false
---

# Spec-Driven Planning

**`plan.yaml` is REAL YAML, and nothing in it is prose for a human** (DEC-182). Instantiate from
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/templates/plan.yaml`.

**Every write goes through a `plan-merge.py` verb. There is no other route** — updates are
locked and validated before landing; the shape gate denies `Edit`, `Write` and shell redirects
(DEC-182).

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py apply \
  --file <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/plan.yaml --proposal -
```

**No markdown in any value — no backticks, no `**bold**`, no links.** The loader rejects it or a
resolver reads it as a path nobody wrote (DEC-182).

Shipped `PLAN.md` files are never rewritten; their reader stays.

## Every task needs four things

`harness_yaml.py` (`REQUIRED_TASK_FIELDS`) refuses a task missing any required field and names
it; the four below are what those fields must CONTAIN. A task missing any is **not written**:
return the gap rather than guess.

1. **Exact file anchors**, as a YAML list, one entry per file, each one of four forms: `path`;
   `path#symbol`; `{path: <p>, quote: <q>}`; or `{path: <p>, create: true}` for a new file whose
   directories do not exist yet (a greenfield tree — a bare `path` still needs its directory).
   **Never `path:NN`** — a line number points at
   different code the moment `main` moves; `apply` refuses it (DEC-232). Not a comma string, not
   backticked, **no trailing annotation** like `(delete)` — the resolver takes the value verbatim.
   **A task owns its files.** Slice work across many files by file ownership — each file in
   exactly one task — or keep it as one task with a per-file checklist; never as layers over
   shared files, because each layer's gate then runs against a tree the next layer will move.
   A whole-tree `verify:` belongs to the LAST task that touches those files, or to validate.
   `plan-merge.py check` prints one `OVERLAP <path>: T-a, T-b` line per shared file; treat
   each as a question to answer, not a line to ignore (BUG-1725).
2. **Complete intent.** `intent:` is the LITERAL DISPATCH PROMPT: the doer receives it and nothing
   else about the task. Specify the actual logic, types, structure and values; detail that only
   JUSTIFIES the instruction belongs in `notes/`. Reject `TBD`, `TODO`, vague verbs without
   targets, "similar to above", "follow the existing pattern", and "implement X" without saying
   what X produces. If you cannot fully specify the task, the *brief* is incomplete: do not write
   the task; raise the gap in `open_questions`, never guess.
3. **A `verify:` command** with the expected result: under 60 seconds, unambiguous pass/fail, no
   human interpretation. If nothing automated is possible, write
   `verify: MANUAL — <what must be built first to make this automatable>` (em dash) — while the plan
   is `pending`, `harness_yaml.load_plan` refuses any other unautomatable-looking `verify:` shape.
4. **`traces:`** — the `SC-NN` ids this task serves, as a list. No citable criterion means out of
   scope or an incomplete brief; an SC nothing traces to is an orphan the `scope` reader hunts.
   `D-NN` goes in `decisions:`, not here.

Plus **`change_type:`** on every task: the qa gate reads it to determine required tests.

## Routing is resolved at plan time

Every task carries `execution_mode:` — `team` or `main-session-direct`; the loader refuses any
other value — with `execution_agent: <persona>` for `team` or `execution_reason: <why>` for
`main-session-direct`. **A task that needs BOTH routes is TWO TASKS**; there is no split mode
(DEC-182). An ungranted surface is a **declared** main-session step with its ordering constraint
written down (DEC-179).

Every plan opens with a `lanes:` block, resolved against
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/team-config.yaml` at a named SHA.

**Before handing a plan back, run
`python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py check --file <plan path> --root <harness checkout>`
and fix every FAIL line.** It resolves every `files:` anchor, `execution_agent` route and
`traces:` id; CI re-runs the route check on `main` (DEC-183). A served repository's plan
(`.harness/<repo>/features/`) also takes `--code-root <code worktree>` — the `CODE` line of
`feature-worktree.py path` — and its anchors resolve there; `check` refuses it without one.

## `verify:` is a literal block, and this one has teeth

Write `verify:` as a literal block `|` or a single-line plain scalar, **never a folded `>`**. The
lead carries the string **verbatim** to the member, which cross-checks it against the plan and
returns `BLOCKED` on any mismatch (`harness-zero-micro-management`); a folded scalar loads as a
different string, so a correct task blocks.

## The panel result

`plan-merge.py record-panel` writes `panel:` from the lead's digest. **You never transcribe a
panel by hand and never edit a finding's severity** (DEC-229); read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/panel-recording.md` when the
digest lands.

## The D-NN bar (DEC-149)

A choice earns a `D-NN` (`plan.yaml decisions:`) — and the user's attention at approval — only
when ALL THREE hold: **hard to reverse**, **surprising without context**, **a real trade-off**.
Anything failing one is a digest note. A rejected alternative a future scan would re-suggest is the
classic D-NN — record the reason. A perspective is not a decision; `harness-brief` has the test.

## The glossary

`<HARNESS_CONTROL_PLANE_ROOT>/.harness/glossary.md` is the ubiquitous language — challenge drift
before it lands in a perspective, code wins over a stated meaning (DEC-149;
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/glossary-stewardship.md`).

## Citations and baselines rot — anchor them so they cannot

- **Cite the FIELD or the SYMBOL, never the line**: `feature.json github.parent`, not
  `feature.json:41` (DEC-232).
- **A recorded baseline carries the sha it was observed at, and the condition**: `observed exit 1
  at <sha>, BRIEF pending` — the signature itself can change the answer.

## Approval is not yours

pm authors the pending proposal; `apply` seeds a new plan's YAML `approval:` mapping with only
`status: pending`. Only the **main session**, on the user's explicit signature, invokes
`sign-approval` to write `approved`, `approved_by` and `date`; the rework ruling and
`approval.rulings` risk acceptances are theirs too (DEC-120, DEC-226). Neither pm nor the
orchestrator approves. Main alone may invoke `revoke-approval` on the operator's word (DEC-229).

A task-set-changing verb after signature resets `approval.status` to `pending`, records
`reset_at`, `reset_reason` and transient `resume_station`, and pauses the feature at Plan.
Reapproval consumes the transient metadata and emits the `RESUME:` receipt (DEC-229).
`approval.rulings` each name a current `panel.findings` PF-id, with `who`, `date` and a
one-clause reason; an absent id is refused, so reworded findings require fresh risk acceptance.

Capture and print stdout from every task-changing `plan-merge.py` invocation. Only when the
captured output contains its exact `APPROVAL-RESET:` receipt, run
`gh-sync.py status <feature-dir> plan` after the local reset has landed. No `APPROVAL-RESET:`
receipt means no remote call. This applies to `apply`, `add-tasks`, task-changing `amend`, and
`delete-items --task`; it never guesses from the verb or from the prior approval state.

