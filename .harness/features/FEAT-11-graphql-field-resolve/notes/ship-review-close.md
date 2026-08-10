# FEAT-11 — ship review — one GraphQL query for project field ids

**For the operator. Written 2026-08-10, branch `feat/FEAT-11-graphql-field-resolve` at `aea7824`.
Nothing is pushed and no PR is open — the merge is yours.**

---

## The conclusion first

**The factory no longer burns 104 GraphQL points to move one item between stations. It burns 2.**
That call sits inside `factory_decompose`'s per-task loop, so the practical difference is a factory
that used to exhaust the 5000-point hourly budget mid-run and stop, versus one that does not.

**Eleven of the twelve success criteria are proven. The twelfth — SC-01, the cost measurement
itself — is yours to run and cannot be delegated.** That is the documented expected end state, not a
gap: the proof writes to a live Projects v2 board, which is outside every agent's authorization in
this flow. The script is written and waiting at
`.harness/features/FEAT-11-graphql-field-resolve/notes/uat-SC-01-graphql-cost.md`.

**Two decisions need you.** One is blocking — SC-01's total clause may be arithmetically unmeetable
as written. The other is the D-03 partial-success question, where both pm and I recommend accepting
rather than amending.

| | Before | After |
|---|---|---|
| One station move | 104 GraphQL points | 2 |
| Field + board id resolution | two calls (`field-list` 102, `view` 2) | one call, cost 1 |
| Failure states told apart | 1 | 4, each naming your own input |
| A four-task decompose | exhausts the hourly budget | see the open ruling below |

---

## How this briefing was assembled — and what that costs you

**No report round was spawned.** Every run wrote a digest to disk and I read them, including the
plan-phase runs I never participated in. Three lead spawns to re-narrate files I can open would have
been spend with nothing to surface it. The cost of that choice is that this is my reading of those
digests rather than each lead's own summary; the paths are below so you can check any claim against
its source.

Assembled from: `runs/plan-product/digest.md`, `runs/plan-contract-validator/digest.md`,
`runs/plan-fix-product/digest.md`, `runs/t01-eng/digest.md`, `runs/t01-qa-validator/digest.md`,
`runs/mf1-eng/digest.md`, `runs/2026-08-10-01-q5-product/digest.md`,
`runs/2026-08-10-02-validator/digest.md`, `runs/goalcheck-product/digest.md`,
`runs/mf2-eng/digest.md`, `runs/distill-{eng,product,validator}/digest.md`, plus `notes/qa-c0.md`,
the four `notes/review-harness-*-c0.md`, `notes/research-FEAT-11-goal-check.md` and
`notes/uat-SC-01-graphql-cost.md`. Paths are relative to
`.harness/features/FEAT-11-graphql-field-resolve/`.

**Every gate result quoted here I re-ran myself rather than relaying** — the task verify, both test
kinds, the three sha256 sentinels, the byte-identity of both mutant restores, and the expertise
format gate.

**One verdict is mine rather than a squad's, and you should know which.** pm's goal-check returned
SC-11 `not_met`, I routed the fix, and then **I closed SC-11 myself instead of re-spawning the
goal-check.** The criterion's declared method is `automated` with `unit` evidence; I read the landed
assertion, confirmed its mutant proof named the reddening checks in advance, and re-ran both kinds —
that is the declared method executed, not a shortcut around it. But nothing on disk shows pm
agreeing it closed, so `runs/goalcheck-product/digest.md` still reads `not_met`. If you want the
paper trail, a pm re-run is one dispatch.

---

## What each squad did

**Engineering** ran three times, all PASS, all first-pass. T-01 replaced the two-call path with one
named-field GraphQL query and a single diagnosis walk that tells four failures apart: an owner login
that resolves to nothing, an organization-owned board, a board number that does not exist, and a
field the board does not offer. The old code conflated them. `_field_list` was deleted rather than
kept as a fallback, because keeping the 102-point path in the tree preserves the thing being removed.
TDD order is evidenced in the receipt — 11 of 108 checks red against the unchanged module first. Two
later runs fixed test assertions, below.

**Validation** ran twice. The blocking test-matrix gate passed **after one fix cycle** and earned its
blocking status. It also established something the record had been wrong about for a while: the
integration *kind* had never been shown green — every "97/97" before that segment was one script out
of twelve. The four-reviewer panel then returned PASS at `severity_max: info` with zero must_fix,
re-raising none of the four known items I named in its dispatch while still probing an unmeasured
shape (`projectV2` present with `id` absent) and finding it fails safe with no write. Security
confirmed your inputs travel as GraphQL variables, never interpolated into the query text.

**Product** ran the plan phase, struck two dead markers from `DESIGN.md`, and ran the goal-check that
found the last defect and wrote your UAT script.

---

## The two defects the gates caught, both of the same kind

Neither was a bug in the shipped code. Both were **assertions that could not fail** — checks
reporting green for a reason unrelated to what they claimed to prove. This is the failure mode this
factory is most exposed to, because it is invisible in a green suite.

