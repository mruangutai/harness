# Receipt — which hook copy fires in a worktree (Q3/Q4/Q6, MEASURED) — 2026-08-03

Main session, at `65d2621`. Run because three open questions and two of my own claims all
turned on one unmeasured value, and I had twice stated a conclusion firmer than the
evidence.

## Method

One additive line inserted in the **worktree's** `check-domain.sh`, immediately after
`payload=$(cat)` (before every early exit, so any `agent_type` triggers it), appending
`BASH_SOURCE`, `CLAUDE_PROJECT_DIR` and `pwd` to a scratch file. `bash -n` and
`test-check-domain.py` (11/11) re-run after insertion and before spawning. Then one
throwaway `general-purpose` agent attempted a single `Write`. Then reverted and proved
byte-identical to HEAD (`git diff --quiet`), with `11/11` and `30/30` re-confirmed.

**The design cannot produce a false positive.** If the main checkout's copy had fired,
the probe line would never have executed and the file would never have appeared —
absence would have been the answer.

## Result — 11 fires, all identical

```
SOURCE = <worktree>/.claude/skills/harness/bin/check-domain.sh
CPD    = <worktree>
PWD    = <worktree>
```

`<worktree>` = `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog`

**The worktree's copy executes, `CLAUDE_PROJECT_DIR` is the worktree, and therefore
`root` is the worktree** (`check-domain.sh:64` takes `root` from that variable and the
manifest is readable there, so the `_derived` fallback is never reached). Consistent
across all 11 invocations — not intermittent, not racy.

## What this settles, including two things I got wrong

- **Q3 — RESOLVED.** The worktree copy fires with a worktree `root`. Combined with the
  coupling already established (the `settings.json` command path is itself
  `${CLAUDE_PROJECT_DIR}/...`, so script and root cannot diverge), there is no residual
  ambiguity. **SC-05, SC-06 and SC-08 ARE exercisable before merge** — no
  `verify: after-merge` is needed, and the panel can review observed behaviour rather
  than code.

- **Q6 — the premise is FALSE, and so was my claim.** I told the user, and wrote into
  `PLAN.md`'s approval note, that the `SubagentStop` validator "resolves the main
  checkout's `validate-digest.py`", so DEC-173's widened schema was "not in force until
  this branch merges." That was wrong. I had verified only that the two copies *differ*
  (main 0 `GATE_FIELDS`, worktree 2) and then asserted which one runs. Hooks resolve
  through the same `${CLAUDE_PROJECT_DIR}` as `check-domain.sh`, now measured as the
  worktree. **DEC-173 IS in force for agents spawned here.** I retracted the claim once
  as unproven; it is now positively disproven.

- **The 13 fenced return templates ARE live.** Same resolution path. I flagged the
  possibility that they were inert and never resolved it; they are not inert.

- **T-10 protects the right repository.** The bootstrap marker resolves to
  `<worktree>/.harness/.pyyaml-bootstrap`, which is what the new `.gitignore` rule
  covers. The feared "marker written into the main checkout" cannot occur.

- **Q4's diagnosis rested on the same false premise.** The orchestrator reasoned that
  T-09's probe append raised into `except Exception: pass` "because the main checkout has
  no `FEAT-05-pyyaml-file-parsers` directory". `root` is the worktree, which *does* have
  that directory — so the append had a writable target and the swallowed-exception theory
  does not hold. **T-09's non-execution therefore has an unidentified cause, and remains
  a verify-method defect** (`RESOLVED VIA: mechanism-unknown` satisfies its greps while
  the criterion is unmet). Do not treat Q4 as answered by this receipt; only its proposed
  explanation is eliminated.

## Incidental observation, not chased

**11 hook fires for what the agent reported as one write attempt.** Not investigated —
it is outside this probe's question and the count does not affect any conclusion above
(all 11 agree). Worth a look if hook latency ever matters: at the measured 80.63ms for
the governed path, an 11x multiplier on a single tool call would be ~0.9s of hook
overhead. Recorded so the number is not rediscovered from scratch.

