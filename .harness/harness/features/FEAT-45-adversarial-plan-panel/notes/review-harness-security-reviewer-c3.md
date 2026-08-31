# Security review — FEAT-45-adversarial-plan-panel — cycle 3

review_sha `d78f393a7d5addc1cbd2f31628aed18c54983b9a`, scope `main...d78f393` (merge-base `ba338d8`,
71 files, +7931/-152). Working tree confirmed byte-identical to the pin for every file cited below
(`diff <(git show d78f393:<path>) <path>` empty for `validate-digest.py`, `inflight_registry.py`,
`harness_boundary.py`, `harness_yaml.py`).

**VERDICT: PASS.** The central forgery this cycle was built to close — a self-consistent
`artifact:`/`reviewed: plan:<path>` pair naming some OTHER genuinely-pending feature, submitted by an
agent that reviewed nothing — is now REJECTED, demonstrated live at the exact production call shape
(`feature_dir=None`, CLI/`hook_mode` invocation). F2 and F3's guards are also independently confirmed
closed AND confirmed non-regressive on the legitimate case they exist to serve. No must-fix findings.
Two low, non-gating backlog notes below.

## 1. The central forgery (dispatch item 1) — CLOSED, DEMONSTRATED live

Built the exact shape: fixture git repo (`owner`, checked out on `main`), a genuinely pending,
unsigned `FEAT-OTHER` (`plan.yaml: approval.status: pending`, `feature.json: review_sha: none,
branch: feat/other-branch` — a DIFFERENT branch than the checkout). Digest:
```
code_grade: n_a
reviewed: "plan:.harness/harness/features/FEAT-OTHER/plan.yaml"
artifact: .harness/harness/features/FEAT-OTHER/notes/review-harness-code-reviewer-forged.md
```
Ran via `HARNESS_PROJECT_DIR=<owner> python3 validate-digest.py harness-code-reviewer digest.md`
— the real CLI entrypoint, `validate(sys.argv[1], text)`, `feature_dir=None` by default, identical to
what `hook_mode()` falls back to whenever `harness_feature` is absent (the ordinary Claude-Code-only
case, and the ordinary case generally — see §2).

