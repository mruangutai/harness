# Observations — harness-backend-dev — FEAT-32

- 2026-08-22 (T-03): correlating text-splice line ranges to parsed `id`s is much cheaper and more
  robust done POSITIONALLY against `yaml.safe_load`'s own list order than by re-parsing each
  spliced text snippet as its own YAML fragment. `yaml.safe_load` preserves block-sequence order,
  so `zip(text_item_ranges, parsed_list)` is a safe correspondence as long as the two counts match
  — and if they don't, that mismatch itself is the signal something about the file's formatting
  (e.g. a list item not starting with a dash at the block's established indent) broke the
  text-index assumption, worth a `MergeRefusal(5)` rather than a silent misalignment.
- 2026-08-22 (T-03): a lock scheme that never removes its lock file (D-02's flock design in
  `harness_merge.py`) makes "assert the lock file is gone after a refusal" — the exact assertion
  `test-expertise-merge.py` uses for its O_EXCL scheme — actively WRONG when copied to a test for
  a flock-backed tool. Check which locking primitive a tool actually uses before reusing another
  tool's lock-cleanup assertion; the two schemes have opposite cleanup contracts by design.
- 2026-08-22 (T-03): building a symlink-based destination-escape fixture (dot-dot alone can't
  produce "literal ends in the matching tail, resolves elsewhere") is a repeatable three-step
  recipe: (1) create a real target dir with no `features/` ancestry in its own path, (2) inside
  a fixture tree, symlink the last matching path segment (e.g. `FEAT-99-fixture`) to that real
  target, (3) pass the CLI a path built by joining through the symlink — its string literally
  ends in the legal tail, but `os.path.realpath` resolves through the symlink to the disqualified
  target. Confirming the check is load-bearing (not just "it looks right") means mutating the
  resolve-vs-argument choice in the destination check itself and rerunning against the fixture.
- 2026-08-22 (T-03): I wrote the CLI before the test file on this task — caught it before running
  anything and restarted in the correct RED-then-GREEN order. Worth flagging to future runs of
  myself: seeing a fully-specified algorithm in a plan's `intent:` makes it tempting to just start
  implementing since "the test is obvious anyway" — that temptation is exactly backwards; the more
  fully specified the algorithm, the cheaper it is to write the test first, so there's no excuse.
- 2026-08-22 (T-04): I made the EXACT mistake T-03's own entry above warned about — wrote the
  full observations-merge.py CLI before test-observations-merge.py existed, caught it only when
  about to run the suite. Reading a prior run's own observation is not sufficient friction;
  what actually stopped it was noticing mid-flow that no test had failed yet. Recorded again
  because two instances of the same warning in one feature's log means the warning alone isn't
  the fix — the fix was deleting the file and restarting, which I did.
- 2026-08-22 (T-04): a symlink destination-escape fixture must reproduce the FULL tail the
  regex requires, not just "ends in the last named segment." plan-merge.py's PLAN_TAIL ends at
  the FEAT-dir + filename, so symlinking `FEAT-99-fixture` alone gives a literal path ending in
  the legal tail. observations-merge.py's OBSERVATIONS_TAIL has one more required literal
  segment after the FEAT-dir (`observations/`) before the filename — a symlink built the same
  way, with the escape target lacking an `observations/` subdir, produces a literal path that
  fails the tail match under EITHER the resolved-path check AND the mutated argument-only
  check, so the fixture doesn't discriminate the mutant at all (both sides refuse, silently for
  the wrong reason). The escape target itself must carry the trailing required segments (here:
  `outside-real-target/observations/harness-pm.md`) so the literal path really does satisfy the
  regex tail; only then does the resolved-vs-argument mutant separate correctly-refused from
  wrongly-applied. Always trace the tail regex segment-by-segment against the fixture path
  rather than porting a sibling tool's symlink recipe verbatim.
- 2026-08-22 (T-05): THIRD time this feature I wrote production code before the test — this time
  on a REWIRE task, where the trap is worse because most of the surrounding test file already
  passes unchanged and it *feels* like there's nothing new to make fail first. There was: I
  edited the test (three assertion swaps + case10) and only then noticed I'd already rewritten
  `expertise-merge.py`. Recovered correctly — `git show HEAD:<path>` to get the original back,
  ran the edited test against the untouched original, watched case10 genuinely RED (`exit 6`,
  stale lock treated as busy under the tool's own O_CREAT|O_EXCL scheme), then reapplied the
  rewrite for GREEN — but three strikes on the same mistake means I need an actual habit change,
  not another entry: on any task touching an existing test file, run `git diff --stat` on BOTH
  files before writing a single line of the production file, and refuse to touch the production
  file until that diff shows the test file already changed.
- 2026-08-22 (T-05): when a rewire moves a destination-refusal check onto `harness_merge
  .require_destination`'s fixed message template, the OLD custom stderr wording cannot survive
  byte-for-byte — its prefix ("expertise-merge: REFUSED — ... is not an Expertise file.") differs
  structurally from the shared helper's ("REFUSED: ... is not {what}."). The plan's own tests
  (case9) only assert `returncode == 9`, never a literal stderr string, so this is safe — but
  it's worth checking a task's "same wording, unchanged" instruction against what the test
  ACTUALLY pins before assuming a wrapper function can reproduce the old text verbatim through a
  shared helper with its own fixed format; when it can't, keep the old docstring on a thin wrapper
  (preserves the documented WHY) and accept the shared helper's own runtime phrasing.
- 2026-08-22 (T-06): a case's stale-claim fixture must hardcode the TTL as a plain literal
  (`ASSUMED_TTL_SECONDS = 3600`) rather than read the module's own `CLAIM_TTL_SECONDS` to build
  "now minus TTL minus one" — reading the module's live constant makes the fixture tautological
  and unable to diverge when that exact constant is the mutation target (P-05: an oracle built
  from the thing under test can't disagree with it). Caught this before writing the fixture,
  from the dispatch's own worked-example reddened-case list matching what a self-referential
  version would NOT have produced.
- 2026-08-22 (T-06): a locked_update-backed module needs its own directory to exist before the
  first write — `harness_merge.locked_update` opens `path + ".lock"` via `os.open(..., O_CREAT)`,
  which raises FileNotFoundError if the parent directory (here `.harness/`) is missing. A registry
  nested one level under the checkout root needs an explicit `os.makedirs(..., exist_ok=True)`
  ahead of the `locked_update` call — the shared core has no reason to create directories on your
  behalf, since it doesn't know your path convention.
- 2026-08-22 (T-06): my first draft of case 7's "informational" residual-shape line reported a
  hardcoded `0` instead of an actual measurement — caught before returning by rereading my own
  receipt draft and noticing I was about to assert a number I hadn't watched happen. Fixed to
  detect the real signal (a subprocess exiting non-zero with no result file written, meaning an
  uncaught `MergeRefusal` actually propagated) so the reported count is load-bearing, not
  decorative. A number attached to "informational" is not exempt from being checked.
