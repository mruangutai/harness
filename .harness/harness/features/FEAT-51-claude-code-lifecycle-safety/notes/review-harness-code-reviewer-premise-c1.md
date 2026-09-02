# Premise check — FEAT-51 panel send-back (review_sha fa5ce88e, base 0bc57c88)

Measurement-only dispatch. Four falsifiable predictions, each confirmed or refuted with a
command and its real exit code. No re-review, no REQ grading beyond the mechanical
`code_grade` the contract requires.

## P1 — hook_mode fail-open: REGRESSION, not pre-existing. CONFIRMED

Pre-change refusal condition (`git -C <wt> show 0bc57c88:.claude/skills/harness/bin/validate-digest.py`):

`validate-digest.py:1686` (at 0bc57c88) — `if _kids:` — fires on nonempty `_kids` alone,
**no condition on any parsed verdict token** (there is no `_return_verdict` variable at
0bc57c88 at all).

Post-change condition, same file at fa5ce88e:1711 — `if _kids and _return_verdict in
VERDICTS:`.

A lead with live children and an absent/null `last_assistant_message` therefore exited 2 at
0bc57c88 and exits 0 after this diff. This is a REGRESSION the diff introduced, not a
pre-existing gap.

## P2 — shipped-binary reproduction. CONFIRMED (both halves)

Scratch root, real claims via `inflight_registry.claim()`: eng-lead's own claim (dispatcher
`Feat51Build`) + one live child (`harness-frontend-dev`, dispatcher `harness-eng-lead`),
feature `FEAT-TEST`. Payload: `{"agent_type": "harness-eng-lead", "harness_feature":
"FEAT-TEST"}` — no `last_assistant_message` key.

- Shipped (fa5ce88e, worktree HEAD) binary:
  `echo '{"agent_type": "harness-eng-lead", "harness_feature": "FEAT-TEST"}' | HARNESS_PROJECT_DIR=$SCRATCH python3 .../bin/validate-digest.py --hook`
  → **EXIT=0**. Registry after: parent claim GONE (released), child claim (`harness-frontend-dev`) PRESENT.
- Pre-change (0bc57c88) binary, same payload/claims (executed in-process via `exec()` with a
  spoofed `__file__` pointing at the real bin dir, so sibling-module imports resolve
  identically — no `--hook` semantics differ from a subprocess run):
  → **EXIT=2**, stderr carries `check-digest: BLOCKED - returned with children in flight
  (harness-eng-lead)`. Registry after: parent claim ALSO gone (release-before-check is
  unchanged across both versions), child claim PRESENT.

Both predictions hold exactly as stated.

## P3 — no test covers this combination. CONFIRMED

`test-validate-digest.py` (fa5ce88e, worktree HEAD == pin, file clean per `git status`):

- T-09 cases 1–11 (`run_t09`, `:1283-1425`) are the only live-children/registry cases. Cases
  6, 9, 10, 11 are the only ones with `agent="harness-eng-lead"` (a lead) + live children —
  all four fire `_t09_fire(root, "harness-eng-lead", LEAD_BLOCK, ...)`, and `LEAD_BLOCK` is a
  well-formed terminal `VERDICT:` text (checked at its definition and every call site: none
  passes `None` or omits the key).
- `_absent_key_case()` (`:739-745`) and the `null-passthrough` case (`:747-748`) are the only
  cases with an absent/null `last_assistant_message` — both use `agent_type: "harness-qa"`,
  a member, not a lead/orchestrator (`norm("harness-qa")` is not in `("lead", "orchestrator")`
  at `validate-digest.py:1633`), and neither sets up any registry claim, so `_kids` is `[]`
  regardless.

No case combines a lead/orchestrator payload, a live child claim, and an absent-or-null
`last_assistant_message`. Cases checked: all of `run_t09` (1–11), `_absent_key_case`,
`null-passthrough`.

## P4 — quarantine.py adopt cross-feature bypass, gate half. CONFIRMED (both halves)

`plan-sign-gate.py:372-377` (pin fa5ce88e):
```
match = re.fullmatch(
    r"\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/(.+)",
    rel,
)
if match is None or match.group(2) not in _reg.CANONICAL_ARTIFACTS:
    return None
```
`match is None` short-circuits `return None` before `orphan_write` at `:380` is ever reached.
The caller (`plan-sign-gate.py:405-406`, `if quarantine is not None: ... else: sys.exit(0)`)
treats `None` as "not a quarantine situation" — confirmed exactly as predicted, no new reading
required.

End-to-end reproduction, `mktemp -d` scratch root, canonical `feature.json` at
`.harness/harness/features/FEAT-TEST/feature.json` (content `CANONICAL-ORIGINAL`), staged
`feature.json` at `.harness/harness/features/FEAT-TEST/notquarantine/harness-backend-dev-sess1/feature.json`
(content `STAGED-BOGUS-ADOPTED`, same depth as a real quarantine entry, sibling dir named
`notquarantine` not `quarantine`), no claim in the registry for session `sess1`/feature
`FEAT-TEST`:

- Gate: `HARNESS_PROJECT_DIR=$SCRATCH3 plan-sign-gate.sh` fed `{"agent_type":
  "harness-backend-dev", "session_id": "sess1", "tool_input": {"command": "python3
  .../quarantine.py adopt --file $STAGED --root $SCRATCH3"}}` → **EXIT=0**, empty
  stdout/stderr — no refusal at all.
- `python3 .../quarantine.py adopt --file $STAGED --root $SCRATCH3` → **EXIT=0**,
  `ADOPTED .../FEAT-TEST/feature.json FROM .../notquarantine/harness-backend-dev-sess1/feature.json`.
  Canonical `feature.json` content after: `STAGED-BOGUS-ADOPTED` (overwrote
  `CANONICAL-ORIGINAL`).

Both predictions hold exactly as stated.

## code_grade (mechanical, per protocol)

`python3 .claude/skills/harness/bin/code-grade.py --base $(git merge-base origin/main
fa5ce88e) --head fa5ce88e` → base resolved to `0bc57c88...` (matches the pin). 63 functions
graded; 4 `RESULT: FAIL`:

| function | file:line | grade | severity |
|---|---|---|---|
| `cmd_adopt` | `quarantine.py:100` | 3 | **high** — below the grade-4 production bar; blocks the build |
| `quarantines` | `plan-sign-gate.py:339` | 2 | med — reasoned per protocol, does not block |
| `_invocation` | `plan-sign-gate.py:309` | 2 | med — reasoned per protocol, does not block |
| `case_1_2_adopt_plan_unions_tasks_and_preserves_approval` | test-quarantine (test code, bar 3) | 2 | med |

`code_grade: fail` (a gated grade-3 production function, `cmd_adopt`, is below its bar). This
is a mechanical fact only — not a re-review; `cmd_adopt` is the same function P4 already
examined for the containment gap, so the grade result is reported here rather than argued
with.

## Summary

All four predictions CONFIRMED. Nothing refuted. No unexpected findings tripped over beyond
the mechanical `code_grade: fail` on `cmd_adopt`, reported above per contract.
