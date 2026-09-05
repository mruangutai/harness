# Plan repair c5 — FEAT-55 — both operator rulings applied in one revision

**Both rulings are discharged; the plan still parses, `status: plan`, `approval.status: pending`,
`panel:` byte-unchanged.** Three `plan-merge.py amend` calls (`T-03 verify`, `T-03 intent`,
`T-10 intent`) plus one ordinary edit to `BRIEF.md` SC-10. No compare-and-swap conflict occurred.
`git diff --stat` touches exactly `plan.yaml` and `BRIEF.md`.

## Edit 1 — ruling 1, T-03 case F gains the zero-`updateIssue` assertion (`amend T-03 intent`)

Before (`plan.yaml:532-534` at read time):
> F. FAKE_TYPES=partial (Task not declared), fresh fixture: assert ZERO argv containing "issue
> create" reached the fake, the process exit status is non-zero, and the combined stdout+stderr
> names both "Task" and "github.issue_types".

After (`plan.yaml:532-539`):
> F. FAKE_TYPES=partial (Task not declared), fresh fixture: assert ZERO argv containing "issue
> create" reached the fake, ZERO argv containing updateIssue, a non-zero process exit status, and
> that the combined stdout+stderr names both "Task" and "github.issue_types". T-04 section 4
> computes missing_types over the parent and every task together, before any create and before any
> type-apply, so a refusal ordered after apply_issue_type - a backfill that types an
> already-recorded issue on a run specified to refuse cleanly - mutates a real existing issue's
> native type with every other plan-defined gate green, and this case is what fails when it does.

Wording mirrors T-05 case G (`plan.yaml:784`) and T-07 case I (`:970`), both of which read
`ZERO argv containing updateIssue` inside the assert list, and both of which close with the same
"each would otherwise ship with every plan-defined gate green" consequence. Cases A–J and H2 are
otherwise byte-identical.

## Edit 2 — `PF-8b5853220e5f2768339090bdbc44b1a5` FOLDED, disclosed (`amend T-03 verify`)

**This low finding was folded into the same revision because that is the option the operator
selected** (panel `fix_order` entries 1 and 2: same task, same verify block).

Before (`:470`): `for s in IT_feature IT_bug IT_task IT_defect IT_epic updateIssue issueTypes 4242 adopted created; do`
After (`:470`): `for s in IT_feature IT_bug IT_task IT_defect IT_epic updateIssue issueTypes 4242 adopted created partial github.issue_types; do`

Now matches T-05's loop (`:719`) and T-07's (`:882`). `verify:` remains a literal `|` block.

## Edit 3 — ruling 2, T-10 §6 accepts any explicitly named repository (`amend T-10 intent`)

Before (`:1172-1176`):
> 6. The opt-in. Accept exactly one argument, --create-in <owner/name>, and require its value to
> EQUAL the repository resolved in step 1: on a mismatch print "probe-issue-types: SKIP --create-in
> <value> does not name the configured repository <repo>" to stdout and exit 2, creating nothing.
> Retyping the repository is the whole safety of the flag.

After (`:1177-1216`): the equality binding and its exit-2 SKIP are gone. `--create-in` names the
TARGET; classification of steps 2–4 runs against the TARGET and the create happens there. The
explicit opt-in is stated as the whole safety mechanism (absent the flag, nothing is created
anywhere — D-19 untouched). Three failure shapes now map onto §7's **existing four verdicts, no
fifth token**: TARGET not enabled → `CAPABILITY ABSENT <target>`; capability query fails →
`SKIP capability query failed on <target>`; `gh` cannot reach it → `SKIP gh cannot reach <target>`.
All non-equality §6 guarantees survive verbatim in substance: the `missing_types` refusal before any
create (`SKIP` + `refusal_text(...)`, exit 0, nothing created), label `harness`, read-back via
`issue(number:N){ issueType { name } }`, close in a `finally`, and one `LIVE PASS` line naming the
repository, the number and the deletion command — **now the TARGET, i.e. the repository actually
written to, explicitly "not necessarily the configured github.repo"**. §5's read-only default
(`CAPABILITY PRESENT` against the configured repo) is unchanged; §7 now says each verdict names the
repository it reports on — configured repo by default, TARGET when the flag was supplied.

## Consistency fallout

**(a) T-10 `verify` was NOT amended.** It exercises only the default invocation: it asserts exit 0,
exactly one verdict line, that the line names the configured `github.repo`, that nothing is created
(`created issue|LIVE PASS` must be absent), and that an absent `gh` SKIPs. The ruling changes only
the opt-in path, which this block never invokes, so no clause contradicts the new §6. Amending it
would have added an unrunnable live-write assertion to a plan-time gate.

**(b) Decisions — inspected D-01 … D-20 (the whole list); grepped it for `create-in`, `configured`,
`opt-in`, `probe`, `github.repo`, `EQUAL`. Changed: NONE.** The only hits are D-08 (the eighth
read-back purpose "the type read-back the probe makes under its create opt-in" — still true), D-09
(registers the kind; says nothing about the destination) and D-19, whose clause reads: *"it creates
a throwaway live issue only when the operator passes an explicit opt-in flag naming the target
repository"* — correct under the ruling, since the flag still names the target and the target need
not be the configured repo. No decision asserted the equality that was removed; the equality lived
only in T-10 §6.

**(c) BRIEF SC-10** — the clause "or a create opt-in naming a repository other than the configured
one" is struck from the environmental-skip list, and the lead-in widened to "when run against the
pinned `github.repo`, or against a repository the operator names explicitly through the probe's
create opt-in". A live pass in the named repository now counts explicitly, "whether or not that
repository is the configured one". Retained verbatim: *"It never reports a pass derived from a
fixture."*, the four genuine environmental skips (no `gh`, `github.sync` false, unpinned repo,
failed capability query), the `#1289 enabled-repository acceptance` pointer, and
`verify: automated        evidence: issue_types_live`.

**(d) `## Verification gaps`** — CONFIRMED and left untouched. Its bullet already reads "creates a
real issue in the repository the flag names", which agrees with the ruling.

## Carried findings — roll-call, all six untouched

| id | cited surface | state |
|---|---|---|
| `PF-56a2ce7a…` | BRIEF SC-12 adopted marker | untouched |
| `PF-1286544c…` | T-06 `backlog-issues.json` writer | untouched |
| `PF-452948…` | T-06 `verify` file list | untouched |
| `PF-e27f1c30…` | T-05 case F compat-mode assertion | untouched |
| `PF-0c12a033…` | `adopted` provenance marker | untouched |
| `PF-9a71cb9a…` | duplicated eighth-purpose row | untouched |

No ruled edit collided with text a carried finding cites. `PF-8b585322…` is fixed (folded, above)
and `PF-60f3544b…` is fixed; `PF-08da2089…` is the T-10 finding the second ruling allows. The
`panel:` mapping itself was **not** rewritten — dispositions are the main session's to move.

## Verification run

- `python3 -c "...harness_yaml.load_plan(...)"` → `12 plan pending`; 9 panel findings, ids
  unchanged and in the original order.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`.
- `git diff --stat` → `BRIEF.md | 14 +++--`, `plan.yaml | 67 +++++++-------`, 2 files, no other
  tracked file. plan.yaml hunks are at `470`, `533`, `1172`, `1193` — all inside `tasks:`; the
  `approval:` block (`:4-5`) and `panel:` (`:146-274`) are outside every hunk.

## Open questions

None blocking. Advisory: T-09's `runner_note` still describes the registered `cmd` as needing "gh
authenticated against the pinned `github.repo`" — that is the read-only default invocation, which
the ruling did not change, so it was left alone.
