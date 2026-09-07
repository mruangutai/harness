# Observations - harness-pm

- 2026-09-06: BUG-148 — a correction to DECISIONS.md cannot be an appended dated note: DEC-205 ends
  the amendment convention and tests/integration/test-gen-decisions-index.py:836 rejects any line
  starting with the bold token Amendment. The dispatch's phrase "dated correction note" had to be
  planned as an in-place rewrite that names the dates inside the sentence.
- 2026-09-06: FEAT-05-pyyaml-file-parsers/STATE.md is 165 lines against check-domain.sh's 120-line
  budget with 7 headings against 2 (check-domain.sh:1798-1805), so a Write of it is denied pre-hoc
  and only Edit works. Any task touching an old STATE.md needs that spelled out in its intent.
- 2026-09-06: proving a multi-conjunct verify ladder needs a mutant: on the pre-change tree the
  first grep exits and the later phrase greps are never reached. Built temp copies of both target
  files with the proposed corrected text and ran the same ladder against them.
- 2026-09-06: BUG-148 cycle 1 shipped an SC naming `python3 run-unit-tests.sh --kind integration`; the file is a bash script (shebang line 1), so the invocation was a SyntaxError, not a test run. The FLAG was valid, which is what made it read as checked. Measured corrected form `bash ... --kind integration` = exit 0, both named tests ok, 65s wall.
- 2026-09-06: BUG-148 T-01's verify greped five literals while its intent enumerated four; the fifth ('the artifact under change is the artifact doing the checking') appeared in no REQ, no SC and not in D-01's three-clause list. A doer following the intent exactly would have failed the verify. Mechanical check: extract every grep -qF literal from verify, assert each is a substring of intent — 0 gaps after the fix, and it also proves the absence-greps quote the stale sentence the intent tells the doer to rewrite.
- 2026-09-06: BUG-148 fix c1 — a criterion baselined on `git merge-base origin/main <sha>` is unmeetable on any branch whose base already carries other features' ship commits; pinning it to the plan's own `lanes.resolved_at` sha is the fix, and it costs nothing to write it that way first.
- 2026-09-06: BUG-148 — proving a re-baselined `git diff <base>..<review_sha>` at HEAD == base only proves it executes; the range is empty and the allowlist is never exercised. Report that, not a green.
- 2026-09-06: BUG-148 — `plan-merge.py amend --field verify --expect-sha256 <sha from --show>` is the whole route for a one-line verify change; --show prints the block and its sha in one call.
- 2026-09-06: panel transcription dispatch named sequential ids (PF-1..PF-5); panel_findings.py mints content hashes and its docstring says sequential ids let a risk acceptance drift onto a different finding on re-run. Used the tool, recorded the deviation in panel.transcription_rule and the DIGEST.
- 2026-09-06: the dispatch enumerated two readers; check-state.sh INV-32 (:534) demands should-not-exist + scope + goalcheck at approval, and BUG-148's goalcheck HAD run outside the validator run (notes/research-BUG-148-goalcheck-plan-c0.md, its F-2/F-4 cited by the panel). Recorded it as a third reader entry rather than shipping a record that reddens INV-32 at signature.
- 2026-09-06: reader entries key on `reader:`, never `id:` — check-state.sh builds by_reader off `reader` (:539), so an `id:`-keyed entry is invisible to the gate and reads as a reader that never ran.
- 2026-09-06: plan-merge.py apply appends a NEW top-level key after the base's last line and carries every base block byte-for-byte; the panel landing at line 187 of a 186-line base is itself the proof that tasks/decisions were untouched.
- 2026-09-06 (BUG-148): set-panel is the only route to a disposition; building the value-file by loading plan.yaml and replacing one field per matched id kept all five findings' content-hashed summaries verbatim while safe_dump changed presentation (+277/-116 lines in plan.yaml). A str representer forcing '|' on multi-line values keeps the file readable; the tool's reload-equality check is what makes that safe.
- 2026-09-06 (BUG-148): amend on depends_on without --yaml-value exits 4 with 'is a list, not text' - the refusal names the fix, so it costs one retry, not a diagnosis.
