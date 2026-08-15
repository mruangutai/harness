# Pre-merge delta scope check — FEAT-20-migration-detector — PR #376 at 045dcd9

**Verdict: PASS.** The delta `ea476fd..045dcd9` does add one render surface, measured — but it is
generated output from a pre-existing, unmodified shared tool, not UI authored or changed by FEAT-20.
One real accessibility defect was found in that surface and is recorded non-gating, with the
attribution stated explicitly so it isn't lost.

## U1 — re-run the census over the delta (measured, not assumed to hold)

`git diff --name-only ea476fd..045dcd9 | wc -l` → **32 files** (not the 22 from the `88b1182..ea476fd`
window cited in my prior scope-out — different window, checked fresh).

`git diff --name-status ea476fd..045dcd9`: 12 modified `.md` Expertise files, 1 modified `STATE.md`,
1 modified `feature.json`, 15 added `.md` notes/logs, 1 added `.html`, 2 added
`observations/*.md`. **The census flips: one `.html` file is new to this window** —
`notes/ship-review-2026-08-14.html`, 91 lines with an embedded `<style>` block (CSS custom
properties, a `prefers-color-scheme` media query, an explicit `data-theme` override,
`:focus-visible`, `prefers-reduced-motion`). Its markdown source, `ship-review-2026-08-14.md`, is
also new (125 lines).

**This is the measured finding, and it matters more than the verdict it feeds:** a naive
extension-census "0 render surfaces, still holds" would be wrong for this delta. It does not hold —
it flips, and the flip is real.

**But the surface is not FEAT-20's.** Traced its origin:
- `.claude/skills/harness/bin/render-brief.py` — the generator — is **absent from
  `ea476fd..045dcd9`** (`git diff --name-status` returns nothing for that path) and **present at
  `ea476fd`** (`git cat-file -e ea476fd:.claude/skills/harness/bin/render-brief.py` succeeds).
  Unmodified by this feature.
- The CSS is not FEAT-20-authored boilerplate coincidentally matching a pattern — it is
  **byte-identical** to the same block in every prior ship-review HTML in this repo. Checked
  directly, not sampled: `diff <(sed -n '2,64p' <each-of-9-prior-files>) <(sed -n '2,64p'
  ship-review-2026-08-14.html)` returned **IDENTICAL(2-64)** for all nine — FEAT-03
  (2026-07-31), FEAT-04, FEAT-06, FEAT-10 (×2), FEAT-11, FEAT-12, FEAT-13, FEAT-14 (2026-08-12).
  Only line 1 (the `<title>`) varies per feature.

Conclusion: FEAT-20 did not build, edit, or touch this render surface. It is the ordinary output of
an already-shipped, unchanged reporting tool, incidentally dated inside this review window because
that's when FEAT-20's ship review ran.

## U2 — batch text (only if the delta touched it; it didn't)

Zero `.py` / `.sh` files appear in `ea476fd..045dcd9` (confirmed above via the full name-status
list). The detector's own output strings — `layout: features CLEAN | docs CLEAN`, `examined N
feature dir(s)...`, `[legacy]`/`[migrated]`/`[both]`/`[neither]`/`[unreadable]`, `NOT APPLICABLE:`,
the CANNOT VERIFY wordings — live in `check-state.sh` / `layout_migration.py`, neither touched here.
**Condition not met — not re-reviewed**, per the dispatch's own instruction. The ship-review
markdown/HTML *quotes* those strings narratively (e.g. `features: CLEAN`, `docs: CLEAN`, `examined
20 feature dir(s)...`) but a quote in a report is not the source string; it was not re-audited as
a contract.

## U3 — accessibility and theme parity, explicit for both surfaces in play

**For the feature's own batch text:** not applicable, unchanged — no colour channel exists in CLI/CI
output, and no line of it moved in this delta (see U2).

**For the discovered render surface (`ship-review-2026-08-14.html`): applicable, examined, one
real finding — not a blanket pass and not an omission.**

WCAG contrast ratios computed directly (`python3`, standard relative-luminance formula, verified
against hand arithmetic and rerun to confirm):

| Pairing | Light | Dark |
|---|---|---|
| `--quiet` on `--paper` (`.eyebrow`, `h4`/`h5`/`h6`) | **3.39:1 — fails AA (4.5:1)** | 4.86:1 — passes |
| `--quiet` on `--sunk` (`thead th`) | **3.16:1 — fails AA** | **4.43:1 — fails AA (by 0.07)** |
| `--slate` on `--paper` (`.derived` footer) | 5.33:1 — passes | 7.50:1 — passes |

Two of three `--quiet` pairings fail WCAG AA for normal-size text in **both** themes; the third
fails only in light. This is a real, low-contrast defect in a token used for section eyebrows,
sub-headers, and every table's column headers — legible-but-marginal in isolation, and the kind of
thing that reads fine to a sighted reviewer skimming quickly and fails a contrast checker or a
low-vision reader immediately. Intrinsically this is a WCAG AA failure — **high** severity if it
were introduced or touched here.

**It is not touched here.** Confirmed above: same tool, same bytes, present since 2026-07-31 across
nine prior features. Gating FEAT-20's merge on a defect neither authored nor regressed by this
feature's build would misattribute the defect and delay an unrelated, already-verified feature
without fixing anything — the defect ships again on the next feature's ship-review regardless.
Recorded as a **non-gating open question** for the tooling owner, not a `must_fix` here (P-11:
extending remedy scope into code the diff never touched is not this role's call).

Minor, same-surface, same-provenance, not separately filed: `<th>` cells in the backlog table have
no explicit `scope="col"`; browsers infer it for a simple single-header-row table, so this is a
nicety, not a defect.

## Known limit — not verifiable from source

The backlog table (`B-1`..`B-11`) sits inside `.scroll{overflow-x:auto}`; whether it renders
usably at typical viewport widths, and whether the light/dark toggle behaves as the CSS comment
claims ("the viewer's explicit toggle can override the OS in both directions"), requires actually
rendering the page. Not verifiable from source — human or UAT check required if this template's
fidelity is ever formally reviewed.

## What this review does not re-litigate

R-1..R-5 (panel), and the plan-time vacuous-CLEAN finding (fixed, confirmed closed at `ea476fd` per
my prior review) — untouched.
