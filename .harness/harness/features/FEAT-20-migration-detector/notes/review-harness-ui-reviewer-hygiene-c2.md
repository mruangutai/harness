# Review — harness-ui-reviewer — FEAT-20 follow-up, confirmation pass on PR #385
## (6296149 vs a714bd0, base 3c75aa6)

## Verdict on my own c1 finding: PRESERVED, not resolved — and now wider by design

My c1 med (`review-harness-ui-reviewer-hygiene.md`) was: the `neither` clause is singular
("a coupled reader matches neither form") but the blame list behind its em-dash is unfiltered and can
carry a contradicting tag (`[both]`). The operator's M-1 ruling (widen `blame()` to every
`CANNOT_VERIFY` cause, per `check-state.sh:1295-1332` diffed against `a714bd0` below) does not touch
this wording at all — it is a pure mechanical refactor of *which causes* append `blame()`, not of
*how* the append reads:

```diff
-                "unreadable": lambda: (
-                    "a coupled reader could not be read — "
-                    + ", ".join(... _lmod.blame(_srep))),
-                "neither": lambda: (
-                    "a coupled reader matches neither form — "
-                    + ", ".join(... _lmod.blame(_srep))),
+                "unreadable": "a coupled reader could not be read",
+                "neither": "a coupled reader matches neither form",
 ...
-            return _fmt()
+            _text = _fmt() if callable(_fmt) else _fmt
+            _named = ", ".join("%s [%s]" % (p, f) for p, f in _lmod.blame(_srep))
+            return _text + (" — " + _named if _named else "")
```

