# UI review — BUG-1309-mirror-build-entry — cycle 4 — pin `af132780`

## Scope decision

Measured census of the pinned commit's diff (`git show --stat af132780`):

```
.claude/skills/harness/bin/merge-gate.py |  5 ++++-
tests/integration/test-merge-gate.py     | 12 +++++++-----
```

(`.agents/skills/harness/bin/merge-gate.py` is the byte-identical mirror twin, confirmed
`ls -la` on both — 6678 bytes, same mtime.) Two `.py` files, zero hits for
html/css/scss/tsx/jsx/vue/svelte/less. No rendered UI surface changed. Per project
Expertise P-01, harness is files-only with no build step — this is the expected default,
confirmed rather than assumed.

**Decision: `in_scope: true` anyway**, on the one thing the dispatch names explicitly and
that sits in this role's lane regardless of rendered surface — the merge gate's DENY
message is operator-facing copy, and this pin changed its wording (adds `feat`
interpolation to the internal-error deny reason).

## The message, both states

Source (`merge-gate.py:128,154`): `feat = "this feature"` is set once, before the try
block that resolves the branch and matches a `feature.json`. It is overwritten to the
real feature's directory name (`feat = os.path.basename(feat_dir)`) only *after* a
`feature.json` has matched the current branch. The final `except Exception: deny(...)`
uses whichever value `feat` holds at the moment something throws.

**State A — matched, then an internal error** (e.g. `feature_schema.recovery_command_for`
throws after a feature is identified):
> `merge-gate: FEAT-9001-real's Build-entry receipt, so this merge is denied. Repair the
> feature record and re-run the merge.` *(read from source; f-string substitution, no
> branching to trip — not separately re-executed since G-01 evidence bar is met by direct
> literal read)*

**Verdict on A: actionable.** Names the feature, names what failed (Build-entry receipt
evaluation), names the next step (repair the record, re-run). An operator with two
features mid-merge now knows which one to go fix — this is the concrete improvement the
pin delivers over cycle 3's un-interpolated text.

**State B — the `"this feature"` fallback.** I read this, per the dispatch, "as an
operator would when that fallback fires" — and reconstructed it in-process (no disk
writes; `exec()` against the tracked source with monkeypatched `open`/`glob`/
`subprocess.run`, per the write-guard's fallback instruction) to confirm it is reachable
by ordinary conditions, not only by contrived JSON corruption:

1. **Zero feature match at all** (`glob` returns no `feature.json`, i.e. a branch with
   no harness feature association whatsoever) plus a broken `feature_schema` import →
   denies with the fallback text. [executed, in-process]
2. **A real, matched, healthy feature present, but `git` is not invocable**
   (`local_branch()` in `merge-gate.py` calls `subprocess.run(["git", ...])` with **no
   `try`/`except`** around it — unlike `gh_head()`, which does catch `OSError`). A
   `FileNotFoundError` from that call propagates out of `head_branch`, is caught by
   `main()`'s outer `except Exception`, and denies **every merge in the repo**,
   regardless of which feature it belongs to, with the same fallback text. [executed,
   in-process, `gh pr merge 42` command, matched `FEAT-9001-real` feature.json present
   and irrelevant to the outcome]

Both reproductions print the identical reason string:
> `merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is
> denied. Repair the feature record and re-run the merge.`

**Verdict on B: not actionable, and the remedy is actively misleading.** In this state
the code has, by construction, either not identified any feature or hit a fault before
reaching one. The message still tells the operator to "repair the feature record" — but
there is no known record to repair (case 1 has no feature at all; case 2's real feature
record is fine, the fault is `git` being unreachable). Following the stated remedy does
nothing in either reproduction: re-running the merge without fixing `git`'s
availability, or without any feature record touched at all, denies again. Contrast with
the DEC-138 allow-path two lines above in the same function, which interpolates the
caught `failure` string into its stderr line — the fallback deny path has that same
information available in spirit (an exception occurred) but discards it: no `str(exc)`,
no stderr line, nothing distinguishing "we don't know whose merge this is" from "we know
whose it is and something broke."

This is not a re-litigation of cycle 3's fixed defect (that was the malformed-JSON-record
case, closed by the `isinstance(document, dict)` skip, which reproduction 1 no longer
needs to exercise — I forced the same code path a different way, via import breakage and
via an unguarded `subprocess.run`). It is a narrower, still-open instance of the same
*symptom class*: an operator with no stake in `this feature` can still be denied and told
to fix something that isn't broken. I am not grading whether the code *should* deny here
(that's a correctness call outside this lens — CodeC4/SecC4's territory, since one path
runs through a genuinely missing exception guard in `local_branch()`); I am grading
whether the **copy** is actionable in that state, and it is not.

## Verdict

Not gating on its own — this is copy quality on a fail-closed defensive branch, not an
accessibility exclusion (no colour, contrast, or keyboard dimension applies to this CLI
text). `severity_max: med`. Flagging as advisory for the fallback text specifically:
either interpolate the caught exception (mirroring the DEC-138 stderr precedent) or drop
the "repair the feature record" imperative when no feature has been matched, since it
does not hold in that state.

## Non-findings / carried forward

- Nothing else in the diff (test file only) presents operator-facing text; the 18-case
  suite revision was not re-read for wording since it's test scaffolding, not shown to a
  human at decision time.
- No prior UI-reviewer finding on this feature was reopened.
