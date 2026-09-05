# BUG-1303 — cycle-3 panel record transcribed into plan.yaml

**BLUF: `panel:` now records the cycle-3 run — PASS, both readers `ran`, zero new findings — and the
eleven carried findings are provably the same eleven, all `resolved`. Approvals stay `pending`; the
plan reaches signature with a current panel record and nothing requiring an overrule.**

## What changed

Two scalars inside the top-level `panel:` mapping, and nothing else:

| key | before | after |
|---|---|---|
| `last_run` | `runs/2026-09-05-07-validator` | `runs/2026-09-05-08-validator` |
| `cycle` | `2` | `3` (int) |

`readers` already carried exactly the required shape — `scope: ran`, `should-not-exist: ran`, neither
with `persona:` or `reason:` — so it was left untouched (the build script reported
`readers: already exact required shape, untouched`). `transcription_rule` and all eleven `findings`
were carried through unmodified.

Source of truth: `runs/2026-09-05-08-validator/digest.md` — `VERDICT: PASS`, `severity_max: none`,
`must_fix: []`, both members PASS with zero findings (scope = harness-code-reviewer,
should-not-exist = fable-advisor; digest.md:53-58 accounts for both as `ran`). No `PF-` id was
computed and none was needed: cycle 3 raised nothing.

## How it was written

`panel-value.yaml` was built **mechanically**, never retyped: `yaml.safe_load` the plan, take its
existing `panel` mapping as the base, mutate `last_run` and `cycle`, `safe_dump` the object. Then

```
plan-merge.py set-panel --file <FEATDIR>/plan.yaml --value-file /tmp/bug1303_panel_c3/panel-value.yaml
```

exit 0, `PANEL cycle 3 -> ... / APPLIED`. plan.yaml was never opened with Edit or Write.

## Acceptance — all seven proven, not asserted

The before-snapshot / after-compare script (`/tmp/bug1303_panel_c3/capture.py`, removed after use)
printed 15 checks, all PASS:

1. plan.yaml loads under `yaml.safe_load` — PASS.
2. `approval == {'status': 'pending'}`, sole key `status` — PASS. No `by`/`date`/`overrules`/`review_sha`.
3. `panel.cycle == 3` (int) and `panel.last_run == "runs/2026-09-05-08-validator"` — PASS.
4. `panel.readers == [{reader: scope, status: ran}, {reader: should-not-exist, status: ran}]`,
   no `persona`, no `reason` — PASS.
5. 11 findings; `open` = 0; `resolved` = 11; the id list is **element-wise identical** to the
   pre-write capture, and the full findings list compares equal object-for-object — PASS.
6. **The comparison actually run:** before the write, `tasks`, `requirements` and `decisions` were
   each `safe_dump`ed (sorted keys) and sha256'd, and every task's `verify:` string was sha256'd
   individually; after the write both were recomputed and compared.
   `tasks d9cd548c3fe1 -> d9cd548c3fe1`, `decisions 5692272f20af -> 5692272f20af`,
   4/4 `verify:` digests equal. **Caveat recorded honestly:** plan.yaml carries no top-level
   `requirements` key (requirements live in `BRIEF.md`), so that region compared `None == None` —
   `6a3a80ad810f` is the digest of the literal `null` dump, not of any content. The tasks and
   decisions digests are the load-bearing ones.
7. `check-plan-routes.py <plan.yaml>` — exit 0, `0 violation(s) across 1 plan(s)`. The one
   `DEVIATION T-01` line is the expected DEC-174 carve-out output (deviations do not gate).

`git diff` is not available as a cross-check here: the feature tree's `plan.yaml` is untracked
(`git ls-files --error-unmatch` exit 1, `check-ignore` exit 1), so the sha256 region comparison is
the byte-level evidence.

## Open questions

None from this dispatch. The digest's own Q1 (cycle-2 Q1 on T-02's absence clause) is recorded there
as MOOT and non-blocking; nothing in `panel:` carries it forward.
