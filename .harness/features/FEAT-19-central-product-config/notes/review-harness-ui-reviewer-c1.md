# Review — harness-ui-reviewer — FEAT-19 — Mode A — c1

**Verdict: FAIL.** One must_fix: `DESIGN.md` covers four refusal branches and states so
explicitly three times, but `plan.yaml` T-01's algorithm specifies five raise sites. The fifth
is unwritten in the plan, the design, and the tests.

## 1. Scope-in call — agree, it is right

SC-12 requires the resolution to be *observable* in one command's output, the plan wires that
through `factory_cli.body`/`payload` (an existing, precedent-bearing grammar — FEAT-11's
`DESIGN.md` is a whole document about one stderr line), and D-01/D-03/D-04 already treat
operator-facing text as load-bearing. The designer's scope-in is the correct call; "no
end-user surface" would have missed a real, checkable operator-facing contract.

`needs_prototype: false` is also right: one non-interactive command, one line of output, no
flow to operate, no `conventions:` in the manifest to prototype against. Agreed.

## 2. The branch count — checked against `plan.yaml`, not taken on the designer's word

`DESIGN.md` asserts "four" in three places: the scope line ("the four refusal lines"), the
BLUF ("two of the plan's four refusal messages"), and Contract 2 ("for the four failing
branches"). T-01's algorithm (`plan.yaml:99-127`) has **five** `raise ProductConfigError`
sites:

1. 3c — outside both roots (`plan.yaml:101-105`)
2. 4a — registered nowhere (`plan.yaml:110-112`)
3. 4b — product config file missing (`plan.yaml:118-121`)
4. 4b — product config file malformed/not-a-mapping (`plan.yaml:122-123`)
5. **step 5 — harness's own `.harness/harness.json` missing or unparseable** (`plan.yaml:125-127`)

Contract 3's table (`DESIGN.md:53-58`) has a row for 1–4 and none for 5. Branch 5 is reached
whenever a session resolves to the harness config (3a — session inside the harness root — or
the fleet-absent fallthrough at step 2) and that file cannot be read. `plan.yaml:125-127`
gives it no `what`/`value`/`next_step` text at all — unlike every other branch, which has the
message content spelled out in the intent. T-01's own test-case list (`plan.yaml:139-163`)
has no case exercising this raise either. So this branch is currently unwritten in the plan,
the design contract, and the test suite — nothing forces it into existence except this
review.

**must_fix:** `DESIGN.md` needs a Contract 3 row (or equivalent) for T-01 step 5 — the
harness-config-missing-or-unparseable branch — specifying `value` (the harness.json path
that was looked for, by the same logic Contract 2 already applies to 4b) and a `next_step`
that is an action, not an observation, matching Contract 3's own rule. Correct the "four"
count to five in the scope line, the BLUF, and Contract 2's opening sentence.

This depends on a plan clause currently in flux: **T-01's `intent:` step 5**, being rewritten
concurrently under the architecture send-back. Whoever re-authors it needs to give step 5
`what`/`value`/`next_step` text the way steps 3c/4a/4b already have it, and `DESIGN.md` needs
a row to hold it to.

Severity: `med`, not `high` — this is a corrupted-control-plane edge case, not a path any
normal operator hits. But `must_fix` non-empty gates FAIL regardless of severity, and the
document's own scope claim ("the four refusal lines") is false against the plan it cites,
which is exactly the kind of gap this mode exists to catch before it becomes rework.

## 3. Checkability

Contracts 1, 2, 4, 5 are tight — literal key lists, a literal grammar string, a literal cited
line/test-case pair, a literal path-resolution function call. An implementation can be judged
pass/fail against each without interpretation.

Contract 3's corrections for 3c and malformed-JSON are looser: "slot 3 must be an action
parameterized by the two roots, e.g. ..." gives an example, not literal required text. This is
advisory looseness, not a must_fix — the plan itself only says "names both roots" (generic),
so the design is filling a gap rather than pinning one string; a future reviewer can still
judge "is this an instruction or an observation" without a byte-for-byte diff.

## 4. Contradiction with plan/BRIEF — none found

Checked each Contract 3 correction against the plan text it corrects:
- 3c: plan says `next_step` "names both roots" (generic) — design's correction ("action
  parameterized by the two roots") narrows the phrasing but doesn't add behaviour the plan
  forbids; `value` stays the session root per the design's own note, matching plan.
- malformed JSON: plan says only "raise ProductConfigError naming the file" — design supplies
  the missing `next_step` text ("repair the file to a JSON object") and pins `value` to the
  file path. This fills a gap the plan left silent, it doesn't override specified text.
- Contract 1's three-key JSON payload and "config body MUST NOT be printed" match
  `plan.yaml:84-87`'s `main()` description exactly (prints product/config_path/source, "minus
  the config body itself").
- Contract 5's relative-path handling is already implied by T-01 step 3's
  `os.path.realpath(os.path.abspath(...))` normalization of `session_root`; the contract
  documents existing plan behaviour rather than adding new behaviour.

No contract change here quietly moves planned behaviour into pm's territory.

## 5. Measured-claim spot-check (Contract 4)

Both citations checked directly against the files at `63b83c7`, not taken on narration:
- `check-domain.sh:69` — `if [ "${1:-}" = "--resolve" ]; then` — literal match.
- `test-check-domain.py` case (c) (line ~883) asserts `r_nobody.stdout.split() == ["NOBODY"]`;
  case (d) (line ~890) asserts `r_nobody.returncode == 0 and r_nobody.stdout.strip() != ""` —
  both claims ("literal NOBODY", "non-empty stdout at exit 0") verified accurate.
- The stated grammar `factory: {tool}: {what}: {value} — {next_step}` matches
  `factory_cli.body()` + `factory_cli.message()` verbatim.

No mislabelled measured claim found; the document's self-labelling (contract language
everywhere except the two cited files) holds.

## Open questions

- Non-blocking, routed to the host (pm), not gating this review: `plan.yaml`'s step 2
  fleet-absent fallthrough goes straight to step 5 without passing through step 3's
  root check. If fleet.yaml is absent, a session rooted **outside both the harness root and
  workspace_root** would skip 3c's refusal entirely and resolve to harness's own config —
  the exact silent fallback SC-13/REQ-04 forbid. This doesn't gate my review: the output on
  that path is the success payload, already covered by Contract 1, so there is no
  unspecified *text*. But it is the cheapest moment to catch it, with T-01 live under
  rewrite.