The exact string for cause `"neither"`, readers `[x:neither, y:both]`, is **byte-identical** before
and after this PR. I executed the *new* `_cv_wording` against a constructed `SurfaceReport` (output
below); the *old* composition (`a714bd0`'s literal lambda, still visible in the diff hunk above)
concatenates the exact same clause text with the exact same unfiltered `blame()` call and the exact
same `" — "` join, so the two produce the same string by construction — I derived this from the diff
rather than separately executing the pre-image path:

```
"a coupled reader matches neither form — x [neither], y [both]."
```

**So my c1 med is PRESERVED verbatim, not resolved.** What changed is scope, not wording: before this
PR, only `unreadable` and `neither` called `blame()` unfiltered (my c1's two examples); M-1 makes
**every** `CANNOT_VERIFY` cause do so, so the same contradiction class is now reachable through
`unreadable`, `no-evidence`, and `undeclared-segment` too — confirmed below by construction, not
inferred. The comment added at `:1296-1301` — "the cause clause explains WHY the surface cannot be
verified... the blame list names WHICH readers carry a defective or disagreeing form" — is source-code
narrative for a future maintainer; it changes nothing about what the string looks like to the person
reading terminal output at session entry, who never sees that comment. Judged adversarially against
the rendered text alone, `"a coupled reader could not be read — a [unreadable], b [neither]"` still
reads as "the following were not readable: a, b" to someone without the source in front of them, when
`b` in fact *was* read and simply matched neither pattern — a materially different failure. The
comment's framing is correct in intent; it is not present at the point of read.

## All five causes, constructed and rendered (measured, not reasoned about)

Built `SurfaceReport`s against the real `blame()` (`layout_migration.py:262-273` at `6296149`) and ran
them through `_cv_wording` copied verbatim from `check-state.sh:1295-1319`:

```
unreadable, readers=[a:unreadable,b:neither,c:migrated,d:legacy]
  → "a coupled reader could not be read — a [unreadable], b [neither]."

neither, readers=[x:neither,y:both,z:legacy]              <- the c1 case, unchanged
  → "a coupled reader matches neither form — x [neither], y [both]."

no-evidence, readers=[p:both,q:legacy]
  → "no evidence of either shape under /fake/root — p [both]."

no-rows, readers=[]
  → "no reader rows for this surface."                     <- no dangling separator, confirmed

undeclared-segment, readers=[m:migrated,n:legacy], detail=("some/undeclared/path",)
  → "evidence under an UNDECLARED segment: some/undeclared/path — declare the repository in
     .harness/factory/fleet.yaml or move this out of .harness/ — m [migrated]."
```

`no-rows` is the one cause where `blame()` is provably always empty (`readers=[]` is hard-coded at
`layout_migration.py:233`, the only construction site for that cause), and the guard
`(" — " + _named if _named else "")` correctly produces no trailing em-dash — confirmed, not assumed.

## New finding — `undeclared-segment` now stacks two em-dash clauses of different kinds (not previously filed)

This one is genuinely new to `6296149`, not carried from c1: in `a714bd0`, `undeclared-segment` was
one of the causes M-1 itself named as *not* calling `blame()` at all (validator digest M-1 table,
row `undeclared-segment` → "diverges: yes" because CI named a reader and session entry did not).
Fixing that divergence is correct. But the fix reuses the same bare `" — "` separator that already
sits inside `undeclared-segment`'s own clause text, which — unlike the other four causes — already
ends in an embedded, specific remedy:

```
"evidence under an UNDECLARED segment: some/undeclared/path — declare the repository in
 .harness/factory/fleet.yaml or move this out of .harness/ — m [migrated]."
```

Three structurally different things are now joined by two visually identical em-dashes: a diagnosis
clause, an embedded remedy clause, and a blame list — followed immediately by the generic `_lrem`
sentence ("Finish or revert this surface..."), meaning the full INV-27 line for this cause carries
**two remedies and a blame list** with no distinguishing punctuation between any of them. A reader can
plausibly parse `m [migrated]` as trailing onto "...or move this out of `.harness/`" rather than as a
separate blame item — the two joins are typographically identical. This is a legibility defect
distinct from A-1 (it is not a *contradiction*, since no tag here disagrees with the clause — `m
[migrated]` is consistent with "undeclared segment" evidence), so I am not folding it into my c1 med.
Rating it **low**: isolated to one of five causes, doesn't invert meaning, but it is a real ambiguity
a fix should not have introduced while fixing M-1's coverage gap.

## Proposed remedy — not invented, the file's own sibling convention

Not a decision I can take, but concrete so this doesn't loop a third time: the `MIXED` branch at the
same call site (`layout_migration.py`'s `render()` and `check-state.sh:1325-1327`) already renders its
reader list with a labelled join, not a bare dash — `"...readers {_ev}; readers {_rd}"` (`_rd` is the
same `"%s [%s]" % (p, f)` blame format). The proposed fix for `CANNOT_VERIFY` is to match that existing
convention rather than invent new wording: replace `check-state.sh:1319`'s
`_text + (" — " + _named if _named else "")` with a `"; readers: " + _named` labelled join (still
appending nothing when `_named` is empty). One line, cause-agnostic, no re-filtering — and it makes
`CANNOT_VERIFY`'s join match the file's own `MIXED` precedent instead of reading as an extension of
whichever clause happens to precede it. It also resolves the `undeclared-segment` double-dash as a
side effect, since the blame list would no longer share punctuation with the clause's embedded remedy.

## Answering the four items directly

1. **Diagnosis-plus-evidence, or contradiction?** For `neither` (and now `unreadable`,
   `no-evidence`): reads as **contradiction-adjacent** at the point of read — a singular clause
   immediately followed by tags that don't all match it, with nothing in the rendered text (as
   opposed to the source comment) signalling "this list is broader than the clause." `no-rows` is
   clean (empty list, no dangling dash, confirmed). `undeclared-segment` is not contradictory but is
   now visually ambiguous (new finding above).
2. **Is `[both]` under "matches neither form" now legible?** No. The comment's WHY/WHICH framing is
   accurate as *design intent* but is not rendered anywhere the operator reads it; the string itself
   is unchanged from before this PR. **My c1 med is PRESERVED**, not resolved, not reduced — and its
   blast radius widened from 2 of 5 causes to 3 of 5 (all but `no-rows`, which is structurally immune,
   and `undeclared-segment`, which has its own new-but-different problem). Concrete alternative, cited
   from the file's own existing convention (see above): replace the bare `" — "` blame-list separator
   at `check-state.sh:1319` with `"; readers: " + _named`, matching the sibling `MIXED` message's
   `"; readers {_rd}"` join already in the same file.
3. **`undeclared-segment`'s double em-dash** — judged above as a new, low-severity, non-contradictory
   but genuinely ambiguous construction, introduced by this PR's fix (not present pre-M-1, since that
   cause didn't call `blame()` before). The same proposed remedy (item 2) fixes it as a side effect.
4. **DESIGN.md-governed surface in this diff?** None, measured: `git diff --name-status
   3c75aa6..6296149` — **16 files**, all `.sh` / `.py` / `.yaml` / `.md`:
   `check-state.sh`, `layout_fixtures.py` (new), `layout_migration.py`, `test-check-state.py`,
   `test-layout-migration.py`, four new review notes
   (`review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-hygiene.md`),
   `observations/harness-validator-lead.md`, `plan.yaml`, `.harness/logs/2026-08-14.md`, two deleted
   `.harness/members/backend-dev/FEAT-02-t0{1,2}.md` receipts, `docs/harness/DECISIONS-INDEX.md`,
   `docs/harness/DECISIONS.md`. No `.html/.css/.scss/.tsx/.jsx/.vue/.svelte`, no `DESIGN.md` itself, no
   rendered UI surface. This is **8 files beyond c1's original 8-file census** (the 4 review notes, the
   observations log, the 2 backend-dev deletions, and `DECISIONS-INDEX.md`) — all non-UI panel/log
   artifacts. Confirms c1's original census extended, not contradicted. This does not scope me out of
   items 1-3 — the INV-27 wording remains the dispatch-handed surface per P-06.

## Not filed (out of scope / already handled)

- #365, #367, #368-#375, #377, #378, #380, #381, #384, #279 — pre-briefed, not re-derived.
- M-1's coverage question (which causes call `blame()` at all) is closed and correctly fixed; that is
  code-reviewer's/qa's territory, not re-verified here beyond reading the diff to confirm the wording
  claim in the dispatch.
- No accessibility or theme-parity dimension applies: batch/CLI stdout text, no markup, no
  colour-only state encoding, no rendered surface — both explicitly n/a, not silently omitted.

## Verdict rationale

My own gate: `must_fix` non-empty or `severity_max >= high` → FAIL. Neither holds. A-1 (preserved,
now wider) and the new double-em-dash finding are both legibility defects in disclosed, still-
actionable text (form tags remain individually correct; only the framing around them is loose) —
`severity_max: med`, consistent with c1's own bar for the same class of defect. PASS, advisory only.

```yaml
VERDICT: PASS
DIGEST:
  headline: "My c1 med is PRESERVED, not resolved: the neither-cause message is byte-identical before and after M-1's fix, and the widening (every CANNOT_VERIFY cause now appends blame() unfiltered) makes the clause/list mismatch reachable via 3 of 5 causes instead of 2; a new, distinct low-severity double-em-dash ambiguity appears in undeclared-segment, which M-1's fix newly wired to blame() without a distinguishing separator. No DESIGN.md-governed surface in this diff (16 files, measured — 8 beyond c1's original census, all non-UI panel/log artifacts)."
  mode: B
  in_scope: true
  severity_max: med
  findings: 2
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: ["n/a — batch/CLI stdout text, no markup, no colour-only state encoding, no rendered surface"]
  open_questions:
    - { id: Q1, question: "Proposed remedy for both the preserved A-1 and the new undeclared-segment double-dash: replace check-state.sh:1319's bare '\" — \" + _named' with a labelled separator, e.g. '\"; readers: \" + _named' — matching the sibling MIXED message's existing '\"; readers {_rd}\"' join at the same call site, so this is the file's own convention rather than invented wording. One line, cause-agnostic, no re-filtering. Not a decision I can take; approval-gated same as M-1/M-2 remedies.", blocking: false }
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-ui-reviewer-hygiene-c2.md]
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-ui-reviewer-hygiene-c2.md
```
