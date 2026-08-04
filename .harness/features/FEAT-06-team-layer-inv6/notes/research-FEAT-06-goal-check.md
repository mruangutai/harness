# Goal-check — FEAT-06 team layer and INV-6

**VERDICT: FAIL — on one conjunct, not on the feature's substance.** 13 of the 14 non-uat SCs are
met with named, discriminating evidence. **SC-05 is unmet as declared**: its second conjunct
("`teams/` holds exactly two files") has no registered assertion anywhere under `bin/`. SC-13 is
`pending_uat` — the user's call, untouched by me.

## Anchor

`git rev-parse HEAD` → `9f87c48dae0ced97e7655dffb9daddeba4708324` (= `review_sha`).
`git status --porcelain .claude/ docs/` → **empty**. This matters: `test-team-catalog.py` reads the
live working tree (`CLAUDE_PROJECT_DIR or os.getcwd()`), not the pin, so a dirty read path would
have made every check-(1)..(10) row evidence for something other than the pinned diff. It is clean.

`.claude/skills/harness/bin/run-unit-tests.sh` → **exit 0**, 13 scripts, output saved and cited by
line below as `unit.txt:N`.

## The SC-05 ruling — UNMET as declared

The count conjunct is **factually true today** (`ls -1 .claude/skills/harness/teams/` → `build.yaml`,
`review.yaml`, count 2). I still rule it unmet, and the line I am drawing is this:

> **Present-but-weak evidence is a met row with a noted limitation. Absent evidence is unmet.**

- `test-harness-yaml-corpus.py:180` asserts `n > 0` per root. That is the *parse-corpus-non-vacuity*
  assertion, not a count. The `teams=2` visible in the output comes from the f-string label at
  `:174`, which asserts `not bad` — parse validity — and nothing about cardinality.
- `test-team-catalog.py`'s ten checks never reference `teams/` file counts.
- No `== 2` over that directory exists anywhere under `bin/` (grepped).

SC-05's binding contract is its `verify: automated  evidence: unit` line, and that line covers the
whole criterion, both conjuncts. Admitting my `ls` output as the evidence would convert half of a
signed `automated` SC into `inspection` at goal-check time — the method is fixed at approval (P-03).
Signing it while citing `test-harness-yaml-corpus.py` would be citing a test that does not cover the
conjunct, in the feature chartered to remove checks that appear to exist and do nothing.

The boundary is **asserted vs. not asserted at all**, and SC-02 is the contrast that sharpens it:
its second conjunct ("both consumers read the definition from there") is covered by a use-site read
in each consumer — `check-state.sh:160` and `validate-digest.py:477`, both `in
harness_yaml.PLACEHOLDER_UNSET` against the single definition at `harness_yaml.py:302` — plus
behavioral corroboration, since `test-check-state.py` case (h) can only pass if `check-state.sh`
resolves the constant, the literal having been removed from that file. SC-05's count conjunct has
no assertion of any strength.

**Remedy, stated precisely so it cannot be routed wrong** (I did not fix it — reporting only):
add one `check(...)` to **`.claude/skills/harness/bin/test-harness-yaml-corpus.py`** asserting
`counts[<teams root>] == 2`, reading the `counts` dict already computed at `:172`.
**NOT `test-team-catalog.py`** — T-07's approved `verify:` requires that script's output to name
exactly **ten** checks, so an eleventh would break a signed verify. T-05's verify counts no checks,
so an 11th check in the corpus script breaks nothing. Both files sit inside the DEC-174 carve-out
(extended by D-05), so the fix is main-session-direct either way.

## SC-03 — the isolation test, not the raw diff

A literal before/after diff makes SC-03 *look* violated: two lines appear that are not INV-6 lines
(`run dir panel-validator …` and `run dir goalcheck-product …`, both "orphaned work"). The
discriminating check settles it in the other direction:

```
git show 635ef14:…/check-state.sh  →  run over the CURRENT tree
diff  old-code-on-current-tree  new-code-on-current-tree   →  IDENTICAL (no output)
```

The pre-fix script produces byte-identical output to the post-fix script on one and the same tree.
So **no invariant's verdict changed**, INV-6 included (it fires on nothing). The two extra lines vs
the `635ef14` capture are tree state, not code: both run dirs were created after the capture, and
`goalcheck-product` **is this goal-check's own run dir**. Not a defect; the panel already routed the
`feature.yaml` bookkeeping and I do not re-raise it.

## SC-12 — per-task reason check

Independently re-derived, not relayed. `.harness/team-config.yaml`'s only relevant write grants are
`docs/**` (`:116`) and `.claude/skills/harness/bin/**` (`:155`, `:197`) — nothing grants
`teams/**`, `harness/SKILL.md` or `harness-team/SKILL.md`.

| Task | Surface | Stated reason | Actually applied | Match |
|---|---|---|---|---|
| T-01 | `check-state.sh`, `validate-digest.py`, `test-check-state.py`, `harness_yaml.py` | carve-out | domain **is** granted (`bin/**`); DEC-174+D-05 binds | yes |
| T-02 | `teams/review.yaml` | domain-ungranted | no grant on `teams/**` | yes |
| T-04 | `teams/build.yaml` | domain-ungranted | no grant | yes |
| T-05 | `test-harness-yaml-corpus.py` | carve-out | `bin/**` granted; mission extension binds | yes |
| T-06 | `harness/SKILL.md` | domain-ungranted | no grant; not one of CLAUDE.md's five | yes |
| T-07 | `test-team-catalog.py`, `run-unit-tests.sh` | carve-out | `bin/**` granted; D-05 binds | yes |
| T-08 | `docs/**` | squad-dispatched | granted at `:116` | yes |
| T-09 | `harness-team/SKILL.md` | domain-ungranted | no grant | yes |
| T-10 | `teams/gate-probe.yaml` | domain-ungranted | no grant | yes |
| T-11 | `harness/SKILL.md` | domain-ungranted | no grant | yes |

Execution shape confirmed against the three commits: `f45fd0f` carries T-01/02/04/05/06/09/10/11
main-session-direct; `9f87c48` carries T-07 the same way; **only T-08 was dispatched**, to
`harness-documentor` (`runs/t08-product/state.yaml:69` `persona: harness-documentor`, `:76`
`verdict: PASS`). No `runs/` dir exists for any other task. Both walls held; every label is correct.

## Open items for the user

1. **SC-05's count conjunct** — my ruling above. Fix is one line; the user may equally rule it a
   one-time completion fact and accept it. That call is theirs, not mine to close.
2. **SC-13 (uat) is a live blocking gate.** `gates.uat: blocking_when_uat_criteria_exist` and SC-13
   is the one `verify: uat` criterion in the BRIEF. It stays `pending_uat` until the user reads the
   two artefacts named in the DIGEST and rules.

## Not findings

BRIEF's `## Verification gaps` (no runner executes `build.yaml` or a ship; markdown behaviour is
proven only as text; the whole-repo state diff has no runner; PLAN `verify:` lines self-execute for
nobody — issue #19) were signed open by the user and are not re-raised here.
