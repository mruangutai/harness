# Review — FEAT-16-factory-per-repo-board — c0 — UI scope check (re-run)

Self-scoped OUT. `git diff --name-only a7c429c..ec195ec` returns 38 files (verified via `wc -l`
and enumerated), all `.py`, `.yaml`, `.json` or `.md` — no rendered surface in this diff. Confirms
D-11 (`plan.yaml:159`): no prototype gate fires for FEAT-16 because every literal `files:` entry
across all eleven tasks is `.py`/`.yaml`/`.md`. The only human-facing surfaces are a CLI command and
GitHub's own Projects board UI, neither of which this diff renders or owns.

Also checked `ec195ec..HEAD` (two commits — `12e93f9`, `132e2ce`): touches only `feature.json`,
`notes/qa-c0.md`, `observations/harness-qa.md` — no code, no rendered surface. Scope-out holds
through HEAD, not just at the pin. No `[harness:human]` commits in `a7c429c..ec195ec`.

**Correction to the sibling artifact at this same path stem:** `review-harness-code-reviewer-c0.md`
(written by an earlier run against this same dispatch) states the diff is 32 files; the actual count
is 38 (verified above). The conclusion is unaffected — every one of the 38 is still `.py`/`.yaml`/
`.json`/`.md` — but the count in that earlier artifact is wrong and should not be cited downstream.

**Role/dispatch mismatch, same as the earlier run:** the dispatch addressed `harness-ui-reviewer`
(task framing, DESIGN.md/accessibility/dark-light-parity language, and an output path under that
agent name), but this spawn is `harness-code-reviewer` per the skills and Expertise injected at
spawn. The write-domain guard rejected the `harness-ui-reviewer` output path
(`.harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-ui-reviewer-c0.md`);
this artifact and its sibling live at code-reviewer-permitted paths instead. If the panel's
accounting requires a UI-reviewer-persona sign-off specifically, that slot remains unfilled — the
orchestrator's call, not mine.

No stage-1/stage-2 code review of the `.py`/`.yaml` changes was performed here — out of scope for
this dispatch, which asked only for the UI/rendered-surface check.
