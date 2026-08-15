# Review — harness-code-reviewer — panel2 — FEAT-10

Reviewed: `b89c00a..8bbb246022d660492b14fcb9bafec7729b0ba23d` (one commit, 53 files). `2a3e91c`
and `b89c00a` out of scope, not opened. `.harness/harness.json`'s `test_matrix` (DEC-187) not
re-litigated. LEAVE list (DECISIONS docs, logs, feature-dir process artifacts) not reviewed.
Checked for `[harness:human]` commits in range: zero — the range is one commit, `8bbb246` itself.

## VERDICT: FAIL

One `must_fix` finding, `high` (F1). A second finding (F2) is a real plan/code mismatch worth a
ruling but is not `must_fix` on its own — see why below, which is a correction to my own first
pass after checking `factory_land.py`'s recovery path.

---

## Finding 1 (must_fix, high) — `factory_decompose.py`: a station-set failure orphans the task from the board forever, with no self-healing path

**Where:** `factory_decompose.py:361-370` (step 7), read together with `load_factory`/`write_factory`
(`:90-134`, `:177-209`) and `sort_dispositions`/`_owes_edges` (`:216-240`).

**Trace, answering the dispatch's task-5-of-10 scenario directly.** Step 6 creates every task's
issue up front, in one loop, before step 7 begins — so by the time step 7 starts, `factory["issues"]`
already holds all ten task numbers. Step 7 then, per task:

```python
item_id = factory_gh.project_item_add(owner, board_number, url)
factory["items"][tid] = item_id
write_factory(feat_dir, factory)                       # <-- receipt written HERE
factory_gh.project_field_set(owner, board_number, item_id, station_field, ready_option)
```

The item id is persisted to `feature.yaml` **before** `project_field_set` is called. If task 5's
`project_field_set` raises (the new `gh project view` call, or the pre-existing `_field_list` call,
or any transient `gh` failure), the exception propagates uncaught out of the loop — tasks 6-10 in
this step are never reached — and the wrapper exits 2. At that point: `issues` holds all ten,
`items` holds `{1,2,3,4,5}` (task 5's board-add receipt survived the crash; its station-set did
not).

**On re-run**, `sort_dispositions` sorts by `(has_issue, has_item)` alone for the first three
dispositions (`:232-239`). Task 5 now has both an issue *and* an item, exactly like tasks 1-4 —
the ledger carries **no receipt at all for whether the station-set half of step 7 succeeded**, so
task 5 is indistinguishable from a task that completed cleanly. Its disposition becomes
`edges_unwritten` (or `full`), never `new`/`partial`. Step 7's own guard —
`if dispositions[tid] not in ("new", "partial"): continue` (`:363`) — therefore skips task 5 on
every future run. `project_field_set` is never retried for it, by construction, forever.

**Consequence, and why there is no self-heal.** Task 5's issue and board item genuinely exist, but
its station is never set to `ready`. `factory_claim.py`'s poll query is `status:"Ready" is:open`
(`factory_claim.py:237`) — an item with no station set never matches it, so the task is invisible
to every future claim poll and never reaches `factory_claim`, `factory_workspace` or
`factory_land`. Unlike Finding 2 below, there is no later step in the journey that ever touches
this item again to correct it — the item simply never enters the pipeline. Nothing refuses,
nothing exits non-zero on a later run, and the payload (`:428-436`) reports `issues` only — no
field anywhere tells the operator task 5 never reached `ready`. This directly breaks REQ-01
("shows the operator every piece of work... and which station each one is at") and REQ-03 (an
agent can take the next available piece of work — this one can never be taken), and it falsifies
SC-16's "station set to the fleet's ready option" for exactly the task that hit the failure.

