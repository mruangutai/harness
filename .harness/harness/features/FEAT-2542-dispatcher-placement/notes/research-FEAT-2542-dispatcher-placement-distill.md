# harness-pm distill — FEAT-2542-dispatcher-placement

**BLUF.** I applied one craft batch of four replaces. All three relayed candidates are accepted, and so is own-log bullet 4. The other six own-log bullets are rejected as duplicates or as too narrow. I made no repository-tier ops.

- Batch: `8788965837ffda64aaf7fcb992cc4f2d40d9f626fd28c39bbc972bf60fe68818`
- Receipt: `.harness/harness/features/FEAT-2542-dispatcher-placement/notes/expertise-receipt-3f4d42b57f315e6317fc15cd2d54ac24dc7aee5ab0a63b375a666eebc5de8d24.json`
- Destination: `.harness/expertise/harness-pm.md`. The tool result showed outcomes REPLACED for P-18, P-08, P-01 and O-12.

## Cap state before judging
- **Craft:** Patterns 15/15, Gotchas 15/15 and Outcomes 10/10 were all full. Open was 0/5.
- **Repository (harness):** Patterns 12, Gotchas 15/15 (full), Outcomes 2, 34 lines.

Every accepted entry had to get in by displacing an existing entry or replacing it with a sharper version.

## Per-section counts (from the tool result)
| Section | Before | After |
|---|---|---|
| Patterns | 15 | 15 |
| Gotchas | 15 | 15 |
| Outcomes | 10 | 10 |
| Open | 0 | 0 |

The repository file is unchanged at 34 lines, within the 40-line budget.

## Relayed candidates
- **C1 — accepted. Replaces P-18 with a sharper version.** My characterization listed a producer's outcomes by cause and missed an ok row with a null field. It also had to note that an omitted feature is turned into a legitimate default (`legacy`) that must pass. The old P-18 only covered external payloads and container shapes. The new P-18 widens the trigger to any producer result and adds success-row field shapes and producer defaults. It keeps the identity-binding clause. P-11 covers removed branches and does not overlap.
- **C2 — accepted. Replaces P-08 with a more general version.** P-08 already covered a verify checked against intent prose. Two failures were new: a prescribed literal that broke a gate's cap, and printed commands that would not run as an operator would paste them. The replacement keeps P-08's task-boundary remedy and fits in 50 words.
- **C3 — accepted. Displaces O-12.** My goal-check reasoned that mutant n3 fails open. QA ran it and measured a fail-closed exit 2. O-06 is about whether the harness ran the real artifact, and O-07 is about using an earlier commit as a free mutant. Neither says to run a severity claim before grading it. O-12, a narrow Python symlink/sys.path recipe, was the weakest Outcome. My current Expertise had no equivalent entry from a concurrent distill.

## Own log (observations/harness-pm.md)
1. **Census the tests that rely on a fallback before tightening it — rejected as a duplicate of P-11.** P-11 already covers data-carrying instances and requires a test witness for each change.
2. **An except branch that on-disk data cannot reach needs fault injection — rejected.** It describes one instance. The general method, isolated copied bin trees, is already a repository-tier style fact.
3. **A trace wrapper as a branch witness — rejected.** O-06 covers asserting that the branch under test was reached.
4. **Name predicted reds per assertion and gate on set equality — accepted. Displaces P-01.** The gate held at both validate rounds: 97=97, then 110=110. It made mispredictions loud. P-01 (role-identity protection) was the narrowest Pattern.
5. **The main-session-direct commit is never the pin; bind tested_sha by byte-identity — rejected as a duplicate of G-09 and G-19.** The part about fixing the DEC number first is a one-repo detail, and repository Gotchas is full with nothing weaker to displace.
6. **Collapse a matrix when the dropped dimension is read after the deciding branch — rejected.** It is too narrow to beat any full-section Outcome.
7. **A grilling's "extend case-N" delivered as 4 of 5 shapes — rejected.** P-04 already requires a separate assertion per item.

## Principles applied
- None cited. This is a distill: I reviewed no diff and ran no suite.
