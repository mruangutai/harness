# Goal-check — BUG-1304 — twelve criteria at review_sha `af5ddd7a`

**Ten of twelve met. Two unmet, neither a behaviour defect: SC-05 is a TEST-only gap (one clause
unasserted on both routes), SC-07 is a RECORD gap (one clause absent from plan.yaml D-02).** The
enforcement behaviour the brief asks for is present and discriminating everywhere I could reach it.
All three suites run green at this tree (`test-check-domain.py` 0 FAIL lines; `test-bash-write-guard.py`
38/38 `[bug1304]` PASS, 0 FAIL; `test-inflight-registry.py` 11/11 bug1304 cases PASS) — cited per row,
never as a substitute for a row.

**Scope answer the ship decision needs: BRIEF.md at `af5ddd7a` contains NO `verify: uat` criterion.**
Read end to end; the method tally is `11 automated / 1 inspection / 0 uat`, and the string `uat` does
not occur in the file at all. `gates.uat: blocking_when_uat_criteria_exist` therefore **does not apply**.

**Frozen-guard provenance verified, not assumed:** both fixtures are byte-identical to the pre-change
guards — `diff <(git show af5ddd7a:tests/integration/fixtures/prior-check-domain.sh.fixture) <(git show
a4e8ecf7:.claude/skills/harness/bin/check-domain.sh)` = 0 lines; same for `bash-write-guard`.

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | automated/integration | `test-check-domain.py:4474` — exit 2, `contains=first` proves stderr names the assigned worktree |
| SC-02 | met | automated/integration | `test-bash-write-guard.py:1043` (redirect) and `:1047` (in-place `sed`), each own case, exit 2 with `contains=first` |
| SC-03 | met | automated/integration | Write/Edit `test-check-domain.py:4476`; Bash `test-bash-write-guard.py:1051`; both routes reach one message builder, `harness_boundary.py:302` |
| SC-04 | met | automated/integration | five separate allow assertions: `test-check-domain.py:4483`, `:4485`, `:4489-4491`, `:4492-4493`, `:4503-4505`. Fifth is discriminating — claim sits in the owner-root registry, and adding `FEAT-1304-C-linked` to that SAME registry flips it to exit 2 (`:4506-4511`), proving the main-checkout registry IS scanned (`harness_boundary.py:260`); the allow is `worktree_for_feature` returning None (`:268-270`). Bash twin `test-bash-write-guard.py:1079-1092` |
| SC-05 | **not_met** | automated/integration | exit-2 halves all present — pointer `test-check-domain.py:4525`, `test-bash-write-guard.py:1106`; ambiguous `test-check-domain.py:4543` and `test-bash-write-guard.py:1122` both assert `"FEAT, FEAT-X"`. **Gap: the malformed-pointer case asserts only the exit code** — no `contains`, so "the stderr names the worktrees the agent holds" is unproven on either route |
| SC-06 | met | automated/integration | helper bodies read, not just call sites: `test-check-domain.py:4429-4443` (marker check `:4434-4435`, positive control `:4436-4437`, conjunction `:4440`) and `test-bash-write-guard.py:986-1001` (`:996-998`). Applied to every SC-01/02/03/05 case: `4475, 4477, 4481, 4527, 4546` and `1044, 1048, 1052, 1056, 1108, 1127`. No pre-change assertion carries the exit code alone |
| SC-07 | **not_met** | inspection | DECISIONS.md half MET — DEC-218 states all five in one place: bound `git show af5ddd7a:.harness/harness/docs/DECISIONS.md:6849-6851`, destination-not-spelling `:6854-6855`, both routes `:6851`, preserved traffic `:6859-6862`, unresolvable/ambiguous `:6858-6859`; index row `DECISIONS-INDEX.md:218` with anchor `@6844` matching the header line. **plan.yaml half FAILS**: `git show af5ddd7a:...plan.yaml` D-01 `:455`, D-02 `:460`, D-05 `:475`, D-06 `:480`, D-08 `:489-491` answer four questions, but **how a claim resolving AMBIGUOUSLY is treated is absent from D-02 — the token `ambiguous` occurs nowhere in the whole `decisions:` block (453-687); every occurrence (781, 882, 929, 1139, 1149, 1386, 1536) is inside a task** |
| SC-08 | met | automated/integration | `test-check-domain.py:4549-4557` — worktree basename `BUG-1304` (`:4551`), claim `feature` the long id (`:4554`), exit 2 (`:4555-4557`); Bash twin `test-bash-write-guard.py:1130-1139`; pre-change proof `:4558` / `:1142` |
| SC-09 | met | automated/integration | `test-check-domain.py:4560-4567` and `test-bash-write-guard.py:1174-1182` back-date `started_at` by `CLAIM_TTL_SECONDS + 5` in stored JSON — no clock mocked. Compatibility-host runtime holds by construction: `inflight_registry.claim()` defaults `runtime="claude"` (`git show af5ddd7a:.claude/skills/harness/bin/inflight_registry.py:487-488`). Both routes refuse; both carry the full SC-06 proof (`:4567`, `:1181`) |
| SC-10 | met | automated/integration | `test-check-domain.py:4581-4583` (exit 2 naming the file), paired well-formed control exit 0 `:4587-4590`, pre-change proof `:4584`; Bash `test-bash-write-guard.py:1195-1207` (`:1200` pre-change). Unreadability is raised, not swallowed: `harness_boundary.py:264-276`, `test-inflight-registry.py:1142-1165` (case 37) |
| SC-11 | met | automated/integration | retention `test-inflight-registry.py:1176-1216` — reconcile `removed == 1` + record kept (`:1185-1188`), `live_children == []` + record kept (`:1194-1197`), `orphan_write is False` + record kept (`:1203-1206`), backstop record still pruned (`:1215-1216`). Dispatch half asserted SEPARATELY and by behaviour: `case_bug1304_retention_admission` `:1219-1242` — retained expired claim on disk, fresh `claim_with_receipt` ADMITTED (`:1232`), both records remain (`:1234`), dispatch answer still shows one (`:1238`). `now` injected as a literal, `started_at` stored; no clock mocked |
| SC-12 | met | automated/integration | one fixture, both routes, both directions: allow half `test-check-domain.py:4603-4606` / `test-bash-write-guard.py:1216-1219`; refusal half naming the corrupt registry `:4607-4611` / `:1220-1225`; refusal half carries the SC-06 proof `:4612` / `:1228`. Disjoint from SC-10's fixture (`:4592-4602` / `:1209-1215`). Scoping is structural: `harness_boundary.py:273-276` returns before raising when the destination is already inside a proven member |

