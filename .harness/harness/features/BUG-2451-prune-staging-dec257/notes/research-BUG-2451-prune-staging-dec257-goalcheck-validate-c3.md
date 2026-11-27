# Goal-check — BUG-2451 validate c3 (harness-pm)

**BLUF: PASS.** At review_sha a97dbc6a both perspectives are still discharged and SC-01..SC-04 are still met. The DEC-238 amend is met, and all five keep rows are untouched by this feature. The merge of origin/main did not change T-01's surfaces: the DEC-238 bullet and the ship paragraph equal their 5e51124e text plus exactly the one refusal sentence; DEC-257 is byte-identical to the merge base; the index regenerates identically. MF-2R's four acceptance lines hold as far as they bear on the code-maintainer perspective. **A-3 is resolved, measured.** There are no must-fix findings and no new findings.

## Pin and method

- Pin: a97dbc6a8337cfbe9402d2a727aa28797a1efaf8. I graded `git show a97dbc6a:<path>` and a `git archive a97dbc6a` extracted to /tmp/b2451-c3-pm/arc. I did not read the control-plane copy. The probes ran on per-probe copies of that archive; the worktree was not touched.
- The merge base is bda4a7eb, which equals origin/main. `git diff origin/main...a97dbc6a --stat`, with feature records excluded, lists exactly T-01's five files: pruner 66, DECISIONS-INDEX.md 18, DECISIONS.md 14, harness-ship.md 15, test 413.
- **Change since the c2 pin.**
  - Among the five files, `git diff b7e1f26e a97dbc6a` changes only the test and the two decision documents.
  - The pruner and harness-ship.md: 0 diff lines.
  - Every DECISIONS.md hunk between b7e1f26e and the pin lies in other decisions, at @5581, @6379 and @7320 to @7341. Those hunks come from upstream through 6e8c8c58. The feature's own DECISIONS.md diff against origin/main is the single DEC-238 hunk at @8138.
  - a97dbc6a changes feature.json only. HEAD f2fb2d5d, after the pin, also changes feature.json only.
- **Hashes at the pin.**
  - Test sha256: da00345e…fbcd57, which matches the fix record.
  - Pruner sha256: a6bc1fe5…99ad7a, unchanged since c2.
- **Run at the pin.** Command: `env -u HARNESS_AGENT_TYPE -u CLAUDE_PROJECT_DIR -u HARNESS_PROJECT_DIR python3 tests/unit/test-prune-run-evidence.py`. Result: rc 0, 52 PASS, 0 FAIL by grep of the `^FAIL` prefix, `all checks passed`. This confirms the orchestrator's 52/0 claim at the pin's tree.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | pass | SC-02, SC-03 | The pruner is byte-identical to c2, so both refusals still come before any mutation in both modes; this is the c2 measurement and the code did not move. The DEC-238 bullet (DECISIONS.md:8137) and the ship paragraph equal 5e51124e plus one refusal sentence (difflib: exactly one `insert` opcode each, sentence count 1). No forbidden claim is found in the scanned surfaces, in any letter case. |
| code maintainer | pass | SC-01, SC-04 | 52/0 at the pin. The c2 RED measurements against 47d6c54d (12 FAIL) and b2c1f55e (4 FAIL) carry over: the pruner is unchanged, and the test only gained checks. The five-file guard now reddens on a capitalised claim and on a one-character DEC-257 edit (see MF-2R below), so the regression the maintainer relies on catches the forms of drift it previously missed. |

## Success criteria (at a97dbc6a)

- **SC-01 met (automated).** The suite exits 0 with 52/0. The three T-01 `grep -Fx` lines are present in the output. `gen-decisions-index.py --stdout` diffs equal to DECISIONS-INDEX.md in the archive. RED-first is the c2 evidence: the subject is unchanged, and the test file changed only in the five-file guard.
- **SC-02 met (automated).** The pruner and its refusal tests are unchanged since c2. Nothing that SC-02 reads moved.
- **SC-03 met (inspection).**
  - The DEC-238 bullet and the ship paragraph each equal 5e51124e plus the one sentence, literally, with no whitespace folding.
  - Both are byte-equal to the c2 pin.
  - The index regenerates equal.
  - The guard scans the pruner docstring and source.
