# UI review — BUG-240 — cycle 0 — Mode B

**Scope examined.** No `DESIGN.md` exists for this feature (confirmed:
`git -C worktree ls-tree ed047fde .../BUG-240-workspace-hard-reset-guard` lists only
`BRIEF.md`/`STATE.md`/`feature.json`). Both files named in the batch context read in full via
`git show ed047fde:<path>`. `factory_workspace.py`'s diff is 46 lines: docstring paragraph,
`import harness_boundary`, `_BIN_DIR`, `_control_plane_root()`, and the two `factory_cli.refuse()`
calls at lines 143 and 156 — no rendered UI, no HTML/CSS. `test-factory-workspace.py`'s diff is
199+ lines of assertion code, no operator-visible surface of its own. Per dispatch, the CLI
refusal copy is in-remit and is audited below.

## Refusal-copy audit (in-remit per dispatch)

Both new `refuse()` calls populate all four `factory_cli.refuse(tool, what, value, next_step)`
fields, matching the grammar `body()`/`message()` impose
(`factory_cli.py:32-43`): `factory: {tool}: {what}: {value} — {next_step}`.

Composed lines (tool=`"workspace"`, value=`os.path.abspath(path)` in both):
- Identity: `factory: workspace: refusing to reset the harness control-plane checkout: <path> —
  the control plane is never its own scratch workspace: point workspace_root in fleet.yaml at a
  directory that is not this checkout`
- Dirty: `factory: workspace: refusing to reset a checkout with uncommitted changes: <path> —
  commit, stash or discard the work in that checkout, or point workspace_root at a scratch
  directory`

**REQ-03 (path + which condition + exit status):** satisfied. Both lines name the checkout path
via `value`; the distinguishing tokens ("control-plane" vs "uncommitted") make the two conditions
unambiguous — test cases 2/3 and 5 pin exactly this discrimination
(`test-factory-workspace.py`: `"uncommitted" in err_lines[0]` /
`"control-plane" in err_lines[0] and "uncommitted" not in err_lines[0]`). Exit status is
`EXIT_REFUSED = 2` via `refuse()`, confirmed at `factory_cli.py:26-52`.

**New, non-blocking finding — `what` grammar diverges from the house convention.** I grepped
every `factory_cli.refuse(` call site in the repo (`board_lifecycle.py`, `factory_claim.py`,
`factory_decompose.py`, `factory_land.py`, `factory_workspace.py` — 20 sites). Every sibling's
`what` argument states the detected **fact/condition** as a noun phrase: `"branch equals the
default branch"`, `"repository not recognised"`, `"project is not linked to this repository"`,
`"field is not single-select"`, `"cannot audit"`, `"issue not found on the board"`, `"station
option not offered by the board"`, `"issue enumeration may be truncated"`. None restate the
refusal verb — `refuse()` itself already signals refusal. The two new BUG-240 sites are the only
ones in the population whose `what` begins `"refusing to reset …"`, folding the action
(refuse) into the fact field. Both composed lines still read clearly and remain fully
actionable, and REQ-03's naming requirement is met either way — this is a convention-consistency
observation, not a defect. Low severity, does not gate.

## Not applicable
Accessibility / theme parity / rendered layout: not applicable — batch text on stderr, no colour
encoding, no visual surface to render. Confirmed not-applicable rather than omitted.

## Verdict
PASS. No must_fix. One low-severity advisory (wording convention) recorded above, distinct from
the settled F-01/F-02/ALT-5 items and not re-litigating any of them.
