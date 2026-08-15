# Review — harness-ui-reviewer — FEAT-20 follow-up, c3: judging my own c2 remedy
## (delta 6296149..d15daa3, d15daa3 = HEAD, tree verified clean at this SHA)

## Verdict on my own c1 med: RESOLVED (was PRESERVED at c2), one non-gating residual

My c1 med, restated in c2: the `neither` cause's clause is singular ("a coupled reader matches
neither form") but the blame list behind a **bare** `" — "` reads as if it continues/elaborates that
same clause, so a `[both]`-tagged reader inside the list reads as **contradiction-adjacent** — nothing
in the rendered text signalled "this list is a separate field, broader than the clause."

The implemented remedy — `check-state.sh:1305-1308`, `_suffix = f"; readers: {_named}" if _named else
""` — is exactly what I proposed in c2 (labelled join, matching the sibling `MIXED` branch's
convention). Rendered and run through the real code path (`layout_migration.blame`/`blame_text`,
`check-state.sh`'s composition, constructed `SurfaceReport`s — see below): the list now sits behind an
explicit `"; readers: "` label, structurally demarcated from the cause clause rather than trailing it
via a bare dash. That demarcation is what removes the misreading: a reader no longer has to infer
whether `[both]` is being offered as an *instance of* "matches neither form" — the label states it is
a separate roster of blamed readers, not an elaboration of the clause (the appositive reading the bare
dash invited is gone).

**Judged RESOLVED, not merely reduced**, for the specific defect I filed: the syntactic ambiguity that
made the list look like elaboration of the cause is gone.

**One residual, explicitly non-gating:** the label says *who* is blamed, not *why* a tag that
disagrees with the singular cause (`[both]` under a `neither` cause) is included — that is
`blame()`'s deliberate, operator-ruled policy (M-1: every `CANNOT_VERIFY` cause appends the full
blame list, no per-cause filtering). This delta's own `docs/harness/DECISIONS.md` amendment blesses
exactly this shape ("an empty list appends nothing... not a filtered sentence or a per-cause label").
Re-filing the residual would be re-litigating a signed ruling — recorded as advisory, non-gating, not
as a finding to act on.

## All five causes + the c1/c2 test cases, rendered through both real code paths

Constructed `SurfaceReport`s, executed `layout_migration.cause_text`/`blame_text`/`render()` and
`check-state.sh:1300-1308`'s literal composition directly (imported and run, not re-typed).

`render()`'s per-surface line (`layout_migration.py`, the tool's own CLI output):

```
unreadable:        features: CANNOT_VERIFY — evidence legacy; a coupled reader could not be read; readers: path/a.py [unreadable]
neither (simple):  features: CANNOT_VERIFY — evidence legacy; a coupled reader matches neither form; readers: path/a.py [neither]
neither + [both]:  features: CANNOT_VERIFY — evidence legacy; a coupled reader matches neither form; readers: path/a.py [neither], path/b.py [both]
no-evidence:       features: CANNOT_VERIFY — evidence none; no evidence of either shape under /fake/root
no-rows:           features: CANNOT_VERIFY — evidence none; no reader rows for this surface
undeclared-segment: features: CANNOT_VERIFY — evidence legacy+migrated; evidence under undeclared segment: .harness/foo/features/x/feature.json — declare the repository in .harness/factory/fleet.yaml or move this out of .harness/
mixed (for asymmetry, below): docs: MIXED — evidence legacy+migrated; readers: path/a.py [legacy], path/b.py [migrated]
```

`check-state.sh`'s INV-27 composition (session-entry text, the surface operators actually read):

```
unreadable:
  INV-27 CANNOT VERIFY features: a coupled reader could not be read; readers: path/a.py [unreadable]. ...

neither (simple):
  INV-27 CANNOT VERIFY features: a coupled reader matches neither form; readers: path/a.py [neither]. ...

neither + [both]  <- the c1 case:
  INV-27 CANNOT VERIFY features: a coupled reader matches neither form; readers: path/a.py [neither], path/b.py [both]. ...

no-evidence:
  INV-27 CANNOT VERIFY features: no evidence of either shape under /fake/root. ...

no-rows:
  INV-27 CANNOT VERIFY features: no reader rows for this surface. ...

undeclared-segment (blame empty, no readers with a defective form):
  INV-27 CANNOT VERIFY features: evidence under undeclared segment: .harness/foo/features/x/feature.json
  — declare the repository in .harness/factory/fleet.yaml or move this out of .harness/. ...

undeclared-segment (blame non-empty, real reachable state — readers computed independently of cause):
  INV-27 CANNOT VERIFY features: evidence under undeclared segment: .harness/foo/features/x/feature.json
  — declare the repository in .harness/factory/fleet.yaml or move this out of .harness/; readers: path/a.py [both]. ...

mixed (for asymmetry, below):
  INV-27 docs: layout is MIXED — evidence legacy+migrated; readers path/a.py [legacy], path/b.py [migrated]. ...
```

