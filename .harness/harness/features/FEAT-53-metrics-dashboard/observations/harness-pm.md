# Observations - harness-pm

- 2026-09-01: FEAT-51 dispatch said the grilling artifact lists seven 'Not yet specified' items; it lists eight (lines 88-107) — the trend.jsonl schema bullet and the touchpoint-counting bullet are separate. Classified all eight; a dispatch's own count of an artifact's items is not evidence.
- 2026-09-01: FEAT-53 c2. A whole-file plan recreate is safe if it is built by exact-substring
  replacements that each assert count==1; the transform refused twice on a bad anchor before writing
  anything, which is the amend guarantee without 25 amend calls. Kept the pre-image at /tmp and
  diffed id sets after apply - dropped [] both collections.
- 2026-09-01: FEAT-53 c2. Two new plain-scalar decision values failed safe_load on ": " inside prose
  ("cannot be the net: its newest..."). safe_load is the only check that catches it; write "-" not ":"
  in any plain scalar and always reload before handing the file on.
- 2026-09-01: FEAT-53 c2. BRIEF.md cited a grilling artifact that exists in the owner checkout's
  working tree but is untracked on the feature branch, so the citation does not resolve from inside
  the branch a reviewer reads. Test the existence of a cited artifact AT the branch, not on the disk
  you happen to be standing on.
- 2026-09-01: FEAT-53 c2. A criterion can be unreachable by its declared method for only PART of its
  enumeration (SC-06: 107/122 greppable, 12/3 not, because they live inside 1024/3x2/ES2022). The
  honest fix is to name the covered subset in the criterion AND record the residue under
  ## Verification gaps, not to widen the grep or drop the clause.
- 2026-09-01: FEAT-53 goal-check vs the grilling artifact. Three prior reviews all read the plan for internal consistency; none compared it to the operator's Settled list, and the reversal of a settled item (a real web-framework backend, reversed by D-03) survived every one of them while its engineering merit was praised. Reading the operator's own words is a DIFFERENT check from reading the brief.
- 2026-09-01: an anti-hardcoding sweep that pins the forbidden digits IN THE PLAN (T-07/T-14 grep 107 and 122) goes blind the moment the measured figure moves - the repo is at 106 tracked .py now, so the current mix evades the guard. Specify re-derivation at build time, never the literal.
