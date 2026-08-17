# Review — harness-ui-reviewer — FEAT-22-docs-layout-migration (Mode A, unit 4)

BLUF: FAIL. One must_fix. `DESIGN.md` is legitimately absent — confirmed by reading `BRIEF.md` and
`plan.yaml` in full: no rendered UI, palette, type or spacing decision anywhere in this feature.
Per the dispatch, the operator/maintainer-visible strings this plan rewrites were audited against
the plan's own verify coverage. T-03's four detector-invisible sites in `harness_boundary.py`
(`:84`, `:111–112`, `:221`, `:315`) carry required semantic content changes with **zero enforcing
assertion anywhere in the plan** — not the task's own verify, not T-10's depth sweep, not SC-10.
Everywhere else audited is clean, and two of those clean results were non-obvious enough to verify
directly rather than assume.

## Scope check

- `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`, matching the plan's pinned
  `lanes.resolved_at` and `BRIEF.md`'s stated base. Confirmed before reading anything else.
- `plan.yaml` (1081 lines, 11 tasks) read in full; no `DESIGN.md` exists under this feature's
  directory and none is referenced. This is a directory-move-plus-resolver-rewrite feature — shell,
  Python and markdown text, no markup, no CSS, no rendered surface.
- The dispatch names the in-remit surface explicitly: the operator-visible strings this plan
  rewrites. Audited all six items it lists, plus swept `harness_boundary.py` for every `grant(ed)`
  occurrence to check for sites beyond the two the dispatch already named.

## Finding 1 — must_fix, severity high

**T-03's verify enforces only lexical presence/absence of the legacy/migrated path spellings. It
cannot and does not check that the *semantic* content the task's own intent requires was actually
written, or written correctly — and the gap is wider than the two sites already flagged.**

`plan.yaml:327–340` (T-03 verify), for `harness_boundary.py`, checks exactly two things: that the
migrated glob-shape regex (`\.harness/[^/"]+/docs/\*\*`) appears somewhere in the file, and that no
legacy substring (`docs/harness` or `"docs", "harness"`) survives anywhere in it. Both are whole-file
lexical checks. Four sites in the file require content beyond a token swap (`plan.yaml:363–391`):

- **`:84`** — required new content, not a substitution. The intent (`plan.yaml:366–369`) mandates
  adding a clause stating the entry is now logically REDUNDANT and why. No assertion anywhere in the
  plan checks for this — not even `grep -qi redundant`. Confirmed by grepping the whole plan for
  `redundant`: it appears only in `D-02`'s and `T-08`'s prose (`plan.yaml:114,116,366,820`), never
  inside a `verify:` block. A build that swaps the path token at `:84` and drops the required clause
  passes T-03's verify unchanged.
- **`:221`** — a pure token swap manufactures a directly **false** sentence, not a stale one. The
  docstring at `harness_boundary.py:220–225` (0f12f14) reads "team-config.yaml grants `docs/**` and
  holds no `docs/harness/** entry anywhere`." T-02 adds exactly a `.harness/*/docs/**` entry to
  `team-config.yaml`. Respelling the glob token to the new form while leaving "holds no ... entry
  anywhere" in place produces a sentence that is false the moment T-02 lands, and the lexical check
  cannot see it — the failure mode isn't a leftover legacy string, it's a claim about the file's
  *contents* that the migration itself falsifies.
