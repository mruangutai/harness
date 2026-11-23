# BUG-2420 — validate c0 goalcheck: PASS

Both signed perspectives pass; SC-01–03 are met. No decision disposition or product finding requires remediation. This grades delivered behavior, not the independently pending QA matrix or ship readiness.

## Evidence boundary

- Review pin: `c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`; pre-fix base: `d5be53927009df8e7848f860f9d0b4b03b89f9ad`. Source, tests, BRIEF, plan and cited red/green receipts were read with `git show`/`git diff` at these immutable refs, not moving HEAD.
- Below, `F` means `.harness/harness/features/BUG-2420-plan-merge-first-task-station`, `U` means `tests/unit/test-plan-merge-first-station.py`, `I` means `tests/integration/test-plan-merge.py`, and `S` means `.claude/skills/harness/bin/plan_merge/stations.py`; all content citations are at the review pin.
- Historical green execution was at `695363b871e8e0cd879dd96e09e4d168854b4c16`, not re-executed here. Its source/test/config subjects are unchanged through the review pin: the diff over `.claude/skills/harness/bin`, `tests`, `.harness/harness.json` and `.harness/team-config.yaml` is empty. Pinned test blobs match the red receipt: unit `4bee13087c80da239186404766e4e7172af347a7`, integration `4077b9aaacef4c13dd4b84838f061c48f5785dfb` (`F/notes/red-first-T-01.md:3–5`). No builds, tests, linters or formatters were run by this reader.

## Perspectives

- **operator — pass:** SC-01 and SC-02 discharge first-station insertion, clear genuine-absence refusal and preserved approved signature. `U:91–152`, `S:193–299`; red `F/notes/red-first-T-01.md:9–41`, green `F/notes/green-T-01.md:8–25`.
- **code maintainer — pass:** SC-03 discharges the unchanged drafting path; SC-01 additionally protects existing rewrite and nested prose. `I:5142–5162`, `U:94–128`; green `F/notes/green-T-01.md:12–21,134–141,710–714`. The base-to-pin production diff changes only S, with the two T-01-owned tests; no adjacent writer or production documentation changes.

## Success criteria

| Criterion | Outcome | Specific evidence |
|---|---|---|
| SC-01 | met | Three rows in `U:91–113` cover insertion indent, rewrite, missing-id exit 3/no write and STATION/APPLIED receipts; `U:118–138` protects task identity, nested verify prose and absence wording. `S:207–266` bounds the search to tasks, matches exact field indent and splices only the station line; `S:293–299` emits an unambiguous absence message/task list or success output. Red insertion fails its expected-line assertion (`F/notes/red-first-T-01.md:11–24`), while rewrite/missing controls pass; matching green is `F/notes/green-T-01.md:8–22`. Existing exact one-line rewrite/no-write integration controls also pass there at lines 134–141. |
| SC-02 | met | `U:47–48,144–152`: the original complete APPROVAL string, including approved status, must occur verbatim after a successful insert, with exactly one approved-status occurrence; an unchanged failed operation cannot pass. Red success/approval assertions fail with rc=3 (`F/notes/red-first-T-01.md:26–39`); both pass in `F/notes/green-T-01.md:23–24`. The production transform only splices within the task (`S:277–284`), without invoking signature/reset logic. |
| SC-03 | met | Exactly one new registered drafting-path case, `I:5142–5162,5304`: begins with tasks empty, applies a status-less T-01, asserts the exact resulting task mapping has no status, sets building and reloads it. Red station/reload assertions fail with the actual missing-status defect (`F/notes/red-first-T-01.md:44–51`); green `F/notes/green-T-01.md:710–714`. The diff adds no separate inline-empty union-mechanics cases. |

`F/plan.yaml:25–36` traces T-01 to all three SCs and owns exactly S, I and U. Neither perspective nor criterion is orphaned.

## Decision dispositions and settled authority

`F/plan.yaml:22–23` at the pin has `decisions: []` and `decisions_affected: []`: zero amend/strike rows to grade; no invented DEC verdicts. Actual conformance supports the empty disposition list: the bounded station fix retains signature ownership and controlled station writes (product `.harness/harness/docs/SPEC.md:80–85,171–195`; `.harness/harness/docs/DECISIONS.md` DEC-120 at 2317 and 2408–2410, DEC-174 at 4482–4485 and 4506–4522, DEC-225 at 7427–7466). No public schema, signature authority or policy clause changes, and no DECISIONS.md-owning task is needed or authorized.

Main-session-direct routing and delegated signature are settled by `F/notes/answers-2026-11-22-signoff.md:5–37`, with pre-signature conditions discharged in `F/notes/research-patch-c4-signoff.md:7–11`; they are not reopened. The earlier product research's absent-doc observation is superseded by that correction. This is the explicitly requested read-only validate assessment, not a new patch planning panel or replanning run.

## Principles applied

- **Outcome-Oriented Execution** (`harness-craft/references/outcome-oriented-execution.md`): grade the final inserted-station/unchanged-approval behavior using discriminating red-to-green evidence, rather than treating planning receipts or a future matrix result as proof. Final matrix execution remains QA's separate gate; no compatibility workaround is introduced.

## Findings and open questions

None. No source, plan or production documentation edits were made; only this assessment was written.
