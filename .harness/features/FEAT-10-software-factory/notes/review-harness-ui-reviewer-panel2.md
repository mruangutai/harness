# UI review — FEAT-10 · panel2 · CLI output surface

Mode B. Pinned SHA `8bbb246022d660492b14fcb9bafec7729b0ba23d`, diff only (53 files; `2a3e91c` and
`b89c00a` not opened). Contract: `.claude/skills/harness/bin/factory_cli.py:10-16` (module
docstring) + `.harness/features/FEAT-10-software-factory/DESIGN.md` C-3 (`## C-3`, lines
147-207ish). Surface audited: stdout/stderr/exit code of the seven factory tools, plus
`check-state.sh:858-908` (INV-24) per explicit dispatch instruction.

**No rendered surface exists here** — everything below is source-level (argv, `print`, `sys.exit`,
exception construction). That is a strength for this review, not a gap: the whole surface is text
I can read exactly as the operator will see it, so the observability caveat this role normally
states does not bind this review.

## VERDICT: PASS, severity_max med

Two genuinely new findings, both med. Two carried findings confirmed still present, unchanged
(F1, F3 — cited, not re-derived). No must_fix; nothing rises to high.

---

## New finding 1 (med) — `factory_workspace.py`'s git-failure path is the one exception class in
the whole factory that was never registered for clean reporting, and it fails in two different,
never-observed shapes

`factory_workspace.py:38-61` (`run_git`) prints one honest diagnostic line to stderr and then
raises a plain `RuntimeError` on a non-zero git exit — fully anticipated, documented in the
function's own docstring ("a failed git command is not 'nothing to do'"). But
`factory_workspace.py:140` registers only `expected=(factory_config.FleetError,)` — unlike every
sibling entry point (`factory_config.py:185`, `factory_decompose.py:440`, `factory_claim.py:337`,
`factory_land.py:106`), none of which omit their own module's expected exception type. So the
`RuntimeError` falls through to `factory_cli.run`'s generic trap (`factory_cli.py:88-93`), and the
operator sees **two stderr lines for one failure**, the second one mischaracterising a routine,
documented case as unexpected. Measured, not inferred — ran the actual `run_git`/`factory_cli.run`
code in-process with `subprocess.run` mocked to return exit 128 (no source file touched; read-only
per this role):

```
factory: workspace: git clone https://github.com/acme/widgets.git /tmp/x failed (exit 128): fatal: repository 'https://github.com/acme/widgets.git' not found
factory: workspace: unexpected failure: RuntimeError: git clone https://github.com/acme/widgets.git /tmp/x failed with exit 128 — re-run with FACTORY_DEBUG=1 for a traceback
```

Second, sharper instance of the same asymmetry: a **missing git binary**. `factory_gh.py:90-95`
gives a missing `gh` a purpose-built message — `"gh not found: gh — install gh, or point
FACTORY_GH at its path"`. `run_git` has no equivalent for a missing/misconfigured `FACTORY_GIT`;
`subprocess.run` raising `FileNotFoundError` is not caught at all in `factory_workspace.py`, so it
also falls into the generic trap. Measured the same way:

```
factory: workspace: unexpected failure: FileNotFoundError: [Errno 2] No such file or directory: 'git' — re-run with FACTORY_DEBUG=1 for a traceback
```

No mention of `FACTORY_GIT`, no "install git" guidance — worse than the RuntimeError case, because
here the operator gets nothing but a raw Python errno string for a case the sibling module solved
cleanly one file over.

