# FEAT-53 engineering ledger-repair evidence

## Scope and ruling

Binding ruling: `notes/answers-2026-09-22-resume-ui-lane.md` directs recording
unrecorded INV-40 amendments for T-02, T-20, T-24, and T-25, and repairing the
malformed `2026-09-16-02-eng` engineering digest. This receipt is records-only.

## Reproducible signed/current comparison

Signed source: `d9b6354b6837ca4762fccf8518a45c6b9f414b4b`:
`.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`. Current source:
this feature's `plan.yaml`. `plan-merge.py:2303-2313` defines the signed hash as
canonical UTF-8 JSON over exactly `files`, `intent`, and `verify`, recursively
key-sorted with `,`/`:` separators and `ensure_ascii=False`.

```sh
python3 -c "import sys,subprocess,json,hashlib;sys.path.insert(0,'.claude/skills/harness/bin');import harness_yaml;old=harness_yaml.load_str(subprocess.check_output(['git','show','d9b6354b6837ca4762fccf8518a45c6b9f414b4b:.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml'],text=True),'<signed>');new=harness_yaml.load_file('.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml');a={t['id']:t for t in old['tasks']};b={t['id']:t for t in new['tasks']};h=lambda t:hashlib.sha256(json.dumps({k:t[k] for k in ('files','intent','verify')},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();[(print(i,'signed=',h(a[i]),'current=',h(b[i]),*[(k,'was=',repr(a[i][k]),'now=',repr(b[i][k])) for k in ('files','intent','verify') if a[i][k]!=b[i][k]],sep='\\n')) for i in ('T-02','T-20','T-24','T-25')]"
```

The extraction ran successfully. Computed signed hashes match `feature.json`;
computed current hashes are:

```yaml
T-02: 70ff97357c0b6a161a6bc304cbe859fb249875bf7d4bfb0451c23587786d0d72
T-20: f888af3db9cd9a74bd3b8621a437093cf0c24d8633efbe19f46b4631282e8cd4
T-24: 54ddcdf5de32b4d496fb2b9c7f1dd294b8a9f4d152c8b351ea7018d051844bab
T-25: 2e675f0401099b37ccd3931ef212889ea868015d495b27e72d641c5ddc8195fd
```

`repr()` establishes that only T-02 `verify.was` and `verify.now` end in
`\n`. They intentionally use YAML `|`; every other scalar below has no
trailing newline and intentionally uses `|-`.

## Historical amendment entries

`was` is the signed preimage and `now` is the current parsed plan value. These
are the only changed signed fields; all `intent` fields are no-ops and omitted.

