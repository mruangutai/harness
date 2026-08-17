# UI review — FEAT-22 docs layout migration — panel/validator squad — 2026-08-16-13

**Verdict: PASS.** In scope (the dispatch is right that `org.html` deserved a look), and the look
clears it: a 100%-similarity rename with a byte-identical blob, self-contained, so its rendering at
the new path cannot have changed. No `must_fix`.

## Range measured

`git diff --name-only 0f12f14..e26e628` → **32 files** (matches the claim).
`git rev-list --count 0f12f14..e26e628` → **5 commits** (matches the claim).

## Census taken (counts, not adjectives)

- Extension census across all 32 files for `html|css|scss|less|tsx|jsx|vue|svelte`: **1 hit** —
  `.harness/harness/docs/org.html`. Nothing else in the range is a rendered UI surface.
- `git diff --summary -M 0f12f14..e26e628 -- '*org.html*'` → `rename {docs/harness =>
  .harness/harness/docs}/org.html (100%)`.
- `git diff <old-blob> <new-blob>` on the two `org.html` git objects directly (not a checkout diff)
  → **empty output**. Content is byte-identical; only the path moved.
- Read the full new-path blob: **348 lines**. Greped it for `href=|src=|<link|<script|<img|<style`
  → only one match, an inline `<style>` block (line 2). Greped separately for `<a |onclick|
  addEventListener|\.md` → **zero `<a>` tags anywhere**; every `.md`/path mention in the body is
  inert `<code>` prose, not a navigable reference. Net: the document has **no external references at
  all** — no stylesheet link, no script src, no image src, no anchor to a sibling doc. A file with
  zero relative references cannot break by moving one directory deeper. This is the strong form of
  the claim, not a "probably fine": nothing in the file resolves a path, so nothing to re-resolve.
- Checked the other 4 moved docs: `SPEC.md` and `BUILD.md` are 100%-similarity renames, zero content
  delta. `DECISIONS-INDEX.md` is 98% (2 real content lines changed — see below). `DECISIONS.md` is
  99% (one 25-line amendment appended at EOF; the other 5,943 lines are untouched, per the BRIEF's
  own partition rule that historical decision text stays as written).
- `DECISIONS-INDEX.md` diff, read in full: header line "open `docs/harness/DECISIONS.md`" →
  "open `.harness/harness/docs/DECISIONS.md`", and two row annotations (`DEC-189`, `DEC-194`) picked
  up amendment tags unrelated to path spelling. **Verified the header's advertised path resolves**:
  `git cat-file -e e26e628:.harness/harness/docs/DECISIONS.md` succeeds, and `git ls-tree e26e628 --
  .harness/harness/docs/` shows all five files present at the new location. This directly confirms
  SC-01 and the navigability half of SC-06 (the byte-identical-to-generator half is qa's integration
  runner to confirm, not mine — I checked structure/resolution, not generator output equality).
- `CLAUDE.md` diff: two path references (`docs/harness/SPEC.md` table row, and the "before changing
  any harness doc" instruction) updated to `.harness/harness/docs/...`. Both resolve (same ls-tree
  check above covers `SPEC.md` too).
- Checked `team-config.yaml` (org.html's own footer says it is "generated from `SPEC.md` §2–§13 and
  `team-config.yaml`", so a change there is a shared-source-changed-surface-nobody-looked-at risk).
  The only change is one added domain-grant line, `{ path: .harness/*/docs/**, upsert: true }`, for
  the documentor role. Nothing about roles, ownership colours, or the org diagram's structure
  changed — org.html itself is unchanged (see above), so nothing it depicts has drifted from this
  edit. No regression.
- Read both DEC-174 carve-out files in the diff (`check-domain.sh`, `check-state.sh`, in scope per
  the dispatch's routing note): each carries exactly one changed line, a path literal inside a CLI
  warning string (`docs/harness/DECISIONS.md` → `.harness/harness/docs/DECISIONS.md`). Correct,
  consistent with the move, and not a UI surface (batch/CLI text, no colour-only state encoding).
  **No CHANGE needed — nothing to route to the operator's main session.**
- `DESIGN.md`: none exists for FEAT-22 (`ls` on the feature dir shows `BRIEF.md`, `feature.json`,
  `notes/`, `observations/`, `plan.yaml`, `runs/`, `STATE.md` — no `DESIGN.md`), and the BRIEF's own
  "Verification gaps" section states plainly: "there is no UI... here." Confirmed by inspection, not
  assumed from the dispatch's framing.

## Mode A / Mode B split

This is Mode B (post-build, at a pinned SHA) — but there is no contract to hold it against: no
`DESIGN.md` was ever authored for this feature, correctly, because it moves files without changing
any rendered surface's content.

## Accessibility / theme parity

`org.html` does have styled UI (light/dark via `prefers-color-scheme` and a `data-theme` attribute
selector), but the diff's delta to that content is **zero** — nothing newly auditable here. Not
applicable to this review, stated explicitly rather than omitted (G-02).

One pre-existing, non-gating observation: the file defines `:root[data-theme="dark"]` /
`[data-theme="light"]` CSS selectors but the diff shows no `<script>` anywhere in the file that ever
sets `data-theme` — those selectors currently have no code path that activates them, so the page
runs on `prefers-color-scheme` alone. This is unchanged by this diff (content is byte-identical to
the pre-move version), so it is not a finding against this feature — recorded as **info** only, per
the house rule against extending remedy scope into untouched code (P-11).

## Executions

None — there is nothing in the UI remit here to execute (no test, no render). SC-07/SC-08 (unit and
integration suites) are qa's to run; SC-02/SC-05/SC-06 (automated, unit/integration evidence) are
also outside this role's execution lens. My checks were all direct inspection: blob diffs, greps,
`git cat-file -e`, `git ls-tree` — 8 discrete inspections total, enumerated above.

## Open question

None blocking. One non-blocking note for the record: SC-06's "byte-identical to generator output"
half is not something a source-level UI review can confirm — that's `gen-decisions-index.py`'s own
integration test (`test-gen-decisions-index.py`, in the diff, `INTEGRATION_SCRIPTS`), which is qa's
lens, not mine (O-02).

## Working tree

`git status --porcelain` confirmed clean of tracked-file changes before this note was written; only
this note and pre-existing untracked review artifacts from earlier rounds are present.
