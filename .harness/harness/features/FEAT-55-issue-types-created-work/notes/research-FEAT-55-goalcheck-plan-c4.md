# Goal-check c4 — does this plan deliver the operator's stated intent?

**YES.**

Re-answered end to end against `.harness/notes/grilling-issue-types-2026-09-04.md` `## Settled`,
`notes/answers-plan-panel-20260904.md` and `…-c2.md` — not against c3's verdict. All five Settled
clauses are gated: overrides+defaults (D-18 `:116-119`, T-01 `verify:287-293`), parents default
Feature with the same override (D-18 `:117`, T-07 D `:929-935`), unavailable ⇒ labels preserved +
exactly one diagnostic per invocation (T-03 C/D/I `:517-527,559-560`; T-05 C/F `:753-758,778-784`;
T-07 C/G `:925-928,952-957`), active ⇒ no `bug`/`chore` (T-03 B `:514-516`, T-05 B `:751-752`,
T-07 B `:922-924`), and crash-between-create-and-type recovers without delete or duplicate
(D-10 `:84`, D-20 `:124-145`; T-03 G `:540-547`, T-05 E `:770-777`, T-07 E `:936-942`). All five
creation routes carry REQ-01 (T-03/04 open, T-05/06 backlog, T-07/08 factory). Out-of-scope (a) is
enforced positively and by absence (T-03 H/H2/J, T-07 F/H). Both operator rulings are applied and
neither is widened. Read at `plan.yaml` sha256 `41c0bd34a0e2…`, `BRIEF.md` `31c97a661634…`;
1333 / 209 lines; 12 tasks, 20 decisions, 9 panel findings, `approval:` pending (`plan.yaml:4-5`,
`BRIEF.md:205-209`). **I verified both files are byte-unchanged by me: the two sha256 values above
were recomputed after my last read and are identical to the values at entry; I wrote only this note
and my observations log.**

`check-plan-routes.py <plan.yaml>` — observed output, tail quoted verbatim:
`OK T-12: declared main-session-direct (.claude/skills/harness/references/github-mirror.md ungranted)`
then `0 violation(s) across 1 plan(s)`, exit 0. **Violation count printed by the tool: 0.**

## The three c5 changes, each on its own terms

**(a) T-03 case F's zero-`updateIssue` assertion — MATCHES in strength.** Side by side:
F `:532-535` / G `:788-791` / I `:973-976` each assert ZERO argv containing `issue create`, ZERO
argv containing `updateIssue`, non-zero exit, and stdout+stderr naming both `Task` and
`github.issue_types`. On the ruled assertion the three are now identical. SC-08's per-command
zero-type-assignment requirement (`BRIEF.md:132-139`) therefore has a falsifiable grading on all
three routes, each in that command's own file (`:464`, `:718`, `:881`), and each case's existence is
gated by its `CASE` loop (`:467`, `:721`, `:884`). One residual asymmetry, advisory only: G adds
"no `backlog-issues.json` afterwards" (`:791`) and I adds "factory.yaml records no numbers"
(`:976-978`); F asserts no analogous negative over `feature.json`. Neither the ruling nor SC-08
requires it → **C4-01, low**.

**(b) T-03's required-string loop — binds case F the way the other two bind theirs.** `:470` now
carries `partial` and `github.issue_types`, matching T-05 `:724` and T-07 `:887`. Parity achieved.
Known limit, uniform across all three and unchanged by this edit: the loop is a file-global
`grep -qF`, and both strings are already present in each file's fake description (`:490`, `:738`,
`:905`), so the loop bounds the file, not the case; the case is bound by its `CASE` marker only
(**C4-02, info**).

**(c) T-10 §6 — SC-10's live pass is REACHABLE as written.** §6 `:1177-1216` drops the equality and
runs the step 2-4 classification against the TARGET, mapping all three failure shapes onto the four
existing verdicts, with the explicit opt-in retained as the whole safety mechanism (`:1180-1182`).
The three surfaces I was told to test against it agree: T-10's unchanged `verify` (`:1133-1144`)
exercises only the default invocation and asserts a configured-repo verdict plus "nothing created" —
no clause of it reaches the opt-in path, so no contradiction; BRIEF `## Verification gaps`
(`:190-194`) already reads "creates a real issue in the repository the flag names"; SC-10
(`:144-160`) now counts a live pass "whether or not that repository is the configured one".
Residual gate, disclosed not defective: §1 (`:1157-1160`) still SKIPs on `github.sync` false, an
unpinned repo, or absent/unauthenticated `gh` before the flag is honoured — here `github.repo` is
pinned, so the live pass is reachable, and BRIEF lists those same four as environmental skips.

**T-09's `runner_note` — DECIDED: CORRECT, not a misstatement.** The registered `cmd` is the
DEFAULT invocation and T-09 forbids the flag in it (`:1114-1117`); the default path is steps 1-5,
which resolve and report the configured `github.repo` (`:1157`, `:1172-1176`) and create nothing.
The ruling changed only the opt-in path, which `cmd` never invokes. `runner_note` (`:1111`)
describes the `cmd`, not the flag, so "gh authenticated against the pinned `github.repo`" is exactly
true of what is registered. No repair needed; widening it to mention `--create-in` would misdescribe
the registered kind.

## The eleven baseline findings — roll-call against current text

