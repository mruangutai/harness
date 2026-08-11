# Receipt — harness-backend-dev — plan-eng review of T-01 (FEAT-13)

## BLUF

Two blocking holes. F1 (job 2): the `None`/raise enumeration never distinguishes "repository
carries no `issue` key at all" from "`repository.issue` is null" — a plausible, literal
implementation collapses both into `None`, re-triggering the duplicate board add this feature
exists to prevent, and no enumerated test catches it. F6 (job 3): step 5's assertion is a call
*count* ("`project_items` zero times, `issue_board_item_id` exactly once"), which pins nothing
about the arguments passed — and the plan itself reorders two call-site signatures
(`_find_item_id`, `_find_existing_item_id`), including silently changing `factory_land.py:92`'s
first argument from the board owner to the repo string. An argument mis-wire there sails past
every unit assertion the plan enumerates (the Recorder stub records and returns, it does not
validate) and only reddens in the integration script. Two lower-severity findings: an unstated
exit-code change in `claim --issue` for a repo-mismatch edge case (F4), and a stale in-code comment
that becomes false after the change lands (F5). Job 1 is clean; job 3's registration/idiom
questions are answered accurately but the discriminating question surfaces F6.

## Findings

**F1 — high — `plan.yaml:140-158`.** The `None` list states "repository.issue is null → None"; the
raise list never states "repository carries no `issue` key at all → raise." A conforming
implementation of exactly the listed rules —
`issue = repository.get("issue"); if issue is None: return None` — satisfies every one of the
step-5 enumerated assertions (checked each against `plan.yaml:242-256`: none of them constructs a
`repository` dict that omits the `issue` key while keeping `repository` itself present and
non-null). That collapse makes an unrecognised/truncated-shaped response — one where `issue` is
simply absent rather than explicitly `null` — read as "no item," which re-triggers the duplicate
board add `issue_board_item_id` exists to prevent (BRIEF REQ-05, D-03).
Remedy: add to the raise list, "`repository` is a dict carrying no `issue` key at all (distinct
from a dict where `issue` is explicitly `null`)," and add a step-5 test-factory-gh.py bullet:
"a response whose `repository` dict carries no `issue` key at all (as opposed to `issue: null`)
RAISES, asserted as a separate case from the issue-null case."

**F2 — low/info — `plan.yaml:145-158`.** Type-vs-presence asymmetry, narrower than first drafted:
the sibling `project_items` (`factory_gh.py:180-186`, cited by the plan as the precedent) does
`total = out.get("totalCount"); if total is None: raise`, which already covers `totalCount` present
but explicitly `null` — a builder imitating the sibling gets that case for free. The residual gap is
`totalCount` present, non-`None`, and non-int (e.g. a string) — `total > len(nodes)` then raises a
bare `TypeError`, not `GhError`. Per `factory_cli.py:72-96`, `run()` traps *both* expected and
unexpected exceptions at the same exit code (`EXIT_REFUSED`, 2) — this does **not** fail open, it
still blocks. The consequence is diagnostic quality: the printed message becomes "unexpected
failure: TypeError: ... — re-run with FACTORY_DEBUG=1" instead of the actionable
`what`/`value`/`next_step` triple every other raise in this module carries (`factory_gh.py:32-45`
docstring). Not must-fix; one added line covers it: "`totalCount` present but not an int raises
`GhError` explicitly."

**F3 — info — `plan.yaml:145-146` vs `factory_gh.py:254`.** The plan tells the new helper to raise
when the envelope carries no `data` key; the cited sibling `_project_field_resolve` does
`data = env.get("data") or {}` and does not raise there — it lets a later explicit null-check
produce the real message. This is a deliberate, and correct, divergence (an empty-dict silent
default would still need the same downstream checks either way), but the intent's "reuse verbatim
in shape" instruction earlier in the same paragraph could read as blanket imitation. One sentence
in the plan — "the `data`-key check is a deliberate exception to imitating the sibling, not an
oversight" — would remove the ambiguity for a builder cross-referencing both functions.

