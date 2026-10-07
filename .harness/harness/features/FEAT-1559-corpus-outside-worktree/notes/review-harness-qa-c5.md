# QA gate — FEAT-1559 cycle 5 (run validate-c4-validator, pin f8a67546bcb42b6a5fd4327398615a4cfc07ae4d)

**BLUF: PASS.** Both required kinds are green at the exact SHA in a disposable full non-linked clone (unit exit 0, 52 files, 767 PASS; integration exit 0, 80 files, 2341 PASS). The c4 must-fix (top-level directory beginning with a literal `"` -> `git sparse-checkout set --stdin` exit 128) is closed: red at `35587d8d` production, green at the pin. `quote()` roundtrips through git for every byte 1..255 except `/`, with the git-side limits listed below (whitespace-edge dir names). No source, test or fixture was edited. Only my own evidence has examined the c4 fix in this gate; code-reviewer/security lanes are separate (O-07).

## Phase 1 (BRIEF + plan only)
For SC-01/SC-07/SC-08 repair: a top-level cone name of any legal byte content converges (repair 0, verify 0, name materialised, other features hidden); a name written to git stdin (sparse cone, hash-object paths) arrives as itself; a newline in a hidden-feature filename never splits hash-object input. Expected unit-level pin of the quoting predicate (SC-13 style, negative case per predicate): see coverage_gaps.

## Subject
Disposable full clone `/tmp/qa1559c5/clone` (`git clone --no-hardlinks --no-checkout` + `update-ref --no-deref HEAD` + `restore --staged --worktree`), HEAD f8a67546…, git-dir == common-dir (non-linked), shallow false, 5271 tracked files, status 0. Delta 35587d8d..f8a67546 (I read it, not the receipt): production = `worktree-state.py` only (+`_C_QUOTED`, `quote`, `stdin_lines`; `present_blobs` and `repair` use `stdin_lines`); test = +12 lines in `tests/integration/test-worktree-state.py`; the rest is notes/STATE/feature.json. Grep of `bin/`, `hooks/` for `--stdin|--stdin-paths|--pathspec-from-file`: the only name-bearing git stdin writers are `worktree-state.py:211` and `:333`; `:213` feeds link text as content. Matrix: T-01..T-05 `cross_module` => unit + integration always; T-06 abandoned, SC-10 deferred (settled).

## Required kinds (env -u HARNESS_AGENT_TYPE, cwd = clone)
| Kind | Command | Exit | Discovered | State |
|---|---|---|---|---|
| unit | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | "pool: 8 workers, 52 files, 14.55s"; 767 PASS | satisfied |
| integration | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | "pool: 8 workers, 80 files, 83.78s"; 2341 PASS | satisfied |

Discovery counts are nonzero and equal c4's (52/80); `test-worktree-state.py` (29 tests incl. the new one) ran as a script in the integration listing (`PASS test-worktree-state.py`, exit 0, 21.28s). Token audit: unit log `FAIL BUG-1290 5a/5b/5c` is `test-factory-claim-mutation.py`'s deliberate mutation proof (repo G-09); `ERROR could not resolve scan root` is the census self-test "unresolved root refuses" (ok line follows); no `----- ... (exit N)` with N != 0 in either log. Honest skips in integration: `test-corpus-real-owner.py` 2x `SKIP (host prerequisite missing): … clone is the owner itself`; `no conversion manifest` (T-06/SC-10 deferred to #2101); live manifest validation skip.

## Original c4 leading-quote probe (re-run, `probe_quote.py`, fixture owner + `FEAT-1-alpha` worktree, CLI `--repair --json`)
| Committed name | `35587d8d` production | pin f8a67546 |
|---|---|---|
| top-level `"quoted/file.txt` | repair rc 2: `git sparse-checkout set … exited 128: fatal: unable to unquote C-style string '"quoted'` | repair rc 0; verify 0; file on disk; hidden feature absent |
| hidden `…/notes/line\nbreak.md` | repair rc 2: `git hash-object: could not open '…/notes/line'` | rc 0, verify 0, hidden file absent |
| both | rc 2 (hash-object error first) | rc 0, verify 0 |

## Regression test closes the finding — `test_names_git_would_unquote_on_stdin_converge` (`tests/integration/test-worktree-state.py:99`)
- **Fail-first (natural RED, own reproduction):** test file from the pin run against `35587d8d` production: `Ran 29 tests … FAILED (failures=1)`; `AssertionError: 2 != 0 … 'error': "git hash-object … could not open '.harness/harness/features/FEAT-2-beta/notes/line' for reading"` (`old-run.log`, retained at `/tmp/qa1559c5-evidence/`). Because hash-object fails first, the test's red on old code is the newline arm; the leading-quote arm's old red is shown by the probe above (exit 128), and by arm mutant A below.
- **Per-arm discrimination (each site mutated alone in my disposable clone, restored, `git status` 0):** A) `repair` raw `"\n".join(cone)` -> test FAIL, repair rc 2, `sparse-checkout set … exited 128 … unable to unquote C-style string '"quote'`; B) `present_blobs` raw `"\n".join(files)` -> test FAIL, `2 != 0` hash-object error. Both arms are load-bearing and independently detected (O-06). After restore: `test-worktree-state.py` 29/29 OK, `test-corpus-real-owner.py` 6/6 OK.

