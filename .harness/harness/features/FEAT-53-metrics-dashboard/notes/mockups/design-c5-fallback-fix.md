# DESIGN.md · B-21 third — dead `react-charts` fallback struck — 2026-09-02

*(Filed under `notes/mockups/` because `check-domain` permits harness-visual-designer only
`notes/mockups/**` and `notes/prototypes/**` for per-feature notes — the dispatch's suggested
`notes/research-*` path is denied for this role. Contents are a contract-edit record, not a mockup.)*

**Done. DESIGN.md now carries zero `react-charts`/`React Charts` references, and its fallback clause
matches BRIEF `## Constraints` and the operator's 2026-09-01 ruling (DEC-3).** One clause changed in
C-2's opening paragraph; no CAP row, no other section, no other file. No library is named anywhere in
the replacement — the point of the ruling was that the dead reference is struck and no replacement
invented.

## The restated clause — `DESIGN.md:249-252`

Anchor for the pm's note: **section `## C-2 — the two chart shapes and the three tables`, opening
paragraph, third sentence.** Post-edit line numbers, read back from the file after the edit, are
**249–252** — the bolded span opens mid-line 249 and closes on line 252. Prefer the heading anchor
over the number: this file already moved once in this run.

Verbatim, as it now reads:

> **Where a capability's `If absent` cell names a server-side workaround, that workaround is the
> fallback; no replacement charting library is named in advance, and naming one would be an operator
> decision taken on T-18's probe evidence, needing its own plan Decision.**

The sentences either side are untouched: the preceding "Each chart capability below is a pass/fail
question eng-lead can put to the charting library's current alpha API" and the following "The three
tables carry no capability list because they need none…" survive verbatim. Lines 252-254 were
re-wrapped only — no wording change — to restore the file's ~100-column wrap after the clause
shortened. File length 586 → 587 lines.

## Every occurrence, and its disposition

Case-insensitive sweep of the whole file for `react[- ]?charts` — both spellings, hyphenated and
spaced — found **exactly one** occurrence before the edit and **zero** after.

|#|Where|What it said|Disposition|
|---|---|---|---|
|1|`DESIGN.md:250` (pre-edit), C-2 opening paragraph|"React Charts (BRIEF `## Constraints`) is the second; a third library is neither"|**Removed.** Replaced by the clause above|

Nothing was deliberately left: this file has no quoted historical record, no prototype disclosure and
no open question mentioning the package. The single hit was the one B-21 named. The only charting
library still named in DESIGN.md is the primary, in `## Substrate` material untouched here.

## Why the restatement is truthful, and composed only of approved material

- **The fallback that exists** is the per-capability `If absent` cell. Every CAP row carries one, and
  eight name a concrete server-side or ours-to-supply workaround (CAP-02, CAP-03, CAP-04, CAP-06,
  CAP-09, CAP-11, CAP-12, CAP-13). Four are marked hard requirements (CAP-01, CAP-05, CAP-07, CAP-11)
  and are exactly T-18's swap trigger; CAP-08 is pre-settled to three stacked plots and is not a
  fallback at all. The clause now points at that column by name, which it previously did not.
- **The library fallback that does not exist**: npm `react-charts` last published 2023-11-02 with a
  React 16 peer, against this client's React ≥19 substrate (`DESIGN.md` `## Substrate`), so it fails
  the substrate check and cannot install beside Astryx. BRIEF `## Constraints` lines 75-79 already
  record this; DESIGN was the last artifact contradicting it.
- **Whose decision a replacement is**: the operator's, on T-18's probe evidence, needing its own plan
  Decision. That is D-08's pre-existing trigger shape restated — no new mechanism, no new library.

## Out of scope, reported not fixed

- `notes/research-FEAT-53-plan-c5-fixes.md:142-145` (sibling pm's artifact) says DESIGN.md:250 "still
  reads" the old clause, and `plan.yaml:1985-2003` (C4-03/C4-04) says no post-fix DESIGN anchor could
  be cited because the fix was not yet visible. Both were true when written and are now stale. **The
  heading + line anchor above is what they need**; updating them is the pm's, not mine.
- `notes/research-FEAT-53-plan-amend-t15.md:27-28` still names "swap to React Charts" inside a quoted
  T-15 dispatch. Historical note, not a live contract, and outside this dispatch.

## Open questions

None. Nothing here needed a decision the operator had not already made.