**This is a new instance of the same defect class as carried finding F3**
(`.harness/features/FEAT-10-software-factory/runs/panel-validator/digest.md`, rank 3): an
anticipated exception type omitted from a tool's `expected=` tuple, so it prints as `"unexpected
failure: {ClassName}: ..."` instead of the clean single-line grammar the rest of the contract
uses. F3 was about `YamlParseError` from `harness_yaml.load_file`/`load_plan` (still present,
unchanged at the pin: `factory_config.py:73`, `factory_decompose.py:279` are still raw calls, not
wrapped). This finding is the same class at a different call site (`RuntimeError`/
`FileNotFoundError` from `run_git`, not `YamlParseError`). The prior panel priced F3 at med on the
grounds that the path still fails closed at exit 2 with zero mutation and the actionable detail
(here, the real git stderr line) still reaches the operator in the RuntimeError case — same
reasoning applies, so med, not high. The FileNotFoundError sub-case is thinner still on
information content and is worth a look when F3 is fixed, since the same fix pattern (wrap at the
source, register the wrapper's type in `expected`) covers both.

Test coverage note: `test-factory-workspace.py`'s only check on this path, `(K)` (lines ~266-270),
replaces `run_git` wholesale with a recorder that raises `RuntimeError` directly — it never
exercises the real `run_git`, so it asserts exit code 2 only and has never observed the two-line
stderr shown above. Nothing in the tree has measured this until this review.

---

## New finding 2 (low, advisory) — `check-state.sh` INV-24: three of four messages lack the
remediation step the file's own convention establishes elsewhere

INV-24 (`check-state.sh:858-908`, never reviewed before this pin) is judged here on the dispatch's
own bar: name the violation, name the values, say what to do. Its own file sets a real precedent
for the third part — `check-state.sh:143` ("Run /harness-init."), `:312-314` ("Set it in
.harness/harness.json (default 20)."), `:920-921` ("Pin the repo... or turn sync off.") all end
with an instruction. Three of INV-24's four `bad.append` messages do not:

- fleet.yaml absent (`:879-881`) — names the violation and the path, no instruction (e.g. "declare
  the repository in fleet.yaml").
- fleet file does not parse (`:885`) — names the parse failure, no instruction.
- **duplicate-issue collision** (`:904-907`) — the invariant with real operational teeth (two
  features claiming one board issue); explains the consequence ("the board and the harness
  disagree about what is in flight") but gives the operator no path to resolution. This is the one
  worth fixing first if any are — it is the message an operator is least likely to already know
  how to act on.

The fourth (`:890-892`, repo not declared) is fine — it lists the fleet's valid names, which
functions as the instruction. This is not a C-3 violation (`## C-3` explicitly binds "the five
tools with a command line," and `check-state.sh` is not one of them) — it is an internal-
consistency gap in never-reviewed code, judged against the standard the file itself sets.

---

## Confirmed carried, not re-derived

- **F1** (`runs/panel-validator/digest.md`, rank 2, med) — `factory_land.py:75-84`'s `"already
  exists"` predicate on `gh pr create` failure is unchanged at the pin: same substring check, same
  fail path past the push (point of no return). Still present.
- **F3** (rank 3, med) — `factory_config.py:73` (`load_fleet`) and `factory_decompose.py:279`
  (`load_plan`) are still raw, unwrapped `harness_yaml` calls; no tool's `expected=` tuple includes
  `YamlParseError` (verified again at the five call sites listed above). Still present, unchanged.
  New finding 1 above is the same defect class, new call site.

## The two named priority anchors, judged directly

- **`factory_decompose.py:287-293`** — the missing-`feature`-key refusal. Clean: `refuse(TOOL,
  "plan has no usable feature id", plan_path, "add a top-level \`feature: <FEAT-id>\` key to the
  plan before publishing")`. Names what, names the value (plan path), gives a concrete next step.
  Consistent in shape with the sibling "plan not signed" refusal three lines above. Confirmed by
  reading the surrounding control flow that this check runs before `preflight()` — stdout is
  genuinely empty, exit code is 2, matching the documented grammar. No finding here; this anchor is
  clean.
- **`factory_gh.py:268-271`** — `project_field_set`'s new `gh project view` lookup, which raises
  (via the generic `run_gh` wrapper) rather than falling back. Traced through all three callers
  (`factory_decompose.py:370`, `factory_claim.py:330`, `factory_land.py:99`): all three register
  `factory_gh.GhError` in `expected=`, so `factory_cli.run` prints `str(exc)` verbatim — the clean
  single-line C-3 shape, not the generic "unexpected failure" wrapper. Considered and downgraded to
  not-worth-listing: this path's `value` (board owner only) and `next_step` (gh's own first stderr
  line) carry less structural context than its two sibling error paths in the same function (field-
  not-found, option-not-found, both of which name the board *number* in their message), but the
  message is still legible and actionable end to end, and C-3 does not specify a required shape for
  `next_step` beyond "the operator can act on it." Not manufacturing a finding against a bar the
  contract doesn't set — noted here as considered, not filed as a defect.

## Also considered, deliberately not filed

- The `"issue not found on the board"` refusal (`factory_claim.py:232-235`, and
  `factory_land.py:94-98` via a hand-built `GhError`) sets `next_step` to a location string
  (`"board {owner}/{board_number}"`) rather than an instruction, unlike sibling refusals in the
  same functions. The message stays comprehensible (issue number + board named), the fix is
  inferable, and C-3 does not define `next_step` semantics narrowly enough to call this a
  violation. Style nit, not filed as a ranked finding.
- `factory_cli.py:10-16`'s module docstring states exit 2 means "nothing mutated" without the
  qualification `DESIGN.md:160`/171-179 (the point-of-no-return table) carefully states
  ("...before the tool's point of no return"). This is developer-facing documentation, never
  reaches stdout/stderr, and the operator never sees it — outside this role's remit (operator-
  facing text), noted only as a drift between two contract documents worth a maintainer's glance.

## Exception-class-name leak (prior panel's F3 framing) — checked broadly, not systemic beyond F3
+ new finding 1

Grepped all seven tools for raw `except Exception`/bare exception printing outside the
`GhError`/`FleetError` machinery: `factory_decompose.py:71` and `:207` both swallow silently
(no print, no leak). No new leak site found beyond the `YamlParseError` (F3) and `run_git`
exception (new finding 1) cases above — the custom-exception-with-controlled-`__str__`() pattern
(`factory_gh.GhError`, `factory_config.FleetError`, both with explicit docstrings forbidding a raw
class name in `value`) is otherwise applied consistently.

## Open questions

None blocking. One non-blocking observation for the harness owner: F3's fix point (source-level
wrap, per the prior panel's decided-not-yet-implemented Q2) would be the natural place to also wrap
`run_git`'s `RuntimeError`/`FileNotFoundError` — one fix pattern closes both instances of the same
defect class.