**F4 — med — `plan.yaml:210-224` (D-02) vs `factory_claim.py:226-256`.** Confirmed by direct trace:
today, `claim --issue 216` where the board carries a row for issue #216 under a repository not in
the fleet (or not matching `args.repo`) reaches `factory_cli.nothing_to_do` (`EXIT_NOTHING`, exit
1) — the pre-loop refuse at `:231-235` is not taken because `project_items` matches by number
across the whole board, and the mismatch is only caught by the step-4 `repo_names`/`args.repo`
filter, which empties `candidates`. Under D-02's per-fleet-repo iteration, that same case never
finds an id in any fleet repo tried, so the plan's "keep today's refusal verbatim" fires
(`factory_cli.refuse`, `EXIT_REFUSED`, exit 2) instead. This is a real exit-code change (1 → 2) for
a case neither an SC nor a REQ names, and it runs against the BRIEF's explicit "no tool changes
what an operator observes" goal. `intent:` line 224's "the exhausted-without-a-win path ... exit
code is unchanged" is true as stated (it describes step-5c candidate-loop exhaustion, a different
code path), so it does not contradict this — but it also does not cover this case, leaving it
unaddressed. Remedy: either add one sentence to `plan.yaml` acknowledging the exit-code change for
"issue found on the board under a repo outside the fleet, or not matching `--repo`" (making it an
explicit, operator-visible decision), or add a task-5 assertion pinning today's `EXIT_NOTHING` for
that specific case if the operator wants it preserved.

**F6 — med — `plan.yaml:258-263` vs `factory_land.py:87-92`, `factory_decompose.py:454`.** Step 5's
stated site assertion is a call *count*: "`project_items` called ZERO times ... and
`issue_board_item_id` exactly once." A count pins nothing about what was **passed**, and the plan
itself silently reorders / repurposes call-site arguments while rewriting the three signatures.
Concretely at `factory_land.py:92`: today's call is `_find_item_id(owner, board_number,
args.issue)` where `owner = fleet["board"]["owner"]` (the board owner). Step 3 renames the
signature to `_find_item_id(repo, number, board_number)`, which needs the call site changed to pass
`args.repo` (the `"owner/name"` repository string) in the first slot — but the intent only says
"update the call site at `:92`," never naming which variable replaces `owner`. A builder who
mechanically keeps passing the in-scope `owner` variable produces a call that looks superficially
right (same call count, same "exactly once") but is wired to the wrong value. This does **not**
fail loud at the unit layer the way I first assumed: step 5 tells the builder to add
`issue_board_item_id` to the land/decompose/claim **Recorder** stub, and a Recorder records and
returns a canned id — it never validates the repo string's shape, so `owner` in place of `args.repo`
sails past every listed unit assertion and only reddens in `test-factory-integration.py`, where the
real `factory_gh.issue_board_item_id` runs and its "malformed repository" check finally fires.
Remedy: (1) step 5's per-site assertion must pin the **recorded argument tuple** — the
`"owner/name"` repo string, the issue number, and the board number — not just the call count; (2)
step 3's land instruction must say explicitly that the call site at `:92` passes `args.repo`, not
the board-owner variable already in scope under the name `owner`.

**F5 — low — `factory_claim.py:268`.** The in-code comment "5a. self-ownership FIRST, and only
under --issue — must precede every skip below" becomes false the moment D-05's closed-issue check
lands immediately before 5a (`plan.yaml:229-233`, "place that check BEFORE the self-ownership
branch at 5a"). `intent:` does not instruct updating this comment. Remedy: one line in step 4's
intent — "update the `# 5a.` comment at `factory_claim.py:268` to say the closed-issue check now
precedes it, not that 5a is first."

## The four jobs, briefly

