# Observations — harness-validator-lead — FEAT-25-claim-feature-root

Lead-tier findings from the qa segment (run `2026-08-19-2-qa-validator`), measured at source
while `harness-qa` ran the gate. Line anchors are at branch `feat/FEAT-25-claim-feature-root`.

- 2026-08-19: **Fail-open in `test-layout-migration.py`'s report block.** `:416-418` reads
  `if not ok and detail:` and `fails += 1` sits INSIDE that conditional. A failing case whose
  `detail` is empty prints `FAIL - <name>` and the script still exits 0. Reachable today: `:304`,
  `:308`, `:312` call `check()` with two arguments, so `detail` defaults to `""` — the three
  `case 18` assertions covering `lm.exit_code()`'s clean/mixed/cannot-verify mapping. Since
  `run-unit-tests.sh:59-66` routes purely on exit status, those three cannot redden the blocking
  gate. Swept `test-*.py` for the same shape: EVERY other suite increments its counter directly in
  the `else:` of `if ok:`, unconditional on detail. Isolated to this one file. Pre-existing, not
  introduced by FEAT-25 (this feature added only case 22).

- 2026-08-19: **It does NOT vacate SC-06.** T-03's verify greps the ok-line TEXT
  (`hasok "case 22: ..."`), so a failing case 22 prints `FAIL - case 22…` and the grep returns
  non-zero regardless of exit code. "The gate has a soft spot" and "this criterion is unproven" are
  different findings; conflating them produces the wrong remedy.

- 2026-08-19: **Case 22 does not pin row PRESENCE.** `test-layout-migration.py:409-410` asserts only
  `code == 0 and "features: CLEAN — evidence migrated" in features_line`. Its own comment at
  `:403-406` claims it covers "every FEATURES reader, including factory_claim.py" — the assertion
  checks neither. Form IS pinned conditional on presence (a present row reverted to legacy → reader
  disagrees with migrated evidence → MIXED → case 22 reddens). The undetected mutation is deleting
  the `READER_TABLE` row TOGETHER WITH its `layout_fixtures.STUB` entry, since `layout_fixtures.py:72-75`
  raises a loud import-time `RuntimeError` if the key sets diverge, catching either deletion alone.
  Row presence is bound only by T-03's `verify:` block, which the gate command does not run.
  Narration standing in for an assertion — the FEAT-24 shape.

- 2026-08-19: **The broader vacuity worry about case 22 is structurally foreclosed** and I was wrong
  to suspect it. `layout_migration.py:237-238` makes an empty row set `CANNOT_VERIFY` with cause
  `no-rows`, and `:257-261` carries a comment saying exactly why. CLEAN-over-empty cannot happen.

- 2026-08-19: **Q2 from the build digest is confirmed cosmetic, on evidence rather than trust.** The
  sc13b distinctness assertion derives its input from the real poll's stderr —
  `test-factory-claim.py:994` does `re.findall(r"skip #(\d+) — (.+)", err)`, so `reasons` holds
  eight; and `:997-998` asserts against `range(901, 909)`, which IS eight issues. Both assertions
  carry full power at eight. Only the two labels say "seven". Leaving them is correct, and SC-07's
  substantive half is discharged for the sc13b widening.

- 2026-08-19: **SC-03's no-monkeypatch clause is met, and it is the feature's strongest evidence.**
  The mechanism is a `CLAUDE_PROJECT_DIR` redirect on a FORKED subprocess — `test-factory-integration.py:399`
  sets `env["CLAUDE_PROJECT_DIR"] = root`, so `factory_claim.py`'s import-time `FEATURES_ROOT`
  resolves under the temp root via `factory_config.harness_root()`'s probe. No module patching. The
  fixtures now sit at `<root>/.harness/harness/features/<feat>` (`:715`, `:1079`), so a stale
  two-segment constant would look in `<root>/.harness/features/` and find nothing — case (F) genuinely
  binds the constant. A loud guard backs it: every case asserts stderr never contains "IGNORING it",
  which fires if the probe missed and `harness_root()` silently fell back to the real checkout.

- 2026-08-19: **Stream discipline holds at source (SC-05).** `_blocker_reason_text`
  (`factory_claim.py:187-`) is a pure function returning a string; it adds no print of its own, and
  every print site in the file carries `file=sys.stderr`. The new B5-ter cases read `err`, compute
  `absent_root` rather than re-spelling it (`test-factory-claim.py:849`, `:864-869`), and assert
  `out == ""`.

- 2026-08-19: **The ok-line prefixes differ between suites and both verify literals are correct.**
  `test-factory-claim.py:42` emits `ok    {name}` (four spaces), matching T-01/T-02's `"ok    $1"`.
  `test-layout-migration.py:415` emits `"ok   - "` (three spaces, dash), matching T-03's `"ok   - $1"`.
  `grep -qxF` is exact, so this was worth checking rather than assuming.

## How I work — candidates for distillation, not for this file's use

- Polling a filesystem path for a member's artifact is not a substitute for a message channel. I hold
  no `SendMessage` despite `harness-team` referencing it, so two checks I wanted to add mid-flight
  could not reach the running member. Raised as an `open_question`, not carried as a workaround.
- Spawning a placeholder agent to reach a messaging tool I do not hold wasted a spawn. Check the
  tool list before designing a routing move around it (G-12).
