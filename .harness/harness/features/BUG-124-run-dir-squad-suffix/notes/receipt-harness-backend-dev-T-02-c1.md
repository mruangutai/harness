# Receipt — harness-backend-dev — BUG-124 T-02 — run c1

## Files touched
- `.claude/skills/harness/bin/dispatch-guard.sh` (edited)
- `tests/integration/test-dispatch-guard.py` (edited — appended cases only, cases 1-17 byte-unedited)

Not touched: `.claude/skills/harness/bin/harness_boundary.py`, `tests/unit/test-harness-boundary.py`
(T-01, already landed and read-only here), `.harness/team-config.yaml`, `plan.yaml`, `BRIEF.md`,
`feature.json`, `STATE.md`, `.claude/skills/harness/SKILL.md`.

## What changed

`dispatch-guard.sh`:
- After `GUARD_BIN_DIR` is computed, one shell block runs a non-isolated `python3 -c` (house
  precedent: check-domain.sh's pop-sys.path[0]-then-insert-bin-dir-as-argument pair) that resolves
  the root, parses `.harness/team-config.yaml` once through `harness_yaml.load_str` with no
  try/except (the bare parse — F-4), and prints `harness_boundary.run_dir_grant_globs(root)` one
  glob per line. Its exit status is captured via `if _globs=$(...); then _derived=0; else
  _derived=1; fi` so `set -uo pipefail` is never tripped by a non-zero substitution.
- `HARNESS_RUN_DIR_GLOBS` and `HARNESS_RUN_DIR_DERIVED` are now passed alongside
  `HARNESS_GUARD_BIN_DIR` into the existing `python3 -I` invocation — unchanged otherwise (case 16
  still pins system-Python compatibility).
- Inside the `-I` body, immediately after the `harness_boundary`/`inflight_registry` import
  try/except and before `_root_for`/the checkout resolution/the single-flight claim: the run-dir
  shape check. `refs = hb.run_dir_refs(prompt)`; refs with no globs prints one of two DISTINCT
  SKIPPED lines depending on `HARNESS_RUN_DIR_DERIVED` (manifest declares no grant vs. derivation
  failed) and falls through to the claim step either way; refs with globs computes `bad` via
  `hb.run_dir_slug_ok` and, if non-empty, prints the refusal (BLOCKED line, anchor-rewritten tail
  via `.replace(".harness/", "[.]harness/")`, compliant forms from `hb.run_dir_forms`, squad-suffix
  explanation, D-05 quoting-convention line) and `sys.exit(2)`. The whole block is wrapped in
  `try/except Exception`, printing and falling through on its own failure. No apostrophes anywhere
  in either new python body or the new shell comments.

`tests/integration/test-dispatch-guard.py`:
- New helper `_checkout_with_run_dir_grants(suffixes)` (does not edit `_checkout`) builds a
  throwaway checkout whose `leads:` carry one run-dir grant glob per caller-supplied suffix, and
  copies the same two personas `_checkout` copies.
- Six new case functions registered in `main()` after `case_17_...()`, covering (a)-(i) from the
  task intent: `case_18_inverted_slug_refused_no_claim_and_paste_back_safe` (a, b, g, h),
  `case_19_matching_slugs_not_refused` (c), `case_20_no_run_dir_reference_untouched` (d),
  `case_21_grant_less_manifest_fails_open_and_says_so` (e), `case_22_derived_vocabulary_matches_
  invented_squad` (f), `case_23_broken_derivation_distinguished_from_grant_less` (i). Every new
  check asserts exit code AND a distinguishing string; every case uses its own
  `CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR`-scoped throwaway checkout.
- Case 18b/22's compliant-form assertions check for the exact `<task-or-purpose>-<suffix>` string,
  not a bare `-eng`/`-oddsquad` substring, after discovering `-eng` appears vacuously in the
  guard's unrelated `harness-eng-lead.md` tool-grant-lookup-failure noise (since the dispatched
  persona in these cases is itself named `harness-eng-lead`).

## RED PROOF

Iron Law order followed: production code was written, then (per plan direction to write tests
FIRST) I reverted `dispatch-guard.sh` to the pre-T-02 (post-T-01) committed state via the `write`
tool, wrote/appended the test cases, ran them RED, then reapplied and byte-verified the T-02
implementation, then re-ran GREEN.

### RED run 1 — local pre-T-02 file, restored via `write` tool from `git show HEAD:...`

