# Goal-check cycle 2 — BUG-1304 — twelve criteria at review_sha `c5869301`

**ALL TWELVE MET.** The two cycle-1 gaps are closed: SC-05's stderr clause is now asserted on both
routes with the HELD-WORKTREE path as the needle, and SC-07's plan half now answers all five boundary
questions by decision id. The ten previously met were re-graded from scratch at this sha — no verdict
carried forward — and none was weakened by the four ABC splits.

**Scope answer for the ship record: BRIEF.md at `c5869301` carries ZERO `verify: uat` criteria**
(method tally `11 automated/integration + 1 inspection + 0 uat`; the token `uat` does not occur).
`gates.uat: blocking_when_uat_criteria_exist` is therefore satisfied **VACUOUSLY**, not by execution.

**Frozen-guard provenance re-verified at this sha, not assumed:** both fixtures are byte-identical to
the pre-change guards — `diff <(git show c5869301:tests/integration/fixtures/prior-check-domain.sh.fixture)
<(git show a4e8ecf7:.claude/skills/harness/bin/check-domain.sh)` = 0 lines; same for `bash-write-guard`.
Suites re-run at this tree: `test-check-domain.py` exit 0, 0 `^FAIL`, 28/28 `[bug1304]` PASS;
`test-bash-write-guard.py` exit 0, 0 `^FAIL`, 39/39 `[bug1304]` PASS; `test-inflight-registry.py` 147/147.
Both `run_bug1304_claim_set()` returns are summed into the runner total (`test-check-domain.py:4711`,
`test-bash-write-guard.py:1323`), so a case failing would redden the suite. **No row below rests on an
exit code.**

