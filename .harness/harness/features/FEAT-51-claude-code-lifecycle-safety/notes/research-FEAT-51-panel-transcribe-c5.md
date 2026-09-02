# Panel transcribe — cycle 5 — WRITTEN

**BLUF — the cycle-5 panel record is transcribed into `plan.yaml`'s top-level `panel` key. Two
readers, both `ran`; seven findings, all `disposition: open`; three `high`, three `med`, one `low`.
Nothing outside the `panel` block moved: the diff is one hunk, `@@ -16,4 +16,45 @@`, 49 changed
lines (−4/+45).** This note supersedes its own earlier BLOCKED revision; the F-3 wording was ruled at
the lead's tier in favour of the digest's `T-06`.

## Label → id — the panel's vocabulary against the file's

| label | reader | severity | id |
|---|---|---|---|
| F-1 | `should-not-exist` | high | `PF-2b48984b50ff69c5dfdf8afa20c3956b` |
| VL-1 | `validator-lead` | high | `PF-5d8bf4a531ff09d8a871da695f0702e1` |
| SR-2 | `scope` | high | `PF-ba976e85d89cca1d56310530d12a05ef` |
| SR-1 | `scope` | med | `PF-e050d4756f4ab0a6a5e7fe71461a8262` |
| F-2 | `should-not-exist` | med | `PF-e380f685c0697fb709ff29f65af0cf24` |
| SR-3 | `scope` | med | `PF-7f73167ab7fd5d5961d92df08c08e89f` |
| F-3 | `should-not-exist` | low | `PF-6ac0675ca516deebb12428be36b02096` |

Every id was recomputed this pass by `panel_findings.py id`, one invocation per finding, with
`--summary` taken by `safe_load` from `runs/plan-panel-validator/digest.md`'s own `findings:` block —
never retyped, never taken from the prior spawn's table. All seven reproduced that table exactly,
including F-3 under the ruled `T-06` wording. The alternative `T-07` wording hashes to
`PF-314aff7f7a11d8d85ef32c4320ad2d79` and is **not** in the file.

**The digest's prose section and its `findings:` block agree on all seven.** F-3 reads `depends_on
T-06` at `digest.md:78` (prose) and `:135` (block); `plan.yaml`'s T-08 carries `depends_on: [T-06]`.

## VL-1 — recorded, nothing lost

`reader: validator-lead`, id computed under that same reader. It appears in `findings:` only and has
**no `readers:` row**, because it was a lead's fan-in synthesis, not a panel step. The severity,
summary and consequence-bearing wording are the digest's. Nothing about VL-1 was dropped, merged into
a reader's finding, or relabelled.

`readers:` therefore has exactly two entries, matching the two steps that ran. No `goalcheck` entry
was invented to satisfy `check-state.sh` INV-32, which expects three — see Q1.

## Verbatim-ness — one deliberate encoding choice

Summaries are emitted as double-quoted YAML scalars. The first apply wrote the two em dashes as
`\u2014` escapes; they load correctly, but a later reader recomputing an id by pasting the **raw**
line would hash the escape text and get a different id. The file was rebuilt from the preserved
original with literal characters, and the round-trip is asserted: every loaded summary is
byte-identical to the digest's.

## Gate results — all seven acceptance items, exit 0

1. `plan-merge.py apply` → `APPLIED <plan.yaml>`, **exit 0**.
2. `check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`, **exit 0**. Four DEVIATION
   lines on T-01/T-02/T-07/T-09 (the expected DEC-174 carve-out output); zero VIOLATION lines.
3. `yaml.safe_load` → ok.
4. `panel.readers` → 2 entries, both `status: ran`, personas `fable-advisor` and
   `harness-code-reviewer`; neither carries a `reason`.
5. `panel.findings` → 7 entries; `{high: 3, med: 3, low: 1}`; every `disposition: open`; no
   `resolved_by` on any; all ids match `^PF-[0-9a-f]{32}$` and `len(set(ids)) == 7`. Asserted by
   regex and set-length over the loaded YAML, not by eye. `last_run: plan-panel-validator`,
   `cycle: 5`.
6. Unchanged: `schema: plan/1`; `feature: FEAT-51-claude-code-lifecycle-safety`;
   `source_issues: [280, 551]`; top-level `status: plan`; 9 tasks, all `status: ready`; 17 decisions;
   `lanes.resolved_at: ad93d43e1f232ec1ab87e08ccf70a01a08c206b7`; 21 lane rows covering every task
   file (set difference empty); the `# NO approval MAPPING` comment block at `:7-14` intact; **no
   `approval` key** — the string `approval:` occurs 0 times in the file.
7. `diff` pre-change original vs final: **1 hunk, `@@ -16,4 +16,45 @@`, 49 changed lines (−4/+45)**,
   entirely inside `panel`. Final file is byte-identical to the proposal.

Route: `sha256` (`152aebac5c9a4a6ad22f926e51e8e3fecd31fc46f6eccf40f8db60b72d584075`, matching the
prior spawn's record) → `shutil.copyfile` → splice `panel` only → diff → `rm` by absolute path →
`apply`. No YAML dumper ever rendered the file; the untouched region is the original's bytes.

## No adjudication was performed

**No finding was resolved, dismissed, re-severitied, softened, reworded or fixed here.** Every
severity is the reader's own. F-1, VL-1 and SR-2 are `high` and gate; they enter the operator's
batched signature review under DEC-176. Only `approval.rulings` — the main session's write — can
overrule any of them. The panel's fix order (`digest.md:83-91`) and its two blocking/non-blocking
questions (Q1 on F-1's two remedies, Q2 on the F-2 spike) are unchanged and still live in the digest.

## Open questions

- **Q1 (non-blocking)** — `check-state.sh` INV-32 (`:396-417`) expects three `readers:` entries; the
  cycle-5 panel ran two. The gate and `teams/plan-panel.yaml` disagree. No entry was invented to
  silence it; the record is honest and the gate is wrong about this run.
- **Q2 (non-blocking)** — the template's `reader` enum (`templates/plan.yaml:70,77`) is a comment
  offering only `should-not-exist | scope | goalcheck`, with no word for a lead's fan-in finding,
  which VL-1 is. No validator enforces it (INV-32 reads only the `readers:` list;
  `check-plan-routes.py` does not touch `panel`), so `validator-lead` is truthful and breaks nothing
  — but the schema comment is knowingly out of step with the record.
