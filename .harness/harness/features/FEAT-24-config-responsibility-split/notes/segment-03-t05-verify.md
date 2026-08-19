# Segment 03 — T-05's tests are real but named wrong, and two per-key cases are missing

## Outcome

The qa gate — this project's only blocking gate — returned **FAIL**, and it is right to, for a
narrower reason than it gave. **T-05's `verify:` block fails at its first assertion.** Until it
passes, the build is not done, simplify does not run, and the panel does not run.

**The file is `test-check-state.py`, which is T-05's — `execution_mode: main-session-direct`, a
DEC-174 carve-out. It is yours by hand; no agent may write it.**

## What is actually true — I measured all of it rather than relaying qa

**Your three cases exist, run, and PASS.** `test-check-state.py` exits rc=0 and emits:

```
ok - (v.13) a board missing `stations` is REPORTED, naming the offending key, and the gate still completes
ok - (v.14) an explicit null board records NOTHING — not a violation, and no traceback
ok - (v.15) a done card in this board's OWN `done` column (Shipped) is not a violation — the expected column is read from the declaration
```

**So qa's headline is wrong.** It claimed T-05 "never got its own required test cases written" and
that SC-12 has "zero automated evidence". Both are false: v.13 asserts exactly SC-12's behaviour —
reported, naming the key, gate completes. I am recording that correction because the record is what
every later reader trusts.

**But qa's FAIL is correct.** T-05's approved `verify:` requires **five** ok-lines, matched with
`grep -qxF` — exact, whole-line, after stripping the `ok - ` prefix. None of your three matches, and
two of the five have no case at all.

| Required by the approved verify | Present? |
|---|---|
| `INV-26 reports a violation when the board declaration is unusable` | no — v.13 says it differently |
| `INV-26 completes the gate rather than aborting on an unusable board` | no — v.13 folds it into the same case |
| `INV-26 expects the declared station for status: backlog` | **no case at all** |
| `INV-26 expects the declared station for status: building` | **no case at all** |
| `INV-26 expects the declared station for status: done` | v.15 covers this behaviour, named differently |

**The missing two are not a naming problem — they are a coverage shortfall**, and it is this
feature's own recurring defect: a clause quantifying over N keys with fewer than N fixtured. One
case for `done` cannot see a `backlog` lookup that was never migrated. The verify was written to
demand one per key precisely because of that.

## CORRECTION TO MY OWN EARLIER READING — and it is this feature's signature defect

Above I wrote that the INV-26 block is clean of station-name literals. **That reading was worthless
and I am striking it.** T-05's verify slices `sed -n '/INV-26 BEGINS/,/INV-26 ENDS/p'`, and those
markers **do not exist** — `grep -c 'INV-26 BEGINS'` returns **0**, same for `ENDS`. The slice is
therefore EMPTY, and an empty slice trivially contains no literals. I read "no matches" as "clean"
when it meant "nothing was searched". That is precisely the vacuous-grep failure this feature exists
to remove, committed by me, in the middle of reporting on it. The qa lead caught it and was right.

The verify's own positive control exists for this: it requires `derive_station` to appear in the
slice before the literal greps are trusted. With no markers it fails loudly — which is the design
working, and is why T-05's verify can never reach green today.

## What the edit must do — TWO parts, not one

### Part A — `check-state.sh`: add the two markers (this is what the intent's item 7 asks)

A line containing `INV-26 BEGINS` immediately above the existing `# --- INV-26 (issue #277)` comment
at `check-state.sh:1100`, and a line containing `INV-26 ENDS` immediately after the block's last
statement. Without them the slice is empty and every literal-absence grep below proves nothing.

### Part B — `test-check-state.py`: the five ok-lines

1. **Split v.13 into two cases** carrying the first two ok-lines verbatim — one asserting the
   violation is REPORTED and names the offending key, one asserting the gate COMPLETES rather than
   aborting. They are separate properties and the verify wants them separately visible.
2. **Rename v.15** to `INV-26 expects the declared station for status: done`.
3. **Add two cases**, `backlog` and `building`, each asserting the expected column is read from the
   board's declaration for that key — the same shape as `done`, one per key.
4. **Keep v.14 exactly as it is.** The verify does not name it, and it is load-bearing: it is what
   stops v.13 being satisfied by an invariant that reports every board it sees.
5. Each new or split case proven able to fail, with the mutation asserted as applied — the same
   discipline you already used for v.13/v.14/v.15.

The remaining verify clauses already pass: the positive control finds `derive_station` in the
INV-26 slice, and no station-name literal survives inside it. I checked the block myself — an
earlier count of mine that suggested a stray `Done` literal was my own sloppy slice, not the code.

## Verify

`plan.yaml` T-05's `verify:` block, verbatim, from the repo root. It currently prints
`T-05: the unusable-board case did not pass or did not run`. It must print `T-05 GREEN`.

## What is running while you do this

One eng fix, on `test-factory-gh.py` only: closing the `validate=True`/`validate=False` fail-open qa
found and could not close itself. Discriminating fixture `aGV!sbG8=` — raises under one mode,
silently decodes to `b"hello"` under the other. It cannot collide with your file.

## Then

Matrix re-check → four-angle simplify → re-pin `review_sha` → review panel → pm's goal-check on all
13 SCs → close-out and the ship briefing.

## Three more findings from the same gate, ranked

- **SC-02 `ready` is non-discriminating.** `test-factory-decompose.py:413` asserts the DEC-192
  literal itself, so a reverted lookup for `ready` still passes. Re-fixture to a non-DEC-192 value.
  A team dev can do this — it is not a carve-out file. AFTER your T-05 edit, so the suite has one
  moving part at a time.
- **`integration.detect` in `harness.json` is stale.** It names 4 files while `INTEGRATION_SCRIPTS`
  runs 12, so under a literal reading T-02 could never satisfy its required kind whatever tests it
  had — a rule that makes a `change_type` unsatisfiable by construction. qa ruled `matrix_ok: true`
  on whether the kind's command exercises the changed paths, which is the right substance. One-line
  config fix, not a test-writing loop.
- **A third falsified statement stands, and no criterion names it.** `DECISIONS.md:6090` — DEC-196's
  own `##` heading still reads "and its own board declares no stations", which T-06 falsified. An
  amendment body cannot reach a heading and DEC-188 forbids a quiet rewrite, so retitling with a
  strike record is a decision-level act and yours. SC-11 is met as written either way — it names the
  two paragraph statements and both carry amendments. **Recommend taking it:** T-10 exists because
  there is no propagation checker, so a falsified statement left standing after it is the exact
  failure DEC-188 describes.

## The gate's own self-correction, recorded because it is the healthy kind

qa published a claim mid-run that SC-02's five keys were covered with discriminating values, then
retracted it: it had inferred coverage from `plan.yaml`'s spec instead of measuring the test file —
the same substitution the gate exists to catch. It said so in its own return rather than letting it
stand. That is the record working.

