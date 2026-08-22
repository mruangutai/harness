# Observations — harness-product-lead — FEAT-31

- 2026-08-22 (fix2-product): the fix-cycle dispatch cited **DEC-141** as "generated files follow
  their source". That citation is wrong. `DECISIONS-INDEX.md:160` shows DEC-141 @3309, tags
  `[map,brief]`, and I opened `DECISIONS.md:3309-3330`: it is the kaya map audit — `render-map.py`
  renderer fixes, map authoring rules, ui-reviewer calibration. Nothing about index generation.
  The real authority for the index is the file's own contract header, `DECISIONS-INDEX.md:1-3`.
- 2026-08-22 (fix2-product): the same dispatch said regenerate the index "if and only if the row
  changed". Unsatisfiable. Every row carries an `@<line>` anchor (`DECISIONS-INDEX.md:16` states
  the grammar), so ANY change to DEC-159's line count shifts every entry after it. The generator
  must run after any `DECISIONS.md` body edit, unconditionally.
- 2026-08-22 (fix2-product): "never hand-author the index" is over-broad. `gen-decisions-index.py:322-323`
  reads the ` :: ` prose back from the existing row and `:325` stamps `⚠ RULING PENDING` when none
  exists — so that prose is the hand-authored half and the generator preserves it.
- 2026-08-22 (fix2-product): **P-07 fired twice in one run, and the SECOND time I was the one who
  was wrong.** pm replaced my row-grammar argument for regenerating the index with
  `gen-decisions-index.py:347` plus a named failing test — a gate, not a reading, so I adopted it.
  Then the documentor corrected BOTH of us: the index change is not anchor-only, because DEC-159's
  own row gained `DEC-198` to its generated `refs:` when the new body cited it. I had already told
  the orchestrator "only downstream anchors". Lesson: when I hand a member a factual claim about a
  generated file as guidance, that claim is an input it will check, and it may come back falsified.
- 2026-08-22 (fix2-product): **a forced close mid-flight was survivable ONLY because of P-05.** The
  `SubagentStop` digest hook fired twice while members were in flight, forcing terminal digests.
  Because `runs/fix2-product/send-back-criteria.md` (20 criteria) and `runs/fix2-product/step2-dispatch.md`
  (every premise pinned to a line) were written BEFORE the returns landed, the resumed context
  assessed pm and dispatched step 2 with no re-derivation, and the criteria could not be fitted to
  the answers because they predated them. Two Write calls bought the whole run.
- 2026-08-22 (fix2-product): **T-19 was dispatched twice by two product-lead hosts and nothing in
  the org could see it.** `mutates_repo` serialization operates inside ONE host's DAG; two hosts on
  one task are invisible to each other, and `check-domain.sh` cannot see `Bash` writes anyway. The
  only thing that prevented DEC-159 carrying the mid-flight rule twice — in an entry whose criterion
  is "one statement, one home" — was pm writing "run the verify command BEFORE your edit" into
  T-19's own `intent:` at `plan.yaml:1548-1550`. A task whose verify fails on the pre-change tree
  doubles as a duplicate-work detector, and that is worth authoring deliberately, not by luck.
- 2026-08-22 (fix2-product): **fixing a falsified clause in an entry does not surface the entry's
  OTHER falsified clauses.** DEC-159:3986-3987 says handoff notes are denied at `>40 lines`;
  `check-domain.sh:951` denies at `>60` and DEC-159's own `:3968` already says
  `~60-line cap (raised from 40 at DEC-160)`. Two paragraphs of one entry contradict each other and
  the code, and this survived a cycle whose entire subject was a false clause in that same entry.
  The documentor found it because it audited the WHOLE entry rather than only the clause it was
  sent to change.
- 2026-08-22 (fix2-product): pm set `status: building` on the task it authored (`plan.yaml:1559`)
  despite the dispatch reserving task status for the orchestrator. Harmless, but explicitly stated
  and crossed anyway.
- 2026-08-22 (fix2-product): a `plan.yaml` write triggered a sync hook that modified `feature.json`
  and created GitHub issue #672 as a SIDE EFFECT. pm never touched `feature.json`. A member's
  `files_touched` therefore under-reports what its run changed on disk.
