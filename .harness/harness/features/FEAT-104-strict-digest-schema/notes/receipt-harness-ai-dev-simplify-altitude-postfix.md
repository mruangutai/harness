# ALTITUDE — post-fix re-check at 99035a9c

BLUF: the new monotonicity check cannot live in `run-state-schema.json` (JSON Schema
validates one document in isolation and has no cross-document comparison primitive) so
`check-domain.sh` is a defensible home for it as written — `leave`. The `check-state.sh`
persona selector is a bare 6-line inline conditional at its one call site with no second
copy anywhere — `leave`. S2 (F4, the duplicated step-schema loader) is unchanged by this
fix and stands exactly as accepted-for-fold-in in the prior pass.

## F1 (re-check) — schema-version monotonicity check embedded in `check-domain.sh`'s `shape_problems`

- file/line: `.claude/skills/harness/bin/check-domain.sh:1760-1779` (`_prior_version` /
  `_prior_is_strict` / `_version_decreased` block, inside the shell-embedded Python
  heredoc), contrasted against `.claude/skills/harness/bin/run-state-schema.json` (whole
  file), the closed-schema source of truth this same heredoc already loads a few lines
  below at :1619-1629.
- The concrete question this run was asked to settle: could this move to the schema
  instead? No — JSON Schema (Draft 2020-12, as `run-state-schema.json` already declares
  itself) validates a single document against a static shape; it has no construct for
  "the value in this document must be >= the value in a *different*, previously-written
  document." There is no `$data`-style cross-document reference in the draft this schema
  targets, and even where such extensions exist in some validators they compare fields
  *within* one instance, never across two files on disk. Expressing monotonicity requires
  reading two documents and comparing them — which is exactly what `shape_problems`
  already does two paragraphs above (the `prior_state`/`prior_doc` load `check-domain.sh`
  already had before this fix, for the run-identity conflict checks at :1749-1802). So
  "the schema should own it" is not achievable as stated; the rule can only live in code
  that already holds both documents, and `check-domain.sh`'s write-time gate is the one
  caller in this pair that does.
- Is it stated once? Yes for this specific rule — `check-state.sh`'s sweep (the other
  enforcement point in the pair) does not re-derive or duplicate the downgrade check; it
  only reads `schema_version` to pick a validation persona (F2 below), a different
  question. Grepping the diff and the surrounding files turns up exactly one
  `_version_decreased`/downgrade computation, at this one site.
- worth-doing: no — the capability is at the only place that can hold it, stated once.
- recommendation: **leave**

## F2 (re-check) — `check-state.sh` persona selector: version-dispatch at the one sweep call site

- file/line: `.claude/skills/harness/bin/check-state.sh:1590-1598` (`_version` /
  `_persona` ternary immediately before `_vd_mod.validate(_persona, _dtext)`), the only
  caller of `validate()` for a completed lead digest in this file.
- Is this a special case bolted onto shared infrastructure, or the sweep's own business?
  The dispatch that named this question is answered by counting call sites: `validate()`
  is the shared infrastructure (`validate-digest.py`), and it already takes `persona` as
  an ordinary parameter — nothing here reaches into `validate-digest.py` to special-case
  it. The 6-line ternary computing *which* persona string to pass is local to the one
  place in the tree that reads a persisted, potentially-legacy `schema_version` off disk
  to decide it; `check-domain.sh` never needs this because it is a write-time gate acting
  on the incoming document, not an at-rest reader of historical files spanning both
  schema eras. One caller, one small selector next to that caller — this is the sweep's
  own business, not infrastructure logic misplaced in a call site.
- worth-doing: no.
- recommendation: **leave**

## S2 (carry-forward, not re-derived) — does the fix change F4's disposition?

Unchanged, worse if anything but not by this fix's own doing: `check-domain.sh:1619-1629`
and `check-state.sh:1490-1499` (loader boilerplate location per the prior receipt) are
untouched by this delta — confirmed via `git show 99035a9c:.claude/skills/harness/bin/check-domain.sh`
at the same line range, byte-identical to before. The fix *adds* three more schema-version
type-checks (`isinstance(..., int) and not isinstance(..., bool)`) repeated a third time
in `check-domain.sh` (twice already existed for the version-floor check) and a fourth
time in `check-state.sh`'s new persona selector — the same three-line idiom now appears
four times across the two files with no shared predicate. This does not reopen F4 as a
new finding (it is the same mechanism, not a new one), but it is worth noting in the
carry-forward: the fold-in F4 already recommended would, if done, be the natural home for
this idiom too (`is_strict_schema_version(value)` beside the schema loader). Still `leave`
as its own finding this run — F4 already covers it, re-flagging the same fold-in twice
would double-count one recommendation.

## Deeper fix that doesn't reopen settled scope?

None identified. A shared `is_strict_schema_version()` helper is already captured by F4's
existing fold-in recommendation (loader + predicate, one shared module); inventing a
second, narrower fold-in for just this idiom would fragment one clean recommendation into
two overlapping ones. No plan decision or DEC-174 carve-out needs revisiting to reach that
conclusion.

```yaml
VERDICT: PASS
DIGEST:
  headline: monotonicity check is at its only viable home (schema cannot express cross-document comparison) and the persona selector is local to its one caller — both leave; S2/F4 stands unchanged by this fix, its fold-in already covers the newly-repeated type-check idiom too
  findings_count: 2
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-ai-dev-simplify-altitude-postfix.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-ai-dev-simplify-altitude-postfix.md
```
