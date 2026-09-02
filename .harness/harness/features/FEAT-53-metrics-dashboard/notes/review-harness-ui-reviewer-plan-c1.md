# UI-reviewer — DESIGN.md contract review (Mode A, pre-build) — FEAT-53

**Verdict: FAIL.** 4 MUST-CHANGE-BEFORE-SIGNATURE findings, 4 ADVISORY. Highest severity: high
(twice) — an unlabelled honest-gap for the usage/attribution KPI, and a fully unpinned
keyboard/focus/screen-reader contract.

**Evidence basis, stated plainly:** DESIGN.md, BRIEF.md, plan.yaml and the routing/signals research
note were read in full at `.claude/worktrees/harness/FEAT-53/…`. The prototype
(`notes/prototypes/FEAT-53/`, 8 components + theme.js + fixture.js + README) was **read as source
only — I did not render it.** Its own README says the same of its author ("Not verified: how it
looks. No browser was available"). I did not verify appearance beyond what is legible from source
(colour tokens, hatch CSS, structure). `code_grade: n_a` — no code exists to grade.

## 1 — Substrate smuggling: not found, one enforcement gap

No second substrate. The hatch fill (rule 4) composes a StyleX `repeating-linear-gradient` over an
Astryx primitive; StyleX is already a declared **Astryx peer dependency**, confirmed in the
prototype's own README ("`@stylexjs/stylex` 0.19.0 is listed explicitly because Astryx declares it a
peer") and `theme.js`, which applies it through Astryx's `style` escape hatch with no extra build
step. Genuinely a composition, not a smuggled dependency.

- **F1 [ADVISORY, med].** Rule 3 ("charting is not a substrate exception… contributes no components,
  no typography, no palette", DESIGN.md:35-38) is **asserted, not pinned with a check** — unlike
  rule 2, which names its own grep ("`grep` for a hex literal outside that file is a violation, and
  that is the check", DESIGN.md:28-30). No task verify greps for a chart-library default
  palette/theme prop left unset. Rule 3 also names **TanStack Charts** specifically; D-08
  (plan.yaml) names a fallback trigger to React Charts on 4 named CAP failures, and rule 3's wording
  does not visibly survive that swap. Recommend generalizing rule 3 to "the charting library" and
  naming a concrete check (e.g. "every colour/dash/marker prop on a chart component resolves to a
  token; no chart-library default colour scale is left unset").

## 2 — Honest-gap states: hardest look, one is missing entirely

Two of the three named real gaps are precisely specified:
- **Trend-empty → S-1** (DESIGN.md:229-236): exact copy, exact treatment ("no axes, no gridlines, no
  zero baseline, no chart mounted at all"). Two builders converge; unmistakable for a measurement.
- **Python-only ratio → S-3** (DESIGN.md:249-259): exact sentence template, disclosure requirement,
  and the SC-06 anti-literal rule stated three times over. Precise and unconfusable.

- **F2 [MUST-CHANGE, high].** The third named real gap — **77% of commits carry no attribution
  prefix** (`notes/research-FEAT-53-routing-and-signals.md`, Signal 2), giving KPI 6 large NAMED
  unattributed buckets (`no_prefix`, `human`, `feature_only`, `unresolvable_step_id`, D-13) — has
  **no C-4 state and no panel-level visual spec at all**. C-1 gives it one sentence: "the two-tier
  split, with the unattributed count named on the tile rather than dropped" (DESIGN.md:148-149).
  C-2 declares "**Only two shapes exist** in this feature" (DESIGN.md:159) — a pre-binned ordinal
  histogram and a temporal line chart — and neither fits a categorical multi-bucket breakdown by
  tier and unattribution reason. Two builders will visibly diverge (donut vs. stacked bar vs. plain
  list). This is exactly the "gap with no state" the dispatch asked to find.

- **F3 [MUST-CHANGE, med].** **S-2's hatch fill pins only the 45° angle** ("45° hatch fill",
  DESIGN.md:244 and 273) and never states stroke width or period. The prototype independently chose
  `repeating-linear-gradient(45deg, ${T.unavailable} 0 1px, transparent 1px 6px)` — 1px stroke, 6px
  period (`theme.js` hatchFill) — a value invented by the prototype's author, not derivable from
  DESIGN.md. Two builders produce visibly different fills from the contract alone. Pin stroke width
  and period next to the angle.

- **(a)/(b) answers for S-1, S-3, S-4:** precise enough for two builders to converge, and none is
  mistakable for a real measurement — each pins an exact copy string, and each differs from a real
  value in at least glyph or axis presence. **S-2 fails (a)** on F3 above and on F5 below.

## 3 — Accessibility and light/dark parity as contract terms

**Contrast table recomputed and verified correct.** WCAG 2.x relative-luminance against `surface`
(`#F6F7F9` light / `#161A21` dark), all 9 tokens, both themes: computed ratios match the table's
claimed values to 2 decimals in all 18 cells, including the two near-miss rows (`grade-4` light
4.92, `unavailable-stroke` 3.00/3.89). `series-1` vs `series-2`'s stated hue-only separation (1.51
light / 1.21 dark) also checks out. The table is trustworthy; no row fails.

Non-hue redundancy table (§C-3) is genuinely pinned per-distinction (dash+marker+label for series,
axis-position+label+count for bins, etc.) — checkable, not asserted-and-stopped.

- **F4 [MUST-CHANGE, high].** Beyond colour, **nothing pins keyboard operability, focus visibility,
  or focus management, and almost nothing pins screen-reader naming.** The only ARIA reference
  anywhere in the document is CAP-05's `aria-hidden` on the decorative chart. No mention of a focus
  ring/outline token, of what is a focus stop and what is not (window control, theme toggle, tile
  links, table row links, disclosures), or — critically — **focus retention across the three-route
  drill and the theme toggle**, which is the exact defect class (focus loss on state change) known
  to ship invisibly to unit tests. `ui` has no automated runner (BRIEF `## Verification gaps`), so
  SC-15 (inspection) is the *only* gate here, and it can only check what DESIGN pins — right now
  that is nothing for this dimension. This is a completeness gap a reviewer cannot catch post-build
  because there is no contract term to catch a violation of.

## 4 — The three `verify: uat` criteria

- **SC-02** (reach a working dashboard via the documented command): executable as specified — this
  is a documentation/entry-point criterion (T-17), not one DESIGN.md needs to pin further.
- **SC-11** (drill via tile → `/features?sort=` → `/features/$featureId`): **executable.** The route
  table and URL-only state (DESIGN.md:152-166) are concrete enough for a user to follow and check.
  Minor gap only: the window-selector control's shape/placement (dropdown vs. segmented control) is
  never pinned — doesn't block SC-11's execution, noted as F8.
- **SC-08** (a user viewing a pre-capability feature sees stated absence, never a zero/flat chart):
  **presupposes a pin DESIGN.md never makes.** S-2 is written entirely in "the feature table"
  register — a multi-feature list where "axes are drawn, because **other features** have data"
  (DESIGN.md:238-239). It never states what the single-feature drill route
  `/features/$featureId` (C-1's third level: "that feature's… trend lines", DESIGN.md:157) shows
  when *that one feature itself* is pre-capability — there is no "other feature" on that page to
  draw axes against. SC-08's most natural reading is exactly this page. This is F5 below and the
  concrete missing pin SC-08's hand-test needs.

- **F5 [MUST-CHANGE, med].** Pin the single-feature-route (`/features/$featureId`) treatment for a
  pre-capability feature explicitly — state whether it is S-1's full-region replacement (there is no
  contrasting feature on this page) or a scaled S-2 treatment, and what it says.

## 5 — CAP-to-task trace, both directions

**Forward — complete.** CAP-01…CAP-13 → T-15 (verify enumerates all 13 by id). 6 tiles → T-06
(throughput+rework), T-08 (defects), T-07 (grading), T-09 (attribution), T-11 (touchpoints), rendered
by T-14. 3 routes → T-13. S-1…S-4 → T-14 (`NoShipRecords`/`PreCapability`/`GradingCaveat`/
`UnavailableValue`, verify greps exactly those names). Theme toggle → T-13. Nothing forward-traced is
missing a task — the KPI-6 gap above is a **DESIGN spec gap**, not a missing task; T-14/T-15 will
build *something* for it, undirected.

**Backward — none found.** No task's `files:` names a UI surface DESIGN.md does not describe.

## 6 — Internal consistency

- **F6 [ADVISORY, low].** "No modal, at any depth" (Component direction) sits beside two live
  mentions of a "disclosure" (S-2's names list, S-3's extension list, DESIGN.md:247, 254) with no
  statement of whether an Astryx `Disclosure` primitive renders inline (compliant) or as a
  popover/overlay. One clarifying sentence removes the ambiguity.
- **F7 [ADVISORY, low].** "Five states are visually distinct… loaded, loading, empty (S-1),
  absent-for-a-reason (S-4), and pre-capability (S-2)" (DESIGN.md:112-113) omits S-3, immediately
  followed by "C-4 pins the four gap states" — confusing enumeration (S-3 is a persistent
  co-occurring caveat, not an alternate replacement state, which likely explains the omission, but
  the wording invites misreading it as 3-of-4 coverage).
- **F8 [ADVISORY, low].** Window-selector control shape/placement is never pinned in Component
  direction (see §4/SC-11 above).
- No REQ/SC contradiction found; rework, grading-never-a-mean, and file-mix-illustration rules are
  stated consistently across BRIEF, DESIGN and plan.yaml.

## Already-ruled (confirmed present, not filed as new)

Confirmed both (i) T-15's `files:` vs `execution_agent` mismatch and (ii) T-05 verify's
`UnicodeDecodeError` risk (explicitly documented in the prototype's own README, "One caveat for
whoever runs T-05's verify") are real and current in this checkout, per the dispatch's pre-briefing.
Not filed as findings.

## Summary table

| id | severity | disposition | topic |
|---|---|---|---|
| F1 | med | advisory | rule 3 has no falsifiable check; wording tied to one named library |
| F2 | high | **must-change** | usage/attribution KPI has no gap-state and no chart shape |
| F3 | med | **must-change** | S-2 hatch angle pinned, stroke width/period not |
| F4 | high | **must-change** | keyboard/focus/screen-reader contract entirely unpinned |
| F5 | med | **must-change** | S-2 single-feature-route treatment unpinned (blocks SC-08) |
| F6 | low | advisory | disclosure vs. "no modal" ambiguity |
| F7 | low | advisory | "five states" enumeration omits S-3, confusing wording |
| F8 | low | advisory | window-control shape/placement unpinned |
