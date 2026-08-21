# FEAT-30 — worktree per feature — validate phase, ship review

**Do not ship yet. One high, verified, introduced by this diff.**

The feature does what it was asked to do: all ten tasks are built, all twelve success criteria are
met, both suites are green, and the four-worktree concurrency proof that is the headline claim
**passes when actually run**. But the review panel found — and I reproduced independently — that this
diff moved Expertise writes off the domain-enforced `Write` route onto a Bash-invoked CLI the write
guard does not recognise. The result is a silent, exit-0, total-truncation write to **any path** from
**any persona**, including the reviewers who are contractually read-only. That gates. Everything
else is medium or below.

One decision is yours before anything else moves, and it is architectural rather than a patch.

## How this document was assembled

**No report round was spawned** — the digests were read from disk instead, which costs three lead
spawns less and loses nothing. Sources, all cited by path:

- `runs/2026-08-21-01-validator/digest.md` — qa gate · `notes/qa-2026-08-21-01.md`
- `runs/2026-08-21-02-eng/digest.md` — simplify · plus `apply-decisions.md`, `lead-cross-angle.md`
- `runs/2026-08-21-03-product/digest.md` — docs
- `runs/2026-08-21-04-validator/digest.md` — review panel · plus the four `notes/review-harness-*.md`
- `runs/2026-08-21-05-product/digest.md` — goal-check · `notes/research-FEAT-30-goal-check-2026-08-21.md`
- Earlier phases: `runs/2026-08-20-01-build-eng/digest.md`, `notes/handoff-plan.md`, `notes/handoff-build.md`

I did not take the digests on trust. Where a claim was load-bearing I re-measured it, and **four
relayed claims did not survive that** — listed under *Claims that failed verification* below.

## The blocker

**F-1 — high, gates.** `bash-write-guard.sh:617-618` does `if not findings: sys.exit(0)`, and that
runs **before** the reviewer read-only denial at `:628` and before the domain walk at `:640+`. A
command like `python3 .claude/skills/harness/bin/expertise-merge.py apply --file <any path>` matches
no write pattern, so `findings` is empty and the guard exits 0 without ever reaching either check.
`expertise-merge.py`'s `cmd_apply` validates neither its caller nor `--file`, and will create or
`os.replace` any path at all.

T-06 created the tool; **T-07, in this same diff, rewired `harness-distill/SKILL.md:28-34` to instruct
every agent — reviewers included — to reach it by exactly that shape.** So the doctrine change and the
hole landed together.

I reproduced all of it against the real hook:

| Attempt | via `expertise-merge.py` | via `echo >` |
|---|---|---|
| `harness-documentor` → another agent's Expertise file | **allowed, rc=0** | blocked, rc=2 |
| `harness-documentor` → `src/main.py` | **allowed, rc=0** | blocked, rc=2 |
| `harness-code-reviewer` (read-only) → `src/main.py` | **allowed, rc=0** | blocked, rc=2 |
| read-only reviewer → `.claude/settings.json` | **allowed, rc=0** | — |
| reviewer → a path outside the repository | **allowed, rc=0** | — |
| `harness-documentor` → `check-domain.sh` | **allowed, rc=0** | — |

The same write is denied through the shell and permitted through the tool. To size the damage I ran
it against a **copy** of `check-domain.sh`: exit 0, output `ADDED P-99` / `APPLIED …`, and the file
went from **67,976 bytes to 71** — the domain hook replaced by three lines of markdown. The real
files are untouched and verified intact.

Two honest bounds. The written content is constrained to the Expertise markdown shape, so this is a
clean tampering primitive for Expertise files — which are injected into every agent spawn, making
doctrine injection the sharpest risk — and a blunt truncation primitive for everything else. Blunt is
still enough: emptying `check-domain.sh` or `settings.json` disables enforcement.

