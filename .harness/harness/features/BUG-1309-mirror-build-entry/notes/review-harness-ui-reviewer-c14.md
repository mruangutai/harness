# UI Review — BUG-1309-mirror-build-entry — panel-c14

## Mode B, adversarial audit of terminal-surface CLI copy

## Census (measured, not predicted)
`git show --stat ac2bc0bb` at c8b23e03: 4 files, all `.py` —
`.claude/skills/harness/bin/merge-gate.py`, `.claude/skills/harness/bin/gh-sync.py`,
`tests/integration/test-merge-gate.py`, `tests/integration/test-gh-sync.py`. Zero
`html/css/scss/tsx/jsx/vue/svelte/less` hits. Consistent with repo-tier P-01 (harness
ships no rendered UI). No `DESIGN.md`/prototype touched — Mode A not applicable.

Per dispatch, the operator-visible surface here is terminal text: `merge-gate.py main()`'s
`permissionDecisionReason` deny strings, and `gh-sync.py _build_entry_recovery_notice`'s
stderr notices. Judged as CLI copy below (P-06: dispatch names this adjacent surface
in-remit despite no rendered UI existing).

## Findings

**F-1 (new, PASS)** — `merge-gate.py main()`'s new multi-owner deny (feature_for now returns
a list; `len(owners) > 1` branch, ~line 165): `'merge-gate: {branch} is claimed by more than
one feature record ({names}), so this merge cannot be attributed to one feature. Correct the
duplicated top-level "branch" field in those feature.json records before merging; no receipt
command clears this.'` — actionable (names the field to fix and where), matches the
established sibling pattern in the same function (`fact, so consequence. action.`), and
correctly withholds a receipt command per contract F-01 ("no receipt command clears this").
Confirmed test-enforced: `test-merge-gate.py` new case asserts `"gh-sync.py" not in reason`.
No promised command that fails to clear the condition — there is no command offered at all,
which is the correct shape here.

**F-2 (new, PASS)** — `gh-sync.py _build_entry_recovery_notice`'s new `recover-terminal`
branch (feature_schema.recovery_command_for path, ~line 1394): `"...the MERGE is refused
until gh-sync.py {command} {os.path.realpath(feat_dir)} --yes records the terminal
receipt"` — actionable, includes the feature-dir argument and `--yes`, consistent with the
sibling era-exempt message three lines above in the same function. Test-enforced
(`test-gh-sync.py`: asserts `expected_command in result.stderr and " --yes" in
result.stderr`).

**F-3 (advisory, non-gating, LOW)** — `gh-sync.py _build_entry_recovery_notice`'s `command
== "open"` branch (~line 1390): `"...the MERGE is refused until gh-sync.py open records
opened"` omits the required `<feature-dir>` positional argument. Confirmed
`gh-sync.py open` needs it (`cmd, feat_dir = argv[0], argv[1]`; usage string lists
`<feature-dir>` as required) — a reader who types the string exactly as printed gets
`usage: gh-sync.py open|...`, not the recovery. Its sibling in `_build_entry_preflight`
(same file, unchanged by this commit) gets this right: `"Run gh-sync.py open
{os.path.realpath(feat_dir)} first."` — so the two messages a reader can hit back-to-back
for the same condition now visibly disagree on whether the path is required.
**Not introduced by ac2bc0bb** — confirmed byte-identical against `de04d841` (this exact
string was the function's unconditional message before this commit; the diff only wraps it
in a new `if command == "open":` guard, moving it unchanged). Per this role's own precedent
(P-11/G-13: a wording defect already present verbatim in a pre-existing sibling is a
non-gating note, not a fix filed against untouched code), this does not gate. Recording it
because the commit made the divergence adjacent and visible for the first time, and it is a
real actionability gap the next pass on this file should close.

## Out of lens
`git_merge`'s global-flag parsing change (merge-gate.py) is logic, not copy — no operator
text changed there. The dispatch's fail-open discrimination probe belongs to CodeRev/SecRev;
not re-litigated here.

## Accessibility / theme parity
N/A — pure stdout/stderr text, no color-only state encoding, no rendered surface to check
contrast or theme parity against (G-02).

## Verdict rationale
No `must_fix`. F-3 is real but explicitly non-gating under this role's established
precedent for untouched pre-existing text. F-1/F-2 (the actual new copy this commit
introduces) are both actionable and test-enforced.
