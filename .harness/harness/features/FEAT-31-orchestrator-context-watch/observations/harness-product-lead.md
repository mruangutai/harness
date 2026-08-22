# Observations — harness-product-lead — FEAT-31

- 2026-08-22 (fix2-product): the fix-cycle dispatch cited **DEC-141** as "generated files follow
  their source". That citation is wrong. `DECISIONS-INDEX.md:160` shows DEC-141 @3309, tags
  `[map,brief]`, and I opened `DECISIONS.md:3309-3330`: it is the kaya map audit — `render-map.py`
  renderer fixes, map authoring rules, ui-reviewer calibration. Nothing about index generation.
  The real authority for the index is the file's own contract header, `DECISIONS-INDEX.md:1-3`:
  `<!-- GENERATED except the text after ` :: ` on each row. Regenerate: gen-decisions-index.py -->`.
- 2026-08-22 (fix2-product): the same dispatch said regenerate the index "if and only if the row
  changed". That is unsatisfiable as a rule. Every row carries an `@<line>` anchor
  (`DECISIONS-INDEX.md:16` states the row grammar; rows 21+ show `@20`, `@34`, ...), so ANY change
  to DEC-159's line count shifts the anchor of every entry after it — DEC-160 @3996 onward.
  The generator must run after any `DECISIONS.md` body edit, unconditionally.
- 2026-08-22 (fix2-product): "never hand-author the index" is over-broad. The text after ` :: ` is
  the hand-authored half and the generator preserves it. For this edit DEC-159's existing ruling
  text (index row 178: "An orchestrator's mission is exactly one phase ... capped handoff note")
  stays TRUE, so no hand edit is needed — but the reason is that the core held, not that hand
  editing is forbidden.
- 2026-08-22 (fix2-product): **P-07 paid, and pm's route was stronger than mine.** I reached "the
  index must be regenerated unconditionally" from the row grammar at `DECISIONS-INDEX.md:16`. pm
  reached the same conclusion from `gen-decisions-index.py:347` (`- {key} @{dec['line']}`) PLUS a
  named failing test, `test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration`,
  with a measured baseline of exit 0 at `abcba0e`. Mine was an argument about a document; pm's is a
  gate that goes red. I adopted pm's as the record. When a member confirms my finding by a route
  that ends in a failing gate rather than a reading, the gate is the version that belongs in the plan.
- 2026-08-22 (fix2-product): **a forced close mid-flight was survivable ONLY because of P-05.** The
  `SubagentStop` digest hook fired while pm was still running, forcing me to emit a terminal digest.
  Because I had already written `runs/fix2-product/send-back-criteria.md` (20 criteria) and
  `runs/fix2-product/step2-dispatch.md` (every premise pinned to a line) BEFORE the return landed,
  the resumed context assessed pm and dispatched step 2 with no re-derivation. The criteria also
  could not be fitted to pm's answer, because they predated it. Writing both files cost two Write
  calls; not having them would have cost the whole run.
- 2026-08-22 (fix2-product): pm set `status: building` on the task it authored (`plan.yaml:1559`)
  despite the dispatch reserving task status for the orchestrator. Harmless here — the orchestrator
  overwrites it — but it is a boundary the dispatch stated explicitly and the member crossed anyway.
- 2026-08-22 (fix2-product): a `plan.yaml` write triggered a sync hook that modified `feature.json`
  and created GitHub issue #672 as a SIDE EFFECT. pm never touched `feature.json`. A member's
  `files_touched` therefore under-reports what its run changed on disk, and the delta looks like an
  undeclared write by whoever reads `git status` next.
- 2026-08-22 (t19-product): the previous run left Q2 open — is there a decision behind the
  DECISIONS-INDEX generation contract? Answered NO, by grepping the whole index: `generat` (case
  insensitive) matches ONLY lines 2-3, the header comment itself. No decision row anywhere in the
  index mentions index generation. So the contract every agent must obey when editing `DECISIONS.md`
  is stated only in the generated file's own header, backed by a test
  (`test_committed_index_matches_a_fresh_regeneration`, `test-gen-decisions-index.py:339`) and by no
  decision at all. A rule with a test and no decision behind it is invisible to the index-first
  reading path CLAUDE.md mandates.
- 2026-08-22 (t19-product): `run-unit-tests.sh --check-kinds` is NOT a test run. Line 26 branches to
  a classification check that only asserts the script arrays agree with `test_kinds.integration.detect`
  in `harness.json` (its own success line, :130, says exactly that). It executes no test, so it can
  never catch a skipped index regeneration. When a dispatch names `--check-kinds` and a specific test
  script as two gates, they are genuinely disjoint — do not treat either as covering the other.
- 2026-08-22 (t19-product): I passed `model: opus` in a member dispatch and `dispatch-guard.sh`
  blocked it. The pin lives in the member's agent frontmatter and a model choice is an escalation,
  not a dispatch parameter (DEC-152/155). The guard caught it; nothing about the task required it.
- 2026-08-22 (t19-product): my observations log was overwritten by a CONCURRENT writer mid-run — I
  wrote two bullets, and the next notification showed the file back at its pre-write content with a
  different block appended. `Write`-not-`Edit` on a shared per-feature path is read-modify-write with
  no compare-and-swap, so a second context holding a stale read silently drops the first's append.
  Restoring cost a full re-Write of 40+ lines from a diff fragment. On a shared observations file,
  re-Read immediately before every Write and treat a "changed on disk" notice as data loss until
  checked, not as someone else's business.
- 2026-08-22 (t19-product): the shipped warning text is NARROWER than the rule it cites.
  `context-watch.py:534-541` tells a warned orchestrator to "end this phase at the boundary and write
  notes/handoff-<stem>.md" with the four sections — the boundary-REACHABLE case only — and cites
  "DEC-159's seam rule" as the authority. So an orchestrator that is genuinely mid-flight is told to
  do the one thing it cannot, and must follow the citation into DEC-159 for its case. That is what
  makes SC-09's in-place edit load-bearing at runtime rather than archival: the tool defers to the
  entry instead of restating it, which is "one statement, one home" actually paying off.
