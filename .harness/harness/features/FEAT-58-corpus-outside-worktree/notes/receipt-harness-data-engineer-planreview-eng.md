# Receipt — harness-data-engineer — planreview-eng (SIMPLIFICATION angle)

Flag-only, plan surface, `harness-simplify` §SIMPLIFICATION. No edits made. Contract items
(lane assignments, `.claude/` vs `.agents/` spelling, the two named harness defects, the
never-materialise-inside/always-available-outside bedrock rule) are NOT re-litigated below.

## Finding 1 — T-01: `corpus_features(root, ref=None)` spells "provider" implicitly where D-05 spells it explicitly, and the two spellings can disagree

- **Anchor:** `plan.yaml:110-115` (T-01's `corpus_features` spec) vs `plan.yaml:44-52` (D-05) and
  `plan.yaml:621-626` (T-12's `corpus: {provider, ref}` mapping).
- **Summary:** D-05/T-12 make "provider" a first-class, explicitly-declared value
  (`provider: history|path`) that `dispatch-guard.sh` enforces by exact match against the
  dispatch text. T-01's actual function signature has no `provider` parameter at all — the
  provider is inferred from whether `ref` is truthy — and T-01's own prose is self-contradictory
  about what happens when `ref` is omitted: "with ref given (**or a default resolved from the
  repository's default branch**) it enumerates from history … and with provider path it lists
  the directories under `<root>`" (`plan.yaml:112-114`). If omitting `ref` still resolves an
  internal default and takes the history branch, there is no code path left that ever reaches
  "provider path" from a caller that just omits `ref` — which is exactly how T-06 and T-08 are
  written to request the path provider (T-06: "This reader takes the PATH provider and only the
  path provider (D-04)" with no `provider=` argument shown; T-08 similarly calls
  `corpus_features(root)`-shaped derivation with no explicit provider). The one caller for whom
  D-04 makes the provider choice load-bearing and non-negotiable (`check-domain.sh`'s
  `_hardlink_plan`, needs inode identity, "git history can supply no inode at any ref") has no
  way, in the signature as specified, to *pin* path provider — it can only omit `ref` and hope
  the ambiguous default-resolution clause does not silently take the history branch.
- **Concrete cost:** `harness-backend-dev` implements T-01 by picking one reading of the
  ambiguous sentence (say, "no ref ⇒ history via resolved default branch, always"). T-06's
  executor then calls the resulting `corpus_features(root)` expecting the path provider per D-04
  and instead gets git-history-derived directory *names* with no filesystem inode behind them —
  `_hardlink_plan`'s `(st_ino, st_dev)` match against those names is meaningless, the hardlink
  escape D-04/T-06 exist to close reopens silently, and `tests/unit/test-corpus-boundary.py`
  case (g) — which only forbids `strict`/`refuse`/`force`-named parameters — passes throughout
  because nothing in T-01's test list asserts provider selection at all.
- **Alternative:** give `corpus_features` an explicit, required-by-name provider argument that
  mirrors D-05's declared field verbatim instead of inferring it from `ref`'s presence:
  `corpus_features(root, *, provider="path", ref=None)`, where `provider="history"` requires a
  non-`None` `ref` (raise, don't silently default) and `provider="path"` ignores `ref` entirely.
  T-06 then reads `corpus_features(root, provider="path")` — a call site that states the D-04
  choice instead of implying it — and the value dispatch-guard.sh enforces at D-05/T-12 maps 1:1
  onto an actual argument instead of onto an inferred one. `provider` does not collide with test
  (g)'s banned substrings (`strict`/`refuse`/`force`), so no existing assertion needs to change.
- **Severity:** high.

## Finding 2 — T-06 keeps `check-domain.sh`'s own corpus-enumerating glob, which T-13's lint (landing after T-06) is written to forbid everywhere but `harness_boundary.py`

- **Anchor:** `plan.yaml:347-353` (T-06 intent) vs `plan.yaml:667-684` (T-13 intent),
  `depends_on` at `plan.yaml:334` (T-06 → T-01 only) and `plan.yaml:657` (T-13 → T-03,T-04,T-05,T-06).
- **Summary:** T-05 (`merge-gate.py`) is written correctly: "resolve the candidate set through
  `harness_boundary.corpus_features` … **rather than globbing the working tree**"
  (`plan.yaml:305-307`) — the glob is retired, not retargeted. T-06 is written differently:
  "**Change the glob ROOT** from the local checkout to `harness_boundary.corpus_root(os.getcwd())`"
  (`plan.yaml:348-349`). Read literally, `check-domain.sh`'s own
  `glob.glob(...,"*","features","*","plan.yaml")` construction survives T-06, just pointed at a
  different root string. T-13, dispatched later in the same dependency chain, defines its lint
  pattern as exactly this shape — "a literal `.harness/*/features/*` string, `glob.glob` over
  it" — and allow-lists **only** `harness_boundary.py`, "by exact basename match … do not
  allow-list by prefix, and do not add a suppression comment mechanism" (`plan.yaml:683-684`).
- **Concrete cost:** the executor of T-13 writes the lint exactly as specified, runs it against
  the tree T-06 left behind, and `check-domain.sh` trips the lint's own positive-control pattern.
  T-13's task is "write a test," not "fix `check-domain.sh`," and its own text forbids the two
  ways out (widen the allow-list, add a suppression comment) — so the executor either violates
  T-13's explicit instruction to land a lint that passes, or discovers a change that belongs to
  T-06 with no live task left to carry it, since T-06 is already a closed dependency by the time
  T-13 runs.
- **Alternative:** state in T-06's intent, the same way T-05 states it, that `_hardlink_plan`
  stops constructing its own glob and instead calls
  `harness_boundary.corpus_features(harness_boundary.corpus_root(os.getcwd()), provider="path")`
  (see Finding 1 for the `provider=` argument) to get the sorted feature-name list, then builds
  each candidate `plan.yaml` path itself (`os.path.join(root, ".harness/harness/features", name,
  "plan.yaml")`, matching D-01's note that today exactly one segment holds `features/`) before
  the `(st_ino, st_dev)` match — so the only corpus-enumerating construct left in
  `check-domain.sh` is the exported API call, and T-13's lint has nothing to catch there.
- **Severity:** high.

## Finding 3 — BRIEF.md states the standing-worktree count as both 30 and 29, undated, in the same document

- **Anchor:** `BRIEF.md:15-16` ("Standing cost: **30 worktrees**, 1217 MB … materialised 30
  times") vs `BRIEF.md:171` ("SC-06 (the **29** standing worktrees)") and `BRIEF.md:197`
  ("Reducing the number of standing worktrees. **29** exist and they stay.").
- **Summary:** the Problem section states the count as a measured host fact tied to a specific
  reading ("Observed at `abff2a84` on this host"), while the Verification-gaps and Non-goals
  sections both independently say 29, with no measurement citation and no note that the count
  moved (plausibly because creating this feature's own worktree bumped 29→30, but the document
  never says so). Neither instance is measured against a checked-in artifact I can compare it
  to, so I cannot say which of the two is stale — only that the same document asserts one count
  twice with two different values and no reconciling note.
- **Concrete cost:** low as currently written, because neither SC-06's graded criterion nor
  T-10's task text hardcodes a number — both enumerate "every linked worktree" rather than
  asserting a fixed count, so the migration and its verify are not gated on which number is
  right. The cost is a reviewer or operator reading SC-06's "29" in Verification-gaps, counting
  30 worktrees on the actual host post-migration, and treating the one-row discrepancy in T-10's
  migration-record as a defect when it is a stale document count.
- **Alternative:** pick the one true count as of plan-signature time, state it once in the
  Problem section with its measurement citation, and have Verification-gaps/Non-goals reference
  it ("the N standing worktrees, see Problem") instead of restating a bare number that can drift
  out from under the Problem section's own figure.
- **Severity:** low.

## Checked, no finding

- **Required-worktree-path set (T-08/T-09/T-10):** T-08 defines `REQUIRED_WORKTREE_PATHS` once;
  T-09 refers back to it by name ("the SAME required-path existence positive control T-08
  defines," `plan.yaml:515-516`) rather than re-listing the paths; T-10's verify runs T-09's own
  `--verify` mode. Single authority, no restatement to drift. Clean.
- **Refusal-message shape ("N of M", corpus root, provider, ref) across T-01/T-03/T-04/T-05:**
  the shape is defined exactly once, as `CorpusIncomplete.__str__` in T-01
  (`plan.yaml:120-123`). T-03/T-04/T-05's tests assert substrings of that single propagated
  message; none re-specifies the message's construction. Clean.
- **D-05's residual vs T-12's required code comment:** T-12 is explicitly instructed to record
  "the residual D-05 states" (`plan.yaml:637-639`) as a one-sentence pointer, not a full
  restatement — decision rationale lives in one place, the code carries a one-line echo of it.
  This is the deliberate, load-bearing kind of duplication the skill's caveat protects, not a
  finding.
- **Fourteen-reader ledger, T-07 vs `notes/receipt-harness-backend-dev-arch-eng.md`:** T-07's
  five-bucket breakdown (7 sweeps / 3 single-feature / 2 path-logic / 1 fixture-only / 1 host
  module = 14) reproduces the receipt's Q1 table and its two "missed readers" exactly, file for
  file. `harness_boundary.py` gets its own bucket in T-07 rather than the receipt's flat
  "path-logic" tag, but T-07's note on it (parity over pre-existing functions only) is a
  refinement, not a contradiction. Clean.
- **Dead references to `refuse_if_incomplete()` / `materialised_count()`:** grepped both cut
  names across `plan.yaml` and the two receipts. Every occurrence in `plan.yaml` is a negative
  assertion (D-01/D-02 stating they were cut, T-01's intent forbidding them, test case (g)
  asserting their absence). No line treats either name as present or to-be-built. Clean.
- **check-state.sh sweep-site count, receipt vs T-03:** the backend-dev receipt's own sentence
  is internally inconsistent ("17 distinct … sites" followed by a 21-entry line list, "— 21
  total"), but `plan.yaml:205-206` (T-03) uses 21 — matching the line-list, not the "17" lead-in
  — and T-03 additionally instructs the executor to "enumerate them yourself at the file's
  then-current state rather than trusting that count," which neutralises any drift risk this
  plan actually carries. Noted for hygiene; not actionable against the plan. Severity: info.

## Empty-angle note

Not applicable — four findings recorded above (3 actionable, 1 info); six areas checked clean.
