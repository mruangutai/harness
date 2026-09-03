# Panel record transcription — FEAT-52 — cycle 5

**`plan.yaml`'s `panel:` now records cycle 5.** 8 cycle-4 findings carried forward byte-identical
(the HIGH flipped to `resolved`), 9 cycle-5 findings created, 3 readers all `ran`. Nothing outside
`panel:` moved — every other top-level key compares identical against the pre-write snapshot.
Send-backs issued in this run: **0**.

## Derivation, finding by finding

| id | reader | sev | disposition | source line that decided it |
|---|---|---|---|---|
| `PF-93ebe15db8b54c3a43adc1c2ad877278` | scope | high | **resolved** | `runs/2026-09-01-02-validator/digest.md:3` "CLOSED on both halves, unanimously"; both halves `closed` in the gating table `:11-12`. `resolved_by` names T-02's third class + new T-15 (landed `runs/2026-09-01-03-product/digest.md:62-71`) and the closing panel run |
| the other 7 cycle-4 | — | med/low/info | open, unchanged | validator digest `:86-87`: not re-measured this cycle, "none has become *wrong*" — so no severity moves and no re-rating |
| `PF-a6c7d602…` NF-1 sne | should-not-exist | med | **resolved** | closed by `runs/2026-09-01-04-product/digest.md:9` (rows re-pinned to post-change spellings, 6+7 collapsed) |
| `PF-a8692862…` NF-1 scope | scope | med | **resolved** | same line: "red proof widened to two fixtures per row plus a third for row 6" |
| `PF-b2e0507f…` NF-3 scope | scope | low | **resolved** | `04-product:46-49` T-02 count corrected to 9 with breakdown |
| `PF-e275539c…` NF-2 scope | scope | med | open | `04-product:59-60` "Deliberately not addressed" |
| `PF-cd38bd20…` NF-3 sne | should-not-exist | info | open | same paragraph; `:61-62` confirms 2a did not absorb it |
| `PF-faff47e7…` NF-2 sne | should-not-exist | info | open | same paragraph |
| `PF-088ee512…` NF-4 scope | scope | info | open | same paragraph |
| `PF-10910123…` R1 | goalcheck | med | open | `notes/…goalcheck-plan-c5.md:41-50` |
| `PF-900f8e07…` R2 | goalcheck | low | open | same note `:51-56` |

Severities are the readers' own, transcribed from the validator digest's table (`:22-28`) and from
the goalcheck note. I re-rated nothing.

## The three calls I judged rather than transcribed

1. **NF-4 is recorded as a finding.** The validator listed it on a `—` row as "considered and
   dismissed", which argues against it — but `04-product:59-60` names `scope/NF-4 (info)` in the set
   bound for the operator's batched signature review under DEC-176. A row the next tier is expected
   to review must exist in the record it reviews. Recorded `info` / `open`, with the reader's own
   dismissal preserved inside the summary, so nothing is misrepresented as live concern.
2. **R1/R2 are goalcheck findings.** They are named residuals of a reader that ran, and INV-32 now
   expects a `goalcheck` entry; recording the reader and dropping its output would make a clean
   reader out of one that found things. R1 = **med**: `03-product` Q2 carries `blocking: false` and
   the lead ranks it above the surviving non-HIGH findings — a substantive coverage gap, not gating,
   which is exactly med. R2 = **low**: the note itself says it "matches SC-12 as written… an
   intent-level narrowing, not an unmet criterion", and CI still catches the drift.
3. **`resolved_by` cites runs, not tasks, for the three cycle-5 closures.** They were plan defects
   repaired inside `plan.yaml` by run `2026-09-01-04-product`; no T-NN carries them, so a T-NN
   citation would be false.

## Ids

Every new id came from `python3 .agents/skills/harness/bin/panel_findings.py id --reader <r>
--summary <s>`; none was typed. After the write I re-ran the tool over the summaries **as reloaded
from `plan.yaml`** and all nine reproduced — which also proves no summary tail was eaten by YAML
(G-12). The eight carried ids kept summary, severity and reader byte-identical, proven by a dict
diff against `/tmp/feat52-plan-before.yaml`.

## Value file — verbatim, as applied

Staged at `/tmp/feat52-panel-c5.yaml` (outside the repo) and applied with
`plan-merge.py set-panel --file <plan.yaml> --value-file /tmp/feat52-panel-c5.yaml`, exit 0,
`PANEL cycle 5 -> …` / `APPLIED …`. `set-panel` exits 5 if the spliced document does not reload as
the value supplied, so this text and the on-disk `panel:` block are the same document.

