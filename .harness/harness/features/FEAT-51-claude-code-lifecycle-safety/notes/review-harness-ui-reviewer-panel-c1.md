# UI Review — FEAT-51 — panel-c1 (Mode B, pinned `fa5ce88e07d0a094570da25bf1110370ef84fcab`)

## Verdict: PASS, advisory only

No rendered UI surface in this diff. One human-facing text surface exists — the operator-terminal
refusal messages — and it was audited as directed. Findings are advisory (low), confirming a
finding SIMPLIFY already raised; nothing here gates.

## 1. Census (the scoping evidence, not a prediction)

`git -C <worktree> diff --stat 0bc57c88..fa5ce88e`: **70 files, +11010/-167.**

By extension bucket (`git diff --stat` scoped per glob, sums to 70):
| bucket | files | +/- |
|---|---|---|
| `.py` | 15 | +1427/-125 |
| `.md` | 44 | +4713/-35 |
| `.yaml`/`.yml` | 5 | +4525/-0 |
| `.sh` | 3 | +42/-6 |
| `.json` | 2 | +176/-1 |
| `.html`/`.css`/`.scss`/`.tsx`/`.jsx`/`.vue`/`.svelte`/`.less` | **1** | +127/-0 |

The one markup hit is `notes/ship-review-plan-signature-c9.html`. Read at the pin: it carries a
closing footer — `Derived from ship-review-plan-signature-c9.md — the markdown is the record; do
not edit this file. Regenerate with bin/render-brief.py.` — confirming it is a generated ship-review
report artifact from an earlier plan-panel cycle, not product UI. Zero component/style files touched.

**Scripts** (`.sh`+`.py`): 18 files — the enforcement/test layer this feature is actually about.
**Markdown**: 44 files — almost entirely per-cycle notes/receipts/research under
`features/FEAT-51.../notes/`, plus `BRIEF.md`, `DECISIONS.md`/`DECISIONS-INDEX.md`, two `SKILL.md`
files. None of these specify spacing/colour/interaction for a rendered surface (P-03) — they are
process records, not a design contract.

## 2. DESIGN.md object check

`git -C <worktree> cat-file -e fa5ce88e:.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/DESIGN.md`
→ **fatal: path does not exist in fa5ce88e.** No `DESIGN.md` exists for this feature at the pin.
Confirmed by direct object check, not inferred from the feature's nature.

## 3. The one in-scope surface: the two quarantine refusal messages (SC-04, SC-11)

Read verbatim at the pin.

**`check-domain.sh:1698-1704`:**
```
check-domain: BLOCKED — {file} is canonical, but {agent} holds no live claim for {feature}.
Its parent is gone and a replacement may already be writing.
  Write the completed result to {quarantine} instead.
  It becomes canonical only when the resumed parent runs quarantine.py adopt on that file.
```

**`plan-sign-gate.py:408-414`:**
```
Refused: {rel} is canonical, but {agent} holds no live claim for {feature}. Its parent is
gone and a replacement may already be writing.
Write the completed result to {quarantine_rel} instead.
A quarantined result becomes canonical only when a resumed parent runs quarantine.py adopt.
```

**Does each tell the operator what happened, why, and the one next action, without opening
source?** Yes, both. Each names the blocked path, states the cause (no live claim, parent gone,
race risk), and gives a single literal remedy command/path plus the recovery mechanism
(`quarantine.py adopt`). An operator reading either message end-to-end has everything needed to act.

**Is the quarantine path copy-pasteable?** Yes. Both call the identical
`inflight_registry.quarantine_rel()` (`inflight_registry.py:279-288`), which returns a concrete,
fully-interpolated relative path — `.harness/harness/features/<feat>/quarantine/<agent>-<session8>/
<basename>` — never a placeholder. It is relative-to-repo-root, not absolute; nearby in
`plan-sign-gate.py`'s own header (`TOOL_PATH`, lines ~34-38) the file states a rule that a
copy-pasteable command should prefer an absolute, disk-confirmed path when one is available and
fall back to relative otherwise. That rule is applied to `TOOL_PATH` but not to the quarantine
path in either gate — a minor inconsistency, not a functional defect, since a relative path from
repo root is normally what an agent/operator is already anchored at.

**Is the duplicated wording consistent, or does the same situation read as two different errors
depending on which tool the operator reached for?** **Confirmed inconsistent — this is a real
finding, and it directly contradicts a rule the file states about itself.** `plan-sign-gate.py`'s
own header (lines ~53-55) says: *"ONE refusal text, used verbatim for EVERY denial. A second
wording would drift and the operator would learn two different answers to one question."* That
rule is written about the pre-existing `sign-approval` `REASON` constant, but the same file now
carries a second, freshly-added refusal (the FEAT-51 quarantine block) that does not match
`check-domain.sh`'s wording for the *identical* situation:
- lead word differs: `check-domain: BLOCKED —` vs `Refused:` — a different severity-word for the
  same event depending on which tool an operator was using when the write failed.
- trailing sentence differs: `...adopt on that file.` (check-domain.sh) vs `...adopt.` (plan-sign-
  gate.py, no `on that file`).
- indentation differs (2-space continuation lines in check-domain.sh, flush-left in
  plan-sign-gate.py) — cosmetic only.

The shared middle sentence (`is canonical, but {agent} holds no live claim for {feature}. Its
parent is gone and a replacement may already be writing.`) is character-identical between the two,
and the quarantine path itself is byte-identical (same function). So the operator gets the same
diagnosis and the same remedy path either way — only the framing words around it differ. This
**confirms** the SIMPLIFY finding rather than contradicting it.

**Does it rise above a backlog row?** No. Nothing here is misleading or actionable-wrong; an
operator who reads either message in full still reaches the correct remedy. It is the exact
class of drift the file's own docstring warns against, so it is worth fixing opportunistically
(e.g. hoist a shared `_ORPHAN_REFUSAL` template both gates format), but it does not meet the `high`
bar (no concrete "operator does X, breaks Y" scenario) and a fix is not compelled by any signed
decision. Leaving it as a backlog item alongside the SIMPLIFY finding is correct.

## 4. Accessibility / theme parity

**Explicitly not applicable.** Both surfaces are plain-text stderr written to a terminal/agent
transcript: no colour is used to encode state, no theme (light/dark) exists for stderr text, no
markup or interactive elements are present. There is nothing for a contrast check or a theme-parity
check to evaluate. This is stated, not omitted.

## code_grade

**B+** — the message content is correct, complete, and gives a copy-pasteable, single next action;
the identified defect is a cross-tool wording drift the file's own header explicitly warns against,
already known (SIMPLIFY), and does not rise to a `must_fix`.

## Open questions
None blocking. One non-blocking backlog note: consider a shared refusal-template constant for the
two quarantine messages, consistent with `plan-sign-gate.py`'s own "one refusal text" rule — not
gating, already tracked by SIMPLIFY.