| SC | verdict | method | evidence at `c5869301` |
|---|---|---|---|
| SC-01 | met | automated/integration | `test-check-domain.py:4486-4488` — refuse loop fires the relative-main case with `want=2` and `contains=first`, the held worktree's absolute path; the refusal text is built at `harness_boundary.py:299-311` and printed to stderr at `check-domain.sh:811-816` |
| SC-02 | met | automated/integration | `test-bash-write-guard.py:1045-1046` (redirect) and `:1047-1048` (in-place `sed`), separate tuple entries driven through `:1052-1053` with `want=2`, `contains=first` |
| SC-03 | met | automated/integration | absolute case `test-check-domain.py:4483` / `test-bash-write-guard.py:1049`, same loop and same assertion as the relative case; one message builder serves both routes (`harness_boundary.claim_set_refusal:287`, called at `check-domain.sh:813` and `bash-write-guard.sh:766`) |
| SC-04 | met | automated/integration | five separate allow assertions: `test-check-domain.py:4492-4494`, `:4495-4497`, `:4503-4505`, `:4507-4508`, `:4519-4521`. Fifth is DISCRIMINATING — the claim is written into the owner-root registry (`:4517-4518`) and adding `FEAT-1304-C-linked` to that SAME registry flips the same destination to exit 2 (`:4522-4526`), so the registry is proven scanned; the allow is `worktree_for_feature` returning None (`harness_boundary.py:233-234`). Bash twin `test-bash-write-guard.py:1058-1063, :1069-1076, :1088-1096` |
| SC-05 | met | automated/integration | **pointer case, held worktree named:** `test-check-domain.py:4545-4548` and `test-bash-write-guard.py:1119-1122` both pass `contains=context["first"]` — the concrete absolute path `<root>/.claude/worktrees/FEAT-1304-A`, which the destination string (`.../worktrees/broken/...`) does NOT contain, so the needle can only match the `holds worktree claim(s): {held}` clause. **ambiguous case, candidates named, separate fixture:** `test-check-domain.py:4562-4564` and `test-bash-write-guard.py:1138-1140`, `contains="FEAT, FEAT-X"`, the sorted basenames the resolver raised on (`harness_boundary.py:237-241`) |
| SC-06 | met | automated/integration | **helper bodies read, not call counts:** `test-check-domain.py:4429-4443` — marker set `:4434-4435`, positive control fired at the SAME frozen hook in the same isolated bin tree `:4436-4437`, conjunction `allow==0 and quiet and control==2` at `:4440`; `test-bash-write-guard.py:986-1001` — same three, conjunction `:995-998`. **RUNTIME assertion count measured from the suites' own output: 10 (check-domain) and 12 (bash-write-guard)** — one `is allowed by the frozen pre-change …` PASS line per call, all PASS. T-03/T-05's `-ge 10`/`-ge 12` greps are a STALE TEXTUAL PROXY (`bug1304_assert_pre_change_allows(` now occurs 9 and 10 times = 1 def + 8/9 call sites); the splits hoisted calls into shared helpers invoked more than once. Not graded on the grep |
| SC-07 | met | inspection | **plan half (`git show c5869301:….harness/harness/features/BUG-1304-worktree-relative-path-guard/plan.yaml`, entries read whole, never greped):** who is bound → D-01 `:455` (empty S unbound and allowed, non-empty binds); destination not spelling → D-01 `:455` ("its RESOLVED destination"); unresolvable assignment → D-01 `:455` (otherwise exit 2 naming S and the proper home) AND D-02 `:460` (no-worktree claim contributes nothing; **new clause** — an AMBIGUOUS claim is "neither guessed into S nor dropped", both routes exit 2 naming the candidates); preserved traffic → D-05 `:475` (Expertise carve-out stated BY ROUTE) with D-06 `:480` (DEC-189 second base left unbound); **both routes refuse identically → D-08 `:490`, and YES, the new clause now carries the question the criterion assigns it** — "the refusal semantics the two edits install are IDENTICAL: both routes evaluate the same claim-set predicate from the shared harness_boundary seam and refuse with the same exit 2 and the same claim_set_refusal text, with no route-local additions", which is exactly the cycle-1 reservation that D-08 spoke only to edit asymmetry. **DECISIONS.md half:** DEC-218 `git show c5869301:.harness/harness/docs/DECISIONS.md:6844` states all five in one place — bound/unbound `:6846-6852`, destination-decides `:6854-6855`, unresolvable-or-ambiguous refuses `:6858-6859`, preserved traffic + Expertise route `:6859-6862`, both routes exit 2 `:6850-6852`; index row `DECISIONS-INDEX.md:218` anchored `@6844`, matching the header line |
| SC-08 | met | automated/integration | `test-check-domain.py:4569-4581` — worktree basename `BUG-1304` (`:4572-4573`), claim `feature` the long id (`:4575-4577`), exit 2 (`:4577-4579`); Bash twin `test-bash-write-guard.py:1147-1161`; pre-change proof `:4580-4581` / `:1160-1161` |
| SC-09 | met | automated/integration | `test-check-domain.py:4586-4588` and `test-bash-write-guard.py:1212-1214` back-date `started_at` to `now - CLAIM_TTL_SECONDS - 5` in the STORED JSON — no clock mocked; both routes then refuse with `contains=first` (`:4591-4594`, `:1218-1220`) and both carry the full SC-06 proof (`:4595-4596`, `:1221-1223`). Compatibility runtime holds by construction: the fixture claims go through `inflight_registry.claim()`, whose `runtime` defaults to `"claude"` |
| SC-10 | met | automated/integration | `test-check-domain.py:4610-4612` (exit 2, `contains=registry`, the corrupt file's own path), paired WELL-FORMED control exit 0 `:4616-4619`, pre-change proof `:4613-4614`; Bash `test-bash-write-guard.py:1236-1238`, control `:1244-1247`, pre-change `:1241-1242`. Unreadability is raised rather than swallowed: `harness_boundary.py:276-284` re-raises `UnreadableRegistry` only after the inside-a-proven-member check |
| SC-11 | met | automated/integration | retention `test-inflight-registry.py:1176-1216`: reconcile `removed == 1` + record kept (`:1185-1188`), `live_children == []` + record kept (`:1194-1197`), `orphan_write is False` + record kept (`:1203-1206`), backstop record still pruned (`:1213-1216`). **Dispatch half asserted SEPARATELY and BY BEHAVIOUR:** `case_bug1304_retention_admission` `:1219-1242` — with the dispatch-expired claim retained on disk, a fresh `claim_with_receipt` for the SAME agent and SAME feature is ADMITTED (`:1229-1234`), both records remain (`:1234-1235`), and `live_claim` still exposes only the fresh one (`:1236-1242`). `now` injected as a literal; all 11 cases PASS in the 147/147 run |
| SC-12 | met | automated/integration | ONE fixture, BOTH routes, BOTH directions: allow half `test-check-domain.py:4635-4638` / `test-bash-write-guard.py:1260-1262`; refusal half naming the corrupt registry `:4639-4641` / `:1264-1266`; refusal half carries the full SC-06 pre-change proof `:4642-4643` / `:1269-1270`. Disjoint from SC-10's fixture (own + corrupt worktrees built fresh, `:4622-4634` / `:1250-1259`). Scoping is structural, not incidental: `harness_boundary.claim_worktrees` returns the proven set BEFORE raising when the destination is already inside a member (`harness_boundary.py:280-284`) |

REQ coverage: REQ-01..REQ-06 trace to shipped code (`harness_boundary.claim_worktrees:264` /
`_registry_claim_worktrees:252` / `claim_set_refusal:287`, `check-domain.sh:770-816`,
`bash-write-guard.sh:734-766`, `inflight_registry.live_claims`). REQ-07 — the cycle-1 gap — is now
covered on both halves: DEC-218 with its index row, and plan D-01/D-02/D-05/D-06/D-08.

## What the splits could have damaged, and did not

`claim_worktrees` split (`_registry_claim_worktrees:252`) keeps the return-before-raise ordering SC-12
depends on. The three test mega-function splits moved calls into shared helpers but changed no
assertion: every refuse case still passes its `contains` needle, and the pre-change helper's
three-part conjunction (`:4440` / `:995-998`) is intact. `deny_bare` (`bash-write-guard.sh:655`) drops
only the Write-tool advice sentence and still exits 2; it is used at the three claim refusal sites
(`:744`, `:749`, `:766`) and nowhere else, and the Expertise case pins the omission
(`test-bash-write-guard.py:1181-1182`).

## Open questions

- Q1 (non-blocking, carried from cycle-1 Q2, graded not deferred): SC-05's clause "the stderr names
  the worktrees the agent holds" is unreachable in the ambiguous case — that branch raises before S is
  built, so the message names candidates only (`check-domain.sh:779-784`,
  `bash-write-guard.sh:743-744`). Graded per-clause: held-worktree naming in the pointer case,
  candidate naming in the ambiguous case, which is what the criterion assigns each. No remedy needed.
- Q2 (non-blocking, record hygiene): T-03's and T-05's `verify:` blocks grep
  `bug1304_assert_pre_change_allows(` for `-ge 10` / `-ge 12`; the textual counts are now 9 and 10
  (1 def + 8/9 call sites), so those blocks read red on a benign refactor. The runtime counts are
  unchanged at 10 and 12. The bound is a stale textual proxy in an approved plan — pm cannot amend it
  here (read-only dispatch, and amending an approved plan is the main session's). Lane: record.
