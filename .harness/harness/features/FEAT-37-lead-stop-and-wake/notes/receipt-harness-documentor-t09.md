# Receipt — harness-documentor — FEAT-37 T-09 + docs sweep

**BLUF.** DEC-70 is scoped in place, the index is regenerated and drift-free, and the sweep found
two live contradictions in SPEC.md, both fixed. **T-09's mandated `verify:` block cannot pass as
written** — it invokes `gen-decisions-index.py --check`, a flag the script does not implement and
refuses with exit 2. The work is done; the grader is broken.

## The verify line, verbatim

```
index=2 scope=0
T09_FAIL
```

`index=2` is the unknown-flag refusal, not drift. The script's own docstring states "There is no
--check" and prescribes `--stdout | diff` instead; that check exits **0** — the index matches the
edited body. `scope=0` passes. Anchor was re-derived by text (em dash, `DECISIONS.md` heading for
DEC-70), never by line number.

## What changed in DEC-70, and why

`ai_behavior`'s `eval` requirement is **narrowed** to prompt, model and tool-integration changes,
with a markdown playbook an agent preloads graded by conduct through a UAT criterion instead —
because for a playbook the dataset and the grader come from one hand and no live behaviour is read
(D-17). Subsumed into the body, no amendment heading (D-09). `test_kinds.eval` is untouched and
stays available. Diff is one hunk at DEC-70; every other index row is byte-identical modulo `@line`.
Index ruling text (right of ` :: `, hand-written) updated to match.

## Sweep — inspected

`docs/PRINCIPLES.md`, `README.md`, `.harness/README.md`, `.harness/harness/docs/SPEC.md`,
`.harness/harness/docs/BUILD.md`, `.harness/harness/docs/DECISIONS-INDEX.md`; bodies of DEC-199 and
DEC-201 read for the corrected bound. Greps: wait/poll/sleep/block-on, once per / only once /
at most once / exactly once, stop_hook_active / SubagentStop / wake / resume / in-flight.

**Fixed, in domain (`SPEC.md`):**
1. §8.3 "Enforcement is **exactly one rejection deep**" — an unqualified once-only claim DEC-199
   corrects. Now states the bound is per consecutive stop sequence and re-fires on a later wake.
2. §9.1 `ai_behavior (prompt / model / **agent** / tool-definition change)` — "agent change" read as
   covering a playbook edit, contradicting the narrowed DEC-70. Narrowed, plus one clause naming the
   conduct route.

**No contradiction found:** `PRINCIPLES.md` rule 11 ("workers are never parked watching a build")
already agrees with the never-wait rule; `README.md` and `.harness/README.md` say nothing about
waiting or wake bounds; `BUILD.md`'s hook rows describe the format contract, not the wake bound.
Index rows for DEC-199 and DEC-201 match their bodies. No lead/orchestrator waiting text anywhere
in domain.

## Open questions

- **Q1 (blocking T-09's own gate).** `verify:` calls a nonexistent flag. Rerunning is futile; the
  clause needs fixing to `--stdout | diff` before T-09 can be graded green.
- **Q2 (not blocking).** SPEC §9.1's illustrative JSON shows `"when": [{ "kind":"unit", ... }]` and
  `"detect": "evals/**|*.eval.*"`, `"cmd": "<project eval runner>"`. Live `.harness/harness.json`
  has `{"always":["eval"]}` with no `when`, `detect: "evals/**|tests/**eval**"`, `cmd: null`,
  `status: unresolved`. Pre-existing divergence, not caused by this feature; left unedited.
