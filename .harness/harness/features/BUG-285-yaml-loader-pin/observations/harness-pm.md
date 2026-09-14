# Observations - harness-pm

- 2026-09-09: BUG-285. A dispatch-supplied insertion anchor ("around :1445") was off by two: the
  T-06 Part C cases end at test-gh-sync.py:1442 and the fix1 Part B comment opens at :1444. Writing
  a bare line number into intent would have pointed the builder inside a comment block; I wrote the
  line number PLUS the two literal strings to re-locate by, which is what survives a concurrent edit.
- 2026-09-09: BUG-285. plan-merge.py apply reads --proposal - from a bash heredoc without tripping
  bash-write-guard.py (no redirect target), so a whole bootstrap proposal goes in one call with no
  temp file. Confirmed APPLIED, exit 0, on a plan that did not previously exist. The observations
  dir is NOT auto-created: observations-merge.py dies with FileNotFoundError on the .lock path.
- 2026-09-09: BUG-285. check-plan-routes.py prints "granted to" the FULL resolved agent set, not the
  one named in execution_agent, so it cannot catch a wrong-but-granted routing choice. consult-when
  in team-config.yaml is the only discriminator; the resolver output does not carry it.
- 2026-09-09: BUG-285 c1. Dispatch mandated `plan-merge.py apply` to REVISE tasks[T-01].intent; apply is add-only and exited 7 CONFLICT (plan-merge.py:1217-1218). The docstring header's verb list (lines 11-16) omits `amend`, which the BUG-1128 block at :1215 adds — so a dispatch written from the header names an impossible route. Used `amend --key tasks --id T-01 --field intent --expect-sha256 <from --show> --value-file <raw dedented body>`; `_render_field` reuses the `|` header verbatim and re-indents the body, so the value file holds the dedented block content exactly as `--show` printed it.
- 2026-09-09: BUG-285 c1. Derived the replacement value with a throwaway script that loaded the plan, string-replaced only step f, and asserted the reverse replacement restored the original intent byte for byte — cheaper and safer than retyping a 5.5 KB block scalar, and it proves "nothing else changed" rather than claiming it.
- 2026-09-09: BUG-285 c1. The goal-check report's replacement wording carried markdown backticks around a git command; the target intent block uses double quotes for every literal it names and no backticks anywhere. Kept the file's idiom and recorded the deviation in the artifact rather than importing decoration into a data value.
- 2026-09-09: BUG-285 c2 — a re-grade note cited team-config.yaml:259 for harness-qa's notes grant; the worktree copy has it at 258 and the OWNER manifest at 259, and check-plan-routes.py says the hook consults the owner copy. Cite the owner manifest's line when a worktree carries a divergent team-config.
- 2026-09-09: BUG-285 c2 — plan-merge amend --value-file preserves the literal block only if the value file ends in a newline; a file whose trailing newline was trimmed would have changed the scalar form. Checked the round-trip with safe_load before and after.
- 2026-09-09: BUG-285 panel transcription — the lead digest carried the SAME finding in two wordings (prose table vs appended DIGEST yaml block); since the PF- id is a content hash the two hash differently. Extracted the value with yaml.safe_load from the fenced block instead of retyping, so the em-dash survived and the post-merge re-derivation matched. set-panel re-emits a summary as a double-quoted scalar with \u2014 escaped — representation change only, hash unaffected.
- 2026-09-11: BUG-285 amend. plan.yaml's approval cannot be reset approved->pending by any route: sign-approval hardcodes status approved (plan-merge.py:1082) and refuses a pm caller, amend rejects --key approval (exit 2), apply carries base approval bytes forward. The template asserts "any change to the task set resets this to pending" and no writer implements it. Amending a SIGNED plan therefore always leaves a stale signature over a changed task set.
- 2026-09-11: BUG-285 amend. Dispatch line anchors for factory_decompose.py load_factory were each one lower than the tree at the same sha. Re-derived every anchor with grep -n before writing them into BRIEF and intent; the off-by-one would have sent the builder to the try instead of the load_file call.
- 2026-09-11: BUG-285 amend. A dispatch claimed a FALSE sentence stood in BRIEF.md ("converged with factory_decompose.py's reader"). grep found the word nowhere in BRIEF.md or plan.yaml - only in the intake note quoting the operator, where it was true. The real defect was omission, not falsehood. Grep for the quoted sentence before rewriting on the strength of it.
- 2026-09-11: BUG-285 amend. suite_layout.py _unit_integration_findings refuses any test-*.py name present in both tests/unit and tests/integration, so moving a bugfix to the unit kind under DEC-217 cannot reuse the integration suite's file name.
- 2026-09-11: BUG-285 amend. check-plan-routes.py exits 1 on a MANIFEST DEVIATION alone (worktree team-config differs from owner's) with every task OK and no VIOLATION line. Read the task lines before treating the exit code as a plan finding.
- 2026-09-11: BUG-285 T-02 — an intent that referenced a verify command by ORDINAL ("the third verify command", block held two) plus a one-off stale line anchor (load_plan cited :479, the call is :480, :479 is the bare try). Both are the same failure: a pointer that stays syntactically fine while the thing it points at moves. Naming the command by what it IS (the inline python3 -c probe) is edit-proof; an ordinal is invalidated by any later block edit — including the unit-kind line I added in the same pass.
- 2026-09-11: BUG-285 panelfix c1. Asked to prove an amendment confined to one field, `git diff` vs HEAD was useless: T-02/T-03 were themselves uncommitted, so the whole task block reads as one insertion hunk and my splice is invisible inside it. What worked: pre-write grep of the `- id:`/`intent: |`/`verify: |` anchor line numbers, then the same grep after — T-01's anchors identical, T-03's shifted by exactly the file's total line delta (+71), plus per-field sha256 from `plan-merge amend --show` for T-01/T-03/T-02.verify. Take the anchor grep BEFORE the write; it cannot be reconstructed after.
- 2026-09-11: BUG-285. A criterion pinning a catch-set defect must grade coverage, not the literal tuple, or the criterion re-creates the defect it was written to catch (SC-06 certified the incomplete pair AS the pass condition). Also worth stating in the criterion when a new check is green pre-change: the non-UTF-8 check is green under the old reader too, so it is a re-narrowing guard, not a red-then-green proof.
- 2026-09-11: BUG-285 T-03 intent amend — the SHAPE paragraph's import enumeration was already short
  of what check 3 used (factory_cli for EXIT_REFUSED) before check 4 was added; an intent that names
  its imports explicitly needs that list re-derived from the checks every time a check is appended,
  or the builder writes a NameError.
- 2026-09-11: plan-merge.py amend --field intent --value-file preserved the literal block scalar and
  the single trailing newline with no re-quoting; building the new value by loading the plan,
  string-replacing three anchors in python and asserting the wrap width before writing the value file
  caught a stray blank line between check 3 and check 4 that byte-editing would have shipped.
- 2026-09-11: BUG-285 panel c2 transcription — extracted every finding summary PROGRAMMATICALLY from the digests markdown finding rows (split on the pipe, cell 4) and from plan.yaml own landed summary, instead of retyping. Cycle 0 recomputed to PF-2242299b369215b13ad577fe4279d52e exactly on the first try; retyping an em dash or a backtick would have minted a new id and orphaned any ruling. F1/F2 share a byte-identical summary with different readers and correctly hash to two distinct ids.
- 2026-09-11: plan-merge amend --show needs --key tasks --id T-NN --field intent; --task is not an accepted flag and the parser exits 2.
- 2026-09-11: BUG-285 goalcheck c3 — proved "T-01 unchanged" by yaml.safe_load of the task at the signature commit (bb488145) vs the working file and comparing per key, not by diffing the file; the amendment commit rewrote unrelated regions so a textual diff would have read as change. Same run: re-measured check-plan-routes.py and got exit 0 / 0 violations where open panel finding PF-142f3a asserts exit 1 with a DEVIATION line — a finding about a tool's output can go stale between cycles, so re-measure before carrying one forward.
- 2026-09-11: BUG-285 set-panel adding one reader produced a 3-line pure insert — no safe_dump reflow at all, contrary to the G-07 worry, because the existing panel was already in safe_dump's own wrapping. Value-file-from-safe_load is the cheap safe route regardless.
- 2026-09-11: check-state.sh INV-32 emits NO line naming the goalcheck reader for any feature once recorded; the absence grep across the whole 1354-line output is the cleanest proof the gate closed.
- 2026-09-11: BUG-285 foldq7 c2 — check-plan-routes.py resolves its MANIFEST from the SCRIPT's own location, not from cwd, so the "run it from the main checkout or it deviates" folklore did not reproduce at 6cb113f4: exit 0 and 0 violations from BOTH the owner root and inside the worktree, control-plane copy and worktree copy alike. A cwd-conditioned verification instruction is a symptom of a transient team-config skew, not a property of the checker.
- 2026-09-11: BUG-285 foldq7 c2 — plan-merge amend --field <f> --show is the cheap byte-identity check on a protected task: it prints the field body plus a sha256, so re-measuring three intent shas cost one loop and proved T-01..T-03 unchanged without a diff or a git read.
- 2026-09-11: BUG-285 foldq7 c2 — a decision citing a notes/ file as its able-to-fail evidence can land and be signed while that file does not exist; nothing in check-state.sh or check-plan-routes.py resolves a notes path inside a decision's prose, so the dangling citation is invisible to every gate.
- 2026-09-11 (goal-check c4, BUG-285): graded a parity criterion by deriving divergence classes from
  both readers' control flow instead of from the plan's input list, and found a class nobody had
  named: gh-sync load_recorded refuses a non-mapping `github:` value (:588-594) while
  factory_decompose load_factory returns its empty factory for a non-mapping `factory:` value
  (:127-128). D-08 had recorded "One divergence SURVIVES" — there were two of the same shape. The
  plan asserted coverage; only the control flow could falsify it.
- 2026-09-11 (BUG-285): to measure a POST-change matrix without touching a live inode, I loaded each
  reader's source, string-replaced the two guards, and exec'd it in a fresh module whose __file__ was
  left at the REAL path — sibling imports and each module's own root resolution both keep working,
  and nothing under .claude/ is written. Cheaper and safer than shutil.copy into a tempdir.
- 2026-09-11 (BUG-285): three of five tasks carried the "unit runner prints 4 FAIL lines at green,
  grade on exit status only" warning; T-02 runs the same command first in its verify and carries no
  such warning. When a measurement trap is inoculated per task, grep every task for the inoculation.
- 2026-09-11: BUG-285 S-03. plan-merge amend --show hashes the RAW BLOCK LINES (header + indented body), not the parsed value, so a sha computed from yaml.safe_load never matches; take the hash from --show and pass the raw body as --value-file. Extracting the current value with a tiny python script and editing that file is the safe route for an 8k-char intent.
- 2026-09-11: BUG-285 S-03. A disclosure-only amendment needs an explicit "this remains open to you" sentence where the operator signs; without it a reader takes a recorded divergence as a closed decision.
- 2026-09-11 (BUG-285): a survey of ONE input class at a time had found 2 members of the present-but-malformed-read-as-empty class over four cycles; ONE 13-class probe run found 6. The sixth was invisible to every type-guard reading because it is reached by COERCION, not by a guard: gh-sync's _opt_int turns "7" into 7 while load_factory's isinstance(parent, int) drops it, so a recorded parent reads as absent from a block that IS a mapping. Enumerate input classes as a matrix before concluding a defect class is closed.
- 2026-09-11 (BUG-285): classifying reader parity by raw return-value diff overstates divergence. Both readers refuse an unparseable feature.json, differing only in exit code (bare SystemExit code=1 vs factory_cli.refuse EXIT_REFUSED=2), which D-11 keeps deliberately. Grade the MATERIAL answer a caller gets, then note the mechanism.
- 2026-09-11: BUG-285 bounded amend. Four table rows closed with ONE guard pair because the OTHER
  reader already carried the shape (gh-sync.py:583-594). Reading the sibling reader before
  designing the guard turned a four-row closure into a convergence argument, and it is what made
  "no new task" defensible.
- 2026-09-11: BUG-285. The dangerous half of a "make malformed refuse" ruling is the ABSENT path,
  not the refusals. Measuring the live corpus first (all 80 feature.json have the block key ABSENT)
  is what showed a single refusal would have refused every live feature, and it is what justified
  splitting the guard rather than replacing it.
- 2026-09-11: BUG-285. Before writing a mandated code shape into an intent, I ran it against a
  patched COPY in a tempdir over 12 inputs. It cost one tool call and converted "the builder should
  be able to satisfy this" into a measured ALL GREEN, including the two absent-path controls.
- 2026-09-11: BUG-285. check-plan-routes.py exited 0 with 0 violations where a cycle-2 panel
  finding recorded a MANIFEST team-config-skew deviation for the same plan. Report what the run
  measured, not what the record predicted, and say which invocation was used.
- 2026-09-11: BUG-285 final amend — a SUPERSEDED decision's own `WHAT IS LIVE NOW` forward-pointer (D-08) went stale when the entry that superseded it (D-14) was itself superseded (D-16). The chain D-08 -> D-14 -> D-16 read correctly by pointer while D-08's live-now clause asserted a false figure. Sweep lesson: when a supersession chain grows a third link, re-grade EVERY earlier entry's live-now clause, not just the one being amended.