## c2 low — `undeclared-segment`'s double em-dash — RESOLVED, not merely moved

c2 flagged: the cause's own embedded remedy already ends in an em-dash ("... — declare the repository
... or move this out of `.harness/`"), and M-1's fix appended the blame list behind a **second,
visually identical** bare em-dash, so `m [migrated]` could plausibly be misread as trailing onto the
embedded remedy rather than as a separate blame item.

Rendered above (last `undeclared-segment` block): the second dash is gone. The line now carries
exactly **one** em-dash (the embedded remedy's own, unchanged) followed by a distinctly labelled
`"; readers: "` clause. There is no longer a second unlabeled join to compete with the first — the
ambiguity is eliminated, not relocated. Confirmed against a real reachable state: `undeclared-segment`'s
reader list is computed before the cause branch is chosen, so a real tree can combine an undeclared
segment with a `both`/`neither`/`unreadable` reader simultaneously; this is not a synthetic-only case.
Recorded as advisory-closed, not re-filed.

## Asymmetry — MIXED (no colon) vs CANNOT_VERIFY (colon) in `check-state.sh`, vs `render()`

Measured, not assumed (see the two rendered blocks above, `mixed` rows):

- `render()`'s per-surface line uses **one** shape for both verdicts: `"; readers: " + named` (colon)
  — for MIXED *and* CANNOT_VERIFY alike (single code path, no per-verdict branch on the join string).
- `check-state.sh`'s own CANNOT_VERIFY composition matches that shape exactly (`"; readers: "`,
  colon).
- `check-state.sh`'s own MIXED composition is the **one outlier**: `f"readers {blame_text}"` — no
  colon, one space.

So this is a **two-way** asymmetry with a single outlier, not the three-way split the dispatch
description suggested — `render()` does not introduce a third shape; it agrees with CANNOT_VERIFY's
form. **Judged: legible, not gating.** Both forms unambiguously introduce a labelled reader list;
neither creates a misreading the way the bare dash did. It is cosmetic drift between two call sites in
the same file, visible only if an operator reads a MIXED line and a CANNOT_VERIFY line from the same
`check-state.sh` run side by side and notices the punctuation differs — plausible, but the meaning
never changes. Recorded as advisory, non-gating: "consistent enough" is the honest read here.

## DESIGN.md-governed surface — measured census

`git diff --stat 6296149..d15daa3`: **12 files changed** (matches the stat and the enumerated names
below one-for-one):

```
.claude/skills/harness/bin/check-state.sh
.claude/skills/harness/bin/layout_fixtures.py
.claude/skills/harness/bin/layout_migration.py
.claude/skills/harness/bin/test-check-state.py
.claude/skills/harness/bin/test-layout-migration.py
.harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-hygiene-c2.md
.harness/features/FEAT-20-migration-detector/notes/review-harness-qa-hygiene-c2.md
.harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-hygiene-c2.md
.harness/features/FEAT-20-migration-detector/notes/review-harness-ui-reviewer-hygiene-c2.md
.harness/features/FEAT-20-migration-detector/observations/harness-validator-lead.md
.harness/features/FEAT-20-migration-detector/plan.yaml
docs/harness/DECISIONS.md
```

No `.html/.css/.scss/.tsx/.jsx/.vue/.svelte`, no `DESIGN.md` itself, no rendered UI surface. Zero
DESIGN.md-governed surfaces in this delta.

## Not filed (pre-briefed)

#365, #367, #368-#375, #377, #378, #380, #381, #384, #279, #386, #387 — not re-derived.

## Verdict rationale

`must_fix` empty, no `high`+. The c1 med is resolved; the c2 low is resolved; the colon asymmetry is a
non-gating cosmetic note. Nothing here gates. `findings: 2` (the residual "readers: says WHO not WHY"
note, and the colon-shape drift), both recorded as advisory/non-gating — `severity_max: low`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both my c1 med and c2 low are RESOLVED by the implemented labelled-separator remedy ('; readers: ' at check-state.sh:1305-1308): the neither+[both] misreading is gone (list now demarcated as a distinct field, not a clause continuation) and undeclared-segment's double em-dash is down to one dash plus one label. Two advisory, non-gating findings remain: the label says WHO is blamed, not WHY a disagreeing tag appears (blame()'s deliberate M-1 policy, blessed by this delta's own DECISIONS.md amendment), and check-state.sh's MIXED branch omits the colon that render() and check-state.sh's own CANNOT_VERIFY both use. Zero DESIGN.md-governed surfaces in this delta (12 files, measured, all .sh/.py/.md/.yaml)."
  mode: B
  in_scope: true
  severity_max: low
  findings: 2
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: ["n/a — batch/CLI stdout text, no markup, no colour-only state encoding, no rendered surface"]
  open_questions: []
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-ui-reviewer-hygiene-c3.md]
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-ui-reviewer-hygiene-c3.md
```
