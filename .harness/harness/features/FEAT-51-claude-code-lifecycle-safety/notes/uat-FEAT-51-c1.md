# UAT — FEAT-51 Claude Code lifecycle safety (SC-10)

**Historical procedure, ~35 minutes.** This was not run in Claude Code and supplies no pass
evidence; the criterion was withdrawn instead.

**Status: withdrawn 2026-09-02.** The operator explicitly chose to skip this Claude Code-specific
UAT and withdraw SC-10. The OMP pre-flight was not treated as a pass because it cannot exercise the
compatibility-host quarantine branch. The procedure below is retained as the historical test that
was offered, not as completed evidence.

**Run from the MAIN checkout AFTER merge**, `/Users/molchairuangutai/GitHub/harness` — a spawned
agent loads its skills from there, not from the FEAT-51 worktree (`BRIEF.md ## Verification gaps`,
DEC-201's measurement). Running it in the worktree measures the wrong tree.

Pick any live feature to act on and substitute it for `<FEAT>` below. `Q1` is the interesting one;
do it first, because a NO there makes the rest of the run informational.

---

## Step 0 — baseline, 3 min

```
cd /Users/molchairuangutai/GitHub/harness
shasum -a 256 .harness/harness/features/<FEAT>/BRIEF.md \
              .harness/harness/features/<FEAT>/plan.yaml \
              .harness/harness/features/<FEAT>/feature.json \
              .harness/harness/features/<FEAT>/STATE.md > /tmp/uat51-before.txt
cp .harness/.inflight-claims.json /tmp/uat51-registry-before.json
cat /tmp/uat51-before.txt
```

Four sha256 lines. If a file is missing, drop it from every later command rather than substituting
one.

## Step 1 — Q1: does the host resume the SAME parent? (most falsifying, ~15 min)

Dispatch any lead that will itself dispatch one member (a product-lead run with one pm dispatch is
the cheapest). **While the member is mid-run, interrupt the parent** (Esc). Then resume the
conversation and let it finish.

Watch two things, and write down what you saw:

- **In the transcript.** A RESUMED parent continues its own turn: it refers to what it dispatched,
  and it looks for the child's result. A REPLACEMENT starts the assessment from scratch, re-reads
  the brief, or re-dispatches the same member.
- **In the registry**, the durable half:
  ```
  python3 -c "import json;d=json.load(open('.harness/.inflight-claims.json'));[print(c.get('agent'),c.get('session'),c.get('claim_id'),c.get('feature')) for c in d['claims']]"
  diff /tmp/uat51-registry-before.json .harness/.inflight-claims.json
  ```
  **Resumption** = the parent's claim keeps its original `session` and `claim_id`.
  **Replacement** = a second claim appears for the same persona and feature under a DIFFERENT
  `session`.

**FALSIFIED if** you see a second claim for the same persona+feature under a different session, or
the post-resume turn shows no knowledge of the dispatch it made. Stop there and record `not_met`;
Steps 2-4 cannot rescue it.

## Step 2 — the orphan's result is quarantined, 5 min

The interrupted member finishes into a parent that is gone. It must write to quarantine, not to the
canonical file.

```
python3 .claude/skills/harness/bin/quarantine.py list --feature <FEAT>
```

**Expected:** at least one entry under
`.harness/harness/features/<FEAT>/quarantine/<persona>-<session8>/<basename>`.
**Failure:** empty output while the member reported it wrote its artifact — that means the write
went somewhere else. If the member never got far enough to write, re-run Step 1 with a longer member
task; an empty quarantine with no write attempted proves nothing either way.

## Step 3 — nothing canonical was overwritten, 3 min

```
shasum -a 256 -c /tmp/uat51-before.txt
```

**Expected:** four `OK` lines. **Failure:** any `FAILED` line — the orphan reached a canonical
artifact and SC-10 is `not_met` regardless of Steps 1-2.

## Step 4 — nothing becomes canonical until YOU adopt, 5 min

Re-run Step 3's `shasum -c` after the run has fully settled (still four `OK`). Then, and only then:

```
python3 .claude/skills/harness/bin/quarantine.py adopt \
  --file .harness/harness/features/<FEAT>/quarantine/<persona>-<session8>/<basename>
shasum -a 256 .harness/harness/features/<FEAT>/<basename>
```

**Expected:** the hash changes only at this command, and the adopted content is merged onto the
canonical file, not substituted for it (for `plan.yaml`, the pre-existing tasks are all still there).
**Failure:** the hash had already changed before you ran `adopt`.

---

## `PF-e380f685c0697fb709ff29f65af0cf24` — does this UAT answer it? **No.**

The question is narrower than this script: *does the host re-enter a parent that returned exit 0
from its Stop hook with a live child claim?* Step 1 measures **operator-driven** resumption after an
interrupt. That is what SC-10 asks for, and it is not the same event — you supplied the re-entry.

What would answer it: a single run in which a lead returns `VERDICT: SUSPENDED`, its Stop hook exits
0 with the child's claim live, **and you touch nothing**. If the parent's next turn arrives with no
input from you, the assumption holds; if the host ends the session, or a fresh parent is dispatched,
nine tasks rest on a false premise. That is backlog item `B-4`, one run, and it is worth buying
separately. If you want it in the same sitting, do it BEFORE Step 1 — it is cheaper and strictly
more falsifying.

## Verdict

```text
SC-10: withdrawn     date: 2026-09-02     Q1 observed: not reached in Claude Code
```
