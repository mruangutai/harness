# Code review — BUG-124-run-dir-squad-suffix — cycle 4 — review_sha 6c037de4

## VERDICT: PASS

Stage 1 (spec compliance) passes clean across all six REQs and nine SCs. Stage 2 finds one real,
currently-latent fail-open defect in the new vocabulary derivation (Q6) that I rule **should_fix, not
gating** — no live trigger exists in `team-config.yaml` today, the fix is a one-line filter, and it
doesn't compromise any REQ/SC as specified. One grade-2 Python function (med, non-blocking per the
grading rule). Nothing else found rises above info.

## Stage 1 — spec compliance

Diffed `git diff 80ce35d1..6c037de4 -- <the four files>` directly; read `harness_boundary.py`,
`dispatch-guard.sh`, both test diffs in full (not truncated), `BRIEF.md`, `plan.yaml` T-01/T-02
intents, and both T-02 receipts (`receipt-harness-backend-dev-T-02-c1.md`,
`...-T-02-c2.md`) at the pinned sha.

| REQ | Verdict | Evidence |
|---|---|---|
| REQ-01 (refused before dispatch runs) | PASS | `dispatch-guard.sh` — the check block sits strictly between the `harness_boundary`/`inflight_registry` import and `_root_for`/checkout-resolution/claim; no state write happens between the import and the check (read myself: lines 94–186). Matches D-04. |
| REQ-02 (names slug + compliant form) | PASS | refusal prints `slug %r` and `hb.run_dir_forms(globs)`; integration case 18a/18b. |
| REQ-03 (compliant/no-ref prompts unaffected) | PASS | case_19 (t01-eng, plan-product, dated slug), case_20 (no run-dir ref at all). |
| REQ-04 (vocabulary derived, no second edit) | PASS | `run_dir_grant_globs` walks generically (any list of path-carrying dicts, not just `leads:`); case_22 proves an invented squad is recognized both directions with zero code change. |
| REQ-05 (fails open, reason on stderr) | PASS | case_21 (grant-less manifest), case_23 (unparseable manifest) — both skip, both state a reason. |
| REQ-06 (paste-safe) | PASS | D-05 `[.]harness/` anchor rewrite (`tail.replace(".harness/", "[.]harness/")`); case_18h round-trips the exact captured stderr through a second dispatch and asserts it is not refused. |

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | PASS | plan T-02 `verify:` reproduced verbatim in receipt-c1, ran to exit 0, `grep -q "eng-t01"` matched. |
| SC-02 | PASS | case_18b: `<task-or-purpose>-eng` present in stderr. |
| SC-03 | PASS | case_19/20 plus receipt: "48 original checks across cases 1-17 unedited and passing" — confirmed against the diff, which only appends `case_18`…`case_23` and never touches an existing case body. |
| SC-04 | PASS | case_22, synthetic `oddsquad` squad. |
| SC-05 | PASS | case_21. |
| SC-06 (verify: inspection) | **PASS, and unusually well-evidenced** | Both T-02 receipts. c1's RED PROOF ran the new suite against the pinned pre-change `dispatch-guard.sh` fetched via `git show 6d969ed3:...`, md5-verified (`ca904b2906ad8d44662db428cb2dbc89`) against the T-01-landed state, and reported the exact 8 FAIL lines covering cases (a)(b)(f)(g) as the plan required, plus two extra text-assertion FAILs in (e)/(i) explained correctly (old file never prints a SKIPPED line at all). c1 additionally ran **two hand-applied mutations** — deleting the D-05 anchor rewrite (only case-18h's two paste-back assertions redden) and collapsing the two SKIPPED texts into one generic line (only case-21/23's text assertions redden) — each restored and re-verified green after. c2 re-ran the same red proof after the launch-line SIMPLIFY, re-confirming md5-identity of the pre-change binary and the same 8 FAIL lines. This is exactly the "recorded command and output demonstrate FAIL against the pre-change guard" bar, not a bare assertion that it was done. |
| SC-07 | PASS | case_18g: `_claims_for(data, "harness-eng-lead") == []` after refusal. |
| SC-08 | PASS | case_18h, and c1's mutation proof shows deleting the anchor rewrite reddens exactly this case and no other. |
| SC-09 | PASS | case_21/23 each assert their own text present AND the other's text absent; c1's mutation proof (collapsing the two lines into one) reddens exactly this pair and nothing else, confirming the messages are not interchangeable in practice, not just in prose. |

No scope creep found: every changed line in all four files traces to T-01 or T-02. No omission found
against REQ-01..06 or D-01..D-05.

## Stage 2 — code quality

### Q6 — `run_dir_grant_globs` fail-open on a future read-only `/runs/` grant — **ruling: real defect, MED, should_fix, not gating**

Confirmed by comparison: `harness_yaml.manifest_domains` (the sibling walker used by
`check-domain.sh`, `harness_yaml.py:392-420`) filters `not entry.get("read")` before treating an
entry as a write grant. `run_dir_grant_globs` (`harness_boundary.py:816-848`) walks the identical
shape — "any list whose members are all mappings carrying a `path` key" — and collects every entry
whose pattern contains `/runs/` **with no `read` filter at all**. The function's own docstring
claims "Every **write-grant** glob… whose pattern text contains `/runs/`" — that promise is false as
written.

**Concrete failure scenario.** If a future manifest edit adds, e.g., a validator/auditor role that
needs read-only visibility into every squad's run digests —
`{ path: .harness/*/features/*/runs/*/**, read: true }` — `run_dir_grant_globs` would fold that glob
into the vocabulary. `run_dir_forms` would print a spurious `<task-or-purpose>-*` compliant form (it
already special-cases a bare `*` segment, so this specific pattern is actually skipped by
`run_dir_forms` — but `run_dir_slug_ok` has no such guard: `matches()` would accept **any** slug
against `*/**`, so `run_dir_slug_ok` returns `True` for every ref). The result: the entire REQ-01
refusal silently stops firing for every dispatch, with **no stderr line at all** — worse than the
documented REQ-05 skip, because the guard looks like it ran normally (exit 0, no SKIPPED message,
since `globs` is non-empty). Whoever adds that grant would have no reason to expect it defeats a
dispatch-time guard three files away.

I checked whether this is live today: verified against `.harness/team-config.yaml` — the only three
`/runs/`-containing patterns (lines 306, 315, 324) carry `upsert: true`, none carry `read: true`. So
**no manifest edit exists today that triggers it** — this is latent, not live, which is why I rule it
MED ("wrong behaviour in an unlikely case") rather than high, and **should_fix rather than must_fix**:
it doesn't affect any REQ/SC as currently specified, and the fix is a trivial, low-risk one-line
addition (`and not item.get("read")` beside the existing `"path" in item` check) with an obvious,
already-in-repo precedent to copy. Zero test in either new suite exercises a `read`-flagged `/runs/`
grant — this whole class is untested. I read this as a valid basis to keep B-1 as backlog rather than
gate, but the backlog item should be framed with this exact scenario, not left as an abstract "future
grant" note — the lead's disposition is correct in outcome, and I record the concrete trigger here so
it isn't re-litigated as vague next time.

### Fail-open site (b): the outer `except Exception` around the run-dir check block

No live trigger found. Every call inside the guarded block operates on typed, already-validated
inputs: `hb.run_dir_refs(prompt)` is a linear regex scan with no nested quantifiers (no ReDoS route);
`hb.run_dir_slug_ok`/`hb.run_dir_forms` operate on `globs`, a list of `str()`-coerced values built by
`run_dir_grant_globs` itself; and `matches()`/`glob_to_re()` build regexes via `re.escape()` on every
literal character, so a malformed glob string can never raise a compile error (checked
`harness_boundary.py:315-337`). I could not construct an input — malicious prompt or malformed
manifest content — that reaches this `except` while a genuine positive finding was computed but
un-reported. This `except` is currently pure defense-in-depth, consistent with DEC-100. No finding.

### Fail-open sites (c): `HARNESS_RUN_DIR_DERIVED == "0"` vs. derivation-failed SKIP branches

Correctly implemented and the strongest-evidenced part of this diff (SC-09 above): distinguished by
text, tested by both cases and by hand-applied mutation in the c1 receipt. No additional silent
swallow beyond the documented REQ-05 fail-open design. No finding.

### SIMPLIFY nest-collapse correctness (commit `64924e19`)

Ruled on correctness only, per the ALREADY-SETTLED list. Traced all three input classes by hand
against the current code (`dispatch-guard.sh:150-186`):
- `refs` empty → outer `if refs:` is false, block is a no-op — matches the original
  `if refs and not globs` / `elif refs and globs` (both require `refs` truthy; empty `refs` satisfies
  neither).
- `refs` non-empty, `globs` empty → falls into `if not globs:` → SKIPPED message, no exit — matches
  original `if refs and not globs`.
- `refs` non-empty, `globs` non-empty → falls into `else:` → computes `bad`, refuses on non-empty —
  matches original `elif refs and globs`.

Behaviour-identical on every input class. No finding.

### Code grading

`python3 .claude/skills/harness/bin/code-grade.py --base 6d969ed375f8458e32c47502ecdcc85bb9916635 --head 6c037de4`
(base = `git merge-base origin/main 6c037de4`, matches the pin). 19 functions graded, 1 gated FAIL:

- **`run_dir_grant_globs.walk`** (`harness_boundary.py:833`) — cyclomatic 11, cognitive 22, ABC 15.1,
  driver cyclomatic+cognitive, bar 4, grade 2. **MED, non-blocking (grade 2 never fails the build).**
  Reason required, my written answer: `walk` combines four responsibilities in one nested closure —
  dict/list dispatch, recursive YAML-tree traversal, grant-list shape classification (the
  `all(isinstance(item, dict) and "path" in item for item in node)` generator), and glob collection.
  The cognitive cost is driven by the nested `if`/`elif`/generator-inside-`if`, not any single
  runaway branch. Extracting the shape check into a named `_is_grant_list(node)` predicate (the
  "name a compound condition" pattern) and the collection loop into its own helper (the "give one
  loop to one function" pattern) would likely restore grade 4+. Not blocking this ship — but this is
  now permanent, shared, security-relevant code in `harness_boundary.py`, so it's worth doing before
  more logic accretes onto it rather than being left as a standing grade-2 exception.

No grade-1 or below-bar-grade-3 function found. `code_grade: grade_2`.

## Open questions

None — Q6 is answered above with a firm ruling, not deferred.
