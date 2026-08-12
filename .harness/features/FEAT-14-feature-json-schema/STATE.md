# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **validate** · status Review
- branch `feat/204-feature-json-schema` · HEAD `d37f9b7` · `review_sha` pinned `1c5fd67`
- cycles_used **6** of 10 · runs **21 against an informational 20 — over the bound**
- **All twelve tasks done. Both HIGHs CLOSED. `must_fix` empty, `severity_max: med`.**
- **Not shippable by an agent: three SCs need the operator (~9 min). Nothing else gates.**
- briefing: `notes/ship-review-2026-08-12-validate.md` (+ rendered `.html`)

| gate | result |
|---|---|
| qa gate (`test_matrix`) | `matrix_ok: true`; its FAIL was the missing-fixtures HIGH, now closed |
| review panel | FAIL → **confirmation pass PASS**, both HIGHs closed by execution |
| goal-check | 12/18 met, 3 closed by the fixes, 3 operator-owed |
| four project gates | green: unit+integration 0 · validator 0 · check-state 0 · routes 0/10 |

### Both HIGHs are closed, and this time by execution rather than reading

**HIGH-1 — schema gate failed open.** Fixed at `0b33188` by the main session (DEC-174 carve-out).
Same broken `feature_schema.py`, only the handler differing: **exit 1 with a raw traceback before,
exit 2 with a purpose-written message after**. The new fixtures discriminate — against the pre-fix
handler exactly one case fails. All three routes converge on one function, and the message dedup
suppresses redundant *text* but never the exit-2 *outcome*: the caller accumulates and decides once,
with no per-file exit path. That dedup was the real risk, not the `except` clause.

**HIGH-2 — `gh-sync.py` could re-file GitHub issues.** Fixed at `1c5fd67`. Crashing the write at
`os.fsync` and at `os.replace` both leave `feature.json` byte-identical with no temp residue. Six
reader states measured: absent and no-`github`-key proceed (first sync intact — the regression this
fix could most easily have caused), zero-byte / non-mapping / non-mapping-`github` refuse loudly,
valid loads. Post-fix tests against pre-fix source fail exactly 6, all `fix1`, zero others.

**The nuance, verified in both directions:** swapping the reader back to YAML leaves the suite
**74/74 green** — B-5's contract is unpinned (B-17) — while a zero-byte file *still* refuses via the
`isinstance` guard. Two guards close the irreversible outcome; the mutant removes one. So the gap is
laxity, not the external damage that made this HIGH. Advisory, and measured rather than argued.

### One regression my own fix cycle introduced — recorded, not smoothed

`1c5fd67` narrows `feature.json` from **0644 → 0600** on every `save_recorded`, because `os.replace`
carries the `mkstemp` source's bits where the old `open(p,"w")` preserved the file's. I measured both
sides. My first briefing row called this "converged-with rather than introduced"; that was wrong and
is corrected to a `bug` in the backlog (B-20). LOW, so it did not buy another cycle.

### Operator-owed — legwork done, none may be marked met by any agent

**SC-10** (5 min, `FEAT-11/notes/receipt-feature-key-drop.md`; pm swept all 17, zero unrecorded) ·
**SC-11** (pm recommends MET; residual `factory.issues`/`factory.items` unconstrained) ·
**SC-15** (script at `notes/uat-FEAT-14-sc15-readability.md`; ten keys is the real maximum).

### Decided rather than escalated

Accepted the MED→HIGH promotion of the `gh-sync` defect on evidence I measured · sequenced the fix
cycle before the confirmation pass · did NOT spend a cycle on B-17/B-18/B-20 (all advisory;
`must_fix` empty and `severity_max` med, which is the standing not-critical definition) · restored an
orphaned live mutant and byte-verified it · retried the panel once after permission rejections ·
adopted an interrupted run's Phase 1 · corrected `cycles_used` twice, both traceable · ran the mirror
after confirming `close-task` never calls `save_recorded` · removed all probe worktrees.

### My own errors, kept in the record

An atomicity probe patched `json.dump` where the code calls `json.dumps`, so no crash was injected
and I briefly read a normal write as a failure — the instrument was wrong, not the code. A PYTHONPATH
shim lost to `check-domain.sh:96`, which prepends its own bin dir, so that probe proved nothing until
I redid it in a worktree. Both are why every claim above was re-measured.

### Deliberate non-actions

No distillation or ship-refresh — feature-close steps, and three SCs remain operator-owed. No
`handoff-validate.md` — that seam is crossed at operator acceptance, not here. No `gh-sync ship`, no
push, no PR, no merge.

## Open Questions

- Q1 non-blocking, **main session (DEC-174)**: B-19 — the schema-gate fix is test-verified on the
  Write route only; POST-Edit, the Bash sweep, the dedup aggregation and the `ImportError` branch
  have no fixture, so the crash-vs-import message distinction is unpinned. `test-check-domain.py` is
  a carve-out, so no squad may write it.
- Q2 non-blocking: B-17 — pin B-5's reader contract with the inverse comment-bearing fixture.
  `test-gh-sync.py` is not a carve-out; ordinary fix cycle.
- Q3 non-blocking: B-20 — restore the file mode in both writers, or accept 0600.
- Q4 non-blocking: B-18 — `save_recorded`'s `doc = {}` on the absent-file path. **Reachability is
  unknown; do not fix before answering whether `gh-sync open` ever runs with no `feature.json` yet.**
  Writing a guard for an unreachable path is the more expensive mistake.
- Q5 non-blocking: B-2 — the plan-authorship remedy. All eight plan defects lived in a `verify:`
  clause never executed before signature. Not a carve-out, so dispatchable.
- Q6 non-blocking: B-21 — the `fix1` message predicates are decorative; the branch property they bind
  is real. Seventh instance of the assertion-that-cannot-fail class on this feature.
- Q7 non-blocking: nobody exercised the **deployed hook wiring** — every `check-domain.sh` result
  came from driving the script as a subprocess, which says nothing about whether `settings.json`
  still routes Write/Edit/Bash to it. Invisible to both reviewers by construction.
- Q8 non-blocking: B-3, B-4, B-6..B-13, B-15, B-16 — twelve further residuals, strikeable by ID.
