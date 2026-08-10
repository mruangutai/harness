# Operator ruling — FEAT-10's task issues belong to the factory

Date: 2026-08-09
Asked by: main session, relaying `feature.yaml` `gate_status.github_mirror`
Answered by: Mike Ruangutai

## The question

`gh-sync.py open` was deliberately not run for FEAT-10. Both `gh-sync.py` and the factory that
FEAT-10 is building publish a `T-NN` task issue into `mruangutai/harness` — the repo is both
`harness.json` `github.repo` and a candidate fleet member. Running both yields two issues per task,
and 13 issues are not cheaply reversible.

## The ruling

**Wait for the factory to own it.**

`gh-sync.py open` stays UNRUN for FEAT-10. The factory's own publish step — T-04, "Publish an
approved plan as issues on the board" — is the owner of this feature's task issues. Do not run the
legacy mirror for FEAT-10 to close the gap, and do not treat the absent `T-NN` issues as a defect in
a goal-check or a review.

## What this means for the ship gate

The board currently carries FEAT-10 only as the wayfinding effort `#181` and its 16 resolved
tickets `#182`–`#197`. There are no `T-NN` issues and there must not be any until the factory
creates them.

If T-04 lands and works, FEAT-10's tasks get published by the factory and the question is closed
permanently for this feature. If T-04 does not land, the fallback is one command — `gh-sync.py open
.harness/features/FEAT-10-software-factory` — and it is the operator's call to run it, not a
cleanup step anyone should take unasked.

## Carry this into the CEO briefing

State the mirror as deliberately skipped and owned by the factory. It must not read as an
unexplained gap next to the other features, which all carry mirrored task issues (FEAT-08 is `#85`
with `#86`–`#97`; FEAT-09 is `#98` with `#99`–`#102`).
