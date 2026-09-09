# Panel transcription — BUG-201 plan panel step 3 — c0

**Done: `plan.yaml` now carries a top-level `panel` (`last_run: 2026-09-06-01-validator`, `cycle: 0`),
three readers all `status: ran`, and exactly ten `disposition: open` findings — written through
`plan-merge.py set-panel` only, with every id computed by `panel_findings.py` and re-derived through its
CLI after the write.** No severity was reassigned, nothing folded was double-carried, nothing invented.

## The ten findings as transcribed

| PF- id | reader | sev | what it is |
|---|---|---|---|
| `PF-d26198866e2756a2288bf70a4226659b` | `goalcheck` | `med` | F-01 · `factory_claim.py:108-109` → `None`, `gh-sync.py:1155`/`:1265` → `{}`/`None`; wrong cause reported |
| `PF-6dda61c31b87efdc801848fb78af21fa` | `goalcheck` | `med` | F-02 · SC-02 passable by a deny-everything write route / exit 9 |
| `PF-cc2bcfa945e44f6616257a66db45325d` | `goalcheck` | `low` | F-03 · SC-05 satisfied by a FAIL from any cause |
| `PF-e9eff4c667f72ba3c65f06fecbc161d0` | `goalcheck` | `low` | F-04 · no task proves a *correct* plan's consumers behave as before |
| `PF-4e86832239a56c223544656261a83cd7` | `goalcheck` | `low` | F-05 · D-03 lane reading under DEC-174 |
| `PF-4f91801bd1344ae2e8d1818b26cbd518` | `goalcheck` | `info` | F-06 · exit-2 at `check-plan-routes.py` graded as satisfying "before it can be consumed" |
| `PF-092cbd0b966447a02c1a6c5188f25c27` | `goalcheck` | `info` | F-07 · self-dependency acceptance is the null action |
| `PF-7beea12ebdabef0e2f946b763f7be080` | `goalcheck` | `low` | F-08 · SC-03's literal 67 is already 68; SC-03 re-graded met → partial (lead's L-1, retired here per Amendment 1) |
| `PF-3116cd3b98020bc5b450be865f3754bb` | `should-not-exist` | `low` | P-1 · T-01 case 6 cannot fail any plausible implementation |
| `PF-e159de1959db1573573a45c1ed92a175` | `should-not-exist` | `info` | P-2 · non-list `depends_on` rejection is a **declared** widening, exposure zero |

**De-duplication honoured as the lead recorded it** (`digest.md:157-160`): `should-not-exist` F-3 folded
into F-01, the `scope` D-03/DEC-174 result folded into F-05, L-1 retired into F-08 and transcribed once
from the `goalcheck` set. `scope` ran clean — zero findings, carried by its `readers` entry, no
placeholder row.

**Normalization applied to any summary: none.** P-1/P-2 are the lead's `panel_findings` rows verbatim
(they carry no markdown); the eight `goalcheck` summaries are authored one-liners faithful to the step-1
note. Every id is a hash of the exact string on disk, cross-checked through the CLI (10/10 match), so no
`panel.transcription_rule` entry is owed.

## Verification results

- **a. `yaml.safe_load`** loads the file. `last_run == '2026-09-06-01-validator'`; `cycle == 0` as `int`
  (not `bool`); 3 readers, all `ran`, each carrying only `reader`/`status` (no `persona`/`reason`, none
  skipped); 10 findings; severities by reader `goalcheck [med, med, low, low, low, info, info, low]`,
  `should-not-exist [low, info]`; every id matches `^PF-[0-9a-f]{32}$`; every `disposition == 'open'`;
  every finding carries exactly `id, reader, severity, summary, disposition`. No summary was truncated
  by an inline `#` (full char counts 171–249 survive the reload).
- **b. `approval`** is still exactly `{status: pending}` — byte-identical to the pre-write file, and all
  eight pre-existing top-level keys (`schema, feature, approval, status, source_issues, lanes, decisions,
  tasks`) compare equal pre/post.
- **c. Diff route substituted, and why.** `plan.yaml` is **untracked** in this worktree
  (`git ls-files --error-unmatch` → exit 1; `git status --porcelain` → `??`), so
  `git diff --stat -- <plan>` prints nothing and proves nothing. Substitute: a pre-write copy was taken
  before the verb ran, the panel block was excised from the post-write file (lines 70–152, ending at the
  `tasks:` top key) and the remainder compared byte-for-byte — **equal** (13808 → 17559 bytes). The
  addition is the `panel:` block and nothing else.
- **d. INV-32 re-check.** The predicates of `check-state.sh:489-548` applied directly to the loaded file:
  `bad == []`, `warn == []`. All three vocabulary readers resolve to `ran`; no finding is `unrated` or
  outside `{info, low, med}`; no `resolved` row (which `:527` would downgrade to a warning); no
  `approval.rulings`, so no stale acceptance.
- The verb's own guard also holds: `set-panel` refuses unless the spliced file reloads with `panel`
  identical to the supplied value, and in-plan `panel` equals `/tmp/bug201_panel_value.yaml` exactly.

## Open questions

None from this step. The four carried by the panel (Q1 operator-only F-01 landing; Q2 the three
`BRIEF.md` SC amendments — F-02/F-03/F-08; Q3 P-1's T-01 case 6; Q4 panel composition) are unchanged and
travel to the operator's batched signature review. **Deliberately not done here:** no SC/REQ/task/decision
text was touched and `approval:` was not written — both belong to the main session, and pre-empting them
would hide the findings from the review that is supposed to see them.