**Result: `RC=1`, `VERDICT: BLOCKED (contract violation)`,**
`"this feature's recorded branch ('feat/other-branch') does not match the current checkout's branch
('main')"`. The forgery fails. Then rewrote `FEAT-OTHER/feature.json` to `branch: main` (the honest
case — the reviewer genuinely is running inside `FEAT-OTHER`'s own checkout) and re-ran the SAME
digest: **`RC=0`, `digest ok`.** F1's fix is additive-only as designed: it rejects the substitution,
accepts the honest binding. DEMONSTRATED, not inferred.

## 2. Is branch corroboration spoofable? (dispatch item 2) — NO, traced to its source

`_branch_corroboration_error`'s `current_branch` comes from `_current_branch_or_none`, which runs
`git -C <root> rev-parse --abbrev-ref HEAD` — `root` is either `_root_or_none()` (feature_dir=None,
the ordinary path exercised in §1) or, for an **installed validator**, walked up from `feature_dir`
after `_hook_feature_dir` resolves it via `inflight_registry.feature_root(owner_root, feature)`,
where `feature = d.get("harness_feature")`.

Traced `harness_feature`'s provenance in `.omp/extensions/harness-hooks.ts` (the only producer):
`currentFeature` is set from `detectHarnessFeature(event.systemPrompt)` at `before_agent_start`
(the dispatcher's OWN system prompt, before the subagent runs at all), or once from the first
`role: "user"` message (`captureFeatureFromMessage`, gated `if (featureCaptured) return`). The
comment at that gate (`harness-hooks.ts:618-624`) states the invariant directly: *"Nothing after it
is an identity source: not this agent's own output."* A second `setFeature` call with a **different**
value throws (`"conflicting Harness feature markers"`) rather than silently overwriting. There is no
code path from the subagent's own returned digest text (`last_assistant_message`, the thing SEC-01
actually governs) into `currentFeature`/`harness_feature`. Combined with `feature_root`'s own input —
`harness_boundary.linked_worktrees(owner_root)`, a real `os.listdir` of `.git/worktrees` — neither
input to corroboration is under the digest-submitting agent's control. DEMONSTRATED BY CODE TRACE
(TypeScript host logic; not independently executable from this Python-side review, but the gating
logic and its comment are unambiguous).

## 3. `inflight_registry.feature_root` failure modes (dispatch item 3) — fails to PRIOR BEHAVIOR, not open

Exercised all three failure shapes directly against `_hook_feature_dir` (module-level monkeypatches,
same technique as the suite's own `check_hook_feature_dir`):

| failure | result |
|---|---|
| declared feature matches no linked worktree | `feature_root` returns `owner_root` (its own coded fallback) → `_hook_feature_dir` returns `owner_root + <artifact path>` — **byte-identical** to what `_resolve_feature_dir(text, None)` computes unaided (verified by direct equality) |
| `harness_feature` absent/falsy | short-circuits to `None` before ever calling the registry |
| `inflight_registry.feature_root` itself raises | caught by `_hook_feature_dir`'s own `try/except Exception`, returns `None` |

All three converge on `feature_dir=None`, which is not "skip the checks" — it is the FULL
`_resolve_feature_dir`/branch-corroboration path from §1, just anchored at the validator's own
`owner_root` instead of a specific linked worktree. That is exactly the behavior that existed
*before* F5, for every caller that already used `feature_dir=None` (the CLI, and `hook_mode` whenever
`harness_feature` is unset). A missing/stale/dangling registry entry can at most reproduce the
old cross-worktree **false-rejection** shape F5 was written to fix (the checkout the hook process
lives in has a different branch than the feature's own worktree) — a reliability regression back to
pre-F5 behavior, never a new bypass: nothing a submitting agent controls (its digest text) can steer
`feature_root`'s lookup, so this is not an attacker-reachable fail-open. Rated: not a finding.

## 4. Path handling in `_resolve_plan_review_path` (dispatch item 4) — no traversal reachable, one backlog note

`_resolve_plan_review_path` takes `reviewed`'s tail verbatim and, for an absolute path, `realpath`s it
with **zero containment to the checkout root** — digest-controlled, in principle a arbitrary-path
primitive. Traced the one consumer, `_pending_plan_review_error`: the computed `plan_path` is checked
for **equality** against `expected_path` (`feature_dir/plan.yaml`, itself derived from the
non-traversable `FEATURE_DIR_IN_ARTIFACT_RE` regex, which forbids `/` inside either path segment) —
and only on a match does anything ever open the file (`_pending_plan_status_error`). Confirmed live:
`reviewed: "plan:/etc/passwd"` → `RC=1`, `"reviewed plan target '/private/etc/passwd' is not this
feature's plan.yaml (...)"` — rejected by the equality gate, `/etc/passwd` never opened. DEMONSTRATED,
not inferred.

**BACKLOG (improvement, not a defect):** the missing containment is currently harmless only because
the equality check happens to precede the read in this one call site. A future edit that adds a
second consumer of `_resolve_plan_review_path`'s return value, or reorders `_pending_plan_review_error`,
would silently reopen an arbitrary-file-read primitive with no test currently positioned to catch it
(the ordering is enforced by control flow, not by an assertion). Recommend: have
`_resolve_plan_review_path` normalize *and check containment* under `_root_or_none()` up front, the
same shape `_feature_dir_from_artifact`'s regex already enforces for the artifact path — cheap,
and removes the "correct only by call-order" property. **Rated `low`** — not reachable today, pure
defense-in-depth.

## 5. F2 / F3 — independently re-verified, not merely re-read

Ran three digests directly through `validate()` (not the existing suite, a fresh probe):
- all-members-`skipped` (only `fable-advisor`, claiming `VERDICT: PASS`) → **rejected**:
  `"members records no member actually ran — a lead verdict cannot claim an outcome for an entirely
  skipped team."` (F2)
- a mandatory `qa` member marked `status: skipped` → **rejected**:
  `"only the optional fable-advisor may be recorded as skipped; mandatory members must carry their
  verdict."` (F3)
- the legitimate case DEC-207 exists to serve — `fable-advisor` genuinely skipped, `security-reviewer`
  genuinely returns `FAIL` — → **accepted with zero errors**, and the worst-wins cross-check still
  requires `VERDICT: FAIL` to match. F3's narrowing does not reject the case it was built for.

Note on F3's failure direction: a mandatory persona that genuinely cannot run (host crash) has no
legal way to report that today — the digest is rejected outright (`BLOCKED (contract violation)`,
forcing a retry), not silently passed through. That is the safe failure direction (reject > silent
accept) and is a reliability/availability question for QA's test-matrix, not a security gap — flagging
per this cycle's own framing (fail-closed ≠ security finding) rather than omitting it.

## Secrets / data exposure (dispatch item 5)

Swept the full `main...d78f393` diff for credential-shaped strings and dangerous calls
(`api[_-]?key|secret|password|token|bearer|-----BEGIN|AKIA...|ghp_...|xox[baprs]-`,
`eval\(|exec\(|os\.system|subprocess.*shell=True|pickle\.loads|yaml\.load\(|__import__`). Every hit
is the English word "token" in prose about the `{{cycle}}` template placeholder or prior reviewers'
own secret-sweep methodology text — no credential-shaped strings, no dangerous calls, matches c0/c1/c2's
sweeps. Not re-raised.

## Not re-raised (carried, unchanged at this pin)

`panel_findings.py` byte-identical between the c2 pin (`70fd441`) and this pin (`d78f393`) — confirmed
empty diff. **M4** (32-bit truncated `PF-` finding id, `med`, carried from c0) unchanged, still
unrealized (still no live `plan.yaml` ruling in this repo keyed to a `PF-` id). M6/M7 not
security-owned, not re-derived.

## Open question for QA (non-blocking, not mine to fix)

`test-validate-digest.py`'s plan-review tests (`_check_plan_feature_binding`) call
`validator.validate(..., feature_dir=<explicit>, ...)` — the fixture-override seam — never
`feature_dir=None`. My §1 repro is therefore currently the *only* exercise of the exact production
call shape for the cross-feature plan-review forgery; a future refactor that reintroduces the F1 gap
would not be caught by the shipped suite. Same gap QA's own c2 Q3 already flagged for
`_pinned_feature_review_error`/`_skipped_member_error` branches.

```yaml
VERDICT: PASS
DIGEST:
  headline: "the F1 forgery shape is CLOSED and demonstrated live (rc 1 on substitution, rc 0 honest); its corroboration input is traced to host-only dispatch text, not digest content; the new registry lookup degrades to prior full-validation behavior on any failure, never a bypass; F2/F3 both reject the attack shape and accept the legitimate case they were built for"
  in_scope: true
  scope_reason: "validate-digest.py is a trust/attestation gate deciding whether an agent's claimed verdict is trustworthy; every bypass in it is a privilege-escalation of a claim — squarely this role's surface"
  severity_max: low
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "plan-review digest artifact:/reviewed: self-report -> _pending_plan_review_error binding", stride: T, mitigated: true }
    - { boundary: "branch-corroboration current_branch/harness_feature input -> OMP dispatch assignment text (host-only, pre-subagent-output)", stride: S, mitigated: true }
    - { boundary: "inflight_registry.feature_root lookup miss/stale/exception -> installed-validator checkout resolution", stride: D, mitigated: true }
    - { boundary: "reviewed: plan:<absolute-path> -> _resolve_plan_review_path filesystem read", stride: I, mitigated: true, precondition-absent: "containment enforced only by call-order today (BACKLOG, low)" }
    - { boundary: "lead digest members: list, status:skipped -> worst-wins roll-up", stride: T, mitigated: true }
    - { boundary: "panel_findings.py digest[:8] (32-bit) -> INV-32 overrule id matching", stride: T, mitigated: false, precondition-absent: "carried M4, med, unchanged, no live ruling exists to break" }
  open_questions:
    - { id: Q1, question: "test-validate-digest.py's plan-review cases never call validate(feature_dir=None) — the production shape this cycle's fix targets. Should QA add a case matching this review's §1 repro so a future regression is caught by the suite, not only by a manual review probe?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-c3.md
```