REQ coverage: REQ-01..REQ-06 trace to shipped code (`harness_boundary.claim_worktrees`/`claim_set_refusal`,
`check-domain.sh:770-816`, `bash-write-guard.sh:737-761`, `inflight_registry.live_claims`). REQ-07 is the
one carrying the SC-07 gap — its DECISIONS.md half landed (DEC-218 + index row); its plan `D-NN` half is
short one clause.

## The two unmet criteria — routing

- **SC-05 — unproven, not wrong. Remedy is TEST.** `claim_set_refusal` always emits
  `"<agent> holds worktree claim(s): <held>."` on the non-unreadable branch (`harness_boundary.py:291,
  302`), and the malformed-pointer destination reaches exactly that branch (`check-domain.sh:807-816`,
  `bash-write-guard.sh:757-761`), so the message is correct — only the assertion is missing. Fix is one
  argument on each of two existing calls: `contains` on `test-check-domain.py:4525` (T-03's file set) and
  on `test-bash-write-guard.py:1106` (T-05's file set). Both files are `execution_mode:
  main-session-direct` under DEC-174.
- **SC-07 — unproven and unwritten, not wrong. Remedy is RECORD.** The ambiguous-claim treatment is
  implemented (`check-domain.sh:779-784`, `bash-write-guard.sh:738-742`), tested (SC-05 ambiguous
  assertions) and doctrinally recorded (DEC-218 `:6858-6859`); it is simply not in the plan decision
  SC-07 names. Fix is one clause added to D-02's `choice`. **No task's file set contains `plan.yaml`** —
  it is pm-authored, so this is a main-session/pm record edit, and amending an approved decision's text
  bears on the approval signature. Not a code or test change; criterion is meetable as written.

## Open questions

- Q1 (blocking the ship decision, not the build): SC-07's plan half needs one clause in D-02. Does the
  operator want D-02 amended (which touches an approved decision), or SC-07 graded as-is and shipped
  unmet with DEC-218 carrying the doctrine? Not mine to choose.
- Q2 (non-blocking): SC-05's clause "the stderr names the worktrees the agent holds" is only reachable
  in the pointer case — in the ambiguous case the held set is empty by construction and the message
  names candidates instead. If the two-assertion fix lands, write it against the pointer case only.