| F | verdict | current anchor |
|---|---|---|
| F-01 high | still closed | T-03 H/H2 `:548-558`, T-07 F `:943-951`, T-04 §7 `:687-696`, T-08 §8 `:1071-1082` |
| F-02 med | still closed | T-10 `verify` repo leg `:1139`, PATH-stripped SKIP leg `:1141-1143` — unedited |
| F-03 med | still closed | pinned row `:1265` = `:1312`, 511 chars, sha256 `7f065a7a5225` (recomputed) |
| F-04 med | still closed | T-03 D `:523-527`, T-05 D `:759-769`, T-07 G `:952-957` |
| F-05 med | still closed | D-18 `:116-119`, T-03 A `:508-513`, T-07 A `:915-921` |
| F-06 low | still closed | T-01 `verify:290` greps `UnknownWorkNature` |
| F-07 low | still closed | T-06 §5 available-gated `:844-848`; T-05 C `:753-758`, F `:778-784` |
| F-08 low | still closed | D-19 `:120-122` unchanged; T-09 `:1114-1117` forbids the flag in `cmd` |
| F-09 low | still closed | T-06 `verify:811`, T-08 `verify:997-999` run the legacy controls |
| N-01 high | still closed | D-20 `:124-132`, T-03 J `:561-572`, T-07 H `:958-968`, T-04 §6 `:677-682` |
| N-02 low | still closed | backfill inside `missing_types`: T-04 §4 `:622-628`, T-08 §6 `:1037-1041` |

**Which the c5 revision touched: none of the eleven's cited text was edited.** c5 wrote exactly
`:470`, `:532-539`, `:1177-1216` and BRIEF SC-10. Two sit adjacent to a c5 hunk and were re-read in
full rather than inherited: **F-02** (T-10 `verify`, same task as the §6 rewrite, byte-unchanged and
still consistent) and **F-08** (D-19, unedited, and its "naming the target repository" clause is
still true under the widened target).

## `create-in` / `configured repository` / `github.repo` — every hit, with a verdict

| hit | verdict |
|---|---|
| `plan.yaml:1111` T-09 `runner_note` "pinned github.repo" | consistent — describes the read-only default `cmd` |
| `plan.yaml:1139` T-10 verify configured-repo leg | consistent — default invocation only |
| `plan.yaml:1157` §1 resolve from `github.repo` | consistent — environment + default target |
| `plan.yaml:1177-1184` §6 TARGET may differ / "rather than against the configured repository" | consistent — implements the ruling |
| `plan.yaml:1207-1208` "not necessarily the configured github.repo" | consistent |
| `plan.yaml:1215-1216` §7 per-verdict repository naming | consistent |
| `plan.yaml:121` D-19 "naming the target repository" (no literal token) | consistent — the flag still names the target |
| `BRIEF.md:15`, `:181-186` pinned repo returns `issueTypes: null` | consistent — measured fact, unaffected |
| `BRIEF.md:145-149` SC-10 lead-in and live-pass clause | consistent — reworded to the ruling |
| `plan.yaml:174-180` PF-08da2089 summary/why | **stale** — recites the removed equality and cites `plan.yaml:1166-1170`, which is now step 3. Record of a filing, asserts no live plan behaviour; see below |

No surface still asserts the removed equality binding as a requirement.

## Findings

- **C4-01 · low ·** T-03 case F carries no `feature.json`-records-nothing negative, where T-05 G and
  T-07 I each carry their route's equivalent. Outside the ruling and outside SC-08.
- **C4-02 · info ·** required-string binding is file-global on all three routes (above). Uniform.
- **C4-03 · med · the panel record is stale in three places, and I am read-only here.**
  `PF-60f3544bd486…` still `disposition: awaiting_user` (`:170`) after the operator ruled and the fix
  landed; `PF-08da208931…` still `batched_to_signature_review` (`:180`) after being ruled *allow*;
  `PF-8b585322…` still `batched_to_signature_review` (`:191`) after being folded into the c5 edit.
  `harness-spec-driven` wants each carrying `resolved` with `resolved_by:`. This is c3's Q2, now
  three findings wide. → Q1.

## For the panel — evidence bearing on carried, unruled findings (not goal-check findings)

All six (`PF-56a2ce7a…`, `PF-1286544c…`, `PF-452948…`, `PF-e27f1c3…`, `PF-0c12a033…`,
`PF-9a71cb9a…`) remain `disposition: batched_to_signature_review` (`:192-260`), untouched by c5 and
un-adjudicated here. Two observations the panel may want:
- `PF-1286544c…` (T-06's `backlog-issues.json` writer, `:844-848`) is still the subject of T-05
  cases C `:757`, F `:782` and G `:791`; if that finding is later directed as a fix, those three
  assertions need re-authoring. Unchanged from c3.
- `PF-9a71cb9a…` (the duplicated 511-char row): I re-measured it — `:1265` and `:1312` are still
  character-identical, so the drift the finding describes has not yet occurred.

## Open questions for the operator

- **Q1 (C4-03):** who moves `PF-60f3544b…`, `PF-08da2089…` and `PF-8b585322…` to
  `disposition: resolved` with `resolved_by:` — a pm write dispatch before signature, or the main
  session's `approval.rulings` write? Non-blocking; the plan's behaviour is unaffected.