Command: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-dispatch-guard.py` (cwd =
worktree root), against `dispatch-guard.sh` at md5 `ca904b2906ad8d44662db428cb2dbc89` (matches
`git show HEAD:.claude/skills/harness/bin/dispatch-guard.sh`, i.e. the T-01-landed, pre-T-02 state).

FAIL lines:
```
FAIL  case 18a: an inverted run-dir slug is refused
FAIL  case 18a/b: stderr names the slug and the run-dir slug wording
FAIL  case 18b: stderr names a compliant form ending in -eng
FAIL  case 18g: the refusal strands no claim for the dispatched persona
FAIL  case 21: stderr says the manifest declares no run-dir write grant
FAIL  case 22: oddsquad-t01 is refused
FAIL  case 22: the refusal names oddsquad in its compliant form
FAIL  case 23: stderr says the run-dir vocabulary derivation failed
61 of 69 cases passed
```
Cases (a), (b), (f), (g) fail as required (via 18a, 18a/b, 18b, 18g, and the two case-22
assertions). The additional message-text sub-assertions inside cases (e)/(i) also fail here
(expected: the old file never prints a SKIPPED message at all); the pure not-blocked halves of
(c), (d), (e), (h), (i) all pass, unaffected by a guard that blocks nothing.

### RED run 2 — the pinned sha `6d969ed375f8458e32c47502ecdcc85bb9916635`, official RED PROOF

```
rm -rf /tmp/bug124-red-bin
cp -r <worktree>/.claude/skills/harness/bin /tmp/bug124-red-bin
git -C <worktree> show 6d969ed375f8458e32c47502ecdcc85bb9916635:.claude/skills/harness/bin/dispatch-guard.sh \
  | python3 -c "import sys; open('/tmp/bug124-red-bin/dispatch-guard.sh','wb').write(sys.stdin.buffer.read())"
chmod +x /tmp/bug124-red-bin/dispatch-guard.sh
md5sum /tmp/bug124-red-bin/dispatch-guard.sh
  -> ca904b2906ad8d44662db428cb2dbc89  (identical to RED run 1 — dispatch-guard.sh was untouched
     between 6d969ed3 and T-01, as expected: T-01 only touched harness_boundary.py and its test)
DISPATCH_GUARD_BIN=/tmp/bug124-red-bin/dispatch-guard.sh env -u HARNESS_AGENT_TYPE \
  python3 tests/integration/test-dispatch-guard.py
```
FAIL lines: byte-identical set to RED run 1 (same 8 FAIL lines, `61 of 69 cases passed`).

### Mutation proof (h) — anchor rewrite removed

Temporarily changed line 171 from
`print("  %s" % (tail.replace(".harness/", "[.]harness/"),), file=sys.stderr)` to
`print("  %s" % (tail,), file=sys.stderr)` (raw anchor, no D-05 rewrite), then ran the suite:
```
FAIL  case 18h: pasting the refusal back is not itself refused
FAIL  case 18h: the paste-back carries no run-dir slug refusal
67 of 69 cases passed
```
Only case 18h's two paste-back assertions redden, as predicted — the paste-back dispatch now
carries a raw `.harness/.../runs/eng-t01` reference and is refused a second time, proving the case
actually depends on the anchor rewrite. Restored the line, then verified restoration:
`diff /tmp/dispatch-guard.sh.t02-new .claude/skills/harness/bin/dispatch-guard.sh` → identical
(no output), `git status --porcelain -- .claude/skills/harness/bin/dispatch-guard.sh` → shows only
the real diff against HEAD (the full T-02 change), not the mutation.

### Mutation proof (e)/(i) — the two SKIPPED lines collapsed into one generic line

Temporarily replaced the `if os.environ.get("HARNESS_RUN_DIR_DERIVED") == "0": ... else: ...`
branch with a single `print("dispatch-guard: run-dir shape check SKIPPED.", file=sys.stderr)`,
then ran the suite:
```
FAIL  case 21: stderr says the manifest declares no run-dir write grant
FAIL  case 23: stderr says the run-dir vocabulary derivation failed
67 of 69 cases passed
```
Exactly the predicted pair reddens — neither case can pass against a single generic line. Restored
the two-branch text, then re-ran the full suite: 69 of 69 passed, and `diff` against the saved
correct copy showed no difference.

## Final GREEN

```
env -u HARNESS_AGENT_TYPE python3 tests/integration/test-dispatch-guard.py
```
→ `69 of 69 cases passed`, exit 0. (48 original checks across cases 1-17 unedited and passing, 21
new checks across cases 18-23.)

## Task verify — run verbatim, cross-checked against plan.yaml T-02

Cross-checked against `plan.yaml` T-02 `verify:` (line 325 as read) — identical string. Ran with
`HARNESS_AGENT_TYPE` unset first, cwd = worktree root:

```
unset HARNESS_AGENT_TYPE
python3 tests/integration/test-dispatch-guard.py && python3 -c 'import json,sys;q = "HARNESS-FEATURE: BUG-124-run-dir-squad-suffix\n[.]harness/harness/features/BUG-124-run-dir-squad-suffix/runs/eng-t01/digest.md";sys.stdout.write(json.dumps({"agent_type":"harness-orchestrator","tool_name":"Agent","tool_input":{"subagent_type":"harness-eng-lead","prompt":q.replace("[.]", ".")}}))' | .claude/skills/harness/bin/dispatch-guard.sh 2>&1 | grep -q "eng-t01"
```
Output: full 69/69 PASS listing from the test suite, then the guard invocation's refusal was
matched by the trailing `grep -q "eng-t01"` (real repo `.harness/team-config.yaml` carries the
`*-eng` lead grant, so `eng-t01` is correctly refused and its text is echoed to stderr, satisfied
by `grep -q`). Overall pipeline exit: `0`.

## Restoration integrity

`git status --porcelain` at the end shows only the intended changes to
`.claude/skills/harness/bin/dispatch-guard.sh` and `tests/integration/test-dispatch-guard.py` (plus
files already modified by T-01/others before this run started: `harness_boundary.py`,
`test-harness-boundary.py`, `plan.yaml`, and an untracked T-01 receipt — none touched by me).
`.harness/team-config.yaml` is unmodified.
