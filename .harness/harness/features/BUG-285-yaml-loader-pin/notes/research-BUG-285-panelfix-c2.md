# research — BUG-285 panel fix, cycle 2 — T-03 intent check 4

**BLUF: the plan panel's remaining `must_fix` is closed.** BRIEF SC-11 (`BRIEF.md:170-181`) is now
INSTRUCTED, not merely traced: T-03's `intent:` carries a fourth named check for the non-UTF-8
`feature.json` input. Nothing else in `plan.yaml` moved — every other field's sha256 is byte-identical
to the values recorded last cycle. `check-plan-routes.py` exits 0.

## What changed — one field, three edits inside it

`plan.yaml` tasks T-03 `intent:` (sha256 `11b2c394…a4319` → `0f16dcb0…fe1e9`):

1. **Check 4 appended** immediately after check 3's last line, before the `THEN PROVE THE NEW
   ASSERTION CAN FAIL` (D-04 probe) section. It instructs: binary-mode write of `b"\xff\xfetrash"`
   into a fresh `tempfile.TemporaryDirectory`, `load_factory(tempdir)` under
   `contextlib.redirect_stderr`, ONE check joined with `and` asserting SystemExit raised +
   code == `factory_cli.EXIT_REFUSED` + stderr contains the `feature.json` path, and a SECOND named
   check asserting stderr contains neither `unexpected failure` nor `UnicodeDecodeError`. **No
   exception class is named in any assertion** — same discipline check 3 already carries.
2. **Heading count corrected** — `THE THREE CHECKS` → `THE FOUR CHECKS`. It would otherwise be false
   the moment the block is read.
3. **Import list made sufficient** — it enumerated `factory_decompose, json, harness_yaml, os,
   tempfile and contextlib`, but check 3 already used `factory_cli.EXIT_REFUSED` and check 4 uses it
   too; `factory_cli` was missing. Added, with the reason inline.

Style matched to checks 1-3: same `N.` numbering with 3-space continuation indent, same `check()`
helper convention, unquoted phrase names, double-quoted literals, hard wrap at ≤95 columns (the
block's existing max width, unchanged).

## The standing-guard framing is carried into the wording

Check 4 says explicitly that it is **green under the old YAML reader too** (pre-T-02 `load_file` also
caught the decode failure), so its purpose is to stop the catch set being re-narrowed — and it
instructs the builder NOT to write a red-then-green probe for it and NOT to include it in the D-04
probe section, which covers check 3 only. That keeps SC-09's able-to-fail proof scoped to the one
assertion that can actually be reddened.

## Verification (post-write)

| Field | sha256 | expected |
|---|---|---|
| T-01 `intent` | `73412a4220ad01e5a2bc42ef6b7207dc791508aba4e98dc2b19d6b3fbd5bb7a2` | unchanged ✓ |
| T-01 `verify` | `7fee1afa6223d8eb2a9d8cb9e7bc0d8d86590d227f92ce8d2800818a1a6af24d` | unchanged ✓ |
| T-02 `intent` | `d52c04e34431714af83224868309b07d9e351840fe8fb2c0302dd62ad374966d` | unchanged from pre-write ✓ |
| T-02 `verify` | `e3f7e0752124409a4d689156c93fe8c1c905fa9be71cb3cc1cb2933e92588e38` | unchanged ✓ |
| T-03 `verify` | `dca60b2a666d444b22c8547d90f2af517743b7bed984cefe1ed7d95efc6e6d6c` | unchanged ✓ |
| T-03 `intent` | `0f16dcb0ab2e4458e32463484ea4c8747daa3d9caf0386354a9670dbf8afe1e9` | changed, as required ✓ |

- `approval:` / `lanes:` / `panel:` loaded-value digests identical pre- and post-write
  (`d5fdbab3…`, `09ccc878…`, `0b6bb08a…`).
- Loads through `harness_yaml.load_plan`; `intent:` is still `intent: |` (all three tasks) and the
  value ends in exactly one newline (`…(DEC-153).\n`).
- T-03's `verify:` reloaded and compared: byte-identical to the plan's two-command string.
- `check-plan-routes.py <plan>` → exit 0, `0 violation(s) across 1 plan(s)`, OK for T-01/T-02/T-03.
- No production or test source file touched; no git commit.

## Open questions

None. `must_fix` is empty.
