# Fix round c1 build — FEAT-2488 — 2026-11-23

Builder: FixE1, ungoverned, main-session-direct under DEC-174. Contract: `notes/answers-2026-11-24-validate-c0.md`
steps 1–7. Base for the reds is HEAD `987e57b9`. The working tree is uncommitted: there are no git writes and no
plan-merge writes. Main records the step-8 amendments; the reason drafts are at the end of this note.
`HARNESS_AGENT_TYPE`, `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` were unset for every run. Receipts are in
`notes/fix-c1-build/`.

## Files

- `.claude/skills/harness/bin/harness_merge.py`: steps 1, 2, 3, 4 and 6
- `.claude/skills/harness/bin/plan_merge/guards.py`: step 1, plus docstrings
- `.claude/skills/harness/bin/plan_merge/amendments.py`: step 1, plus docstrings
- `.claude/skills/harness/bin/plan_merge/amend.py`: step 5
- `tests/unit/test-harness-merge-journal.py`: red tests for steps 2, 3, 4 and 6; interleave (iv) reshaped for MF-2
- `tests/integration/test-plan-merge.py`: red test for step 5; step 7

C4 is untouched, compared against both 987e57b9 and 2491336e (`10-diff-stat-and-c4-surfaces.txt`). The untouched
files are `check-plan-routes.py`, `tests/integration/test-check-plan-routes.py`, `check_state/`, `union.py` and
`test-checker-structure-locks.py`. C5 holds: the journal schema has no new field, there is no new entry point and no
fsync. The pair is a module constant, as the ruling's MF-2 pre-approved.

## Per step: red, then green

Red runs were made with the production tree byte-identical to 987e57b9; each receipt header records that. Test
sha256 values are unchanged since the red runs: unit `f01c1dd8…`, integration `f2c37d60…`.

| Step | Red at 987e57b9 | Green |
|---|---|---|
| 1 OQ-1 narrowing | `01-red-structure-locks-at-987e57b9.txt`: 54 FAIL, census 2+2+1 broad catches, exit 1 | `04-green-structure-locks-after-step1.txt`: ALL PASS, exit 0, after step 1 alone |
| 2 MF-4 | `02-…`: 2 checks (missing key recreated the ledger) | `05-green-unit-journal.txt`: 142/142 |
| 3 MF-2 | `02-…`: 25 checks (one-member, sibling and three-member journals ×2 routes; feature.json-primary ×3 routes locked `feature.json.lock` then `plan.yaml.lock`; locked_pair_update accepted a non-pair) | `05-…` |
| 4 MF-3 | `02-…`: 5 checks (dangling symlink: `locked_update` timed out; FIFO, and FIFO under another name: timed out; symlink to a valid journal: replayed) | `05-…` |
| 5 MF-5 | `03-red-integration-plan-merge-at-987e57b9.txt`: `2488/show: … stay byte-identical` FAIL | `06-green-integration-plan-merge.txt`: PASS |
| 6 bounding | `02-…`: 3 checks (5000-char name echoed whole; misbound long name was an OSError) | `05-…` |
| 7 MF-6, G-a..G-d | assertion-only, as ruled: green at 987e57b9 in `03-…`, which confirms production already met them | `06-…` |

The unit red is 35/142 checks. The 3 regression guards stay green at HEAD: the explicit-null absence, sign-approval's
nested shape, and the reshaped (iv).

## Verification (working tree; after the last edit)

- `07-code-grade-2491336e-to-working-tree.txt`: exit 0, `PASSING: 132`. The working tree is graded as a throwaway
  commit in a temporary shared clone, deleted afterwards; the repo was never written. The first grade put
  `_read_journal` at grade 3 / bar 4. It was split into `_read_journal` and `_pair_members`, then re-graded.
- `08-full-unit-kind.txt`: `run-unit-tests.py --kind unit`, 68 files, exit 0. Its `FAIL BUG-1290 5…` lines are
  `test-factory-claim-mutation.py`'s expected mutant proof; that file PASSes.
- `09-full-integration-kind.txt`: `run-unit-tests.py --kind integration`, 95 files, exit 0. The first run had one red,
  `test-typescript-typecheck.py`, which is host-only: there was no `node_modules/.bin/tsc` in this worktree. After
  `bun install --frozen-lockfile` (gitignored `node_modules`) the full kind re-ran green, and the receipt is that
  re-run. Neither disclosed host red (test-factory-config under $TMPDIR, INV-29 Kaya) fired.
- `11-verify-T-01.txt` and `11-verify-T-02.txt`: each task's literal `verify:` from plan.yaml, exit 0.
- `12-canonical-reader-audit.txt`: `0 unresolved reader site(s) across 101 Python file(s)`, exit 0.

## Design choices inside the ruling's latitude

- **MF-2 mechanism.** The ruling's second option is used: `harness_merge.JOURNAL_PAIR = ("plan.yaml", "feature.json")`
  at module level. `_read_journal` (via `_pair_members`) requires exactly those two members, in that order.
  `_recover_journal` refuses UNREADABLE, before any lock, any regular journal entry whose name is not
  `plan.yaml.harness-merge.journal`. It then takes only `plan.yaml.lock` and `feature.json.lock`.
  `locked_pair_update` raises ValueError for any other pair, so the producer never writes a journal that recovery
  refuses. The `recover_journals` signature is unchanged.
- **MF-3.** `_require_regular` lstats the entry before any open and before any lock. Only ENOENT counts as gone, so
  `_recover_journal` returns False. `_journal_bytes` opens with `O_NOFOLLOW|O_NONBLOCK` against a swap after the
  lstat.
