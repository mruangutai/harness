# UI Reviewer — scope check — BUG-285-yaml-loader-pin

## Census (measured, not predicted)

- `git diff 6cb113f4..592e6412 --name-only` lists 19 paths, but `git log --oneline
  6cb113f4..592e6412` shows two commits: `75a3ee6b` ("STOPPED BY THE OPERATOR mid-flight")
  and `592e6412` (the fix itself). `git show --name-only 75a3ee6b` confirms its 15 touched
  paths are exactly the frozen planning artifacts (`BRIEF.md`, `STATE.md`, `feature.json`,
  `plan.yaml`, `notes/*`, `observations/*`) under `.harness/harness/features/BUG-285-yaml-loader-pin/`
  — matching the dispatch's claim verbatim. `git show --name-only 592e6412` alone confirms
  the actual review surface is **exactly** the four files named in the dispatch:
  `.claude/skills/harness/bin/factory_decompose.py`, `.claude/skills/harness/bin/feature_json_write.py`,
  `.claude/skills/harness/bin/gh-sync.py`, `tests/unit/test-feature-json-reader.py`.
- `find .harness/harness/features/BUG-285-yaml-loader-pin -type f` — **no `DESIGN.md`** exists
  anywhere under this feature's tree (repo-wide `DESIGN.md` hits are all unrelated features/the
  template). No design contract exists to audit against.
- Extension census for a rendered surface (`html|css|scss|tsx|jsx|vue|svelte|less`) across the
  full `6cb113f4..592e6412` diff: **zero matches**. No colour, layout, dark/light theming, or
  accessibility semantics exist anywhere in this diff — confirmed by measurement, not asserted.

## Scope decision: OUT — Mode A / Mode B design review

No DESIGN.md, no rendered surface, nothing to audit as a design contract or its
implementation.

## In-remit adjacent check: CLI refusal-message legibility (per dispatch instruction)

Read `feature_json_write.py` (`load_feature_json`, `FeatureJsonError`), `factory_cli.py`
(`body`, `message`, `fail`, `refuse`), and both call sites (`gh-sync.py:519-553`,
`factory_decompose.py:111-126`).

Both refusal paths route through the one shared grammar (`factory_cli.body`):
`f"{what}: {value} — {next_step}"`, where `value` is **always the offending path** (never a
class name — `FeatureJsonError`'s own docstring states this precedent explicitly) and
`next_step` carries the underlying cause verbatim (e.g. `could not be read: <OSError>`,
`does not parse: <JSONDecodeError>`).

- `gh-sync.py:553`: `raise SystemExit(f"gh-sync: {e}. Refusing to sync rather than risk
  duplicate issues.")` — names the tool, the failure kind, the path, the underlying error,
  and the consequence to the operator in one line. Not a bare traceback.
- `factory_decompose.py:124`: `factory_cli.refuse(TOOL, "feature.json invalid", path,
  e.next_step)` → `factory_cli.message()` renders `"factory: <tool>: feature.json invalid:
  <path> — <next_step>"` to stderr, then exits `EXIT_REFUSED` (2). Same shape: names the
  file, states the cause, no traceback.
- `load_feature_json`'s read-and-decode happens inside one `try` (`OSError,
  UnicodeDecodeError`) so a non-UTF-8 file cannot escape either caller uncaught — this is
  the exact pre-fix defect (claim 4) the docstring cites, and the message text stays
  legible rather than degrading to a raw exception dump.

No legibility defect found: both paths name the offending file and state an actionable
cause; neither can regress to a bare traceback on the paths read. This finding is advisory
only (Python correctness/exception-handling ownership sits with the code reviewer per
dispatch's non-goals) — reported here strictly as an operator-facing-text observation.

## Verdict basis

Scoped out for design-contract review (no DESIGN.md, no rendered surface — measured, not
inferred). Advisory pass on the one adjacent surface named in the dispatch (CLI refusal
text): clean, no findings.
