# UI review — FEAT-26 pr-linkage-recorded — post-build (Mode B), review_sha bad32441dfc0

## Verdict: PASS — no rendered UI surface; the two named terminal-text commitments hold

## Census (measured, not predicted)

`git diff --stat bad32441dfc0~2 bad32441dfc0`: 38 files changed. Extensions: `.sh` (1),
`.py` (3, all `bin/`), `.json` (12, all `feature.json`/`feature-schema.json`), `.yaml`
(2, `plan.yaml`), `.md` (20, `DECISIONS.md`, `DECISIONS-INDEX.md`, `SKILL.md`, `STATE.md`,
receipts, observations, research notes). Zero hits on html/css/scss/tsx/jsx/vue/svelte/less
— no rendered component, layout, colour, or theme touched. Matches this checkout's
repository-tier Expertise P-01 (harness is files-only, no build step) and confirms rather
than assumes it for this diff.

## The one thing worth a glance: prior Mode A commitments, checked against shipped text

Read `notes/review-harness-ui-reviewer-prebuild.md` first. It named two surfaces "examined
in full" (T-04 `cmd_closes`, T-05 INV-28 warn line) with pinned contracts. Checked both
against `bad32441dfc0`'s actual code and tests, not against the prebuild note's own
narration:

1. **`gh-sync.py closes` stdout purity** — `cmd_closes` (`gh-sync.py:868-880`) prints only
   `Closes #{n}` per recorded number, nothing else; its own docstring states the "ONE
   subcommand whose stdout is captured by the caller" invariant. The dispatcher routes
   `"closes"` to `cmd_closes` *before* `load_config`/the root climb (`gh-sync.py:982-988`),
   specifically so no environmental notice (board-not-configured, a `skip()` line) can
   land ahead of it. `test-gh-sync.py:1570-1613` (four cases: order-preserving, empty,
   absent, zero-gh-calls) backs this. **Commitment met.**

2. **INV-28 warn line naming feature + remedy** — `check-state.sh:1080-1083` emits
   `INV-28: {feat} is Done but its pull request number was never recorded ... Record it
   with \`gh-sync.py record-pr {relpath}\`` per offending feature inside a `for` loop
   (one line each, not aggregated). `relpath` is `os.path.relpath(os.path.dirname(fy),
   root)` — an actual copy-pasteable feature directory, not the ambiguous
   `<feature-dir>` placeholder the prebuild note's gap #1 worried might ship literally.
   That gap resolved in the favorable direction. `test-check-state.py:2195-2248` (six
   cases) backs feature-naming, remedy-token presence, and per-line separation.
   **Commitment met.**

Prebuild gap #2 (no enforcing test for the feature.json-parse-failure branch of INV-28)
remains open exactly as predicted — `check-state.sh:1067-1070` appends the described
message to `bad`, but none of the six `test-check-state.py` INV-28 cases exercise a
malformed `feature.json`. This is not a new finding; it is the same low-severity gap the
prebuild note already rated non-blocking (INV-21's own suite has the identical gap, and a
malformed `feature.json` is already caught elsewhere as a generic VIOLATION). Not raised
as `must_fix` here for the same reason it wasn't at Mode A.

## Accessibility / theme parity — not applicable

Every surface in this diff is CLI stdout/stderr or markdown read by a human or an
operator's pasted-into-GitHub text. No markup, colour, focus, or hit target exists to
audit. Stated explicitly per this role's own instruction, not omitted.

## Out of scope, correctly

Not re-raised: qa matrix classification, DEC-200's single deliberate read-back, DEC-186's
scope question, DEC-192's staleness (#748) — all pre-settled per dispatch instruction.

## What I did not evaluate

`_record_pr`'s and `cmd_open`'s own diagnostic print-lines (`gh-sync.py`) — not named by
the prebuild note's two commitments, not gated by any SC/invariant in this dispatch, out
of remit for this pass.
