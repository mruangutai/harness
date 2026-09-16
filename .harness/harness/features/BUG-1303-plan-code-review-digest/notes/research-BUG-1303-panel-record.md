# BUG-1303 — panel record transcribed, A-5 applied

**BLUF.** The cycle-2 panel (PASS, `severity_max: med`, `must_fix: []`) is now recorded in
`plan.yaml`'s top-level `panel:` — cycle 2, both readers `ran`, eleven findings, eight `resolved`
and three `open`. A-5, the panel's one pm-owned med, is closed by an absence clause in T-02's
`verify:`, which returns **rc 1** on today's unmodified tree. Approvals untouched: `approval:
{status: pending}`, no other key.

## Job 1 — A-5 (med) applied

T-02's `verify:` gained two conjuncts, one per persona copy, immediately after the two presence
greps for the new fragment:

```
&& ! grep -qF "<HARNESS_CONTROL_PLANE_ROOT>/.harness/notes/review-harness-code-reviewer-" .claude/agents/harness-code-reviewer.md
&& ! grep -qF "<HARNESS_CONTROL_PLANE_ROOT>/.harness/notes/review-harness-code-reviewer-" .omp/agents/harness-code-reviewer.md
```

Written through `plan-merge.py amend --field verify --expect-sha256`; still a literal `|` block
scalar, one line, `safe_load` round-trips it (DEC-182).

**Why it discriminates, measured today (worktree working tree, feature dir untracked):**
the stale path occurs **2×** in each copy — the `artifact:` line (T-02 edit 3) and the write-grant
sentence (T-02 edit 4, `.omp/agents/harness-code-reviewer.md:34-36`). So edit (3) without edit (4)
leaves one occurrence and the clause is red. The absence clause alone returns **1** today
(`! grep -qF … .claude/…` → rc 1); the full chain returns **rc 1**, short-circuiting at conjunct 2
(the `code_grade:` grep, `grep -cF` → 0), and `sync-agent-adapters.py --check` → rc 0.

T-02's `intent:` gained one paragraph after edit (4) stating that the verify asserts the OLD
fragment absent in both copies, that (3)-without-(4) is therefore RED, and why presence alone could
not distinguish them. **BRIEF.md not touched** — no SC enumerates T-02's verify clauses; SC-03
speaks to T-01's in-suite presence assertions and SC-08 cites T-02's verify output generically, so
neither becomes wrong or under-specified.

## Job 2 — the panel record

`last_run: runs/2026-09-05-07-validator` · `cycle: 2` · readers `scope` and `should-not-exist`,
both `status: ran` (neither skipped, so neither carries `persona`/`reason`). `goalcheck` is omitted:
it did not run and `plan-merge.py set-panel` requires no full reader set.

Ids computed with `panel_findings.py id --reader <r> --summary <s>` over the summary string exactly
as stored; `panel.transcription_rule` records that, so a later reword visibly yields a new id and an
operator ruling cannot silently migrate.

| id | tag | sev | reader | disposition |
|---|---|---|---|---|
| PF-2e69b27e422520816d381adac766f1a6 | S-1 c1 | high | scope | resolved T-01 |
| PF-6efc08015899ed2657c9d87bc0a20732 | A-2 c1 | med | should-not-exist | resolved T-01 |
| PF-17b83de034aa3c08c64b228bf4feb2e1 | A-1 c1 | med | should-not-exist | resolved T-01 |
| PF-56f01265dc9d28433045d79aad5fdfc2 | S-2 c1 | med | scope | resolved T-01 |
| PF-c4303fdea9c772f8896aa8a1d49b15e4 | A-4 c1 | info | should-not-exist | resolved T-01 |
| PF-7041b66e94ff9bb78ff885acdd8af73f | A-3 c1 | low | should-not-exist | resolved T-01 |
| PF-d37f710e93d107d5127b5df3059fc508 | S-3 c1 | low | scope | resolved T-04 |
| PF-5ba1bdad5e4f89e55fefa3a6bb0ef447 | A-5 c2 | med | should-not-exist | resolved T-02 |
| PF-9c43910b2d2e6e14595b28a0c264a7f9 | A-6 c2 | low | should-not-exist | **open** |
| PF-87f1837ea32b6a51a980a10d527431fc | S-4 c2 | low | scope | **open** |
| PF-49abc17456e3e70e647d1f831bf115d3 | A-7 c2 | info | should-not-exist | **open** |

Every cycle-1 `resolved` is taken from the cycle-2 scope reader's independent re-derivation against
`plan.yaml` text (`notes/review-harness-code-reviewer-planpanel-c2.md`, "Verified closed"), not from
the repair note's prose. Severities are each reader's own, unaltered (`info`/`low`/`med`/`high`).

**The three `open` findings stay open on purpose.** A-6 (T-04 must not overclaim "checked
mechanically"), S-4 (an empty-but-present `CONTRACT_SOURCES` value is a silent no-op) and A-7
(nine personas graded twice) were each judged non-blocking or executor's discretion by the panel —
that is tolerance, not repair. Marking any of them `resolved` would be risk acceptance, which only
the main session can record via `sign-approval --overrule PF-ID:<reason>`.

## Gates run

- `yaml.safe_load(plan.yaml)` → ok; `approval == {'status': 'pending'}`, no key added.
- `check-plan-routes.py <plan.yaml>` → **0 violations** (one expected `DEVIATION` on T-01, the
  DEC-174 carve-out shape; deviations do not gate).
- T-02 `verify:` verbatim from the loaded plan → **rc 1**.

## Open questions for the operator

- The panel's Q1 (apply A-5, or accept it as executor discipline) is answered: applied.
- Q2 in the cycle-2 digest is a harness defect in the plan-review return path, not a plan finding.
  Unaddressed here and out of this feature's scope.