## quote() byte roundtrip through git (ephemeral probes, `probe_bytes.py`, `probe_utf8.py`; every number measured)
Ground truth: git itself decodes the quoted stdin; compared via `git sparse-checkout list` (parsed by an independent decoder AND the tool's `unquote`), `git ls-files -t` skip-worktree bits (H for the target, S for a sibling) and `os.path.isfile`; hash-object via real `present_blobs()` vs python-computed blob sha1.
**A. top-level directory names via `sparse-checkout set --cone --stdin`:** 762 names = bytes 1..255 except 47 (`/` cannot lie inside one component; byte 0 is impossible) x {mid, leading, trailing} position. **753 ok, 9 not ok.** 370 had an on-disk e2e skip-worktree check; 384 (every byte 128..255 as a lone byte: macOS APFS refuses with `Illegal byte sequence`) were checked list-only (git decodes the octal escape back to the exact bytes).
The 9 not-ok are all whitespace bytes 9/10/13/32 at an edge of the name (leading tab, LF, CR, space; trailing the same) plus an LF in the middle (`d\nx`). **Git, not `quote()`:** the control run with `git sparse-checkout set --cone -- <name>` (argv, no `quote()` involved) gives the identical result (leading/trailing whitespace stripped from the stored cone line; LF splits the line into non-cone patterns). Through the real tool at the pin: ` lead`, `trail `, `\tlead`, `d\nx` -> `repair` exit 3 with findings `cone, skip-bits` (named refusal, no crash); identical at `35587d8d` (pre-existing, unchanged by c4). Middle tab/space/CR `tab\tin` converge (0/0).
**A2. valid UTF-8 (so byte values 0x80..0xF4 occur inside creatable names):** 115 byte values (0x80..0xF4 minus C0, C1) x 3 positions = 345 names: 333 ok e2e on disk, 12 ok list-only (APFS rejected an unassigned codepoint), 0 bad.
**B. hidden-feature filenames via `hash-object --no-filters --stdin-paths` (real `present_blobs`)**: 378 files created and hashed (bytes 1..255 except 47 and except bytes 128..255 as lone bytes, x 3 positions; 384 not creatable on APFS, same `Illegal byte sequence`): **0 mismatches in the batch, 0 when hashed one at a time**, including 10 (LF), 13, 34 (`"`), 92 (`\`), 9, 32. Plus A2 B-side: 333 valid-UTF-8 names, 0 mismatches. First probe attempt over-reported 52 mismatches: case-insensitive APFS collided `fAx.md`/`fax.md`; fixed by unique decimal-tagged names, recorded not hidden.
Exclusions summary: byte 0 and 47 untestable by construction; lone bytes 128..255 not creatable as files on this host (list-only for A, untested end-to-end for B; hash-object `--stdin-paths` decode of octal escapes for those is covered only by their valid-UTF-8 multibyte forms); nothing else excluded, no errors other than the nine above.

## SC-12 fresh active-caller (PM request; disposable managed pin, no live conversion)
Pin `…--validate-c4-validator--harness-qa-c5` at f8a67546: unrepaired caller -> `test-corpus-real-owner.py` 1 FAIL `test_check_state_passes_the_corpus_choke_point` (`LAYOUT cone (3) … skip-bits (4) … no invariant ran`, designed refusal of an unconverted caller); `worktree-state.py --repair --checkout <pin>` rc 0 "converged", `--verify` rc 0, status 0; rerun `Ran 6 tests … OK`, no SKIP (caller = pin; test's own probe pin created/removed by the test). Owner HEAD is the mutable host at this moment; this is a fresh run, not a transfer of c4's.

## Per-SC fail-first (automated SCs; tiers per O-03)
SC-01/07 (c4 delta): natural RED vs `35587d8d` (above, retained log) + per-arm mutants. SC-02..SC-09, SC-12, SC-13 and the c1-c3 seven-fix reds: carried verbatim from `review-harness-qa-c1.md`, `-c2.md`, `-c3.md`, `-c4.md` (natural RED where recorded, otherwise bootstrap/constructed mutants; SC-06 positive control, no red exists). Production for those SCs is unchanged by the c4 delta (the delta touches only quoting in `worktree-state.py`), and both full suites are green at the pin. I did not retake those proofs this cycle (G-06 does not apply: no wholesale rewrite).

## Coverage gaps / findings (severity unchanged; unclassifiable to open_questions)
1. No unit-kind assertion pins `quote()`/`stdin_lines()` directly (roundtrip, `"`, `\`, LF, octal for non-ASCII); the contract is held only by the integration arms, which exercise `"` and LF but not `\` or other punctuation. Advisory; my ephemeral probes (not committed) found no `quote()` defect, but nothing committed discriminates the `\` branch (a quote that mis-escapes `\` would pass the committed test; not mutated by me). Open question, non-blocking.
2. Top-level dir names with leading/trailing whitespace or LF cannot be held by git cone patterns; repair refuses with named exit 3 (pre-existing, not c4). Advisory/open question.
3. Retained: SC-13 per-predicate historical red gap; c1 G-1 maximal-clause mutant; detached-HEAD rebase docstring (c4).

## Principles applied
- Verification is the product (rule 7): old red and per-arm mutants reproduced, not credited from the receipt.
- Never falsify the record (rule 15): 9 not-ok names, the APFS exclusions, the skips and my own 52-mismatch probe artefact are all stated.
- Absence/subject/mutant (harness-code-review): the regression test's two arms each mutated alone.

## Cleanup
Pin `FEAT-1559-corpus-outside-worktree--validate-c4-validator--harness-qa-c5` removed via `pinned-checkout.py remove`; `/tmp/qa1559c5` (clone, old-code clone) removed; probe repos removed by their scripts. Raw logs and probe drivers copied to `/tmp/qa1559c5-evidence/` (ephemeral host dir; the guard denied writing to `runs/`).
