# Red-run receipts — every `verify:` clause in FEAT-23's plan.yaml

**BLUF: all four `verify:` clauses were executed in an artificial failing state and observed to
fail, at `b7ae135` (the pinned base), before the plan was written.** No clause here is narrated.
FEAT-22 shipped one clause that could not fail and one that could not pass; this file is the
evidence that neither shape survived into FEAT-23.

**Read the last section before spot-checking the first four.** Two clauses were revised after their
first red run — T-01's and T-03's — so this file records each of them **twice**: the draft probe in
the per-task section below, and the clause **exactly as it now stands in `plan.yaml`** in the
section headed *Final re-run of the SHIPPED clauses*. The per-task sections state the failing state
and the diagnosis; the final section is the authority on what the shipped text does.

**CORRECTION, 2026-08-17.** An earlier version of this paragraph read *"T-02's and T-04's clauses
were not revised, so their two records are identical."* **That was false of T-04**, whose clause
gained two DEC-196 conjuncts after this file's first draft; those conjuncts were red-run separately
and are receipted in `research-FEAT-23-453-station.md`. T-02's clause was not revised and its two
records are identical. The false half is corrected here rather than quietly deleted, because the
record of what was wrong is itself the point (rule 15).

**A LATER REVISION, 2026-08-17, at the pre-signature fold-in.** T-05's clause was revised again
after the architecture and ui reviews — three case labels were added — so **the receipts in
`research-FEAT-23-453-station.md` no longer describe T-05's shipped clause in full.** The revised
clause was re-run in both directions and is receipted at `research-FEAT-23-foldin-red-runs.md`.
T-01's, T-02's, T-03's, T-04's and T-06's clause text is byte-unchanged by that fold-in, so their
existing receipts stand unamended.

The failing state is named per clause. Where the pre-change tree *is* the failing state, that is
said explicitly and the observation is anchored `observed at b7ae135, pre-change` (B-12 form).

---

## T-01 — `gh-sync ship` / `abandon` write the terminal status

**Failing state:** the pre-change tree. `cmd_ship` and `cmd_abandon` never touch `feature.json`
(`gh-sync.py:662` and `:600`, both docstrings assert it), so a fixture staged at `status: "Review"`
stays `"Review"` after either command returns 0.

**Command run:** the two new cases, driven through `test-gh-sync.py`'s own `stage()`,
`write_feature_json()`, `run()` and `read_feature_json()` helpers so the shipped cases are the same
shape. Fixture: `status: "Review"`, `github.parent_origin: "created"`, milestone 7.

**Observed output, at b7ae135:**

```
ok    ship PATCHes milestone closed
...
FAIL - ship sets feature.json status to 'Done' (gh-sync exit 0); got 'Review'
FAIL - abandon sets feature.json status to 'Abandoned' (gh-sync exit 0); got 'Review'
```

The 28 pre-existing cases printed `ok` in the same run, so the red is the two new assertions and not
a broken probe (G-09 / the mutation-harness trap). `gh-sync exit 0` beside an unchanged status is the
defect itself: the command reports success and leaves the state pre-terminal.

**Note the discriminator:** this clause can only pass if the code writes the field. No grep, no
absence check.

---

## T-02 — the simplify skill exists and is self-contained

**Failing state:** the pre-change tree — `.claude/skills/harness-simplify/SKILL.md` does not exist.

**Observed output, at b7ae135:**

```
T-02 RED: .claude/skills/harness-simplify/SKILL.md does not exist
exit=1
```

**Non-discriminating conjunct, declared:** the final conjunct asserts the skill does NOT name the
out-of-repo `code-simplifier` plugin. On the pre-change tree that conjunct is unreachable (the file
gate exits first), and once the file exists it is an absence check that a compliant author passes
without effort (P-01). It is kept deliberately as a regression guard on the harness-native ruling,
not as evidence the task was done — the four presence conjuncts and the source-note citation carry
that. It is written with `grep -qF ... && exit 1` rather than a `wc -l` comparison, so a search that
errors cannot pass it silently (G-14).

---

## T-03 — the simplify step sits in the right place in both flows

