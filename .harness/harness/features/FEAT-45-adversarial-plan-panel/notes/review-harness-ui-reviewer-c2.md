# UI review — FEAT-45 adversarial plan panel — cycle 2

`review_sha` 70fd4414c7d472f50ae17452289e44782f32b5b5. Scope: `git diff main...70fd441` (three-dot,
merge-base `ba338d8`) — the branch's own contribution only, not `main`'s already-reviewed content.

## Census (measured, not predicted)

`git diff --name-only main...70fd441` → **66 files**. Extension breakdown against the rendered-UI set
(`html|css|scss|tsx|jsx|vue|svelte|less`): **zero matches** —

```
$ git diff --name-only main...70fd441 | grep -iE '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'
(no output)
```

All 66 are `.md`, `.sh`, `.ts` (test files, not components), `.py`, `.yaml`, `.json`. No `DESIGN.md`
exists anywhere in this feature's directory (`find .../FEAT-45-adversarial-plan-panel -iname
DESIGN.md` — empty) and no file in the diff is named `DESIGN.md`. Consistent with repo-tier
Expertise P-01: this repo ships no rendered UI, so the classic Mode B audit (fidelity/states/a11y/
theme-parity against a design contract) has no object to examine this cycle, as in c0/c1.

**Verdict for that half: `in_scope: false`, PASS by measurement, not inference.**

## The one surface dispatch named explicitly — operator-facing INV-32 message text

Read at the pin, not inferred (`git show 70fd441:.claude/skills/harness/bin/check-state.sh:170-242`).

The restructured gate (closing SC-05) now has three branches per finding:

```python
if disposition == "resolved":
    warn.append(f"INV-32: {feat} finding {fid} disposition resolved.")
elif fid in overruled:
    warn.append(f"INV-32: {feat} finding {fid} disposition overruled.")
elif severity not in {"info", "low", "med"}:
    bad.append(f"INV-32: {feat} finding {fid} is {severity or 'unrated'} and remains open without an operator overrule.")
```

Rendered to the operator (`check-state.sh:1868-1869`): `warn` lines print as `  note       <text>`,
`bad` lines as `  VIOLATION  <text>`. So the two new lines appear as:

```
  note       INV-32: FEAT-45... finding PF-xxxxxxxx disposition resolved.
  note       INV-32: FEAT-45... finding PF-xxxxxxxx disposition overruled.
```

**Readability: no ambiguity finding.** The `note`/`VIOLATION` prefix distinguishes non-blocking from
blocking at a glance; the two new lines differ only in their terminal word and map 1:1 onto the two
non-blocking outcomes the finding lifecycle defines (`disposition: resolved` written by pm per
`harness-spec-driven/SKILL.md:112-115`, vs. an `approval.rulings` overrule recorded by the main
session). An operator who has seen one panel run before will not confuse them, and confusing them
carries no consequence since both are advisory.

**One non-blocking style note, new text this cycle, not filed as a finding:** the two new lines drop
the copula present in neighboring `warn` messages in the same file — compare `"approval is pending —
awaiting the user."` (`check-state.sh:164`) or `"run counting is INACTIVE"` (`:382`) against
`"disposition resolved."` / `"disposition overruled."` (no `is`). Grammatically terser than the house
voice but not ambiguous — recording it as an `info`-severity observation only, not a `must_fix`.

**Independent check on the fail-open bug the dispatch asked about (M1, c0):** absent `severity` key
→ `item.get("severity", "")` → `""`; YAML-null `severity` → `item.get("severity")` → `None` →
`str(None).strip().lower()` → `"none"`. Neither `""` nor `"none"` is in `{"info","low","med"}`, so
both fall through to the `bad` branch (fails closed) provided `disposition != "resolved"` and the
finding id is not in `overruled` — which holds for a freshly-produced finding with no ruling
recorded. `test-check-state.py:2984-2989` exercises exactly this trio (`PF-unrated`, `PF-absent`,
`PF-null`) and asserts `code == 1`. This corroborates rather than substitutes for code-reviewer's
verdict on the gating logic itself, which is outside this role's lens — I looked only at the text an
operator reads, per dispatch's carve-out, and used the trace to confirm the WARN/VIOLATION split I
was asked to judge is not miscategorizing a should-be-blocking case as advisory.

## Withhold message (M7) — re-confirmed unchanged, not re-raised

`check-state.sh:219`'s `bad` message — `"INV-32: {feat} finding {fid} is {severity or 'unrated'} and
remains open without an operator overrule."` — is byte-identical to the text c1 cited for the carried
`M7` (`low`, states the fact, not the remedy). Confirmed by direct read at `70fd441`, not by trusting
the carry-forward note. No new defect; **not re-raised**.

## Accessibility / theme parity

Not applicable — the changed surface is CLI/batch text with no colour-only state encoding and no
theme. Stated explicitly per this role's own gotcha G-02, not omitted.

```yaml
VERDICT: PASS
DIGEST:
  headline: No rendered UI surface in branch scope (66 files, 0 UI-extension matches, no DESIGN.md); the two new INV-32 operator-facing lines read unambiguously; withhold message M7 unchanged, not re-raised.
  mode: B
  in_scope: true
  severity_max: none
  findings: 0
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: ["not applicable — CLI/batch text output, no rendered surface, no colour-only state encoding"]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-ui-reviewer-c2.md
```