```yaml
amendments:
  - task: T-02
    field: verify
    was: |
      bash .claude/skills/harness/bin/merge-gitignore.sh . --check && git check-ignore -q .claude/skills/harness/bin/dashboard/client/node_modules/react/package.json && git check-ignore -q .claude/skills/harness/bin/dashboard/client/.vite/x && grep -q instrumented_at .claude/skills/harness/templates/gitignore.snippet && grep -q 'touchpoints[.]jsonl' .claude/skills/harness/templates/gitignore.snippet && python3 -c "import subprocess,sys;bad=[p for p in ('.harness/metrics/instrumented_at','.harness/harness/features/FEAT-53-metrics-dashboard/touchpoints.jsonl') if subprocess.run(['git','check-ignore','-q',p]).returncode!=1];sys.exit('ignored or unresolvable, must stay committed records (D-22): '+repr(bad) if bad else 0)"
    now: |
      python3 .claude/skills/harness/bin/merge-gitignore.py . --check && git check-ignore -q .claude/skills/harness/bin/dashboard/client/node_modules/react/package.json && git check-ignore -q .claude/skills/harness/bin/dashboard/client/.vite/x && grep -q instrumented_at .claude/skills/harness/templates/gitignore.snippet && grep -q 'touchpoints[.]jsonl' .claude/skills/harness/templates/gitignore.snippet && python3 -c "import subprocess,sys;bad=[p for p in ('.harness/metrics/instrumented_at','.harness/harness/features/FEAT-53-metrics-dashboard/touchpoints.jsonl') if subprocess.run(['git','check-ignore','-q',p]).returncode!=1];sys.exit('ignored or unresolvable, must stay committed records (D-22): '+repr(bad) if bad else 0)"
    reason: The shell merge-gitignore entrypoint was retired in favor of its Python replacement; the check retains the same observable contract.
  - task: T-20
    field: files
    was: [.claude/commands/harness-plan.md, .claude/commands/harness.md, .claude/skills/harness-uat/SKILL.md]
    now: [.omp/commands/harness-plan.md, .omp/commands/harness.md, .claude/commands/harness-plan.md, .claude/commands/harness.md, .claude/skills/harness-uat/SKILL.md]
    reason: OpenCode command adapters were added so the three human-touchpoint instructions stay identical across supported command surfaces.
  - task: T-24
    field: files
    was: [.claude/skills/harness/bin/dashboard/attention.py, .claude/skills/harness/bin/test-work-dashboard.py, .claude/skills/harness/bin/run-unit-tests.sh, .harness/harness.json, .claude/skills/harness/templates/harness.json]
    now: [.claude/skills/harness/bin/dashboard/attention.py, tests/integration/test-work-dashboard.py, .harness/harness.json, .claude/skills/harness/templates/harness.json]
    reason: The attention integration test moved from bin registration to tests/integration discovery; collector scope and behavior are unchanged.
  - task: T-24
    field: verify
    was: |-
      python3 .claude/skills/harness/bin/test-work-dashboard.py --case attention && python3 .claude/skills/harness/bin/check-kinds.py --files .claude/skills/harness/bin/test-work-dashboard.py
    now: |-
      python3 tests/integration/test-work-dashboard.py --case attention && python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 .claude/skills/harness/bin/upgrade-config.py . --check
    reason: The repository migrated from registered shell suites to directory-selected Python discovery; the attention and configuration checks remain the same.
  - task: T-25
    field: files
    was: [.claude/skills/harness-grilling/SKILL.md, .claude/commands/harness-plan.md, .claude/commands/harness-patch.md, .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/grilling_status.py, .claude/skills/harness/bin/backfill-grilling-status.py, .claude/skills/harness/bin/test-grilling-status.py, .claude/skills/harness/bin/run-unit-tests.sh, .harness/harness.json, .claude/skills/harness/templates/harness.json, .harness/notes/grilling-*.md, .harness/notes/grilling-status-backfill-2026-09-15.yaml]
    now: [.claude/skills/harness-grilling/SKILL.md, .omp/commands/harness-plan.md, .omp/commands/harness-patch.md, .claude/commands/harness-plan.md, .claude/commands/harness-patch.md, .claude/skills/harness/bin/check-state.py, .claude/skills/harness/bin/grilling_status.py, .claude/skills/harness/bin/backfill-grilling-status.py, .claude/skills/harness/bin/dashboard/work.py, tests/integration/test-grilling-status.py, tests/integration/test-work-dashboard.py, .harness/notes/grilling-*.md, .harness/notes/grilling-status-backfill-2026-09-15.yaml]
    reason: Intake adapters were added and grilling/dashboard integration tests moved to directory-selected discovery.
  - task: T-25
    field: verify
    was: |-
      python3 .claude/skills/harness/bin/test-grilling-status.py && python3 .claude/skills/harness/bin/backfill-grilling-status.py --check --root .
    now: |-
      python3 tests/integration/test-grilling-status.py && python3 .claude/skills/harness/bin/backfill-grilling-status.py --check --root . --manifest .harness/notes/grilling-status-backfill-2026-09-15.yaml && python3 .claude/skills/harness/bin/sync-command-adapters.py --check && python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout
    reason: The repository migrated to directory-selected integration tests and now verifies required command adapters before runner layout.
```

## `record-amendments` applicability

`plan-merge.py:2354-2405` makes `record-amendments` a compare-and-splice:
each live field must equal `was`, after which it writes `now`. The live plan
already equals every `now` above. This reconstructed historical list is valid
ledger evidence but cannot be applied to the current plan without restoring
the signed preimages, which is outside this records-only work.

## Historical digest legality

The existing `runs/2026-09-16-02-eng/digest.md` is malformed by repeated
serializations. Block 6 explicitly says it is a byte-derived reserialization
of Block 5; Block 7 explicitly says it is Block 5 with scalar serialization
changed. Block 5 is the sole canonical substantive source.

`check-domain.py:1260-1285` forbids replacing a nonempty run digest: existing
bytes must remain a verbatim prefix. The only legal repair is to append one
complete `VERDICT` / `DIGEST` / `artifact` block reconstructed from Block 5;
the parser selects the final line-start `VERDICT:` block. The lead owns that
append and the new engineering digest; this receipt modifies neither.

## Canonical return

```yaml
VERDICT: PASS
DIGEST:
  headline: Recovered byte-exact signed-task amendment evidence and the legal append-only repair for the malformed historical engineering digest.
  change_type: infra
  applied:
    - .harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-dev-ops-2026-09-22-ledger-repair-eng.md
  suite: n/a
  task: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-dev-ops-2026-09-22-ledger-repair-eng.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-dev-ops-2026-09-22-ledger-repair-eng.md
```