**Failing state:** the pre-change tree — neither playbook carries the step.

**Observed output, at b7ae135:**

```
T-03 RED: .claude/skills/harness/SKILL.md carries no simplify step
          (marker SIMPLIFY, the last build step absent); qa=57 pin=59
exit=1
```

**A first draft of this clause was itself red for the wrong reason and was fixed before it shipped**
(P-08). Anchors written as `the build is not done until the matrix passes` and
`review_sha is pinned before any validator run` both matched nothing: the first is line-wrapped in
the source at `SKILL.md:57`, and the second is written with backticks around `review_sha`. Both were
narrowed to the substrings that actually occur — `the build is not done until the matrix` and
`is pinned before any validator run` — and the clause then reported the real absence with live
line numbers `qa=57 pin=59`. A clause that fails because its own anchor rotted is indistinguishable
from a clause that fails because the work was not done, which is why this was run rather than read.

**Both sides of the span are bounded and each anchor is asserted to occur exactly once** (G-04):
`grep -cF` must return 1 for each, or the clause reports an anchor drift rather than a work failure.

The plan-flow half asserts ordering **within one line** (`harness-plan.md:12` states the whole
sequence on a single line), so it is an ordered regex over that line rather than a line-number
comparison. It pins order, not wording.

---

## T-04 — the decision is recorded and the index regenerated

**Failing state, conjunct 1:** the pre-change tree — no `## DEC-195` entry.

**Observed output, at b7ae135:**

```
T-04 RED: .harness/harness/docs/DECISIONS.md carries no DEC-195 entry
exit=1
```

**Conjunct 2 (index drift) was proved separately, because conjunct 1 exits before it runs.** A
green-by-default conjunct is the FEAT-22 failure shape, so it was mutated rather than assumed: the
docs pair was copied into a temp tree, `gen-decisions-index.py --stdout` was diffed against the
index, then a `## DEC-195` entry was appended to `DECISIONS.md` **without regenerating**, and the
diff re-run.

**Observed:**

```
before mutation: index drift check GREEN (no drift)
after adding DEC-195 without regen: index drift check RED (drifted)
```

So the conjunct reddens on exactly the failure it exists to catch — a documentor who writes the
entry and forgets the regeneration — and is green on the unmutated tree, which proves it is not
reddening for an unrelated reason.

---

---

## Final re-run of the SHIPPED clauses, and the two collisions that were fixed first

The clauses above were drafted, then run against **the task's own `intent:` prose** before shipping
(P-08). Two collisions were found — both would have reddened correct work — and both were fixed in
`plan.yaml` before this file was finalised:

1. **T-01's clause redirected its output to a file.** `... > /tmp/feat23-t01.log`. The build agent
   that runs this clause is `harness-backend-dev`, and `bash-write-guard.sh` denies a redirect whose
   target is outside the agent's domain — measured on this very session, where the same shape was
   blocked for `harness-pm`. The clause was rewritten to capture into a shell variable with command
   substitution, which the guard does not treat as a write. It also now runs `test-gh-sync.py`
   directly (5.8s) rather than the whole integration bucket (**52.5s measured**, uncomfortably close
   to the 60-second ceiling), and captures into a variable rather than piping to `tail`, so no
   earlier output is truncated away (G-03).
2. **T-03's intent instructed a rewording that its own clause forbids.** The draft told the editor to
   change the plan-flow line to begin "the plan squad drafts", while the clause anchors on the
   literal `squad plans,` that the line already carries. The intent now states that both existing
   clauses stay byte-identical and says why.

**Both halves proved, per clause, on the clauses exactly as they now stand in `plan.yaml`:**

```
== T-01 exit=1 :: T-01: the ship status case did not pass or did not run
== T-02 exit=1 :: T-02: .claude/skills/harness-simplify/SKILL.md does not exist
== T-03 exit=1 :: T-03: ... the marker SIMPLIFY, the last build step is absent (qa=57 pin=59)
== T-04 exit=1 :: T-04: .harness/harness/docs/DECISIONS.md carries no DEC-195 entry
```

**And that each can also PASS** — the other half of the FEAT-22 failure, where a clause shipped that
could not pass:

