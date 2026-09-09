# UI Review (Mode B) — BUG-1290, B-27 cycle, review_sha 72a97b9942832169af84479ae36487398d27ca39

## Verdict: PASS, self-scoped out of gating — but with one measured advisory finding

## 1. Changed surface at the pin (`git show --stat 72a97b99`)
6 files changed, 519 insertions(+), 0 deletions(-), all under
`.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/`:
`qa-2026-09-06-15-validator.md`, `receipt-harness-backend-dev-2026-09-06-b27-altitude.md`,
`receipt-harness-backend-dev-2026-09-06-b27-reuse.md`,
`receipt-harness-data-engineer-2026-09-06-b27-efficiency.md`,
`receipt-harness-dev-ops-2026-09-06-b27-simplification.md`,
`receipt-harness-dev-ops-2026-09-06-b27-verify.md`. All six are harness-internal
run receipts/QA notes, not product surface.

## 2. Census
- **Changed paths at this single commit: 6.** By extension: 6/6 `.md`, 0/6
  `html|css|scss|tsx|jsx|vue|svelte|less`. Classification test: extension census across
  the commit's own `--stat` output (repo-tier P-01: harness is files-only, no build
  step; zero rendered UI is the default here).
- **User-facing count: 0.** All six are agent-authored process receipts consumed by the
  next reviewer/orchestrator, not templates/components/styles/HTML/CLI-rendered text a
  human end-user reads as product output.
- Widened the census to the full cycle range (`git diff --stat c488218e 72a97b99`, 22
  files) per constraint that the file set spans `fb9a4ac4`+`72a97b99`: adds
  `tests/unit/test-factory-claim.py` and `tests/unit/test-factory-claim-mutation.py`
  (both `.py`, not rendered UI) plus more `.md` notes and one prior-cycle
  `ship-review-…-13-ship.html`. That HTML predates this pin (introduced at `f5557377`,
  already reviewed at `review-harness-ui-reviewer-b16-c3.md`) and per repo-tier P-02 is
  a generated ship-review report, not authored product UI — not re-litigated here.
- No `.tsx/.jsx/.vue/.svelte/.css/.scss` anywhere in the 22-file range.

## 3. CLI-output legibility check (the one surface a test-only diff can still move)
Ran `tests/unit/test-factory-claim-mutation.py` live against the pinned worktree
(HEAD == 72a97b99, confirmed via `rev-parse`, so this is pin-accurate execution, not a
stale-tree risk per O-09):

```
BASELINE 3/3 ok
MUTANT ACTIVE
FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
MUTATION PROOF: 3/3 cases reddened
MUTANT KEY-COLLAPSE ACTIVE
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed
EXIT_CODE=0
```

**Judgment: a human CAN tell, but only by reading the log in full sequence, not by
grepping `^FAIL`.** The `FAIL  BUG-1290 5a/5b/5c:` lines are byte-identical in format to
the genuine suite's real-failure line (`test-factory-claim.py`'s `_case_line` marker
format), with no distinguishing tag (`(mutant)`, `SIMULATED-`, different stream, etc.).
Disambiguation exists only at two levels: (a) the immediately preceding
`MUTANT ACTIVE` / `MUTANT KEY-COLLAPSE ACTIVE` marker line, and (b) the trailing
`MUTATION PROOF:` / `KEY-COLLAPSE PROOF:` summary plus the process exit code (0here).
A reader who scans the whole block top-to-bottom, or trusts the exit code, is not
fooled. A reader — or a downstream tool — that greps a CI log for `FAIL` in isolation,
or scans for the string `BUG-1290 5b` without the surrounding context, cannot
distinguish this diagnostic firing from a genuine regression, and would see three/four
`FAIL` lines on a run that is in fact a clean, exit-0 pass. This is the same
attribution-vs-legibility gap named in this role's own Expertise (P-10): readable
output can still be unattributable to its true producer/purpose in isolation.

**This does not gate this cycle.** It is not one of the operator's three directives
(D1–D3), it is not part of the diff at this specific pin (72a97b99 touches none of
this file), and severity is bounded because the file is a developer/reviewer-run proof
script, not an operator-visible qa-gate report, and its own exit code is authoritative.
Filed as a residual, non-gating finding.

## 4. DESIGN.md status
No `DESIGN.md` exists for `BUG-1290-factory-claim-repo-root` at this pin (`ls-tree -r`
over the feature's `.harness` tree returns no match), and none is touched by this or
any commit in the `c488218e..72a97b99` range. Not implicated: this is a CLI/text-only,
test-only cycle with no rendered surface, so Mode A's design-contract lens has nothing
to check against.

## Residual findings
- **[bug, low-med, non-blocking]** `tests/unit/test-factory-claim-mutation.py` prints
  `FAIL  BUG-1290 5a/5b/5c:` lines (identical format to real failures) during
  deliberate mutant runs that end in exit 0. A log-grepping human or tool cannot
  attribute these to "diagnostic, not regression" without reading the full surrounding
  block. Suggested remedy (not applied — read-only role): prefix the captured/replayed
  sub-suite's lines with a marker (e.g. `[mutant] FAIL …`) or route them through a
  distinct stream/tag before printing to `sys.__stdout__`.

## Scope confirmation
Zero product UI surface in this diff (measured, not predicted — see §2 census).
Nothing for Mode A or Mode B fidelity/states/interaction/accessibility/theme-parity
dimensions to check; those sections are not applicable here (all six changed files are
plain-text harness process notes with no rendered states, colour, or interaction to
audit).

## Working tree
Confirmed `git status --porcelain` shows only a pre-existing `feature.json` modification
not caused by this review, plus this note. No edits, no commit, no scratch worktree.
