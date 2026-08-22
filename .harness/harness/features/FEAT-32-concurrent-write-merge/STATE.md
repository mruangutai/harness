# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **ship mission, build phase.** `status: Building`, committed through `a044548`. Both signatures
`approved` / `operator` / `2026-08-22` (`plan.yaml:4-7`, `BRIEF.md:431-435`), verified by me. Mirror:
milestone **21**, parent **#700**, sub-issues **#701-717**.

**LANES INTERLEAVE — the sequencing constraint of this feature.** Nine tasks are main-session-direct
under DEC-174 (T-01, T-07, T-08, T-09, T-11, T-12, T-14, T-15, T-16); eight are the team's (T-02..T-06,
T-10, T-13, T-17). `plan.yaml:9-80` (`lanes:`) is the authority.
**DONE:** T-01, T-02, T-03, T-04, T-05, T-07, T-15, T-16 — issues #701-#705, #707, #715, #716 closed.
**BUILDING:** T-06, T-10. **PENDING:** T-08, T-09, T-11, T-12, T-13, T-14, T-17.

**SEGMENT A (T-02..T-05) IS DONE — PASS, 3 SEND-BACKS, AND I RE-VERIFIED ALL FOUR MYSELF AT FINAL
BYTES.** Run `build-eng`, all `harness-backend-dev`. Send-backs: T-02 **2**, T-03 **1**, T-04/T-05
clean. Every `verify:` exits 0, and the newest deliverable byte predates my run — so these results are
current, not superseded. (An earlier mid-flight T-04 verify WAS superseded when its test file changed a
minute later; a mid-flight verify is valid only for the bytes it saw.) **I audited the red proofs
rather than trusting exit codes:** each mutant imports cleanly then fails a proportionate NAMED subset
— `USE_FLOCK` 2/18 (both case4, stale lock after SIGKILL), `UNION_MERGE` 59/110,
`PRESERVE_BASE_BYTES` 22/110, `APPROVAL_REFUSAL` 10/110. All-or-nothing failure would mean a mutant
that died on import. **T-05 deleted only its three sanctioned assertions:** `test-expertise-merge.py`
went 344 lines / 30 `check()` / 3 lock assertions to 409 / **32** / **0** — three removed, five ADDED,
so the suite got stronger; and `expertise-merge.py` now holds no lock or replace primitive of its own.

**SEGMENT B IN FLIGHT:** T-06 (`inflight_registry.py`, backend-dev) then T-10 (registration, dev-ops),
run `t06t10-eng`.

**THE RUNNER IS DOWN AND T-10 IS WHAT RESTORES IT — measured, not assumed.**
`run-unit-tests.sh --kind unit` exits **2 and runs ZERO tests**; the drift detector is a hard
precondition that aborts the whole runner. `--check-kinds` stops at the FIRST unregistered file
alphabetically (`test-dispatch-guard.py`, from T-07), so it has never yet reported segment A's three
new files and the kind cross-check below it has never run. **Bypassing the runner by invoking each
registered script directly: 35 of 36 PASS** (19/19 unit, 16/17 integration). The single failure is
`test-run-unit-tests-kinds.py` at 15/23, and **all 8 of its failures cascade from case 1
("--check-kinds on the real tree exits 0")** — pure registration drift. **CONSEQUENCE: T-10 must land
before the qa gate**, because until it does no suite runs and SC-14's after-observation cannot be
taken. Task `verify:` blocks are unaffected; they invoke `test-*.py` directly.

**A REAL DEFECT RISK, CONFIRMED WITH A CONTROL, pm judging.** `plan-merge.py:37` does a plain
`import yaml` — its approved intent demands "import it plainly" — while `harness_yaml.py:4` declares
itself the ONLY `import yaml` and its loader raises `DuplicateKeyError` at any depth. For a doc with a
repeated `status:` key, stdlib `safe_load` ACCEPTS and silently keeps the last value;
`harness_yaml.load_str` REJECTS naming line and column; **the same doc without the duplicate is
accepted by BOTH** — the control proving the discriminator is the duplicate, not a broken fixture. So
`plan-merge.py` can splice a `plan.yaml` the whole toolchain then refuses to read, both write hooks
failing closed. It fails LOUD, not silent, and it gates the main session's T-14.

**ONE COMMIT BEHIND MAIN AND I CANNOT FIX IT.** `12c66b3` (PR #719) fixed `RUNS_AGENT_EXEMPT` (FEAT-32
exempt at 5; writes land, confirmed at index 5 with `agent` present). `merge` is in `HEAD_MOVERS`
(`bash-write-guard.sh:144`), refused for every governed agent, so **the merge is the main session's
act**, and it must wait until no run is in flight because a HEAD move re-points every file under every
agent in the tree. Both `feature_schema.py` importers in the suite PASS against the stale copy, so
being behind is a correctness problem for what ships, not a gate failure.

