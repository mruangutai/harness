# Receipt — SC-06 re-check (FEAT-10) — harness-pm

Path note: the dispatch named `notes/receipt-harness-pm-sc06-product.md`. `check-domain.sh` denies
that path to harness-pm (permitted set is `notes/research-*.md` and `notes/uat-*.md`), so this
receipt is filed under the granted research path rather than worked around. Raised as Q2.

**SC-06 is `met`.** Evidence is the passing integration case
`case_s "an UNLISTED repository is a violation naming the repo"` in `test-check-state.py`, reached
via `run-unit-tests.sh --kind integration`. The source reads below are corroboration that the
criterion's verb — *fails* — is what the code does; they are not the evidence.

Scope: SC-06 only. No other criterion was re-derived. Assessed the **working tree** (T-08 landed
operator-direct, uncommitted; `review_sha` f9488a2 is HEAD, so a diff shows nothing).

## The `verify:` string

Cross-checked against `plan.yaml` T-08 (`verify:` at plan.yaml:1439-1440) — identical to the string
in the dispatch. No mismatch.

Ran it verbatim: **exit 0.** `run-unit-tests.sh --kind integration` emitted
`PASS test-check-state.py`, and eight `ok - case (s) INV-24:` lines, including
`an UNLISTED repository is a violation naming the repo`.

## Read 1 — the exit path (this is what decides the verdict)

**It holds.** The convention is failure, not report.

- `check-state.sh:890` — the unlisted-repo branch calls `bad.append(...)`, the same list every other
  violation check uses. No new exit code.
- `check-state.sh:952` — `for m in bad:  print(f"  VIOLATION  {m}")` (the `warn` list prints
  `note` instead, at 953).
- `check-state.sh:956` — `sys.exit(1 if bad else 0)`

That heredoc is the script's last command, so its status is the script's status. `bad` is
initialized once at `:93` and is never reassigned, cleared, filtered or indexed before `:956` — a
grep for every non-`append` mention of the name returns only `:6`, `:93`, `:635`, `:952`, `:954`
and `:956` (a comment, the init, a comment, the two prints, the exit). So an entry appended at
`:890` is still present at the exit.

Confirmed behaviourally, not only by reading: a scratchpad fixture (one feature, a fleet listing
`acme/widget`) run against the real script produced
`VIOLATION  INV-24 FEAT-A: records factory repo 'acme/nope', which the fleet does not declare …`
and exit 1. The `VIOLATION` prefix is emitted only for members of `bad`, so the message is
exit-affecting by construction. A clean 0-versus-1 control pair could not be built — the guard
denies writing `.claude/settings.json` under scratchpad, and its absence raises an unrelated
violation in any fixture — so the prefix, not the pair, is the discriminator.

## Read 2 — the test case

**Message-only, and it does not distinguish exit code from printed line.** In
`test-check-state.py`, `case_s`'s helper binds the status and discards it —
`_code, out = run(tmp)` — then asserts only on `[l for l in out.splitlines() if "INV-24" in l]`
plus needle substrings. Had INV-24 been written to `warn` instead of `bad`, that case would still
pass. Non-blocking: the failure semantics are structural (Read 1), so SC-06 stands.

## Read 3 — evidence kind

`evidence: integration` is honoured. `test-check-state.py` is a member of `INTEGRATION_SCRIPTS`
in `run-unit-tests.sh:59`, so `--kind integration` selects it (line 72).

## Not graded (out of scope, per dispatch)

T-08's collision, parent-pair and absent-fleet clauses all showed `ok` and are noted only. INV-24's
trigger is any `factory` mapping, broader than the criterion — not re-opened.

## Open

- Q1 (non-blocking): `case_s` never asserts the exit status. Adding an exit-code assertion to the
  positive cases would make the test itself, not a source read, carry the failure claim. That is an
  enforcement-layer edit (DEC-174) and is the operator's to schedule.
- Q2 (non-blocking): harness-pm's domain has no receipt path. Either grant
  `.harness/features/*/notes/receipt-harness-pm-*.md` in `team-config.yaml`, or stop dispatching
  receipts to this role at that filename.
