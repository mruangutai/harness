# S-03 — Expertise sweep and state gate, measured

**BLUF.** All 13 Expertise files pass the sweep (`OK`, exit 0) — no product-squad file is flagged.
`bin/check-state.sh` as written in the dispatch does not exist (exit 127); the real gate is
`.claude/skills/harness/bin/check-state.sh`, which exits **0** with 47 `note` lines and zero
`FAIL`/`ERROR` lines. `status: skipped` + `verdict: none` on a step is **not flagged, and not
because it is an approved enum** — check-state.sh validates only state.yaml's *top-level* key set
(INV-16, lines 694–780). Nothing anywhere validates per-step `status`/`verdict` values.

## 1. `bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/`

Exit **0**. Full stdout:

```
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```

13 files, all OK. Nothing to route to another lead; nothing for me to fix.

## 2. The state gate

`bash bin/check-state.sh` → `bash: bin/check-state.sh: No such file or directory`, exit **127**.
There is no `bin/` at the repo root (`find . -name check-state.sh` returns exactly one hit).
Ran the real path instead: `bash .claude/skills/harness/bin/check-state.sh` → exit **0**.

Output is 47 lines, every one prefixed `note`. Full text is in this run's transcript; the shape:

- 2 pending-approval notes (FEAT-19 `plan.yaml`, FEAT-08 `PLAN.md`).
- 9 orphaned run dirs on disk not recorded in `feature.json` — including **all three of this
  cluster's distill runs**: `2026-08-16-15-distill-eng`, `-distill-product`, `-distill-validator`
  under FEAT-22. Plus FEAT-21 `2026-08-15-1-validator`, FEAT-15, FEAT-20 (four).
- 26 referenced-but-absent run dirs (FEAT-13, FEAT-09, FEAT-05, FEAT-06) — pruned history.
- 2 INV-22 run-budget notes (FEAT-10 32/20, FEAT-14 21/20).
- 3 INV-17 handoff exemptions (FEAT-21, FEAT-22, FEAT-15 — all-`main-session-direct` plans).
- 3 INV-23 STATE.md shape notes (FEAT-02 illegal sections; FEAT-05 165 lines vs 120 budget, plus
  illegal sections).

**The FEAT-22 orphan note is the one this cluster owns.** `feature.json` does not record the three
2026-08-16-15 distill run dirs; a resume would rediscover them by luck. Not a gate failure, but it
is the orchestrator's to reconcile.

## 3. The `skipped` / `none` question — answered, with the mechanism

The file is
`.harness/harness/features/FEAT-22-docs-layout-migration/runs/2026-08-16-15-distill-product/state.yaml`,
step `S-04-documentor-distill`: `status: skipped`, `verdict: none`.

- **Not flagged.** Exit 0, and no note names that file.
- **Why:** INV-16 (check-state.sh:694–780) checks the *top-level* key whitelist and mapping-ness
  only. `steps:` is on the whitelist; its contents are never descended into. Per-step `status` and
  `verdict` values are unvalidated by any checker in `.claude/skills/harness/bin/`.
- **Precedent is broad, so it is at minimum conventional:** `status: skipped` appears in run
  state.yaml files across FEAT-03, 04, 06, 07, 08, 10, 11 and more. `verdict: none` appears in 11
  distinct state.yaml files. The one-off spelling `verdict: n/a` appears once, in the whole tree.
- **Caveat, stated because it is uncheckable from here:** an unvalidated field's legality rests on
  convention, not on a gate. If the enum ever needs to be binding, INV-16 is where the check goes.

## 4. Product-squad section counts

Command:

```
for f in harness-pm harness-visual-designer harness-product-lead; do p=".harness/expertise/$f.md"; \
  echo "=== $f ($(wc -l < $p | tr -d ' ') lines) ==="; \
  awk '/^## /{s=$0; c[s]=0; order[++n]=s} /^- [A-Z]-[0-9]/{if(s!="")c[s]++} \
       END{for(i=1;i<=n;i++) printf "  %s: %d\n", order[i], c[order[i]]}' "$p"; done
```

| File | Lines | Patterns | Gotchas | Outcomes | Open |
|---|---|---|---|---|---|
| `harness-pm.md` | 112 | 15 / 15 | 15 / 15 | 3 / 10 | 0 / 5 |
| `harness-visual-designer.md` | 33 | 7 / 15 | 1 / 15 | 0 / 10 | 0 / 5 |
| `harness-product-lead.md` | 94 | 15 / 15 | 9 / 15 | 4 / 10 | 0 / 5 |

Counts match every `note:` claim in the distill-product `state.yaml`: pm `P 15->15, G 15->15,
O 2->3`; vd `P 6->7, G 0->1`; lead `P 13->15, G 8->9, O 3->4`. **pm is at cap on both Patterns and
Gotchas** — every future pm entry there is now a displacement, never an addition.

## Open questions

- Q1 (non-blocking): `feature.json` for FEAT-22 does not record the three 2026-08-16-15 distill run
  dirs. Orchestrator's to reconcile.
- Q2 (non-blocking): per-step `status`/`verdict` enums in run `state.yaml` are validated by nothing.
  Harness-defect-shaped, so it belongs here and not in Expertise.
