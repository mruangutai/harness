# UI Review — FEAT-25-claim-feature-root, cycle 1 (SHA 8d7b273)

## Scope check — measured, not predicted

The graded diff is exactly six files under `.claude/skills/harness/bin/` (confirmed via
`git diff --stat d1ffd7f 8d7b273636cfec7fe1cc3d740f70c9153d170b84`):

| File | What it is |
|---|---|
| `factory_claim.py` | CLI tool — polls GitHub issues and claims one via ref-creation race (D-05); the "blocker gate" logic that refuses a claim when a plan dependency is unfinished |
| `layout_fixtures.py` | Shared fixture-data module for the layout-migration detector's test suites (not itself a test file) |
| `layout_migration.py` | The layout-migration detector — per-file check that features/docs surfaces speak one layout language (legacy vs migrated path) |
| `test-factory-claim.py` | pytest suite for `factory_claim.py` |
| `test-factory-integration.py` | pytest integration suite covering the claim/fleet flow |
| `test-layout-migration.py` | pytest suite for `layout_migration.py` |

**File-extension census** (P-01): `grep -i 'html|css|jsx|tsx|svelte|vue'` across all six files
returns zero matches. All six are `.py`.

**DESIGN.md check** (P-02): `find .harness/harness/features/FEAT-25-claim-feature-root -iname
DESIGN.md` returns nothing. No design contract exists for this feature at all — there is nothing
for Mode A or Mode B to hold this diff against.

**Output-surface check**: grepped for `print(`/`sys.stdout`/`sys.stderr` usage. `factory_claim.py`
writes one JSON payload to stdout on success (`factory_cli.payload(...)`) and plain-text
diagnostics (`factory: {TOOL}: ...`) to stderr on every other path — no HTML, no template
rendering, no markup of any kind. This is a batch CLI tool; there is no rendered surface, no
theme, no colour-encoded state, no focus/keyboard concern (G-02: accessibility and theme parity
are explicitly not-applicable here, not merely unchecked).

## One in-remit note: CLI diagnostic message wording (non-blocking)

The diff adds a new branch to `_blocker_reason_text()` in `factory_claim.py` (lines 187–199,
confirmed absent at base `d1ffd7f`) for the case where a claimed issue's `feature:` label
resolves but `plan.yaml` cannot be read. Its two new message strings use a plain hyphen as an
internal clause separator:

> `"issue #{num} carries a feature: label that resolves, but no plan could be read at {path} -
> the feature root does not exist"`

Every other diagnostic string this same tool prints — including the three sibling branches of
this same function (`edge_i`, `unresolvable`, `open`) and every `skip #{num} — ...` line in
`_main()` — uses an em-dash (`—`) as the separator. Because this reason string is interpolated
into `f"skip #{num} — {reason}"` at the call site (line 386), the emitted line mixes both dash
styles in one sentence, e.g. `skip #12 — issue #12 carries a feature: label that resolves, but no
plan could be read at /path - the feature root does not exist`. Cosmetic, not a defect: it does
not affect meaning or machine-readability (the JSON success payload is the only parsed output;
this is stderr diagnostic text only). Severity: low, non-gating.

I also checked whether this new message could misfire on the post-migration normal state (P-09),
since this feature moves `FEATURES_ROOT` from `.harness/features` to `.harness/harness/features`
(confirmed via diff, line 31). `root_exists()` checks the *new* migrated path, and that path
exists on disk now, so the "feature root does not exist" branch does not fire on the current
normal state — only the sibling "plan.yaml is missing or unparseable" branch would. No defect
here.

## Verdict

Scope-out is correct. No rendered surface, no design contract, no accessibility or theme surface
in this diff. One low-severity, non-blocking wording note recorded above per the dispatch's
explicit invitation to rule on CLI message text.
