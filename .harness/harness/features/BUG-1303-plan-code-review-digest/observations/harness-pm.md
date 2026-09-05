# Observations - harness-pm

- 2026-09-05: BUG-1303 plan. bash-write-guard.sh parses the whole command line textually, so a
  heredoc feeding plan-merge.py apply --proposal - is refused when the PROPOSAL BODY contains any
  angle bracket: my first attempt died on a process substitution in a verify and on an
  angle-bracketed review_sha placeholder inside an intent, both reported as "redirect targets" with
  the surrounding text quoted as the target. The documented stdin route therefore cannot carry the
  angle-bracket placeholder syntax the harness templates themselves use. Workaround: phrase
  placeholders in prose (an angle-bracketed placeholder named path-to-plan.yaml) and replace
  process substitution with an inline python3 -c comparison.
- 2026-09-05: plan-merge.py amend --value-file - is not wired to stdin (FileNotFoundError on the
  dash), unlike apply --proposal -. Correcting one field needs a real file on disk; /tmp is
  writable for pm through the Write tool.
- 2026-09-05: measured probe worth repeating before deciding whether a doc-vs-schema guard is
  affordable: import validate-digest.py, take SCHEMAS[norm(persona)] per persona, and grep the
  documenting file for each key. With the four dev personas mapped to harness-digest-dev/SKILL.md
  and the three leads to harness-team/SKILL.md, exactly one gap exists across all sixteen personas
  (harness-code-reviewer, code_grade). That single measurement turned doctrine-or-guard from a
  judgement call into a decision.
- 2026-09-05: BUG-1303 goal-check — a persona's documented `artifact:` line is part of the digest contract the validator enforces (`_feature_dir_from_artifact` runs before every other reviewer check), yet no SCHEMAS-derived conformance guard sees it. Grading "can this persona's documented block validate?" means running the block, not diffing its field names against SCHEMAS.
- 2026-09-05: BUG-1303 c1 — a verify needing TWO ok lines from one 19s suite should pipe the run into a single python filter, not chain two 'suite | grep -qF' runs: the chain re-runs the suite and doubles wall time against the 60s task-verify budget. Proved the filter discriminates offline (both lines rc 0, one line rc 1) before writing it into plan.yaml.
- 2026-09-05: BUG-1303 c1 — validate-digest.py's ALIAS keys ARE the 16 persona names while SCHEMAS keys are the 9 normalised roles; a roster derivation must read sorted(ALIAS), and a completeness check written against SCHEMAS would silently grade 9 rows instead of 16. Loaded the module to confirm before specifying T-01 step (3).
- 2026-09-05: BUG-1303 c2 — before scoping a documented-contract guard from whole-file to block-extracted, I ran the extractor + gap check over all 16 registry personas at HEAD c369fb1f (throwaway /tmp probe using validator.ALIAS/SCHEMAS). Block-scoped == whole-file everywhere and every block was locatable, so the plan's expected-red list survived the narrowing. Narrowing a guard's scope inside a plan can silently add unplanned reds at build time; the probe is cheap and it is the only way to know.
- 2026-09-05: BUG-1303 c2 — check-domain denies pm a notes/plan-repair-*.md file even when the dispatch names that prefix; the grant glob is notes/research-*.md (plus uat-*). Dispatch-named artifact paths do not widen the guard.
- 2026-09-05: BUG-1303 c2 — plan-merge.py amend refuses list fields (exit 4) without --yaml-value; depends_on needs --yaml-value on BOTH the --show that produces the sha and the write.
- 2026-09-05: BUG-1303 panel record. plan-merge.py has a dedicated `set-panel --value-file` verb; it validates only last_run(str)/cycle(int)/readers(list)/findings(list), inserts the block before `tasks:` when absent, and re-reads the spliced file to confirm the panel reloads equal to the value supplied. Extra keys (I added `transcription_rule`) survive.
- 2026-09-05: An absence conjunct is what makes a two-site path fix detectable. `.omp/agents/harness-code-reviewer.md` carried the stale report path TWICE (artifact: line and write-grant sentence), so `grep -qF <new fragment>` greened on either half alone. `! grep -qF <old fragment>` per copy costs one clause and reddens on a half fix; measured rc 1 on the unmodified tree, with the chain short-circuiting at an earlier conjunct.
- 2026-09-05: Panel dispositions were re-derived cheaply because the cycle-2 scope reader's note listed every cycle-1 finding against current plan.yaml anchors. Reading that note before the digests' prose settled all eight `resolved` values without re-grepping the plan.
- 2026-09-05: bash-write-guard blocks a heredoc (`<<'EOF'`) as a redirect even when the command's --entries is stdin; write the entries to a file with the Write tool and pass its path instead.
- 2026-09-05: BUG-1303 c3 — plan-merge amend --show reprints the WHOLE field before the sha line; `| sed -n '$p'` is the cheap way to take just the hash without spending context on a 175-line intent.
- 2026-09-05: BUG-1303 c3 — safest way to amend a long block-scalar intent is a python script that safe_loads the plan, does anchored str.replace with a count==1 assertion per anchor, and writes the value-file; retyping the field invites silent drift. Anchors must use the DEDENTED loaded text (bullets at 4 spaces here, not the raw 8).
- 2026-09-05: BUG-1303 c3 — when a remedy widens an enumeration whose ok-line literal a verify greps, check first whether the existing literal still reads truthfully under the new rule; here "unmapped persona" already covered the empty-list case, so no verify edit was needed and literal identity was preserved for free.
- 2026-09-05: BUG-1303 c3 panel transcription — plan-merge.py set-panel REPLACES the whole top-level panel mapping, so the safe route is to safe_load the plan, mutate only last_run/cycle on the EXISTING panel object and safe_dump that to the value file; retyping findings would change PF- ids computed over the summaries. Also: the feature-tree plan.yaml is untracked by git, so git diff is unavailable as a no-drift cross-check — sha256 over safe_dump of tasks/decisions plus per-task verify strings is the substitute. Note plan.yaml has NO top-level requirements key (they live in BRIEF.md), so a requirements-region diff compares None to None and proves nothing.
