# Rotation carry — FEAT-22, written at e6e74c8 by the build orchestrator

**What this is.** The material that exists nowhere else on disk: accumulated ship-review rows,
accepted residuals, the validation sequence, and budget state. T-10 and T-11 are NOT restated here —
they are fully specified in `plan.yaml` and restating them would only create drift. Read them there.

## Budget and position

- **Cycles 9 of 10.** One remains. A single fix cycle is all that is left; exhausting it is `BLOCKED`
  to the operator with the unmet criteria named, never a quiet stop.
- 16 runs recorded against an informational budget of 20 (INV-22 notes, never gates).
- `review_sha` re-pinned to **e6e74c8**, the commit that contains the work (P-02).
- Two commits on `feat/FEAT-22-docs-layout-migration`, nothing pushed: **e6e74c8** the atomic
  cluster (29 files, five docs as renames R098/R099/R100, zero delete-plus-add), **1246b06** the
  logs alone.

## The validation sequence still owed

T-10 and T-11 first (see `plan.yaml`), then, as orchestrator-sequenced squad segments:

1. **qa gate** — validator squad, `harness-qa`, the `test_matrix` hard gate
   (`harness.json gates.qa_gate: blocking`, the project's only blocking gate). Pin `review_sha`
   before it runs.
2. **Review panel** — validator-lead. Note ui-reviewer belongs to the **validation** squad
   (`team-config.yaml:260`), not product; three of this feature's reviews were mis-hosted.
3. **pm goal-check** through product-lead — every one of BRIEF's **12 SCs** verified by its declared
   `verify:` method. Tasks completing is the builder's claim; the SCs are the goal's.
4. **Close-out** — ship-refresh and distillation as **two dispatches in one message**, never folded
   into one prompt and never serial.
5. **CEO briefing** — assembled by reading run digests off disk, no report round, and **disclosing**
   that no round was spawned plus the digest paths used.

## Ship-review rows — the two that matter most

**B-1. Two verify-quality defects, found from opposite directions, both invisible to review.**
- T-04: `test-no-distribution.py`'s own walk root was missing from the plan's sixteen-site
  enumeration. Post-move the sweep would have visited only an untracked `.DS_Store` and **every
  absence check would have gone vacuously green forever.** Caught only because the plan mandated a
  positive control. *A check that could not fail.*
- T-07: `plan.yaml:927` calls `check-expertise.sh` with no argument; its usage gate exits 2 on empty
  argv, so that clause **cannot pass on any tree**. It survived ten plan revisions and four review
  rounds because no probe ever executed it. *A check that could not pass.*
- **The joint lesson:** a green panel on a small delta cannot distinguish a clean delta from a
  shallow probe set. The r9 ui-review PASSED on cycle 1 and flipped to a high `must_fix` only when
  one probe *direction* was added — not when more was read.

**B-2. The cluster was nearly split across two commits.** T-02's `git mv` left five renames staged;
a separate log commit swept them. Detected by dry-run before the cluster commit, repaired by
soft-reset while nothing was pushed. **Recorded because it is a live procedural hazard:** any commit
made by another pen mid-build inherits whatever the build left staged.

**B-3. Harness defects (all reproduced, none blocking):** `bash-write-guard` misparses redirects —
`>"$u"` rejected with a phantom target, and heredoc **bodies** scanned as command text so `->`
becomes a redirect (folded into #369; workaround is explicit absolute paths).
`validate-digest.py:745` validates **any** artifact path ending `digest.md` against the full lead
schema. Nothing reserves a run id and `Write` does not warn on clobber — two leads collided and one
overwrote an in-flight `state.yaml`. An agent with subagents in flight cannot idle-wait; ending a
turn trips `validate-digest.py --hook`. The playbook instructs recording `phase:` in feature.json,
which `feature-schema.json` deliberately deleted (FEAT-14 D-09/D-10) and the domain hook rejects.
`STATE.md`'s template says the activity stream is appended as each DIGEST arrives, but
`.harness/logs/` is outside the orchestrator's domain.

**B-4. Process:** `plan.yaml` is untracked, so **no revision of this plan could ever be diffed** —
three reviewers corroborated every delta by anchor-matching instead. Consider tracking it or
snapshotting each revision before the next revision-heavy feature.

**B-5. Provenance:** `docs/harness/org.html` names `PLAN.md`, `STATE.md`, `DESIGN.md` as bare
filenames, stale under DEC-182 and DEC-129. Pre-existing, deliberately outside the cluster commit.

**Forward-look:** the operator ruled **#430 accepted** — simplify becomes the last build step,
build-side owned, pre-pin, never the validator lead — sequenced between FEAT-22's completion and
unit 5.

## Accepted residuals — ruled, do not re-litigate

- `harness_boundary.py:228`'s "two of the four" clause survives verbatim; T-03's verify does not
  forbid it and eng-lead ruled it needs no re-sign.
- T-06's title ("instruction-side literals and the two gate diagnostics") under-describes its
  seven-file task; eng-lead ruled `change_type: docs` stands.
- `test-check-domain.py:789`'s `--resolve` subject change has no assertion naming it directly.
- The **negative-grep ceiling**: a check can force a false claim out, never prove the replacement
  right. Declared, accepted.
- T-08 clause 4 is exact-text: **interior markup** (`**ONE**`) reds it; whole-span bold passes and is
  the file's house style.
- T-08 clauses 1-3 never terminate at section end. **T-09's regeneration does NOT compensate for
  amendment placement** — that claim was withdrawn by the simplify pass. D-03's human diff read is
  the real control.
- `test-gen-decisions-index.py:361-363` FAILs when the real index is absent while `:399-401` SKIPs on
  the same condition — pre-existing; a wrong repoint makes one test go quiet rather than red.