**MF-1 (found by the qa gate).** SC-10 says every failure names your own input. Its proof for the
unknown-owner case was `"owner" in str(exc)` — against a message reading *"project owner not found:
owner — check the owner login"*. The word is in the prose twice, so the check was true for every
possible value, including no value at all.

**MF-2 (found by the goal-check).** SC-11 requires the misspelled-owner error be distinct from
**both** the organization refusal **and** the board-not-found error. The suite proved two pairings
and stopped. Inequality is not transitive, so the pair SC-11 names first was never compared.

Both fixes were **watched failing before they were believed**: the source was mutated, the specific
checks predicted by name, and the prediction checked against what actually reddened. In MF-2's case,
had only the other check reddened, the new assertion would have been vacuous and the cycle would have
failed. The source file was restored byte-identically both times and I verified that myself with an
empty `git diff`, not from the report.

**One finding was itself half wrong, and the record says so rather than being tidied.** qa's MF-1
named two vacuous assertions; only one was. The organization message reads *"organization-**owned** …
user-**owned**"* and contains no `owner` substring, so that row already discriminated. The correction
lives in `feature.yaml` `mf1_correction`; the qa digest is left as the dated record of what that run
concluded.

**The pattern matters more than either instance.** Both were multi-clause criteria whose clauses were
scored as covered because *some* assertion touched the area. Two occurrences in one feature is a
counting method that does not work, not two unlucky misses. It is `B-7` below.

---

## What only you can settle

### 1. SC-01 may be unmeetable as written — and you get one run **[blocking]**

pm found this at goal-check, not at plan time, and the arithmetic is the problem rather than the
code. SC-01 asks for a **single-digit total** across a four-task `factory_decompose`. But a decompose
also pays `gh project item-list` at **31 points per task** whenever it has to find an existing board
item — a call this feature never touched and never claimed to change. An all-`partial` run therefore
has a floor around 133 points regardless of how cheap the field resolution became.

There is no free option here:

| Choice | What you get | What it costs |
|---|---|---|
| Measure the **per-move** clause only (2 vs 104) | The number that proves the feature, cleanly isolated | SC-01's total clause goes unproven and is recorded as mis-specified |
| Measure the **total** on an all-new run | The total clause as written | The run creates board items your restore cannot undo — it spends the fixture |

**My recommendation: accept the per-move clause as the proof and record the total clause as
mis-specified at plan time.** The per-move number is what the feature changed, it is discriminating
either way, and the total was written against a cost model derived for the code being changed rather
than for the whole run the criterion measures. Amending an SC is yours alone; I have not touched it.

### 2. A GraphQL partial-success response completes its write **[non-blocking — recommend accept]**

If `gh` exits non-zero but returns a *complete* data payload alongside an `errors` array, the
resolver walks it clean and `project_field_set` finishes its write. **What you would experience:** an
item moves station, `gh` reported the call failed, the run finishes green recording no error, and
recovery is moving the item back by hand. How often that happens is unmeasured — the envelope has no
row in the six-row transport table the plan measured.

This is **signed decision D-03 behaving exactly as written**, so no engineering fix cycle can
legitimately close it; changing it changes the decision. It does not violate SC-07, whose clause is
that a failed resolution never reuses the bare board number as `--project-id` — the id passed is the
real resolved node id. **pm and I both recommend accepting it as a recorded residual against D-03**
rather than amending. If you prefer to amend, that is a new `D-NN` under your approval.

### 3. Before you run the UAT, read its step 0

pm added a step nobody asked for and it is the most valuable thing in the script.
`factory_decompose` does **not** take the board from a flag — it reads `.harness/factory/fleet.yaml`,
which today declares **board 3**, station field `Status`. I verified that line myself. Run the
measurement as originally specified and it writes stations onto board 3, which nobody snapshotted,
while carefully protecting board 6, which nothing would have touched. The script pins an explicit
fleet file first and asserts the board number is 6 before anything runs.

The script also keeps the snapshot and the restore **outside** the differenced measurement window on
purpose — 67 points spent deliberately so the window contains only what is under test — and gets the
option ids for 1 point rather than via the 102-point call this feature exists to remove.

**Board 6 and `mruangutai/harness-factory-smoke-a1` are treated throughout as retained fixtures.
Nothing in this feature deleted them, no agent made a single live `gh` call against either, and
neither is reported as cleanup owed.**

---

## Budget, effort and what the org learned

**11 of 12 cycles spent** — 8 in the plan phase before this mission began, 3 in this one: MF-1, MF-2,
and one a lead charged itself when it discovered it had handed its own members an incomplete source
list and re-ran the round. That third one is worth reading as a good sign rather than a bad one: the
correction recovered six Expertise entries that would otherwise have been lost permanently, because
Expertise is written once per feature, and a member caught the error and returned it upward.

**16 runs against an informational budget of 20 — not crossed, so no note is owed.** The two runs
that cost a cycle are also the two that found the defects, and the panel that cost nothing found
none. That is the gates working in the order they are designed to.