## What is still NOT measured

Whether **skills** (`SKILL.md` preloads) resolve the same way. The probe covers hooks and,
by the shared `CLAUDE_PROJECT_DIR`, agent definitions under `.claude/agents/`. Skill
preloading is a different mechanism and was not exercised. No claim is made about it.

---

## Q4 (panel) — SubagentStop measured too, 2026-08-03

The review panel raised a contradiction: PLAN Amendment 2 says the worktree's hook copies
execute, but `harness-ui-reviewer` reported that the `SubagentStop` validator judging its digest
was the MAIN checkout's `validate-digest.py`. Both concern the same `${CLAUDE_PROJECT_DIR}`
resolution — and this is the claim Amendment 2 already retracted once, so it was measured rather
than argued.

**Method.** Same technique: a probe line inside `hook_mode()` recording `__file__` and
`CLAUDE_PROJECT_DIR`, one throwaway `harness-documentor` spawned to return a well-formed digest,
then reverted byte-identical to HEAD with `test-validate-digest.py` green before and after.

**Result — 15 fires:**

```
file = <worktree>/.claude/skills/harness/bin/validate-digest.py     (every fire)
cpd  = <worktree>        ... on some fires
cpd  = <unset>           ... on others
```

**The worktree's copy runs.** Amendment 2 holds for `SubagentStop` as well as `PreToolUse`, and
the ui-reviewer's inference is wrong. Its digest was judged by the worktree's validator, which
carries DEC-173's schema.

**But it found something neither observation named, and this is why the contradiction was worth
chasing: `CLAUDE_PROJECT_DIR` is sometimes UNSET in a `SubagentStop` hook.** Both earlier probes
covered `PreToolUse` only, where it was always set. So the two hook events genuinely differ in
their environment, which is plausibly what the ui-reviewer noticed and mis-attributed.

**Harmless, checked rather than assumed:**

- `validate-digest.py:597,621` already anticipates it by name — it resolves root through
  `payload.cwd` → env → `os.getcwd()`, with a comment reading "drifts (worktrees, unset
  `CLAUDE_PROJECT_DIR`) must not block a legitimate return".
- `check-domain.sh`, `bash-write-guard.sh` and `check-state.sh` all self-locate via
  `_derived`/`_selfdir` from `BASH_SOURCE`, so an unset variable falls back to the script's own
  repo.

**The lesson worth keeping: an environment measured on ONE hook event does not generalise to
another.** I called Q3 settled and it was — for `PreToolUse`. The panel's contradiction was
resolvable only because the two copies still differ.

### Panel Q4 — recorded in TWO halves, at the re-review's insistence

The re-review asked that this be split, and it is right. My earlier text ran the two together.

**Half 1 — MECHANISM: SETTLED.** The worktree's `validate-digest.py` executes, and DEC-173's
schema is in force for agents spawned here. Established three ways: 15 probe fires with `file=`
the worktree every time; the hook invokes the script on its shebang with no `python3` prefix, so
`__file__` IS the invoked-binary identity; and the panel's own ui-reviewer ran `validate()` from
both checkouts against a `severity_max: n/a` digest — worktree accepts, main rejects.

**Half 2 — CAUSAL ATTRIBUTION: UNCONFIRMED, and unfalsifiable from any record.** I wrote that the
sometimes-unset `CLAUDE_PROJECT_DIR` in a `SubagentStop` hook is "plausibly what the ui-reviewer
noticed and mis-attributed". That is a guess about why another agent concluded what it did, and no
artifact can settle it. It stays labelled as a guess. The unset-variable OBSERVATION is measured
and stands on its own; only the explanation of someone else's reasoning is speculative.

The distinction matters because this receipt is cited as evidence, and a measured fact sitting
beside an unmarked guess degrades the fact.