1. **Integration stub / `state` — clean on `state`, but the new query needs a `project.number` the
   plan doesn't name.** `test-factory-integration.py:129-139`'s `issue view` branch already returns
   a `state` field, defaulting to `"OPEN"` (`:135`) whether or not the fixture set it. Case (D-land)
   seeds `issues={"700": {..., "state": "OPEN", ...}}` explicitly (`:553`); case (F) seeds no
   `issues` at all but decompose's own `["issue", "create"]` branch (`:118-127`) writes
   `"state": "OPEN"` at creation time before land ever reads it. No red-on-arrival risk on `state`.
   `factory_claim.py:262-264` already requests `"state"` in its `issue_view` fields — nothing to
   widen there. Separately: the new query carries `$owner`/`$name`/`$number` only — the board match
   happens client-side in `issue_board_item_id` against each node's `project.number`. The fixture's
   board number is 9 (`test-factory-integration.py:303`, `fleet_dict`). Step 5's integration
   instruction (`plan.yaml:278-284`) says the new stub branch answers "with a totalCount and a
   nodes list" but never says the node(s) must carry `project.number == 9` — if the stub's synthetic
   node uses a different or placeholder project number, every integration case gets `None` back and
   SC-08 reddens for a reason unrelated to the code under test. One sentence closes it: "the node's
   `project.number` must equal the fixture's board number (9), the same value
   `_project_field_resolve`'s stub branch is never asked to match."
2. See F1–F3 above.
3. **Line anchors accurate; the discriminating question surfaces F6.** `test-factory-gh.py:288-295`
   is the `project_field_set` case: asserts `len(calls) == 2` (`:289`) and reads `argv[1:3]` (`:293`,
   `:295`) exactly as cited. `test-factory-land.py:245` is the `field_set_calls == []` idiom,
   confirmed verbatim. All three call sites monkeypatch over a class named `Recorder`; the
   patched-name tuple is `PATCHED_GH` in `test-factory-land.py:123` and `PATCHED` in
   `test-factory-decompose.py:121` and `test-factory-claim.py:121`. Every Recorder already logs
   `project_items` (`test-factory-decompose.py:116-118`, `test-factory-land.py:115-117`,
   `test-factory-claim.py:87-90`). The "per site" phrasing catches a one-of-three-sites-left-on-
   `project_items` defect (the zero-count half discriminates cleanly). It does **not** catch an
   argument mis-wire, because the stated assertion is a call count — see F6. All five files are
   registered in `run-unit-tests.sh:17-18` (`UNIT_SCRIPTS` for the four unit files,
   `INTEGRATION_SCRIPTS` for `test-factory-integration.py`).
4. `test_matrix.cross_module.always == ["unit", "integration"]` (`harness.json`), confirming D-06.
   The D-02 exit-code derivation is correct — see F4. The synthetic `raw_items` row
   (`plan.yaml:214-218`) was traced through `_repo_name_of` (`factory_claim.py:69-84`, takes
   `content.repository` directly, no warning/normalisation), the step-4 filter (`:240-253`, reads
   `content.number` and the repo string, both present), the candidate loop (`:261-319`, re-fetches
   `issue_view` independently — never reads the synthetic row's content again), and the winner
   bookkeeping (`:326-330`, reads only `item.get("id")`, present). No consumer reads a key the
   synthetic row omits — clean.

## must_fix

- F1 (high) — the None/raise collapse on a missing `issue` key.
- F6 (med) — step 5's call-count assertion doesn't pin arguments; land's owner-vs-repo call-site
  rewrite at `:92` is unspecified and can mis-wire past every unit assertion.
- F4 (med) — the unacknowledged exit-code change for the repo-mismatch case under `claim --issue`.

## Out of scope, not evaluated

Operator rulings, land's filed latent bug (#238), the claim poll, harness defect #218, and the four
DEC-174 carve-out scripts — per the dispatch.
