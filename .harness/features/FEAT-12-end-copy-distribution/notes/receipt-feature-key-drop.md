Removed 22 key(s) from FEAT-12-end-copy-distribution's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `awaiting_user`
- old phase: `ship`
- new status: `Review`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
approval_gate: 'PASS - BRIEF ## Approval and plan approval.status both approved/operator/2026-08-10'
briefing: .harness/features/FEAT-12-end-copy-distribution/notes/ship-review-2026-08-10-ship.md
closeout: 'Distillation done. Ship-refresh SKIPPED and not forgotten - there is no
  .harness/codebase/ map in this repository, so the feature files_touched intersect
  nothing. 17 Expertise ops applied BY THEIR OWNERS; check-expertise.sh OK on all
  13 files, and the three reviewer files took INSERTIONS ONLY, verified per file by
  me. My own file: 0 ops - all four sections sit at cap and every candidate was judged
  already covered by P-06, P-15 or G-01. Healthy, not expertise_full.'
commits:
  T-07: e987c6d
  T-10: 9e49ba7
  T-12: ff75afb
  T-13: d543809
  T-14: 65d40cb
  T-14_fix: 8b53ebd
  layer0_nine: f3452bf
counts:
  decisions: 6
  reqs: 8
  sc_automated: 6
  sc_inspection: 4
  sc_uat: 1
  scs: 11
  tasks: 14
cycles_note: 'EIGHT. Four from the plan phase; one in t12-product where documentor
  was returned for writing a claim its own research had disproved; one for the SC-08
  fix cycle, where T-14 passed its own verify with the criterion unmet; one reported
  by goalcheck-product; one by distill-eng. The distill-apply round is NOT counted:
  both returns reported zero send-backs, and DEC-157 counts rework rather than a second
  forward step made necessary by a stale playbook premise. Say so if you read that
  differently. The nine layer-0 tasks never appear as runs at all.'
dec174_check: CLEAR. DEC-12 has 3 inbound references, all under docs/. No remaining
  task names check-domain.sh, bash-write-guard.sh, validate-digest.py or check-state.sh.
effort: https://github.com/mruangutai/harness/issues/203
gate_status:
  github_mirror: gh-sync open ran once; T-07, T-10, T-12 sub-issues closed. Do not
    re-run open
  qa_gate: PASS at d543809 - matrix_ok true, unit 11 PASS, integration 12 PASS, 0
    FAIL, 0 send-backs. Mutation-proven, not merely green
  review: 'FAIL(high) at d543809, 0 send-backs - one must_fix, SC-05 evidence. Panel
    Q1 measured BY ME and it dissolves most of it: see sc05_probe'
  suite: PASS at d543809 - full run exit 0, 23 test scripts PASS, 0 FAIL. Re-run BY
    ME after the commit, so allow-list entry 1 is load-bearing rather than inert
  uat: BLOCKING and OUTSTANDING - SC-06 is the operator's own run against a factory
    checkout of kaya
grilling: .harness/notes/grilling-end-distribution-2026-08-10.md
kaya_push: '7d2f946 on mruangutai/kaya-ai master. VERIFIED BY ME at f3452bf, not relayed:
  T-05''s verify string run verbatim returns REMOTE_CLEAN, and settings.json.harness-bak
  is absent from origin/master, so the D-06 reversal landed. The STOP condition was
  disambiguated as reading B by the operator after all 57 entries were identified
  as deploy.sh artifacts - notes/answers-2026-08-10-04-kaya-stop.md.'
mission: ship
plan_defects: TWO, recorded against the plan and NOT fixed by me - the plan is approval-gated.
  T-06's verify calls factory_config.repo_entry with ONE argument where the signature
  is repo_entry(fleet, name), so it raises TypeError whether or not the task succeeded;
  the work is correct and the verify is wrong. T-14's depends_on names T-11 and omits
  T-08, which measurably blocked it.
playbook_defect: MEASURED. The playbook says write-less reviewers return ops and the
  ORCHESTRATOR applies them. check-domain.sh denies harness-orchestrator every other
  agent Expertise file at exit 2, denies a lead its members files too, and grants
  each reviewer its own at exit 0 because all three hold Write. The documented path
  is impossible; the working one is forbidden by that document.
sc05_probe: 'MEASURED BY ME after the panel raised it, because a probe closes it and
  an inference does not. kaya .harness/ IS tracked - 117 files. The deletion commit
  7d2f946 touched NOTHING under it, so the pathspec held. Kaya''s working tree carries
  exactly ONE modification there, features/FEAT-03-live-review-loop/feature.yaml,
  whose mtime is 2026-08-07 19:57:04 - THREE DAYS BEFORE this feature ran, so it is
  not attributable to FEAT-12. Manifests are 377 identical paths with ZERO sha256
  fields, confirmed by me, so byte-identity was never captured. Net: content integrity
  is strongly evidenced by git for the 117 tracked paths and NOT evidenced for the
  260 untracked ones, and it can never now be captured. The ruling is the operator''s;
  I mark no SC.'
sc05_ruling: 'OPERATOR RULING, 2026-08-11. SC-05 is MET on path-set equality, WITH
  THE WEAKENING RECORDED HERE rather than left implicit. What the criterion claimed:
  same file count AND same per-file sha256. What exists: 377 identical PATHS and zero
  sha256 fields, plus git evidence that the deletion commit touched nothing under
  kaya''s .harness/. So content integrity is strongly evidenced for the 117 TRACKED
  paths and UNEVIDENCED for the 260 untracked ones. The before-state no longer exists,
  so no re-run can close the gap - a second capture would be two after-states. The
  operator accepted this rather than restate the criterion or fail it. Anyone citing
  SC-05 as byte-identity evidence is citing something that was never captured.'
sc08_gap: T-14 PASSED its own verify and SC-08 is still not met. SC-08 requires DEC-113
  to retain ONLY its override-precedence ruling; the section retains ~50 lines narrating
  the deploy command rewrite, its live-risk measurement and its safety properties.
  The verify cannot see this - its grep -q harness/teams clause was green BEFORE any
  edit, matching a later rename record rather than DEC-113, whose ruling names crews.
  Approved-but-unmet, so it is a fix cycle and not a plan amendment.
sc_tally:
  met: 10
  not_met: 1
  note: pm goal-check at d543809 read 9/1/1. Operator ruled SC-05 MET on 2026-08-11
    - see sc05_ruling. SC-06 remains not_met and is the operator's UAT
  partial: 0
segments_layer0: .harness/features/FEAT-12-end-copy-distribution/notes/segments-layer0-2026-08-10.md
t14_scope: JUDGED, not assumed. T-14's verify clause 1 now returns exactly 2 hits,
  DECISIONS.md:152 and DECISIONS-INDEX.md:32. Both are T-14's OWN targets - :152 sits
  inside DEC-12's section, which spans 149 to 158 and which T-14 strikes whole, and
  :32 is DEC-12's index row, which T-14 removes.
tasks:
  T-01: DONE
  T-02: DONE
  T-03: DONE
  T-04: DONE
  T-05: DONE
  T-06: DONE
  T-07: DONE
  T-08: DONE
  T-09: DONE
  T-10: DONE
  T-11: DONE
  T-12: DONE
  T-13: DONE
  T-14: DONE
verified_on_resume: I re-ran T-06, T-08, T-09 and T-11's verifies myself rather than
  accepting the states. T-08 DELETED_AND_DOORS_INTACT, T-09 registry absent, T-11
  SWEPT, T-06's real assertions hold.
```
