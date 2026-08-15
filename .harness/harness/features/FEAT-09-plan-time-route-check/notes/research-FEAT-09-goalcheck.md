# FEAT-09 goal-check — 12 SCs at HEAD `3a5a245`

## BLUF

**11 met, 1 unmet.** SC-08 is `unmet / UNPROVEN` — and **not** for the stale-`:193`-anchor reason
already ruled a planning defect. Its clause-4 fixture (case 17) **cannot fail**: the fixture path is
granted by *two* patterns, and the second (`.harness/features/**`, `team-config.yaml:28`,
harness-orchestrator) is exactly the prefix shape the clause exists to exclude, so a
prefix-comparison implementation would pass the case. The behaviour is correct — needs a test, not a
code fix.

Suite receipt for every automated SC: `./.claude/skills/harness/bin/run-unit-tests.sh` from the
worktree → **exit 0**, 13 scripts PASS, 0 FAIL (`--resolve` block 10/10, route-check 19/19 cases).

## Verdicts

| SC | V | Method | Covering case / receipt |
|---|---|---|---|
| 01 | met | automated | `test-check-domain.py:418` (a), `:423` (b). Both cited grants confirmed: `team-config.yaml:155` (harness-backend-dev) and `:197` (harness-dev-ops), both `.claude/skills/harness/bin/**`. Live resolve returns both, sorted (`check-domain.sh:215`). |
| 02 | met | automated | `:429` (c) literal `NOBODY`; `:436` (d) exit 0 **and** non-empty stdout, split out on purpose. |
| 03 | met | automated | `:441` (e) open pipe answers inside 10s; `:452` (f) closed stdin byte-identical. |
| 04 | met | automated | `:491` (i) `HARNESS_RESOLVE_PATH` set explicitly in the subprocess env; `:495` (j) empty string. Both assert exit 2 **and** the `may not write` denial text (`:489`), so the four resolve-branch exit-2 sites cannot fake it. VF-1 fix item 3 satisfied. In-domain still 0 at `:467` (h). Independently re-measured with payload files: clean / set / empty all exit 2, in-domain exits 0. |
| 05 | met | automated | `test-check-plan-routes.py:64,65,66` — non-zero exit, task id, offending path. |
| 06 | met | automated | `:74` (granting agent) and `:82` (`main-session-direct`). Both shapes. |
| 07 | met | automated | `:91` explicit `UNRESOLVED-GLOB` line; `:96` exit status equal to the same plan with the task removed. |
| **08** | **unmet** | automated | **UNPROVEN** — see below. |
| 09 | met | automated | `:116,117,118`; template carries `## Lanes` (`templates/PLAN.md:7`), both tokens (`:55,:56`), the stanza field (`:64`). |
| 10 | met | automated | Suite exit 0 — the drift detector (`run-unit-tests.sh:9-21`) runs first and would exit 2; registration fixtured at `test-check-plan-routes.py:126`, present in `SCRIPTS` (`run-unit-tests.sh:6`). |
| 11 | met | inspection | `git diff 47ed11f -- .claude/agents/harness-pm.md` → 0 lines at HEAD. Single rule-layer home: `.claude/skills/harness-spec-driven/SKILL.md:38-40` (the run-the-checker mandate, with the token forms at `:28-32`). A grep of `.claude/skills/` + `.claude/agents/` for `execution_mode` / `main-session-direct` finds no second normative statement — only `templates/PLAN.md`, which SC-09 requires. |
| 12 | met | automated | `:135` `DEVIATION` line; `:136` plan still exits 0. |

## SC-08 — why it is unmet

Clause 4 demands the no-prefix-comparison property be **proved behaviourally**, on a path *granted
only* through a mid-pattern wildcard. The delivered fixture does neither:

1. `check-domain.sh --resolve .harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md`
   returns **`harness-eng-lead` and `harness-orchestrator`** — I ran it. The path is not singly
   granted, contrary to `test-check-plan-routes.py:142-145`.
2. The orchestrator grant is `.harness/features/**` (`team-config.yaml:28`). A `startswith` on the
   text before `/**` matches. So would a prefix implementation of the eng-lead pattern.
3. Case 17 asserts only "no `VIOLATION` naming T-01" / "an `OK` line naming T-01"
   (`test-check-plan-routes.py:157-159`), and `OK {tid}` (`check-plan-routes.py:128`) names no agent
   — so the assertion cannot see *which* pattern granted it.
4. Therefore the case passes with or without the property. Clauses 1–3 are source greps (already
   noted as B-2, a different axis); clause 4 was the one behavioural leg and it does not discriminate.

**Behaviour is correct**, which is why the lane is `UNPROVEN` and not `BEHAVIOUR`:
`check-plan-routes.py` contains no matcher; `resolve_agents` (`:45-67`) is the sole path-decision
site and shells out to `check-domain.sh --resolve` with stdin closed, called at `:99`.

This is a **new finding**, not a relay of B-2 (`notes/backlog-detail.md:17-20`, the fnmatch axis) and
not the stale-`:193` anchor (B-5, a planning defect).

## Open questions

- Q1 (non-blocking): no path under `.harness/features/**` can be singly granted, since the
  orchestrator grant covers the whole subtree. A discriminating fixture therefore needs either a
  different mid-pattern grant or an assertion on the resolved agent name — which `OK {tid}` does not
  currently emit. Test design is the fixer's call, not this check's.
