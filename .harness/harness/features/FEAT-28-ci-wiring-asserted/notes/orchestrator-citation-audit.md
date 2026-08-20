# Orchestrator measurement — every case citation in `.github/workflows/tests.yml`

Measured 2026-08-19 at working-tree HEAD (branch `feat/FEAT-27-expertise-repository-tier`).
Read-only. Written by harness-orchestrator to seed the BRIEF or a fix cycle; pm owns the
conclusions, this file owns the numbers.

## The job is ONE job, six steps

`grep -n "^jobs:\|^      - name:" .github/workflows/tests.yml`:

- job id `integration` (line 32), carrying **no `name:` key** — so the job ID is the emitted
  status context, and branch protection on `main` requires exactly that string.
- steps: `Install PyYAML and jsonschema` (59), `Unit suite` (75), `Integration suite` (81),
  `Validate feature execution state` (90), `Plan-route gate` (131), `Layout gate` (185).

## Three case citations. One resolves, one drifted, one is phantom.

| tests.yml | cites | resolves to | verdict |
|---|---|---|---|
| line 177 | `case_19a3b` | `test-check-plan-routes.py:366` | **REAL** — asserts discovery finds the live plan and skips the shipped one |
| line 112 | "case 25" | `test-check-plan-routes.py:1030` `case_25a`–`case_25e` | **DRIFTED** — asserts `status:` values in `plan.yaml` (`building` CLEAN, `Building`/`in_progress` VIOLATION, absent/`done`/`pending` CLEAN). Nothing to do with the CI step it claims to guard |
| line 44 | `case_25b9` | **nothing** — `grep -rn "case_25b9" .claude/skills/harness/bin/` returns no match | **PHANTOM** — the cited test does not exist anywhere |

`grep -c case_25 .claude/skills/harness/bin/test-check-plan-routes.py` = 7 (the def, five
`check(...)` calls, the caller at line 1221). There is no `case_25b9` among them.

## Why the phantom one is the worst of the three

Line 44's comment is the rationale for banning `container:` on the job. It states, in its own
words, that GitHub-hosted runners are non-root, that a container job runs as root, that root
ignores file permissions, and that `test-check-domain.py` and `test-gh-sync.py` assert on
`chmod 000` paths — so under root those assertions "would pass for the wrong reason". It then
says the `Assert the runner is not root` step was removed by owner decision, so the key ban is
"the only thing standing between a container job and those assertions passing vacuously", and
signs off: "`case_25b9` keeps the key banned; nothing checks the uid."

**`case_25b9` does not exist.** So nothing keeps the key banned. The comment's own reasoning
says what follows: adding `container:` makes two suites go quiet rather than red, and
`test-gh-sync.py` has a `skip … (running as root)` branch that makes the quiet silent.

## A fourth hole, self-admitted in the file

Line 185, immediately above the `Layout gate` step:

> THE LAYOUT GATE (FEAT-20/T-03, REQ-06). Nothing in the repository asserts this step is present
> or unneutered.

So the workflow already documents a second unguarded step. #279's title says "a required CI step";
the measured scope is at least two unguarded steps plus one phantom and one drifted citation.

## The structural limit any remedy must state

The required context is the **job id**, and `pull_request` runs the workflow from the PR's own
ref. A guard hosted in `test-check-plan-routes.py` reaches CI only via the `Integration suite`
step (line 81). Therefore:

- it CAN assert that any OTHER step (`Plan-route gate`, `Layout gate`, `Unit suite`, the
  `container:` ban) is present and unneutered;
- it CANNOT protect the `Integration suite` step itself. Delete line 81 and the job still runs
  its remaining steps, still succeeds, still emits `integration`, and the guard simply never
  runs. Green tick, guard gone.

That hole is irreducible from inside the workflow. Closing it needs something outside the PR's
own ref — a second required context, or a check evaluated from the base ref. Whether to close it
is a scope call for the user; **stating it is not optional**, because a remedy that quietly
leaves it reproduces #279's own shape one layer up.