**Your decision, and it is the panel's blocking question.** The guard is **allow-by-omission**:
anything its write-pattern vocabulary does not textually recognise skips both checks. This diff added
two first-party write CLIs and a new HEAD rule, all downstream of that single recognition step.
Teaching it three more patterns is a patch. The durable options:

- **(a) invert the default for known first-party write tools** — enforcement layer, yours under DEC-174
- **(b) have each tool self-validate identity and destination** — squad-appliable, and what F-1's
  must_fix asks for as the immediate close: require an `--agent`, validate `--file` against that
  agent's domain, refuse otherwise with a new exit code
- **(c) a running post-write audit** — enforcement layer, yours

**I did not dispatch (b), deliberately.** It is one of the three options you are being asked to choose
between, and dispatching it would answer your own blocking question for you. I have six cycles left
and can close it in one round the moment you say so.

## Where the feature actually stands

**Goal met.** pm verified all twelve criteria by their own declared methods, independently. Eleven
`met`; **SC-01 `met-with-caveat`** — its "two for harness" half runs against a stand-in checkout, and
pm's argument for accepting that comes from the criterion's own text (`BRIEF.md:154-159` calls it "the
criterion that runs every time", and a per-invocation criterion cannot stand up two live worktrees in
this repo each time). pm flagged that it cannot know whether that reading is what you signed.

**The headline claim passes.** SC-01b runs four real worktrees at once, two per repository, via a real
`fleet.yaml` whose second repo has default branch `master`; four concurrent committers synchronise on
a barrier; all six pairwise write-window overlaps are asserted; no branch outside the four advances.
Exit 0, 14 assertions, and I saw it green five separate times.

**Its discriminating negative genuinely discriminates.** I drove the isolation predicate against a
shared checkout five times: 4/4 committers succeeded every time, zero index-lock failures, and
`IsolationViolation` raised on all five. So the `committer_failed` short-circuit that could have let
case B pass without ever calling the predicate never fired. That surface is latent, not absent.

**Gates.** qa PASSED with `matrix_ok: true` per task for all ten. Suites at the pin, my own
measurement, reproduced three times: unit exit 0, integration exit 0, zero FAIL. Simplify returned an
**empty apply set** across four angles — five candidates, all declined, and nothing touched the
enforcement layer. Docs added 120 lines to `SPEC.md`; both new tools had been documented nowhere.

**Cycles: 7 of 13 used, six left. Every segment this phase reported zero send-backs**, so validate
added none. Runs 12 of 20 — under budget, and a floor rather than a total, since your five
main-session-direct tasks are not runs.

## The weakest thing about the delivered feature

**It has never governed a live flow, and every proof in it is a fixture proof.** `git worktree list`
shows two checkouts: this one — the **main** checkout, where FEAT-30 itself was built — and
`.claude/worktrees/FEAT-31`, a legacy **one-segment** tree. The two-level `<repo>/<id>` layout that
T-04's whole mechanism exists to serve has **zero live instances**. The feature did not dogfood the
isolation it delivers.

Two things soften it, both measured by me. Governance on the live tree is unregressed: inside
FEAT-31, `check-domain.sh --resolve` returns the same personas as at the repository root for both a
granted and a differently-granted path. And a path under a *non-existent* worktree resolves to
`NOBODY` — fail-closed, not fail-open — because the new resolution reads the git pointer rather than
counting segments.

**Second weakest: the gate's own numbers do not mean what everyone has been saying.** The
"213 integration" figure counts lines beginning `PASS `. Only 16 of those are per-script summaries,
and the suite emits a further **738** case results under a different `ok ` convention plus 19 section
summaries. So the number captures roughly a fifth of what the suite asserts and mixes per-case with
per-script lines. It is still sound as a *comparative* regression signal — which is how SC-09 uses it,
and pm's `comm -23` on line identities is sounder still — but "213 integration tests pass" is not a
true sentence, and I had repeated it before I checked.

## Claims that failed verification