**Stage-1 classification is genuinely ambiguous between the two readings, and both are worth
handing to the operator rather than resolving silently.** T-04's own text at `plan.yaml:610-611`
describes the second (partial) disposition's resume as "adding the board item and setting its
station, **then** recording the item id in step 8" — read literally, that orders the record *after*
both calls succeed, which would make the code's actual order (record after the first call only) a
**mismatch** with T-04's own words. But step 8's own enumeration (`plan.yaml:783-785`, "after each
successful issue creation, each successful board add and each successful edge write, write...")
lists exactly three receipt-triggering events, and station-set is not among them — which reads as
the signed design never covering this case at all, an **omission**. I cannot settle which reading
is correct from the text alone; the operator should, since it changes who owns the fix (an
implementer deviation from T-04 vs. a hole in the signed design itself).

**Not a caching problem.** `project_item_add` and `project_field_set` are each individually safe to
retry; the defect is that the ledger's only persisted fact for this pair is the *first* call's
result. That gap predates the S1 fix (any `project_field_set` failure would have hit it), but S1's
added `gh project view` call is a second, independent way to reach the same crash window inside the
same function, making it materially easier to trigger.

**No test exercises the miss.** `test-factory-decompose.py` case 7 (`:391-419`, "resume-after-
partial") only makes `project_item_add` raise, which leaves the item unrecorded and resumes
correctly. Grepped: `raise_on["project_field_set"]` does not appear anywhere in that file. The exact
failure mode this finding describes has zero coverage in either direction.

## Finding 2 (should_fix, med, rank 2) — `factory_claim.py`: the plan's documented recovery does not retry the station-set, but the item self-heals at land

**Where:** `factory_claim.py:270-274` (self-ownership branch) versus `:325-330` (step 6 winner
bookkeeping), and plan.yaml T-05's own "POINT OF NO RETURN" text.

The plan text (`plan.yaml` T-05, "POINT OF NO RETURN") states explicitly: *"a failure in step 6
exits 2 with the claim held and the station possibly still ready; the recorded recovery is to
re-run with `--issue <n>`, which the same agent completes idempotently."* Step 6 is, in order:
`add_label`, `assign`, then `project_field_set(..., stations["building"])` (`:328-330`). If
`project_field_set` raises here — label and assignee already written — the tool exits 2 with the
board item's station still `ready`.

Re-run with `--issue <n>` as the same agent hits the **self-ownership branch** first (`:270-274`):

```python
if args.issue is not None and "factory:claimed" in labels and any(
    a.get("login") == args.as_login for a in assignees
):
    _emit(repo_name, num, issue)
    sys.exit(0)
```

Both conditions are already true, so this fires immediately: it re-emits the payload and exits 0
**without ever reaching step 6 again**. The promised "completes idempotently" does not happen —
`project_field_set` for `building` is never retried, and the board station is stuck at `ready`
while the agent is actually building.

**Correction to my own first pass, checked against `factory_land.py` before finalizing this
report: this is not permanent.** The agent still received its payload from `_emit`, so it proceeds
to `factory_workspace` (which does not consult the board at all) and eventually `factory_land`.
`factory_land.py`'s board read is `_find_item_id` (`:30-36`), which queries `is:open` — **not**
filtered to any station — and its final call unconditionally sets the station to `review`
(`:99`, `factory_gh.project_field_set(..., review_option)`). So the item's station is wrong for the
duration of the build and self-corrects the moment `land` runs. The board lies to the operator
while the build is in flight, but it does not lie forever, and there is no accumulation. That
asymmetry — Finding 1's item never re-enters the pipeline at all; Finding 2's item does, just late
— is why Finding 1 is `high`/`must_fix` and this one is `med`/should_fix. (Permanently stuck is
still possible if the agent dies before landing — that is D-13's already-accepted residual, not a
new one.)

**What is still worth a ruling, independent of severity:** T-05's decided text says the
`--issue`-mode recovery "completes idempotently," and the code plus its own test
(`test-factory-claim.py:467-476`, R4, asserts only "self-owned re-entry never calls create_ref,"
never that `project_field_set` is retried) agree with each other and both disagree with the plan
text. That is a `mismatch` (D-05/T-05) the operator should resolve either by fixing the text or by
making the self-ownership branch redo step 6's bookkeeping.

---

## The four dispatch questions, answered directly

**(a) Uncached lookup cost.** One extra `gh project view` call per `project_field_set` invocation;
inside `factory_decompose.py`'s step-7 loop that is +1 remote call per new/partial task, i.e. an
N-task publish costs N more calls than before the S1 fix (matches the disclosure already in
STATE.md: "3N board calls... where it made 2N" — not re-raised as new). At the task counts this
increment actually has (single digits to low tens per feature), that is cheap in absolute terms.
Caching would need an explicit invalidation story for a value (project number → node id) that is
effectively immutable for the project's lifetime — plausible, but the S1 receipt's stated reasons
for not caching (parity with the already-uncached `_field_list` call, no side effects on import,
no license from the caller-local `id_cache` precedent) are reasonable. **Judgment: uncached is the
right call; this is not where the real cost is.** The real cost is Finding 1 — more calls per loop
iteration means more places the loop can die, and the ledger was never built to survive a death at
this particular boundary.

**(b) Mid-loop failure.** Answered in full above (Finding 1). Publish does **not** resume cleanly:
the ledger recovers everything except whether the station-set half of step 7 completed, and that
half is not idempotent-on-retry across the crash boundary — not because the underlying `gh` call
isn't idempotent, but because nothing in the ledger ever asks it to run again, and (unlike claim's
equivalent gap) nothing downstream ever revisits the item either.

**(c) Raise-never-fall-back on a failed `project view` lookup.** Correct on the merits. A fallback
to `str(number)` would silently resurrect the exact bug the S1 fix exists to close (`--project-id`
with the bare board number 422s). D-02's "the control plane fails loudly" is exactly the right
instinct here, and the S1 receipt's own miss-test (asserting zero `item-edit` calls on a `project
view` failure) is the right shape of test. No finding.

**(d) The new refusal guard (`factory_decompose.py:288-293`).** Placement is correct — after the
plan-signature check, before `factory_gh.preflight()`, so a plan with no usable `feature` costs
zero remote calls (verified by the S2 receipt's `rec.calls == []` assertion and by reading the
diff: `preflight()` is the next line after the guard). Predicate (`not isinstance(feat_id, str) or
not feat_id.strip()`) correctly refuses `None`, `""`, and whitespace-only, and is tested against
all three (`test-factory-decompose.py`, S2 fixtures). **What it does not catch:** a feature id with
internal whitespace (e.g. `"FEAT 10"`) passes `.strip()` truthiness and would still reach
`f"feature:{feat_id}"`, producing a label with an embedded space — untested, low-severity, not
required by any REQ/SC. Not a finding worth blocking on.

---

## INV-24 (`check-state.sh`) — read-only review, per the dispatch's explicit permission

Pin: `check-state.sh:858-908` (the DEC-186 block).

**Process note the operator should see, unrelated to correctness of the invariant itself.** The
pinned SHA `8bbb246` is not reachable from `main` — it lives only on branch
`wip-omp-and-feat10-mixed`. `main` carries a different commit, `28302a6`, with the identical
message but a rewritten tree; at `28302a6`, `check-state.sh` differs from the pinned version by
roughly 150 lines in its root-resolution block (confirmed: `git diff 8bbb246 -- check-state.sh`
against the current tree shows the "omp port" root-resolution code present at the pin but absent
at `HEAD`). My line citations below (`:858-908`) are correct for the pinned bytes I was asked to
review, but they will not match the file at the path the operator would actually edit on `main`
today. Flagged as a non-blocking open question, not a finding against the diff itself.

**Verified the "already a violation elsewhere" claim at `:872-873`(`except harness_yaml.YamlParseError:
continue`).** True. An earlier, unconditional loop over the same `H/features/*/feature.yaml` glob
(`:201-224`, the INV-6..8 section, which runs before INV-24 in the same script) already
`bad.append()`s on exactly this parse failure ("...does not parse, so INV-6..8 and INV-12 cannot be
checked for it"). INV-24's `continue` does not fail open — the file is caught upstream in the same
run. No finding.

**Finding 3 (should_fix, medium) — a feature whose own `parent` collides with one of its own task
issues is silently permitted.** `:892-908`. `_fac_pairs` is keyed `(repo, str(n))` and compared
with `_fac_pairs[key] != feat` — so when the same feature's own `nums` list (its task issues plus
its parent, appended in the same loop) produces a repeated key, the second occurrence's `feat`
equals the first's and the `!=` test never fires. The invariant's own stated purpose — "comparing
parents and issues in one list is the only place in this increment [D-12's container collision]
becomes visible" — describes exactly this shape of hazard (a container issue also recorded as a
task), yet the comparison as written can only ever fire across two *different* `feat` values. A bug
that records the same issue number as both `parent` and a task entry within one feature's own
`factory` block sails through with no violation reported. This is not INV-24 failing its stated
job against two features — its header and its violation message both scope it to a two-feature
collision, and it does that correctly — it is that a *within-feature* repeat is uncovered by any
invariant at all. **Zero test coverage either way** — `test-check-state.py` case `case_s()`
(`:822-874`) has 8 cases, all cross-feature; none exercises a single feature whose `nums` list
repeats a value. Given the dispatch's own framing ("intended or a gap?"), I read this as a gap: the
docstring makes no such carve-out, and the implementation's exclusion of the same-feature case
looks like an accident of the dict-overwrite idiom, not a decision. Not `must_fix` — it requires a
second bug (mis-recording a parent as a task issue) to become live, and the consequence is a missed
detection in an advisory invariant, not board-state corruption in its own right.

**Finding 4 (info, low) — a `None`-valued issue entry can produce a false-positive cross-feature
collision.** `:895-896`, `nums.extend(issues.values())` with no type/None filtering (contrast
`factory_decompose.py`'s `load_factory`, which only ever admits `int` values into `issues`). A
hand-edited or externally-written `feature.yaml` carrying `issues: {T-01: null}` in two unrelated
features for the same repo would key both to `(repo, "None")` and report a spurious "both record
issue None" collision. Low probability — the factory's own writer never produces a `None` value —
and the failure direction is noisy-false-positive rather than fail-open, so it costs operator time
rather than hiding a real defect. No test exercises it either way.

---

## Other modules (factory_cli.py, factory_config.py, factory_workspace.py, factory_land.py, tests)

Read all five plus their test files. Nothing new rises to `must_fix`. Three items land on
**panel-validator**'s earlier F-ids (`runs/panel-validator/digest.md`, read only to check after
landing on these independently) and are carried, not re-argued:

- **F3** (C-3 exception-class-name leak) — confirmed still present: none of the five `expected=`
  tuples (`factory_config.py:185`, `factory_claim.py:337`, `factory_decompose.py:440`,
  `factory_land.py:106`, `factory_workspace.py:140`) include `harness_yaml.YamlParseError`, so a
  malformed `fleet.yaml`/`plan.yaml` still surfaces as `unexpected failure: YamlParseError: ...`
  rather than the canonical grammar. Fails closed (exit 2, no mutation) — carried at its earlier
  `med` rating, not re-escalated.
- **F7** (`factory_config.py --show` with no flag) — confirmed still present: `_main()` with no
  `--show` returns without writing anything to stdout, exit 0. Carried at `low`.
- The dead assertion at `test-factory-integration.py:691-692` and the publish/claim path
  asymmetry (`factory_claim.py:43` vs. publish's any-path acceptance) are both on the dispatch's
  pre-known list (items 3 and 4) — noted, not re-raised.

`factory_workspace.py`'s `RuntimeError` (uncaught by any `expected` tuple, same as F3's shape) is
**not** a new instance of F3: it goes through `run()`'s `except BaseException` branch, whose
"unexpected failure: {type}" format is deliberately built to name the exception type — that branch
exists specifically for the unrecognised case, unlike `message()`/`fail()`, which the docstring
forbids from taking an exception class as `value`. No finding.

`factory_gh.py` itself (T-03's original module, apart from the S1 patch) matches its spec cleanly:
`GhError` construction, `run_gh`'s fail-loud contract, `create_ref`'s narrow 422-and-already-exists
discrimination, and `project_items`' truncation guard were all read against T-03's intent text and
found faithful, with concrete `file:line` matches. No stage-1 scope creep found anywhere in the two
priority files — every change traces to D-14/T-03/T-04 (S1) or T-04's own feature-key handling (S2).

## Stage 1 (spec compliance) — summary

No scope creep found in the reviewed surface. The two omissions/mismatches found are Findings 1
and 2 above: neither `factory_decompose.py` nor `factory_claim.py` actually delivers the
resumability D-14 and T-05's own text promise, specifically for the station-set half of their
respective two-call sequences — though Finding 2's consequence is bounded by `factory_land.py`'s
unconditional station overwrite and Finding 1's is not. Everything else read (label vocabulary,
edge pass ordering, C-3 exit codes, the S2 feature-key guard) matches its plan text with `file:line`
citations given inline above.
