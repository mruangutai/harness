# UI review — i202 · rendered-doc consistency after the strike

**Pinned SHA:** `835b2976` · **Base:** `c4fea5d`

## Scope

Diff `c4fea5d..835b297` touches 11 files, all shell/python/markdown (file-extension census:
zero of `html|css|scss|less|tsx|jsx|vue|svelte`). No `DESIGN.md`, no component, no palette, no
dark/light surface changed. **Out of scope by the normal test.**

Dispatch handed down one adjacent rendered surface to check anyway: `docs/harness/org.html`,
not itself in this diff's file list, but potentially stale relative to what the diff struck.
Per Expertise P-06, a handed-down surface is in-remit even when the diff itself scopes out —
reviewed below.

**Premise check.** The dispatch said a working-tree grep matched `DEC-103|DEC-104|DEC-181|DEC-188`
in org.html. At the pinned SHA (`git show 835b297:docs/harness/org.html`), only `DEC-181` matches
(once, footer). The premise does not fully hold at the reviewed SHA — the working tree is being
written by concurrent flows and is not the object reviewed here.

## Check: does org.html present struck guidance as live?

1. **DEC-103 / DEC-104 (struck whole — the propagation checker, `check-docs.sh`, INV-10,
   `<!-- stale: -->` markers).** Grepped org.html at the pin for `DEC-103`, `DEC-104`,
   `check-docs`, `INV-10`, `<!-- stale`, and, on a second pass, the substance vocabulary
   `invalidat`, `supersed`, `marker`, `INV-`, `check-state` — **zero matches on all of them**.
   org.html never described the propagation-checker workflow or any numbered invariant to a
   reader, so there is nothing in it that is now stale on this account.

2. **DEC-181 (struck in part — surviving half is the 80-line `CLAUDE.md` budget, enforced at
   `check-domain.sh:779-780`; struck half was "and enters the propagation checker's scan roots").**
   One hit, in the footer: `Reference diagram · updated 2026-08-06 (through DEC-181) · generated
   from SPEC.md §2–§13 and team-config.yaml.` This is a dated attribution ("last decision folded
   into this diagram"), not content asserting what DEC-181 says. It doesn't mention scan roots or
   the budget. Accurate on its own terms, points a reader at nothing the tree no longer does.

3. **Is org.html stale against its own declared source, `SPEC.md §2–§13`?** This diff changed
   `docs/harness/SPEC.md` (22 lines, 5 hunks). Read every hunk (`git diff c4fea5d..835b297 --
   docs/harness/SPEC.md`): all five are propagation-checker retraction prose (the header note
   citing DEC-104/DEC-188), the DEC-104 schemas-inline rationale, and four `<!-- ok-stale -->`
   marker deletions (the escape-comment cleanup itself, now moot with the checker gone). None
   touch roster, tiers, command table, gate list, or flow descriptions — the content org.html's
   diagram actually depicts. Combined with the zero-hit greps in (1), org.html never rendered the
   material these hunks changed, so it is not out of sync with its declared source on this diff.

4. **Generator check, at the pin.** `git grep -l "org\.html" 835b297` returns only historical
   feature notes/observations under `.harness/features/FEAT-06.../` and `FEAT-08.../` — no script
   under `.claude/skills/harness/bin/` and no build step references org.html. `git log --all --
   docs/harness/org.html` shows only hand-authored commits (`docs(org.html): catch the diagram up
   through DEC-142`, `feat(org)!: ...`, prior review-fix commits). org.html's own footer claim
   "generated from SPEC.md §2–§13 and team-config.yaml" describes a manual authoring process, not
   an automated pipeline — there is no generator to be out of sync with, at the pin or in this
   diff.

## Failure scenario tested for, and result

Tested: a human opens org.html, reads guidance the tree no longer implements (the propagation
checker, or DEC-181's struck half), and follows it. **Not found.** No mention of the checker
workflow anywhere in the file; the one DEC-181 reference is a dated attribution, not actionable
guidance; and the SPEC.md hunks this diff made don't touch the sections org.html draws from.

## Note not written up (re-opening the ruling, out of scope)

The deleted `check-docs.sh` previously scanned `docs/harness` (which includes org.html) among its
roots. Removing the checker removes that scan. Not reported as a finding — the dispatch forbids
re-litigating the strike, and no live-content divergence was found regardless of whether a
scanner exists to catch a future one.

## Rendered-size caveat

This is a source-level read of a 348-line HTML file. Actual rendered layout/legibility of the
diagram (column widths, table overflow, whether "§2–§13" cross-references still resolve visually)
is not verifiable from source — human or UAT check required if that matters here.

## Verdict

No divergence between org.html and the strike this diff performs, against its own declared
source or against the struck decisions directly. The main diff remains out of scope for this
role by the normal UI-surface test; the narrow check the dispatch required came back clean.