Four claims reached me from a lead or a predecessor and did not survive re-measurement. Each was
cheap to check and would have travelled as fact.

1. **The simplify pass's only HIGH is refuted.** F-ALT-1 held that three feature switches have no
   checked-in proof, so a refactor making them inert would pass every gate. The switch *names* are
   indeed absent from both test files — but flipping `REFUSE_ON_DIRTY`, `REQUIRE_LANDED` and
   `UNION_APPLY` to `False` reddens their suites with 4, 13 and 12 failures, exit 1 in all three. The
   coverage is behavioural, not by-name.
2. **The docs pass's headline finding is overstated.** It held that "the hook cannot see writes made
   via Bash" is falsified and restated in two *preloaded* skills, so every lead reasons from a false
   premise at spawn. `harness-team/SKILL.md:94` names **`check-domain.sh`** specifically and is
   correct — the Bash route is a different hook — and `harness-zero-micro-management` contains no such
   claim at all. What remains is `BUILD.md:147`'s unqualified "the hook", a low docs-precision item.
3. **T-03's recorded red proof is inert at HEAD** — this one is mine, against the operator's own
   narration. Its `verify:` mutates `WORKTREES_SEGMENT` and asserts only a non-zero exit; at the pin
   that leaves **38/38 grant-parity cases green**, the non-zero exit coming entirely from five
   collateral reds about where worktrees *belong*. "16/16 agent cases red under mutation" was true at
   `2819845` and is false at `fbb3bc0`. The 32 assertions are sound regardless: mutating the real
   mechanism (`checkout_relative` → `return None`) reddens 33 of 38 plus 5 of 8 deep-layout cases.
   **This is T-04 working as designed, not a regression** — but the recorded proof now proves nothing.
   The panel went further than I did: `WORKTREES_SEGMENT` has **no use at all** in the grant re-basing
   path, so that mutation *cannot* redden a grant-parity case. My 38/38 and qa's 16/16 are a set
   difference, not a conflict.
4. **My own inference was wrong twice over, in opposite directions.** I reasoned that
   `test-expertise-merge.py` shared `test-feature-worktree.py`'s crash-discards-results defect because
   they share a reporting structure, then measured it and concluded it did not — a broken tool there
   yields exit 1 with 98 reported lines. The panel corrected me again: it **does** share the structure
   (`:253-276`) and escapes only because it drives the tool as a **subprocess**, so a crash lands in the
   child. The insulation is incidental, not designed. My first instinct was right, my measurement
   answered a narrower question than I asked of it, and the structural risk is present in both files.

For the record, the operator's own build-phase narration held up on four of five claims: T-05's red
proof is **exact** (exactly 10 failures against the pre-T-05 guard, all new refuse cases, zero
pre-existing breakage), T-04's counts hold, and D-09's accepted cost is a real assertion in both
directions. Only T-03's has gone stale.

## Two findings worth your attention below the blocker

**The signed intent T-05 did not implement.** `plan.yaml:944-947` requires refusing "a shell
composition that hides the subcommand". It is unimplemented, and none of its own eleven cases covers
it. I verified the gap before the panel named it: `git checkout`, `reset --hard` and `rebase` are all
blocked for every persona including the orchestrator, and `git -C <path> checkout` is blocked — but
`python3 -c "…subprocess.run(['git','checkout',…])"`, a heredoc equivalent, and `g=git; $g checkout
main` are all allowed. The same signed clause also calls the guard a casual-shape filter at `:946`, so
it contradicts itself. **Implement it, or STRIKE it per DEC-188** — a falsified signed requirement left
standing is what DEC-188 exists to prevent, and nothing detects one.

**Both new tools have a silent-success path.** Besides F-1, `feature-worktree.py`'s GATE 3 passes
silently when the artifact directory exists but is empty: `os.walk` yields no files, `landed_fail`
stays `False`, and GATE 3 prints **nothing** before the removal proceeds. SC-04's "names the paths it
verified" is satisfied by naming nothing. I read the code and agree with the panel that it does not
gate on its own — the trigger is narrow — but it is a fail-open in the guard that exists to prevent
silent data loss, and it is a one-line fix.

