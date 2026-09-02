# Security review — FEAT-51-claude-code-lifecycle-safety — panel c1

**FAIL.** Two demonstrated, high-severity bypasses of the enforcement boundary this feature
exists to build — both reproduced end-to-end against the pinned code, not argued. D-18/D-19 are
acknowledged as signed and are not re-raised.

## F-1 (high) — `quarantine.py adopt` canonical-path construction is not bound to a real
quarantine directory; `plan-sign-gate.py`'s only guard for it is a literal-string match on the
path segment `quarantine`, so naming the staging directory anything else skips the orphan check
entirely and the tool overwrites the real canonical file. STRIDE: Tampering + Elevation of
Privilege. OWASP: Broken Access Control / path handling.

- `quarantine.py:63-70` (`_canonical_target_for`): the target is *two directories above the
  `--file` argument's own directory*, joined with its basename — pure directory arithmetic on
  attacker-supplied structure, no check that the file is actually under a `quarantine/` tree.
  `cmd_discard` has `_QUARANTINE_CHILD_RE` (`quarantine.py:47-52`) for exactly this; `cmd_adopt`
  (`quarantine.py:104-135`) has no analogous check — only `basename(...) in CANONICAL_ARTIFACTS`.
- `plan-sign-gate.py:243-249` (`quarantines()`, `ADOPT_TOOL` branch): recognizes an adopt call as
  security-relevant only when the checkout-relative `--file` value matches
  `\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/(.+)` **literally** — the directory segment
  must be spelled `quarantine`. Any other name (or a path outside `.harness/` entirely, since
  `_checkout_rel` — `plan-sign-gate.py:180-183` — returns `None` when the substring isn't found)
  makes `quarantines()` return `None`, and the caller treats `None` as "not a quarantine
  situation" and never calls `orphan_write` at all — not "orphan check said allow", the check
  never runs.
- **Reproduced** (script in this artifact's session, not committed): staged a `feature.json` at
  `<root>/.harness/harness/features/FEAT-99/notquarantine/x/feature.json` (same depth as a real
  quarantine entry, directory just not named `quarantine`) and ran
  `quarantine.py adopt --file <staged> --root <root>` as `agent_type=harness-backend-dev` with a
  session that held **no claim at all** for FEAT-99. `plan-sign-gate.py` exited 0 (not refused,
  no stderr). `quarantine.py` printed `ADOPTED <root>/.harness/harness/features/FEAT-99/feature.json
  FROM <staged>` and the real canonical `feature.json` content changed from `LEGIT` to `PWNED`.
- Actor: any `harness-*` agent with Bash access (every governed member, lead and the
  orchestrator — `check-domain.sh` only matches `Write|Edit`, `bash-write-guard.sh` only
  recognizes `sed -i`/`tee`/`cp`/`mv`/redirects/`python3 -c`, neither fires on
  `python3 quarantine.py adopt`). Damage: silent, unauthenticated overwrite of `feature.json` /
  `STATE.md` / `BRIEF.md` (raw `harness_merge.locked_update` replace, `quarantine.py:130-132`)
  for **any feature in the repo**, not just the caller's own domain or the caller's own feature —
  wider than the accepted D-19 "own-domain generic Bash write," which this is not: D-19 is scoped
  to a canonical artifact inside the writer's own domain, this crosses feature/domain lines with
  zero live-claim requirement. `plan.yaml` is comparatively protected (routes through
  `plan-merge.py apply`'s union/approval checks), so the sharpest impact is `feature.json` /
  `STATE.md` / `BRIEF.md`.
- Recommend: bind `cmd_adopt` to the same discipline `cmd_discard` already has — resolve
  `os.path.realpath(quarantined)` and require it sit under
  `<realpath(root)>/.harness/*/features/*/quarantine/*/`, mirroring `_QUARANTINE_CHILD_RE`, and
  have `plan-sign-gate.py`'s `quarantines()` detect an adopt-shaped invocation by the same
  realpath containment test rather than a literal-segment regex on the as-typed argument. Not a
  fix I am making — reported per role.

## F-2 (high) — `inflight_registry.py`'s `release` CLI has no caller-identity binding, and this
diff newly makes the registry a trust anchor for `orphan_write`'s authorization decision. STRIDE:
Tampering + Elevation of Privilege (and Denial of Service against the legitimate claim holder).

- `release()` (`inflight_registry.py:398-425`) and the `release` CLI verb
  (`inflight_registry.py:520-533`) are **pre-existing, unchanged** by this diff (confirmed via
  `git diff 0bc57c88..fa5ce88e` — only `orphan_write`, `canonical_artifact`, `quarantine_rel` and
  comment text are new). What is new is that `orphan_write` (`inflight_registry.py:301-317`) now
  reads this same claims list to decide whether a *different* agent's write gets redirected to
  quarantine — the registry became an authorization input this feature relies on, without gaining
  any authentication.
- No hook governs a direct `inflight_registry.py` CLI call: `check-domain.sh` matches
  `Write|Edit` only; `plan-sign-gate.py`'s `TOOL`/`ADOPT_TOOL` are `plan-merge.py` and
  `quarantine.py` only (`plan-sign-gate.py:26-29`) — `inflight_registry.py` is absent from both;
  `bash-write-guard.sh`/`gh-close-gate.sh`/`branch-create-gate.sh` do not mention it (grepped).
- **Reproduced**: agent A (`harness-backend-dev`, session `sess-A-legit`) holds a live claim on
  `FEAT-X` via `claim_with_receipt`. Before any interference, `orphan_write` for an unrelated
  agent B on `FEAT-X` correctly returns `True` (B would be quarantined). Then, with **zero**
  proof of identity, a `release --agent harness-backend-dev --feature FEAT-X --root <root>` CLI
  call (as if issued by B, or by anyone) succeeds at exit 0 and removes A's still-live claim. A
  never released it and is still running. Afterward, `orphan_write` for B on `FEAT-X` returns
  `False` — the quarantine boundary FEAT-51 built is now off for the whole feature, because
  `has_compatibility_claim` (`inflight_registry.py:305-307`) sees zero remaining claims.
- Actor: any `harness-*` agent with Bash access, against any other agent's session, on any
  feature. Damage is two-sided from one call: (1) legitimate agent A's own subsequent
  Write/Edit to `feature.json`/`STATE.md`/`BRIEF.md`/`plan.yaml` is now wrongly redirected to
  quarantine (DoS on a live, correctly-behaving writer), and (2) every writer for that feature —
  including the caller — is now unquarantined, i.e. the exact race FEAT-51 exists to catch
  (a stranded orphan racing a replacement writer) goes undetected for the rest of that feature's
  claim-free window.
- Not covered by any test: `test-inflight-registry.py` exercises `release()` only as a direct
  Python call, never asking who is allowed to invoke it (grepped for auth/identity/forge —
  none). Not the same gap as D-19/D-18 — neither of those names the registry itself as unauthenticated.
- Recommend (not made): bind release to caller identity — the only identity signal a subprocess
  currently has is what the hook payload supplies (`agent_type`, `session_id`), which this CLI
  path does not receive at all since it is invoked as a bare shell command, not through a hook.
  This is a design gap worth a decision, not a one-line fix; flagging as `open_questions`.

## Checked, no finding

- **Query-scoped expiry (Lead 3, security angle).** `orphan_write`'s `_expire_where` predicate is
  `lambda claim: _matches(claim, feature=feature)` (`inflight_registry.py:212, 296-300`) —
  confirmed at source: a lookup for one feature only ever expires that feature's own claims.
- **`SUSPENDED` unreachable outside `hook_mode` (Lead 4).** `VERDICTS = {"PASS","FAIL","BLOCKED","ESCALATE"}`
  (`validate-digest.py:35`) never includes `SUSPENDED`; no `SCHEMAS` entry references it; grepped
  the full production tree — the string appears only in `validate-digest.py`'s own `hook_mode`
  regex match/refusal text, `inflight_registry.py`'s refusal copy, and `SKILL.md` prose. A member
  cannot reach the acceptance branch: `_kids` (`validate-digest.py` inside `hook_mode`) is
  populated only `if norm(agent) in ("lead", "orchestrator")`, and `ALIAS`
  (`validate-digest.py:238-248`) is a fixed, closed table — `lead` maps from exactly
  `harness-product-lead`/`harness-eng-lead`/`harness-validator-lead`, `orchestrator` from
  `harness-orchestrator`; no member persona name normalizes into either. For a SUSPENDED return
  with no live children (non-lead/orchestrator, or a lead/orchestrator with none), the dedicated
  suspension branch doesn't fire (`_kids` is falsy) but the return still falls through to the
  generic `validate()` VERDICT-enum check and is refused at exit 2 there — same outcome, different
  code path; verified this is not a silent pass-through.
  **Correction of the earlier `_read`-tool pass:** an initial non-`git show` read of this
  function via the `read` tool (relative path, no worktree prefix) returned older pre-SUSPENDED
  text inconsistent with `git show fa5ce88e:...` and with `sed` on the working file directly —
  matching this feature's documented cross-tree read/write hazard. Discarded; all claims above
  are from `git show fa5ce88e:` and a direct `sed` of the (git-clean, zero-diff-from-pin) working
  file.
- **Fail-open catch-alls (Lead 3).** Confirmed wide `except Exception` around the orphan check in
  both `check-domain.sh`'s heredoc and `plan-sign-gate.py:quarantines()` — this is the
  SC-13-specified, signed fail-open and is not re-raised. Both paths do emit a stderr line naming
  the exception before falling through; I found no way for that print to itself be swallowed
  without also crashing the hook process (which is louder, not quieter).
- **Secrets/data exposure (Lead 5).** `quarantine_rel` truncates session to 8 chars
  (`inflight_registry.py:319-327`); refusal messages surface local absolute paths and session ids
  back to the acting agent's own stderr only — no cross-agent or cross-feature leak found in the
  named files.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "quarantine.py adopt and inflight_registry release are both unauthenticated in ways that let one agent silently overwrite or unprotect another feature's canonical artifacts — demonstrated, not theoretical"
  in_scope: true
  scope_reason: "The diff is an access-control boundary (PreToolUse hooks, a shared mutable claims registry, a quarantine directory) — squarely Tampering/Repudiation/Elevation-of-Privilege territory, not incidentally security-adjacent."
  severity_max: high
  findings: 2
  must_fix:
    - "F-1: quarantine.py cmd_adopt trusts directory-arithmetic on an unvalidated --file path, and plan-sign-gate.py's orphan check is a literal-string match on the segment name 'quarantine' — any other directory name silently skips the check entirely. Bind cmd_adopt to a realpath-under-features/*/quarantine/* containment test (mirroring cmd_discard's _QUARANTINE_CHILD_RE) and detect the adopt route the same way in plan-sign-gate.py."
    - "F-2: inflight_registry.py's release CLI has no caller-identity check, and this diff newly makes the registry an authorization input (orphan_write). Any Bash-capable agent can release another live agent's claim by name, which both wrongly quarantines the legitimate writer and disables the quarantine boundary for that feature. Needs a design decision — no identity signal currently reaches this CLI path."
  threat_model:
    - { boundary: "quarantine.py adopt --file <path>, PreToolUse Bash", stride: "T", mitigated: false }
    - { boundary: "quarantine.py adopt --file <path>, PreToolUse Bash", stride: "E", mitigated: false }
    - { boundary: "inflight_registry.py release CLI (claim forgery/release)", stride: "T", mitigated: false }
    - { boundary: "inflight_registry.py release CLI (claim forgery/release)", stride: "E", mitigated: false }
    - { boundary: "inflight_registry.py release CLI (peer claim removal)", stride: "D", mitigated: false }
    - { boundary: "orphan_write query-scoped expiry (cross-feature sweep)", stride: "T", mitigated: true }
    - { boundary: "SUSPENDED verdict acceptance in hook_mode", stride: "E", mitigated: true }
    - { boundary: "check-domain.sh / plan-sign-gate.py fail-open except clauses (SC-13, signed)", stride: "T", mitigated: false }
  open_questions:
    - { id: Q1, question: "F-2's remedy needs a design decision, not a one-line fix: no runtime identity signal currently reaches a bare CLI invocation of inflight_registry.py (agent_type/session_id only arrive via hook payloads). Should release require a hook-supplied identity, a capability token, or is the accepted mitigation something else entirely?", blocking: true }
    - { id: Q2, question: "F-1's fix (realpath containment check in cmd_adopt, matching cmd_discard) is small and directly analogous to existing code — does it need a full plan task, or can it land as a direct patch under this feature's own scope before ship?", blocking: false }
  files_touched: []
  expertise_update: []
  code_grade: fail
artifact: .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/review-harness-security-reviewer-panel-c1.md
```
