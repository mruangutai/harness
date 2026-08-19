# Layer-0 segments — FEAT-27, the three tasks no agent may execute

**BLUF.** Three of this plan's six tasks are `main-session-direct`. They are not blocked, not
deferred and not a defect — the domain guard resolves their surfaces to NOBODY or to six different
owners, so there is no doer to dispatch. They are yours to execute directly, in the order below.
The other three tasks run as squad segments and are the orchestrator's.

Do not hand any of these to an agent. A dispatch would be correctly refused mid-run, and the
refusal costs a spawn and loses the work.

## Order, and why it is forced

| # | Task | Surface | Why layer 0 | Unblocked by |
|---|---|---|---|---|
| 1 | **T-01** | `.harness/team-config.yaml` | `check-domain.sh --resolve` prints `NOBODY`, and the file is the enforcement data `check-domain.sh` itself reads | nothing |
| 2 | **T-04** | 6 craft + 6 repository Expertise files | granted to six different owners; three of them (a lead, a reviewer, the orchestrator) are not dispatchable task executors — D-03 | T-01, T-03 |
| 3 | **T-06** | `harness-distill/SKILL.md`, `harness-curate/SKILL.md` | under `.claude/` only `skills/harness/bin/**` is granted to anyone | T-03, T-04 |

T-03 is the orchestrator's and lands before this batch is handed over, so at handover all three are
unblocked in exactly this sequence. **T-04 must not start before T-01 lands**: nothing resolves
`.harness/harness/expertise/` until T-01's grant exists, so the write would be denied.

## Where the instructions are — read them from the plan, not from here

Each task's `intent:` is the executable specification and each `verify:` is its gate. **They are
deliberately not copied into this note.** A second copy is a copy that can drift from the approved,
signed artifact, and the intents run to 40+ lines apiece with byte-exact strings in them.

Extract them verbatim:

```
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('.harness/harness/features/FEAT-27-expertise-repository-tier/plan.yaml'))
for t in d['tasks']:
    if t['id'] in ('T-01', 'T-04', 'T-06'):
        print('='*70); print(t['id'], '-', t['title'])
        print('--- FILES ---'); print('\n'.join(t['files']))
        print('--- INTENT ---'); print(t['intent'])
        print('--- VERIFY ---'); print(t['verify'])
PY
```

Run each `verify:` exactly as written, from the repository root, after its task's edits. All three
exit non-zero on an incomplete job and print a per-item `FAIL` line naming what is missing.

## What is verified, and what you must re-check

Verified by me on this branch at `253287f` (= `b4659cd` plus the signed-artifacts commit; no craft
file is touched by that commit, so the `b4659cd` measurements stand):

- **All sixteen of T-04's anchor strings resolve to exactly one line each** in their owning craft
  file — the eleven movers and the five stayers. Re-run the check before editing, because T-01
  lands in between and any Expertise write by any other session would move them:

```
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('.harness/harness/features/FEAT-27-expertise-repository-tier/plan.yaml'))
t = [x for x in d['tasks'] if x['id'] == 'T-04'][0]
print(t['verify'])
PY
```

  The `ROWS` table inside that `verify:` is the anchor list; each row is its own assertion, so ten
  conforming entries cannot green over the eleventh.

- **`.harness/harness/expertise/` does not exist yet.** T-04 creates it. Ten agents have no
  repository-specific entries — do **not** create empty files for them; an absent file is the
  correct state and the hook treats it as normal.

- **`.harness/expertise/` holds 15 craft files**, not 16. `harness-frontend-dev` holds a grant and
  has no file. T-01's sixteen sibling grants are counted from `team-config.yaml`'s grant lines, not
  from the files on disk — work from the grep, as the intent says.

## Three traps, each of which has already cost something

1. **T-01: one unquoted `#` inside a plain scalar has already broken this resolver.** `team-config.yaml`
   is loaded with `safe_load`; a space-`#` opens a comment inside a flow sequence. Keep every added
   comment *after* a value, never inside one. If T-01's verify fails with resolver errors rather than
   `FAIL` lines, that is the shape to look for first.

2. **T-04: do not reword any entry, in either direction.** The eleven are moved verbatim including
   continuation lines. A reworded entry cannot be checked against the anchors the verify uses, and
   rewording is a distillation act this plan does not authorise. Likewise **do not renumber the craft
   files** — a numbering gap is correct, `check-expertise.sh` requires the id prefix and not
   contiguity, and DEC-66 makes the ids stable references.

3. **T-06's `374`-entry figure is a historical measurement and is correct as written.** The tree now
   holds 413 entries across the same 15 files; the sentence names `ada8e99` precisely so it stays
   falsifiable. Do not "update" it to 413 — that would break the verify and misstate what was
   adjudicated.

## Commit disposition — leave it uncommitted

**Do not commit these three tasks.** The commit pen is the orchestrator's (DEC-153), and the
`[harness:t-NN]` commit, the `plan.yaml` status write and `gh-sync.py close-task` have to happen as
one ordered act per task — the parent card's station is *derived* from the plan's task statuses, so
recording `done` after `close-task` leaves the parent stuck in `Building` forever.

On resume the orchestrator will, per task: verify the diff against that task's own `files:` list,
run the `verify:`, commit `[harness:t-NN]`, set `status: done` in `plan.yaml`, then run
`gh-sync.py close-task`.

Two requests that follow from that, and from what happened earlier in this feature:

- **Re-dispatch the orchestrator in the same working session**, so the uncommitted work is not left
  sitting in a shared checkout.
- **Do not switch branches in this checkout while the work is uncommitted.** `HEAD` must stay on
  `feat/FEAT-27-expertise-repository-tier`. A branch switch mid-feature is what sent the signed
  artifacts commit to a chore branch earlier today.

## Mirror

Sub-issues are already open and their cards are the orchestrator's to move: T-01 #565, T-04 #568,
T-06 #570 (milestone 17, parent #494, adopted). Nothing to run here.