- **Step 1, write_plan_and_ledger.** One tuple: `(JournalPending, MergeRefusal, OSError, ValueError)`.
  `_pair_failure` still dispatches by type. No further class was surfaced by any test, so none was added.
- **Step 7.** `_bytes` (open 'rb') moved beside `read()` at :180. The three SC-05 successors now take every snapshot
  through it, and none through `read()` at :176–178. That helper stays, because about 190 other call sites use it
  for text. The SC-05 count stays 8.

## Drafted amendment reasons (for Main's step 8)

### T-01.intent — `--reason`

> Validate c0 fix round 1, ruled in notes/answers-2026-11-24-validate-c0.md (OQ-1 (a); MF-2, MF-3, MF-4 and
> diagnostic bounding inside C5). The departures from the signed text are as follows.
>
> (1) Items 6 and 8 and the docstring (item 10): the replay handler in _replay and the post-publish handler in
> _commit_published catch OSError, not "an Exception". The signed text said "a BaseException that is not an
> Exception propagates unchanged". Now any non-OSError after the rename propagates unchanged as itself, with the
> journal kept, so the next write rolls it forward. The outcome space is therefore no longer total by construction.
> Every failure lands in one of three buckets: MergeRefusal; JournalPending; or an uncaught traceback with the journal
> on disk. The third bucket is confined to interpreter-anomaly classes. The reason is FEAT-63's broad-catch census,
> whose ceiling of 0 sits in check-plan-routes.py, which is forbidden to edit.
>
> (2) Item 4, under MF-2: members must be exactly two, named plan.yaml then feature.json (the module constant
> JOURNAL_PAIR), not "a non-empty list". A one-member, a three-member or a misbound-sibling journal is JOURNAL
> UNREADABLE, exit 5.
>
> (3) Item 4, under MF-4: before_sha256 must be present. Only an explicit null records an absent file; a missing key
> is UNREADABLE.
>
> (4) Item 4, under MF-3: the journal is read only from a regular file. It is lstat'd first, then opened
> O_NOFOLLOW|O_NONBLOCK. A symlink (dangling or not), a FIFO or a directory is UNREADABLE naming the journal. No FIFO
> is opened, and a dangling entry no longer reads as absent and spins locked_update.
>
> (5) Item 6, under MF-2 and MF-3: before the primary's lock, _recover_journal now lstats the entry and refuses
> UNREADABLE any non-regular entry, and any journal not named plan.yaml.harness-merge.journal. A feature.json-primary
> journal is therefore refused before any lock is taken, and the reversed order is unreachable. "Return False when it
> no longer exists" now means ENOENT only; it no longer means os.path.exists. The first-member check is subsumed by
> the pair check. Only feature.json.lock is taken as the further lock, not "each further member's sibling lock".
>
> (6) Item 8, under MF-2: locked_pair_update raises ValueError unless the two paths are plan.yaml then feature.json in
> one directory, not merely "two different files".
>
> (7) Refusal messages echo journal values as a repr truncated to 80 characters (security-low bounding).
>
> (8) Unit cases: interleave (iv) is reshaped, because a primary+X journal is now unreadable. The case is an
> unreadable journal discovered as naming X, which under the lock has become a legal generation that does not name
> X; it returns False and nothing is written. Cases were added for each of (2) to (7), plus sign-approval's nested
> shape.
>
> The signature stands (DEC-23); this is the ledgered judgement.

### T-02.intent — `--reason`

> Validate c0 fix round 1, ruled in notes/answers-2026-11-24-validate-c0.md (OQ-1 (a); MF-5 and MF-6, and the SC-01
> assertions G-a to G-d, in this round). The departures from the signed text are as follows.
>
> (1) Item 2: write_plan_and_ledger catches (JournalPending, MergeRefusal, OSError, ValueError), not "any other
> Exception". _pair_failure still dispatches by type. Any other class propagates as a traceback, and a journal already
> published stays on disk for the next write.
>
> (2) Item 2: _relay_after_commit catches (OSError, ValueError), not "an Exception from the relay".
> changed_state_feedback already absorbs its subprocess's failures. What remains is the stderr print: OSError on a
> broken pipe, ValueError on a closed stream.
>
> (3) Item 3: _recover_plan_journals catches (OSError, ValueError), not "any other Exception". OSError covers the
> listdir and lock-open failures; ValueError covers a malformed HARNESS_LOCK_TIMEOUT_SECONDS. "No recovery failure
> prints a Traceback" now holds only for those classes plus JournalPending and MergeRefusal. Anything else is a bug
> and tracebacks rather than be reported as "no file was changed". The reason is FEAT-63's broad-catch census
> (ceiling 0, check-plan-routes.py forbidden).
>
> (4) Under MF-5: amend.py's _amend_preflight passes recover=not args.show to _resolve_plan. amend --show therefore
> never runs recovery, keeping plan-merge.py's "write nothing" promise and D-02's mutating-verbs-only scope. This is an
> amend.py edit beyond item 5's enumerated list; the signed text did not mandate recovery for --show, and item 4 gave
> the recover=False lever to check.
>
> (5) Tests, under MF-6: case_1985's successor asserts "PermissionError" in stderr. The three SC-05 successors compare
> raw bytes through _bytes (open 'rb'), not the newline-normalizing read(). The SC-05 count stays 8.
>
> (6) Tests, G-a to G-d: (b) now runs through record-amendments as well as amend. (d) asserts the further re-run's
> exit 6 and its message. (f) runs through both verbs and asserts that the exit-5 message names the journal path. A
> new case asserts that amend --show leaves a pending journal and both files byte-identical.
>
> The signature stands (DEC-23); this is the ledgered judgement.
