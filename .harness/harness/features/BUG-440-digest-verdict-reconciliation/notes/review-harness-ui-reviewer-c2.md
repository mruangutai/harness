# UI review — BUG-440-digest-verdict-reconciliation — cycle 2 (pin `a1a67956a5844c67ce098e9580ee6692a92f9a30`)

## BLUF

**PASS.** No rendered UI surface exists in the cycle-2 diff (test-only remedy, measured). The one
adjacent surface the dispatch named — the INV-37 operator-facing gate message — is unchanged byte-for-
byte from cycle 1, and V-08's "info, no change owed" rating is **confirmed, not merely carried
forward**, against a sharper bar than cycle 1 applied. The day-one density concern (4 blocking
findings at every `/harness` entry) is **measured, not assumed**: it does not read as noise.

## 1. Census (measured, not predicted)

`git diff 2964cddb..a1a67956 --stat`:
```
 tests/integration/test-check-state.py | 124 ++++++++++++++++++----------------
 1 file changed, 65 insertions(+), 59 deletions(-)
```
One file, zero rendered-UI extensions (no html/css/scss/tsx/jsx/vue/svelte/less — none expected,
none found). `find … -iname DESIGN.md` under this feature's tree: **no match** — no `DESIGN.md`
exists. This is a Mode B audit of an adjacent text surface, not a rendered-UI review; nothing here
contradicts that framing.

**Verified, not assumed, that the remedy is test-only:** `git diff <old>..<new> -- check-state.sh`
is empty, and the working-tree copy of `check-state.sh` diffs empty against the new pin too. The
INV-37 message text I audit below is therefore the *same bytes* cycle 1 read.

## 2. INV-37 gate message as an interface (`check-state.sh:1552-1557`, unchanged)

Message shape (verified against source, not paraphrased):
```
INV-37: {feat} run {rid}: digest verdict {dm!r} in {digest.md path} differs from
feature.json verdict {rv!r} in {feature.json path}; the gate does not decide which
record is wrong.
```
- **Names both records and both paths, unambiguously** — feature, run id, digest verdict + its
  path, `feature.json` verdict + its path: all six items REQ-01/SC-01 require, present in one line.
- **Correctly withholds the decision it is not entitled to make** — the trailing clause states this
  explicitly, matching REQ-04 ("nothing is repaired automatically… a human decides which record is
  wrong") almost verbatim.
- **No prescribed remedy action** (no "Fix: …" / "Run … for reasons"). I checked this against the
  file's own convention rather than an abstract standard (P-14): of 122 `bad.append`/`warn.append`
  call sites in `check-state.sh`, only 5 carry an explicit remedy clause (`INV-31` ×4 "Fix: …",
  `INV-15` "Run bin/validate-digest.py lead on it for reasons"). Omitting one is the file's norm,
  not an outlier, and here a scripted remedy would be dishonest: REQ-04 is that no single mechanical
  fix exists — either record could be the wrong one, and only a human can tell.

**Verdict: V-08's "info, no change owed" is confirmed at this pin**, on stronger grounds than
cycle 1 stated (cycle 1 asserted intelligibility; this pass checked it against the file's own
remedy-clause convention and found the omission consistent with house practice, not a gap).

## 3. Day-one density: 4 blocking findings among the gate's other output — measured

Ran the *pre-INV-37* `check-state.sh` live against the real control-plane root (read-only; INV-37
isn't merged there yet, so this measures the surrounding volume the 4 disclosed findings will land
in): **801 total output lines, 1 `VIOLATION` line, 800 `note` lines.** Reading the print loop
(`check-state.sh:2504-2505`) confirms the format is fixed: `for m in bad: print("VIOLATION …")`
runs to completion **before** `for m in warn: print("note …")` starts — every violation is emitted
as one contiguous block at the very top of the sweep, ahead of all notes, every time.

Consequence for the disclosed day-one state: INV-37's 4 mismatches join the existing 1 (`INV-29`)
as **5 contiguous `VIOLATION`-tagged lines at the top of ~805 total lines**, not interspersed among
the 800 `note` lines. The uppercase `VIOLATION` / lowercase `note` tag pair is the only structural
marker in the output and it is sufficient: an operator reading top-to-bottom, or grepping
`VIOLATION`, sees all 5 before any note. This is legible and actionable at the disclosed volume —
not noise. (Minor, pre-existing, not introduced by this change: there is no leading summary count
line, e.g. "5 violations, 800 notes" — a general gate-output gap untouched by this feature, not
filed here.)

## Findings

None new. Carrying forward: V-05 (low, output-spoofing via unescaped names, `check-state.sh:1553`)
is unchanged and is security's lens, not re-litigated here.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No rendered UI surface at this pin (test-only remedy, measured); the adjacent INV-37 gate message is unchanged and its 'info, no change owed' rating is confirmed on stronger grounds; the day-one 4-finding volume is measured legible, not noise."
  mode: B
  in_scope: true
  severity_max: none
  findings: 0
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: ["not applicable — batch/CLI text output, no colour-only state encoding, confirmed by reading the print loop (check-state.sh:2504-2505)"]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/review-harness-ui-reviewer-c2.md
```