- **`:315–316`** — a token swap that keeps the current frame ("what makes `docs/**` grant
  `<harness>/…/guide.md`") misattributes the grant: after T-02/T-03, `docs/**` no longer grants that
  path in the harness base; `.harness/*/docs/**` does. The intent (`:387–391`) directs a genuine
  rewrite, not a substitution, but nothing checks which one happened.
- **`:111–112`** — the symlink-escape worked example, and the subtlest of the four because it
  carries **no legacy substring at all** to force a change. `docs/harness/<link>/agents/x.md` with
  `<link> -> ../../.claude` is two path segments deep (`docs/harness/`), so two `../` climbs reach
  root and the link escapes to `.claude/`. The destination is three segments deep
  (`.harness/harness/docs/`), so the re-anchored example needs **three** `../` climbs
  (`../../../.claude`), not two — verified by walking the climb from each directory by hand. T-03's
  intent (`:383–384`) says only "re-anchor on the new directory so the example is reachable," naming
  neither the corrected target string nor the segment-count reason. A minimal re-anchor (same
  `../../.claude`, new base directory) produces a worked example whose arithmetic no longer escapes
  `docs/` — the opposite of what the paragraph exists to demonstrate — and `:112`'s clause "stayed
  inside `docs/` for every comparison" carries none of the legacy `docs/harness` or `"docs",
  "harness"` substrings T-03's whole-file check greps for, so this site is invisible to the verify
  in both directions: neither the current text nor a wrongly-fixed text can trip it.

**No backstop exists downstream either.** T-10's depth sweep (`plan.yaml:930–1030`) is explicitly
"literal-free" for its RESOLVER method, which is scoped to *Python code* that resolves paths (climbs,
globs, module-scope opens) — not to auditing prose truthfulness — and its literal cross-check greps
for the same `docs/harness` pattern, which by T-10's time is already gone from this file regardless
of whether the replacement content is correct. SC-10 (`BRIEF.md:134–137`, inspection-only) asks
whether a file carries "a present-tense claim that the docs live at `docs/harness/`" — a claim about
which *location*, not whether a comment's account of which *glob* grants what is now accurate. A
wrong or missing rewrite at any of these four sites can pass every automated check in the plan, pass
T-10's sweep, and satisfy SC-10 as worded, permanently.

**Why this gates.** The site under `:221`/`:315`/`:84` is `harness_boundary.py`, a DEC-174 carve-out
and (per `plan.yaml:44`, D-03) a carve-out **by content** under DEC-193 — it decides both write-guard
verdicts in the live system. A permanently false or missing explanation embedded in that module's own
comments, with no detection mechanism ever, is the exact "checkable contract" gap Mode A exists to
catch: the intent states the requirement in near word-for-word detail, and nothing can later prove a
build violated it.

**Remedy is cheap and does not require sweeping every prose site in the plan** (shape, not mine to
write): a few targeted lines in T-03's verify — `grep -qi redundant` for `:84`; a negative grep for
the specific false-claim shape at `:221` (e.g. `holds no.*entry anywhere` must not survive); a check
that `:315`'s clause names `.harness/*/docs/**` as the grantor rather than `docs/**`; and one sentence
in T-03's intent spelling out `../../../.claude` for `:111–112` so the fix is unambiguous even without
a verify line. This is the same shape as FEAT-21 ship-review's must_fix on `check-plan-routes.py`'s
diagnostic strings, and the same cheap-before-build remedy applies.

## Checked clean

- **Q1 — the regenerated `DECISIONS-INDEX.md` header (`gen-decisions-index.py:76`).** Enforced at
  BOTH the generator's source and the committed artifact. T-09's verify (`plan.yaml:850–856`) runs
  `gen-decisions-index.py --stdout`, `diff -u`s it against the committed
  `.harness/harness/docs/DECISIONS-INDEX.md`, and separately greps the committed file's header for
  the new path. SC-06 backs this as automated/integration evidence. No gap.
- **T-06's six files** (`CLAUDE.md`, `harness-principles/SKILL.md`, `templates/plan.yaml:44`,
  `check-plan-routes.py:44`, `check-state.sh:676`, `check-domain.sh:953`). Read all six at 0f12f14
  directly. None makes a claim about *which glob or rule grants a path* — each is a pure pointer
  ("read the authority here," "rationale belongs at this path," "this path is an example of a
  granted path"). Grepping every T-03/T-06 file for `grant(ed)` confirms the grant-attribution
  claims live only in `harness_boundary.py` (Finding 1) — nowhere else in this file set. T-06's
  whole-file legacy-absence-plus-new-path-presence verify forces and suffices for a pure pointer
  substitution.
- **`check-plan-routes.py:44`** specifically: the comment's "`docs/harness/SPEC.md` ungranted `<-`
  granted" worked example remains TRUE once respelled to `.harness/harness/docs/SPEC.md`, because
  that path genuinely is granted post-migration (SC-05, tested). This is a substitution that
  preserves truth, unlike `:221`/`:315` where the grantor itself changes — confirmed by tracing
  `is_control_plane_target`'s post-T-02/T-03 behavior rather than assuming the dispatch's framing.
- **`factory_config.py`'s docstring (`:8–16`)** and its two present-tense probe references
  (`:143`, `:151`): straightforward path substitutions whose surrounding reasoning ("the probe stays
  a docs path because...") is unaffected by the move. Caught by T-03's whole-file lexical check.
- **`gen-decisions-index.py`'s docstring (`:2,5,8,10`)**: same — Usage-line path examples, no
  semantic claim beyond "the file lives here," forced to change by the same whole-file check.

## Accessibility and theme parity

Not applicable, stated rather than omitted. Every surface in scope is shell/Python source and
markdown prose; there is no rendered output, no colour, no interactive state. The one HTML artifact,
`org.html`, was audited by `harness-visual-designer` as relocation-safe and is out of this review's
remit per the dispatch.

## Mode A checklist

- Implementable: n/a for the moved-content itself (path substitutions); Finding 1's four sites are
  where "implementable" fails — the intent states exact required content but no assertion can prove
  it landed.
- Complete for what's being built: states_unspecified — none found. T-01's RED STATES section
  enumerates every mid-cluster state the detector and suites pass through, unusually thoroughly.
- Internally consistent: yes, aside from Finding 1.
- Both themes: n/a, no theme surface.
- Checkable: gap found — Finding 1 is precisely this question answered no for four sites.