## Two things only you can do

**The mirror is unsynced and I am not permitted to fix it.** `check-state.sh` reports 11 FEAT-30
board-drift rows: all ten sub-issues (#616–#625) open against a plan reading `done`, and parent #572
at `Building` where the plan derives `Review`. `plan.yaml` already carries `done`, so the ordering
precondition is satisfied and the remedy is ten `gh-sync.py close-task` runs. My attempt was denied by
the permission classifier as an outward-facing action — a correct denial, and not something to work
around.

**Two high findings sit inside the blocking gate itself, and DEC-174 bars every agent from them.**
`test_kinds.unit.detect`'s glob claims all 32 scripts under `bin/` while `--kind unit` executes only
the 18 in `UNIT_SCRIPTS`, so the unit leg of the matrix **cannot fail** for any task whose test lives
there — eight of ten `matrix_ok: true` verdicts rest on that glob. And `integration.detect` names 6
where the runner runs 14, so this diff **moved** backlog item B-1 rather than fixing it; the gap was 8
and is still 8. Fix the consistency check first; it turns the hand-maintained list into a loud failure
instead of a silent one. Worth knowing why nobody caught it: none of the five test files this diff
touches is in `UNIT_SCRIPTS`, so the feature exercised the unit leg zero times.

## Proposed backlog

Unstruck rows become issues on your ship acceptance; anything not listed here dies silently.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `test_kinds.unit.detect` glob claims 32 `bin/` scripts; `--kind unit` runs 18. The unit leg cannot fail. Enforcement config, yours |
| B-2 | bug | `integration.detect` names 6 of the 14 scripts the runner runs. Add a consistency check rather than eight filenames. Yours |
| B-3 | bug | `feature-worktree.py` GATE 3 passes silently on an existing-but-empty artifact directory |
| B-4 | bug | `expertise-merge.py` `compute_union` silently drops a duplicate id *within one proposal* — no `CONFLICT`, no non-zero exit |
| B-5 | bug | `test-feature-worktree.py` discards all 88 results on any exception: `create_four` carries `dest: None`, `case_isolation:196` raises, and the results loop sits outside `main()`'s `finally`. 13 of 17 cases silently skipped at exit 1 |
| B-6 | chore | T-03's `verify:` mutation target is stale — target `checkout_relative`, not `WORKTREES_SEGMENT`. Plan-level, pm under your signature |
| B-7 | chore | The exit-code-only `verify:` shape appears in 6 of 10 tasks — vacuous in 2, non-vacuous in 2, no standing case in 2. Consider one instrument rather than six rows |
| B-8 | bug | `remove` has no cwd guard and no test for one: nothing stops it running from inside the tree it deletes, which is the exact hazard that makes removal the main session's act |
| B-9 | chore | No `worktrees-old` sibling case for the `commonpath` idiom at three sites. The code is correct — I ran the missing case — but a `startswith` refactor would pass |
| B-10 | chore | `expertise-merge.py:37` accepts `[A-Za-z]{1,3}` ids where `check-expertise.sh:44` accepts `[A-Z]{1,3}`. Latent — `check-expertise.sh` exits 0 on every real file today. **Validate, do not narrow:** narrowing makes the line fail `ENTRY_RE`, so `parse_expertise` skips it silently and the entry is lost earlier and more quietly than today |
| B-11 | chore | `BUILD.md:147`'s unqualified "the hook cannot see writes made via Bash" and its "serialization remains the write-safety mechanism" conclusion predate the Bash guard |
| B-12 | chore | The suite's headline `PASS`-line counts are not a coherent unit — 738 case results report as `ok` and are omitted. Report one number that means one thing |
| B-13 | chore | `.harness/README.md` contradicts disk on three counts (`feature.yaml`/`feature.json`, `PLAN.md`/`plan.yaml`, features path). Belongs to the FEAT-21/22 + DEC-182 migration |
| B-14 | chore | GATE 3 spawns two git subprocesses per artifact file — ~1.3s over 83 files against ~10ms for one `ls-tree` plus local hashing. `git hash-object` without `--path` applies no filters, so local hashing reproduces it exactly |
| B-15 | chore | Issue #626 may be one entry short: `DECISIONS-INDEX.md:114` has DEC-95 asserting `.harness/` is per-worktree state, a fourth falsified spelling |
| B-16 | chore | A hard-killed `expertise-merge.py` leaves a lock that blocks every later apply with exit 6 and no self-recovery. Exception paths are already safe via `finally` |
| B-17 | chore | The member digest schema has no shape for a read-only review dispatch, and differs by role: one instruction produced `pass`, `none` and `n/a` from three personas, each citing its own schema, all validated |
| B-18 | chore | `test-expertise-merge.py` labels its seventh case group "case8"; all seven functions are invoked, so cosmetic only |

## Open questions

1. **Blocking — the allow-by-omission decision.** (a), (b) or (c) above. (b) is squad-appliable and I
   can run it in one cycle; (a) and (c) are yours.
2. **Blocking in effect — SC-01's stand-in reading.** pm judged it met from the criterion's own text
   and said plainly it cannot know whether that is what you signed. If you disagree, SC-01 is unmet and
   that is a re-plan, not a build defect.
3. T-05's unimplemented signed clause: implement or STRIKE per DEC-188.
4. Two escape hypotheses remain structural rather than demonstrated, because the panel is read-only —
   a symlink escape from the DEC-153 carve-out, and a nested-`.git` candidate. Closing either needs a
   probe, not another reviewer.
5. **Two routes give two different answers for the same location.** `SPEC.md:2239` argues per-team
   serialization suffices "because the teams are operating on different checkouts", while the carve-out
   at `bash-write-guard.sh:687` blanket-allows any governed agent to write into any worktree on the Bash
   route. DEC-143 and DEC-153 answer differently and each route implements one answer. Intended? And is
   it inside #626's scope, or is #626 only about path spellings?
6. **Is there any *running* post-run audit of HEAD position**, as opposed to the one-shot manual DEC-153
   audit? If not, the HEAD-move residual is uncompensated, unlike the write-side residual — which
   matters more now that HEAD-move refusal is what keeps concurrent worktrees apart.

## What I judged and could be wrong about

I accepted the qa lead's PASS despite `severity_max: high`, because its two findings are barred to
every agent by DEC-174 and a FAIL would have routed remediation to work nobody may perform. I
accepted the panel lead's two severity overrides — the test-harness crash down to med, the id-regex
down to low — because at the pin every case runs and reports, and the regex mismatch has zero live
instances. And I did not dispatch the squad-appliable half of the blocker, on the grounds that it is
one of three options you are being asked to choose between. Each of those is cheap to overturn.

**One attribution I had wrong, and the panel caught it.** The internally contradictory signed intent
is **T-04's** (`plan.yaml:736-739` against `:861-863`), not T-05's — the code reviewer derived that
independently. The substance stands and resolves in the operator's favour: the carve-out at
`bash-write-guard.sh:688` runs before `classify` and is blanket and depth-agnostic, so the intent's
refuse-half really was unreachable. And the delivered handling did more than I credited — it relocated
the refusal half to a reachable site, preserving the paired-case purpose rather than dropping it.

**The panel also rebutted my acceptance of the qa gate's PASS, and it is right.** I accepted that PASS
because DEC-174 barred every agent from its two findings. The panel FAILed on F-1 for the opposite
reason: F-1 has *two* remedies and only one is enforcement-layer, so looping back is meaningful — which
is exactly the test `FAIL` answers. The distinction is remedy availability, not severity.
