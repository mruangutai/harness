# Handoff — FEAT-38-decisions-current-knowledge, ship → operator gate — written at 48bbe7e, resume segment

## Next

**Do not dispatch anything. Every squad-owned gate is green at a current pin; what remains is two
operator decisions.** Present `notes/ship-review-2026-08-29-18.md` (it SUPERSEDES the `-16` briefing).
Four asks, in this order: run the UAT at `notes/uat-FEAT-38.md`; rule on the crossed cycle budget
(11 of 10 — raise it, or accept and ship on the UAT result); strike unwanted rows from the 23-row
proposed backlog; sign or decline the three `verify:` amendments in
`notes/research-verify-block-defects.md`.

**Nothing is waiting on a fix.** `must_fix` is empty at qa, at the panel and at the goal-check. If
the operator returns a UAT pass and a budget ruling, the next act is theirs: PR and merge, both
user-gated, neither attempted here.

## Trust

- `review_sha` is `48bbe7e`; re-pinned this run because T-14/T-22/T-23 landed above the old pin — `feature.json`, and the pin commit is `04d333d` which touches `feature.json` only — verified-at 48bbe7e
- qa gate green at the pin — exit 0, 0 `FAIL`, 0 anchored `^KIND-DRIFT:`, index diff-clean, checkers discovering 20 anchors / 11 claims — `notes/qa-2026-08-29-11-validator.md` — verified-at 48bbe7e by qa; **I did not re-run the suite myself this segment** — UNVERIFIED at my own tier
- Review panel PASS, `severity_max: med`, `must_fix` empty; all three reviewers examined the named file set rather than self-scoping out — `notes/review-harness-{code,security,ui}-reviewer-c2.md` — verified-at 48bbe7e
- 12 of 13 SCs met; SC-13 `unrun` (operator) — `notes/research-FEAT-38-goalcheck-48bbe7e.md` — verified-at 48bbe7e
- SC-04 is met and I measured it INDEPENDENTLY of pm, before dispatching: three sweeps with the three pathspec exclusions, deleted-id sweep run per id for all fifteen, all empty; reachability proved by a positive control in the identical scope (`DEC-138` → 17 files for me, `DEC-188` → 26 hits for pm) — verified-at 48bbe7e
- T-14's five repointed ids are semantically correct, not merely resolving to live headings: `DEC-102`→`DEC-120` matches the base index's recorded successor; `DEC-192`→`DEC-191` is right because `DEC-191` states the eleven-key set with `phase` absent, which is the claim being cited; `DEC-19` was dropped on T-14's own written instruction — panel adjudications, and I read the base index row and `DEC-191`'s body myself — verified-at 48bbe7e
- `DECISIONS.md` is byte-identical between `2557950` and `48bbe7e`, which is what lets SC-11's per-entry coverage carry across the repin — `git diff 2557950 48bbe7e -- <path>` empty — verified-at 48bbe7e by me
- SC-11's 15/15 meaning-preservation is INHERITED (10 entries by the cycle-0 panel, 5 by pm at `2557950`); no entry was re-derived this segment — **UNVERIFIED at my own tier**
- Cycles 11 of 10 — CROSSED; both new cycles are lead-internal send-backs during re-verification, traced to `runs/2026-08-29-11-validator/state.yaml` and `runs/2026-08-29-17-validator/state.yaml` (`ui-review`, `cycles: 1`) — verified-at 48bbe7e
- The board is at `Review` — parent #935 and all of #936–#958 written by `gh-sync.py status`, whose output I read — verified-at 48bbe7e

## Dead ends

- Do not re-render `ship-review-2026-08-29-16.html` hoping to fix its empty code block — the panel proposed exactly that and it does not work. `render-brief.py:131` strips `<!--.*?-->` across the whole document BEFORE fenced-block handling, so a code block whose content is an HTML comment is destroyed on every render. The `-18` briefing works around it by dropping the comment delimiters; the renderer bug is backlog B-19 — verified-at 48bbe7e by reading the renderer and reproducing
- Do not re-report SC-04 as an open gap — T-14 closed it, measured twice, per id for all fifteen ids, with a reachability control — verified-at 48bbe7e
- Do not root any citation sweep at `.agents/**` — symlink onto `.claude`, so a recursive grep traverses nothing and returns a confident zero — verified-at 2557950, unchanged
- Do not use `git grep -E ... \b` for a decision id — git's ERE has no `\b` and the sweep reports a clean tree while citations stand. Use `-P` with `(?![0-9])` — verified-at 48bbe7e
- Do not re-run T-03, T-21, T-06 or T-10's `verify:` blocks expecting green — all four are order-dependent or miswritten — verified-at 2557950, unchanged
- Do not read a bare `PASS` total as comparable across receipts — one tree reads 1117, 1002, 1285 or 1150 depending on the counting expression. Exit status and `^FAIL` count are the comparable numbers (B-15) — verified-at 48bbe7e
- Do not treat `runs/**` digests as durable — `.gitignore:7` ignores them, so they die with the worktree. Durable evidence lives in `notes/` — verified-at 48bbe7e
- Do not `sed -i` anything under the feature dir — the write guard refuses it and directs you to the Write tool, correctly; that is not a malfunction — verified-at 48bbe7e

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-29-18.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/uat-FEAT-38.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-FEAT-38-goalcheck-48bbe7e.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-verify-block-defects.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/feature.json`
