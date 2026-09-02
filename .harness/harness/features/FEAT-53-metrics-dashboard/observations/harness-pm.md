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
- 2026-09-01: FEAT-53 plan c3 - plan-merge.py apply carries a proposal's TRAILING COMMENT BLOCK into plan.yaml. My proposal doubled as the required record artifact (dispatch contract) and ~215 comment lines landed inside the tasks: key range, attached to the last item. No verb removes them - amend --show on that item's last field excludes them (_trim_tail treats them as document) and apply re-emits base item text verbatim. Lesson - when a proposal must also be the human record, feed apply a MINIMAL data-only proposal and keep the record in a second notes file.
- 2026-09-01: FEAT-53 - the worktree's own .claude/skills/harness/bin/plan-merge.py predated set-panel and --yaml-value; the MAIN checkout's copy had both. A worktree can carry a stale copy of the very tool the dispatch names. Check --help before assuming a verb exists.
- 2026-09-01: FEAT-53 - harness-pm has NO grant on a feature's DESIGN.md (check-domain BLOCKED it); grants are BRIEF.md, PLAN.md, plan.yaml, notes/research-*.md, notes/uat-*.md, glossary.md, expertise, observations. A dispatch saying change DESIGN.md where the rulings force it cannot be honoured - raise the forced change as an open question instead.
- 2026-09-01: FEAT-53 loop-back 2. plan-merge.py `amend --show` prints the value AND a `sha256:` line; hashing the --show STDOUT (what I did first) is not that hash and amend refuses with exit 6. Read the `sha256:` line.
- 2026-09-01: FEAT-53. A vitest verify that greps a test LABEL is greened by `test.skip` (label printed, exit 0). Driving `--reporter=json` with `npm run --silent` and asserting `assertionResults[].status == "passed"` closes it, and the snippet is provable offline against synthetic jest-shaped payloads without the toolchain installed.
- 2026-09-01: FEAT-53. `check-domain.sh --resolve .harness/metrics/instrumented_at` answers NOBODY, so a durability gap over a runtime-created data file cannot be closed by giving a task ownership; the honest closure is a recorded accepted risk naming what moves.
- 2026-09-01: plan-merge.py set-panel --value-file takes the BARE panel mapping (last_run/cycle/readers/findings at top level); a `panel:`-wrapped document — the shape an `apply` proposal needs — is refused with exit 5 "missing required key(s)". Cycle 1's value file carried the wrapper because it went through apply, so copying it forward fails.
- 2026-09-01: the FEAT-53 worktree's vendored .claude/skills/harness/bin/plan-merge.py is at 6e3eda57 (BUG-1128) and has no set-panel subcommand at all (exit 2, invalid choice); .agents/skills resolves into the worktree, so the documented verb was only reachable through the main checkout's copy by absolute path.
- 2026-09-01: check-domain.sh grants harness-pm notes/research-*.md and nothing with a .yaml suffix, so a dispatch naming a .yaml value file is denied; YAML-under-.md is the working shape and matches the cycle-1 record.
- 2026-09-01: 13 stored findings all re-hash to their own id from stored reader+summary, which is a cheap post-write integrity check for a carry-forward transcription — folding by safe_dump is invisible to the hash because normalize_summary collapses whitespace.