**Distillation is complete and every Expertise file passes the format gate except one, which this
feature never touched.** Eleven agents updated their files; `harness-visual-designer` got one for the
first time. No file was wiped — entry counts were checked before and after rather than trusted, and
one lead went further and proved its nine untouched entries byte-identical. The one failure,
`harness-documentor.md`, was already red before this feature opened (`git log 8dedeae..HEAD` shows it
untouched); three leads independently declined to spawn documentor to trim three words, each citing
the risk of opening a near-full file with nothing to distill, and I endorsed all three refusals. It
is `B-13`.

**GitHub mirror:** milestone #5, parent #214 (created by this flow), T-01 → #215, now closed. Issue
**#211** — the P0 this feature absorbs — is deliberately left **open** for your acceptance to close.

**Commits, all by explicit pathspec with the tree's unrelated held dirt excluded:** `5c433f2` (T-01),
`2ea9af3` (MF-1 + the marker strike), `15cabe9` (MF-2 + review artifacts + two record corrections to
the executed plan), `aea7824` (the close-out: distilled Expertise, two seam notes, this briefing).

---

## Proposed backlog

Nothing here gates the ship. **Anything you do not strike becomes a backlog issue on your
acceptance; anything not listed dies silently, so this list is deliberately complete.**

| ID | Item | Nature |
|---|---|---|
| B-1 | **D-03 partial-success completes its write.** Decision #2 above. If you accept, this row records it against D-03 rather than opening work | chore |
| B-2 | **A top-level `{"data": null}` envelope reports the wrong cause** — it raises "project owner not found", which is safe (no write) but factually wrong. Unmeasured, possibly schema-impossible | bug |
| B-3 | **`harness-qa` cannot author a test in this repo.** Its grants are `tests/**` and `web/src/**/*.test.*`; every test here lives in `.claude/skills/harness/bin/test-*.py`. The qa segment is gate-and-assess by construction and a missing test can only ever be a finding | bug |
| B-4 | **`harness-pm` has no `notes/receipt-*.md` grant** while the handoff skill instructs every agent to file one there. Same routing-wall class as B-3 | bug |
| B-5 | **`bash-write-guard.sh` mis-parses `cp … 2>/dev/null`** — it reads the redirect target as the `cp` destination and blocks a legitimate in-domain write. A fail-closed hook with a false positive. **It is a DEC-174 carve-out file, so no agent may fix it; this one is yours to edit directly** | bug |
| B-6 | **`BRIEF.md:162` still calls board 6 "the throwaway … already owed cleanup"**, contradicting your own later ruling. pm left it deliberately — changing a signed artifact is a re-signature, not a correction — but it is what the next reader opens | chore |
| B-7 | **Multi-clause criteria are scored as covered when one clause is asserted.** MF-1 and MF-2 are the same defect twice in one feature. Worth a harness-level look at how criteria are counted against assertions | enhancement |
| B-8 | **`GRAPHQL_ORG_OK_JSON` is derived, never observed.** The organization path's discriminating fixture was constructed from reasoning because no org owning a reachable board exists on this account. Disclosed in the BRIEF; recorded so it is not later mistaken for measured | chore |
| B-9 | **Two `ok-stale` markers survive** in `notes/review-harness-ui-reviewer-plan-product.md:63-64`. Left because that file belongs to the validator squad and product could not write it | chore |
| B-10 | **No gate observes TDD order.** T-01 landed in one commit, so red-before-green rests on the build receipt's self-report | enhancement |
| B-11 | **Two of five qa mutants reddened by suite crash** rather than by a named check. Detection held, but a crash halts the linear script and masks every check after it | enhancement |
| B-12 | **`plan.yaml` line anchors shift as the file is edited.** Two digests now cite line numbers that resolve to different (still green) checks after MF-2 inserted three lines. Nothing is falsified; the citations are silently re-pointed | chore |
| B-13 | **`harness-documentor.md` G-04 is 53 words against a 50-word cap**, which makes `check-expertise.sh` red across the whole directory. Pre-existing, not caused here. A permanently-red shared gate stops being read, which is the real cost | bug |
| B-14 | **`harness-pm.md` and `harness-orchestrator.md` are at their Patterns cap**, and `harness-code-reviewer.md` is one below. Every future distillation must displace to add, with no usage data to rank entries by | enhancement |
| B-15 | **No member wrote an observations log this feature.** Distillation ran entirely off run receipts and worked, because those receipts were unusually complete — not because the hot layer is optional. Worth deciding whether the layer is a gap or correctly unused | enhancement |
| B-16 | **`validate-digest.py` has no `suite:` spelling for a run that executes no test suite**, so a distillation run must report a test-suite field that measured nothing | chore |

---

## What I recommend

**Ship it, after you run the UAT.** The code is correct, the gates are green, the two defects found
were in the proofs rather than the product, and both were fixed and proven falsifiable. The one thing
standing between this and done is the measurement only you can take — and the ruling on what SC-01's
total clause should have said.