```yaml
last_run: 2026-09-01-02-validator
cycle: 5
readers:
- reader: should-not-exist
  persona: fable-advisor
  status: ran
- reader: scope
  persona: harness-code-reviewer
  status: ran
- reader: goalcheck
  persona: harness-pm
  status: ran
findings:
- id: PF-93ebe15db8b54c3a43adc1c2ad877278
  severity: high
  reader: scope
  summary: T-02's checker rule is directionally asymmetric - it flags a feature-directory WRITE anchored
    to the control plane but has no mirror rule for a control-plane READ anchored to the feature tree;
    BRIEF SC-04's per-site git-show direction assertion has no task carrier in any of the 14 tasks
  disposition: resolved
  resolved_by: T-02 (third violation class, shared predicate) and T-15 (seven-row pinned-tree proof),
    landed in run 2026-09-01-03-product; closed on both halves unanimously by panel run 2026-09-01-02-validator
- id: PF-4ea5b56692f0684ae2a69722b19bc74f
  severity: med
  reader: should-not-exist
  summary: T-14's text scan cannot prove SC-02's claim - inject-expertise.sh is set -uo pipefail, so a
    set -u abort exits 1 with no literal exit statement anywhere
  disposition: open
- id: PF-da16f6e14bec89a768041c4146c87873
  severity: med
  reader: should-not-exist
  summary: T-11 is a fourth restatement of the emit/consume duty already carried by two skills its four
    personas preload at every spawn
  disposition: open
- id: PF-afe3e3d65fe73e903150941e7e743ddd
  severity: low
  reader: scope
  summary: T-11's verify never invokes check-instruction-paths.py on its own four edited files, unlike
    every sibling anchoring task
  disposition: open
- id: PF-8653185d920aefec6f3db1679675e787
  severity: low
  reader: should-not-exist
  summary: T-05 step 3's second half is an assertion that cannot fail, sold as what makes the first discriminating
  disposition: open
- id: PF-65ac6313d97701eb7f22cff356013640
  severity: info
  reader: should-not-exist
  summary: 'Judgement on D-06 (second anchor, HARNESS_FEATURE_TREE_ROOT): warranted'
  disposition: open
- id: PF-1e26fa824db9045fae1c228c9b45f3c2
  severity: info
  reader: should-not-exist
  summary: 'Judgement on D-07 (spawn-time invocation of the lint over four files): warranted'
  disposition: open
- id: PF-559c6b10afab6a84fdbed61089ed56e3
  severity: info
  reader: should-not-exist
  summary: 'Judgement on D-08 (dispatch-guard exit-2 refusal keyed on the tool grant): warranted'
  disposition: open
- id: PF-a6c7d602504bc779c83acaf5a0dd7c48
  severity: med
  reader: should-not-exist
  summary: 'T-04 F3 and T-08 order the very spans T-15 pins: they respell harness-expertise/SKILL.md:16
    and :37 and harness-handoff/SKILL.md:80 to the .harness/<repo>/features/ form, while T-15 rows 3 and
    6 pin the pre-change .harness/harness/features/ spelling, so literal execution turns the last task
    in the DAG red on correct work'
  disposition: resolved
  resolved_by: 'run 2026-09-01-04-product step plan-repair-fix-c5: T-15 rows re-pinned to the post-change
    spellings, rows 6 and 7 collapsed onto one token under min_occurrences 2'
- id: PF-a8692862f69b4e85cf11d64ee79b61d2
  severity: med
  reader: scope
  summary: T-15's mandated RED PROOF prefixes each row's token with the wrong anchor, which always produces
    a match, so it only ever exercises direction_failures's wrong-anchor branch; the no-occurrence branch
    is never shown red, and that is the exact bare-grep defect T-15's own intent says it exists to fix
  disposition: resolved
  resolved_by: 'run 2026-09-01-04-product step plan-repair-fix-c5: red proof widened to two fixtures per
    row plus a third for row 6, FIXTURE B pinning the no-occurrence branch'
- id: PF-e275539cf9405f6508d8b4ad07b04117
  severity: med
  reader: scope
  summary: Neither T-02 (shape) nor T-15 (7 sites) can detect silent deletion of any of the 30-plus other
    required Harness-owned references; a shape lint only judges tokens that are present. Not repair-introduced.
  disposition: open
- id: PF-b2e0507f06db16824581fde1c2e9eb72
  severity: low
  reader: scope
  summary: T-02's intent claims 11 unsegmented .harness/features/ occurrences; re-derived, it is 9.
  disposition: resolved
  resolved_by: 'run 2026-09-01-04-product step plan-repair-fix-c5: T-02 intent corrected to 9 with the
    README 5 / STATE 3 / BRIEF 1 breakdown'
- id: PF-cd38bd20d720274758c38821a15c3be1
  severity: info
  reader: should-not-exist
  summary: 'Latent hole: a Harness-owned non-feature WRITE (.harness/harness/docs/DECISIONS.md, T-13''s
    lane) has no legal anchor - shape says CONTROL_PLANE, which in a self-dev run writes off the reviewed
    branch, while class 3 forbids FEATURE_TREE. No scope file backticks that path today.'
  disposition: open
- id: PF-faff47e7001a141c9455680e46b2a212
  severity: info
  reader: should-not-exist
  summary: 'Altitude judgement: T-15 is a task, not a test belonging inside T-12 - warranted. Named cost:
    once shipped, its pinned whole-scope run duplicates T-12''s on every unit execution.'
  disposition: open
- id: PF-088ee512395cc576aaad0e1754991ea5
  severity: info
  reader: scope
  summary: Widened predicate could over-flag a control-plane path containing a coincidental <segment>/features/
    span; no such site exists - considered and dismissed by the reader.
  disposition: open
- id: PF-109101235d1aa59cc5da112515d9e256
  severity: med
  reader: goalcheck
  summary: 'R1: issue 356''s headline symptom is never re-measured - no task and no SC fires harness_boundary.classify
    or check-domain.sh on the anchored absolute receipt path with the agent standing in a product base.
    One test-check-domain.py case asserting allow would carry it.'
  disposition: open
- id: PF-900f8e07139778d6f6fd67a50ca2e2b9
  severity: low
  reader: goalcheck
  summary: 'R2: the spawn-time drift scan (T-03 step 5, SC-12) reads only <root>/.omp/agents/<agent_type>.md,
    so drift against the .claude twin is invisible at spawn although CI still catches it. Matches SC-12
    as written - an intent-level narrowing, not an unmet criterion.'
  disposition: open
```

## Open questions

- Q1 (non-blocking): the panel record now says cycle 5 while `approval.status` is still `pending`,
  so INV-32 does not grade it yet. First grading happens at signature.
- Q2 (non-blocking): `04-product` Q1 (T-15 FIXTURE A prose imprecise for row 6) is a live plan defect
  that no panel reader raised, so it is **not** in `panel.findings`. It reaches the operator through
  the 04-product digest only.