- **SC-04 met (inspection).**
  - harness-ship.md at the pin is byte-identical to b7e1f26e, so the step position, both invocations and the commit name are unchanged.
  - The pruner is unchanged, so the CLI, keep, UI-only and symlink behaviour is unchanged.
  - The test retains its coverage; the 52 checks equal c2's count.

## Merge confirmations requested

| Claim | Verdict | Measurement |
|---|---|---|
| DEC-238 bullet = 5e51124e + exactly one refusal sentence | holds | difflib(5e51124e, pin) on the literal bullet: one insert, the sentence, no other opcode. The bullet is equal to the b7e1f26e bullet. |
| DEC-257 section unchanged by this feature | holds | The section at the pin equals the section at origin/main/bda4a7eb and at b7e1f26e. It also equals the test's `DEC_257` constant under the test's own slicing. (It differs from 5e51124e and 47d6c54d, which predate the current DEC-257 text. That is not this feature's diff.) |
| DECISIONS-INDEX.md = `gen-decisions-index.py --stdout` | holds | `diff` on the archive was empty. |
| harness-ship.md restored paragraph unchanged | holds | The whole file has 0 diff lines from b7e1f26e to the pin. It differs from 5e51124e by the one inserted sentence. |
| Feature diff vs origin/main = only T-01's five files plus feature records | holds | See the stat under Pin and method. |

## Decision dispositions (DECISIONS.md at a97dbc6a)

| Row | Verdict | Evidence |
|---|---|---|
| DEC-238 amend (D-01) | met | DEC-238 starts at line 8125 and the bullet is at line 8137. It is the 5e51124e text plus exactly the one sentence, and the index is fresh. Owner: T-01. |
| DEC-174 keep | met | The clause is at line 4521. The section equals origin/main's. |
| DEC-179 keep | met | The clause is at line 4851. The section equals origin/main's. |
| DEC-225 keep | met | The clause is at line 7496. The section equals origin/main's. |
| DEC-254 keep | met | The clause is at line 8408. The section equals origin/main's. |
| DEC-257 keep | met | The clause is at line 8651. The section equals origin/main's byte for byte. |

## MF-2R acceptance as it bears on the code maintainer

The code reviewer owns the mutation census. Below is the reconfirmation of each line from my own probes on archive copies. Every red was `FAIL - five-file current claims and historical restoration`, rc 1, 51/1.

- **L1 holds.** In harness-ship.md, I added `Force-Stage retained records.` to the prune step heading. The guard went red. `claims()` uses `re.IGNORECASE` over whitespace-joined text (test lines 639-642).
- **L2 holds.** In DEC-257, I changed `with no` to `with No`. The guard went red. The exemption is `"" if dec_257 == DEC_257` (line 700).
- **L3 holds.** The unmutated control passes 52/0.
- **L4 / A-3: see the next section.**

## A-3 — resolved (measured)

The DECISIONS.md scan is now the DEC-238 section, plus DEC-257 while it matches the pin (lines 695-701). I ran two probes at the pin, each changing a single line so that no line was added and the index stayed fresh:

- **DEC-100.** `Folded into task 7.` became `Folded into task 7; git add the result.`. Result: rc 0, 52/0.
- **DEC-250.** The Lineage line gained `; Git Add -f it.`. Result: rc 0, 52/0. This probe also uses capitals, so it covers the boundary where L1 and L4 meet.

At c2, the first probe reddened the b7e1f26e test (fix record; I did not re-run that old leg).

**Boundary.** A `git add` written into the DEC-238 section still reddens. My probe planted it inside the ship bullet, so the bullet-equality check also fired; that confound means it proves only that the DEC-238 surface stays guarded, not which check fired first.

## Operator-kept advisories (one line each, not re-raised)

A-1, A-2 and SEC: the pruner is byte-identical to the c2 pin, so all three remain true as recorded at c2 [INFERENCE from unchanged code; not re-probed]. They are backlogged per the ruling.

## New at c3

None.

## Principles applied

- harness-pm P-06: I re-measured A-3's failed premise at the pin with the fix author's mutant and an independent one, rather than citing the green suite.
- harness-pm P-19: I ran one probe beyond A-3's contract, a capitalised claim in another decision, and one inside the still-scanned DEC-238 section. I stated the confound in the second.
- harness-pm G-15: every grade reads the pin, through `git show` or `git archive`. None reads the working tree, which carries an uncommitted feature.json edit and an untracked run directory that belong to the lead.