`cycles_used` **3** of 10 — all three from segment A's send-backs; the four product runs reported zero.
Runs **9** of 20.

## Open Questions

- Q1 **BLOCKING — ONE CONSOLIDATED OPERATOR SIGNATURE, now THREE items. DEC-176 (`@4989`) requires one
  review pass and one consolidated fix, so they travel together.** (a) Amend T-13's intent from seven
  #551 occurrences to **eight** — occurrence 8 is at `runs/2026-08-21-2-product/digest.md:28` from an
  author independent of the STATE.md under suspicion; pm judged it NEW not covered; its "the mechanism
  DEMANDS a false verdict" claim is now measured twice over (`validate-digest.py:705` admits only
  `{PASS, FAIL, ESCALATE, BLOCKED}`, and I proved `none`/`unknown` are rejected using a missing-`branch`
  control). Gates T-13, which gates T-17. (b) Widen T-11 to add `.harness/**/*.lock` and drop its
  verify's path scope — the four lock sites are all under `.harness/`, so that one rule covers exactly
  them. **No do-nothing option**: declining it means SC-13 needs a seventh residue statement, itself a
  signed-text change. (c) The YAML entry-point split above, if pm judges it needs a signature.
  pm is assembling the consolidated request at `notes/operator-request-FEAT-32.md`.
- Q2 **NOT blocking, operator's call, a trade already declined once.** `BRIEF.md:16` also reads "seven
  measured occurrences". Amending the BRIEF resets its approval for prose — the trade refused on SC-14.
  Middle path: amend T-13 only, accepting the BRIEF understates a number the authority states right.
- Q3 **NOT blocking, pm's observation.** T-13's `verify:` asserts only token presence, so seven and eight both pass it; if the intent is amended, bind the count into the verify.
- Q4 **NOT blocking, CARRIED — do not re-raise and do not fix.** SC-14 names **221** as its basis while
  the plan records at `:1448-1464` that the number is not attributable to scripts; the operator declined
  to overturn pm's leave-it recommendation. **The criterion still works** — 221 is a SHRINK DETECTOR
  ("neither count is BELOW its baseline"), which holds whatever the number is composed of, though the
  plan notes a false-positive mode: a script that stopped printing per-case lines while still running
  every case would shrink the count with nothing broken. A goal-check tripping on SC-14 must name this
  as the carried question, never as fresh. The `ERROR`-lines sub-question is CLOSED by the plan at
  T-10's intent: all three carry the word inside a test's own NAME.
- Q5 **NOT blocking, recorded residual from the eng lead, not work.** The exit-6 LOCKED branch of T-03
  case 4 and T-04 case 7 was admitted but never taken in 20 trials each, because a 10-second timeout
  makes the loser wait rather than refuse. The property is pinned by T-02 case 8 and expertise-merge
  case 3 — by the SET, not by those cases.
- Q6 **NOT blocking, backlog.** `RUNS_AGENT_EXEMPT` was hand-fixed for two features. The suite asserts
  the map's MECHANISM, never its COVERAGE (`test-validate-feature-json.py:361-399`;
  `test-check-domain.py:2232` uses `feat not in RUNS_AGENT_EXEMPT` as a fixture *precondition*). Nothing
  asserts the key set matches the corpus — exactly why two features went missing.
- Q7 **NOT blocking, ANSWERED.** No `DECISIONS-INDEX.md` row governs what re-opens a signature, so the
  covered-vs-new principle lives only in a notes file. pm: it deserves an entry as FOLLOW-UP work, not
  folded into T-13, which would smuggle a governance rule in under a concurrency feature's signature.
- Q8 **NOT blocking, the main session's act; an agent composing a GitHub post is forbidden** (DEC-138
  am.6). #551's occurrence record needs updating once Q1 settles. Plus a backlog row against run-dir
  minting: a zero-padded seq once sorted before an existing `-1-` id and overwrote a prior round's
  digest. Dirs are NOT renamed — that would erase the evidence. All dirs minted this phase are correct.
- Q9 **NOT blocking, pre-existing, NOT mine.** `check-state.sh`'s one violation is FEAT-26's unapproved BRIEF.
- Q10 **NOT blocking, backlog, WIDER THAN THIS REPO.** `templates/gitignore.snippet` installs into every
  repo the factory touches, has 8 rules and no lock rule, so a repo-local fix leaves installed projects
  with the same gap. Separate pre-existing drift there: `:7` still reads `.harness/features/*/runs/**`,
  missing the `<repo>` segment the multi-repo migration added.