- T-01's grep strings were checked character-for-character against `test-gh-sync.py`'s `check()`
  output format at `:360`, which prints `ok` followed by four spaces and the case name. Both match.
- T-03's plan-flow regex was run against the exact sentence the intent prescribes: **MATCHES**. Run
  against the current unedited line: **does not match**. So the clause discriminates the edit rather
  than passing on either state.
- T-04's index-drift conjunct was proved green on the unmutated tree and red on the mutation, above.
- T-02's presence conjuncts are satisfied only by a file that does not yet exist.

---

## Lane resolution, run at b7ae135

Every literal `files:` path was delegated to `check-domain.sh --resolve` (DEC-179). Verbatim results:

| path | `--resolve` said |
|---|---|
| `.claude/skills/harness/bin/gh-sync.py` | `harness-backend-dev` / `harness-dev-ops` |
| `.claude/skills/harness/bin/test-gh-sync.py` | `harness-backend-dev` / `harness-dev-ops` |
| `.claude/skills/harness/SKILL.md` | `NOBODY` |
| `.claude/commands/harness-plan.md` | `NOBODY` |
| `.claude/skills/harness-simplify/SKILL.md` | `NOBODY` |
| `.harness/team-config.yaml` | `NOBODY` |
| `.claude/agents/harness-eng-lead.md` | `NOBODY` |
| `.harness/harness/docs/DECISIONS.md` | `harness-documentor` |
| `.harness/harness/docs/DECISIONS-INDEX.md` | `harness-documentor` |

`NOBODY` becomes a declared `main-session-direct` task, never a mid-run rejected write.
**`gh-sync.py` is not one of the DEC-174 four** (`check-domain.sh`, `bash-write-guard.sh`,
`validate-digest.py`, `check-state.sh`), so T-01 is an ordinary team task.

## The write-path probe that settles D-01 (issue #417's discriminating check 2)

A status write from `cmd_ship` is legal on both routes it must survive, and both were measured, not
inferred (G-02):

- **Schema (DEC-191).** `feature-schema.json` lists `status` among the eight **required** keys, with
  enum `Backlog Plan Ready Building Review Done Abandoned`. Writing `"Done"` is schema-valid; the
  closed key set is untouched because no new key appears.
- **Write guard (DEC-174 file, read only).** `bash-write-guard.sh:19` states main-session and
  non-harness callers are ungoverned. The guard was fired with the real payload
  `python3 .claude/skills/harness/bin/gh-sync.py ship <feature-dir>` under three callers:

```
--- agent=NONE                 exit=0
--- agent=harness-pm           exit=0
--- agent=harness-backend-dev  exit=0
```

  The guard parses in-place editors and redirections; a write performed inside a Python process via
  `tempfile.mkstemp` + `os.replace` is not a shell construct and is not seen. In-file precedent
  already exists: `save_recorded()` (`gh-sync.py:418`) writes `feature.json` through exactly that
  atomic shape on the `open` path.

## Issue #417's discriminating check 3, answered

**Nothing anywhere sets `"Abandoned"`.** `grep -rn "Abandoned"` across `.claude/` returns only
*readers* — the schema enum, `check-plan-routes.py:408` `FINISHED_STATUSES`, `check-state.sh:113`,
`:494`, `:507`, `:1177`, `gh-sync.py:172`, and one test fixture. `cmd_abandon`'s docstring claims
`feature.json` is untouched, and it is telling the truth. So abandon carries the identical gap and is
**ruled in scope**: same file, same one-line shape, and INV-26 exempts both statuses. Ruling it out
would have cost a written reason and left a known defect standing behind a fix for its twin.

## DEC-183's plan-COUNT assertion — checked, no task needed

The `integration` job's Plan-route gate does **not** hardcode a plan count. `tests.yml:165-173`
asserts `examined > 0` (feature directories entered) and reports `plans` as information only; the
inline comment records that a `plans == 0` assertion was removed on 2026-08-13 because an
all-shipped repository looks the same as broken discovery. **Landing FEAT-23's own `plan.yaml`
therefore requires no count bump anywhere**, which a handed-down count would have implied (P-14).
