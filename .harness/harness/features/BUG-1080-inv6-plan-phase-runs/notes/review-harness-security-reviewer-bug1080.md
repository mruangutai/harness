# Security review — BUG-1080 (INV-6 plan-phase exemption), a2fb6c0b, worktree-verified

Worktree confirmed: `test-check-state.py` is 3526 lines here (3396 in main checkout — did not
use it). `python3 test-check-state.py` run live: all six new `case_inv6_*` pass, plus the full
suite (no failures observed in output).

## Verdict: PASS, severity_max MED, no must_fix

The exemption is Tampering/Repudiation-shaped but **not privilege escalation**: every actor who
can exploit `code_grade: n_a` already had, via the identical unauthenticated write path, a
strictly *easier* route to the same outcome (forging `review_sha` itself) before this diff
existed. This is the P-02 pattern and the exact shape BUG-1071's own security review graded MED
for `approval.date` (Q2), not the HIGH it gave `panel_era_start` (F1) — the discriminator there
was whether the diff **grants a capability the actor did not already have**. Here it does not.

## 1. Tampering / privilege — narrower than BUG-1071's F1, same shape as its Q2

`feature-json-merge.py append-run`/`set-key` has **no identity source at all** — confirmed by
this repo's own prior security review (`BUG-1030-stale-anchor-write-hazard/notes/review-harness-
security-reviewer-c0.md:180-186`): "allows any top-level key including `status`/`review_sha`/`pr`
with no allowlist... the identity/authorization gap `harness_merge.py`'s own module docstring
already discloses and defers (issue #627)."

Traced the write-time guard stack:
- `check-domain.sh`'s **domain** phase (who may write which path) is registered PreToolUse on
  `Write|Edit` only (`.claude/settings.json:16-22`) and its own source states it explicitly:
  `_domain_phase = _governed and not _post` (`check-domain.sh:328`) — domain enforcement **never
  runs for Bash**. Only `harness-orchestrator` holds `.harness/*/features/**` in `team-config.yaml`
  (:36); no other of the 16 personas — including `harness-validator-lead`, whose grant is
  `runs/*-validator/**` only, never `feature.json` itself — has any domain grant on it.
- `bash-write-guard.sh` (PreToolUse, `Bash`) denies shell redirects/in-place editors
  (`sed -i`, `tee`, `>`, `>>`) but does not, and by its own docstring cannot, parse arbitrary
  argv — `python3 .../feature-json-merge.py append-run <path> '<json>'` is an ordinary
  subprocess call with no redirect and passes clean.
- `check-domain.sh --post` (PostToolUse, `Write|Edit|Bash`) runs only the **shape** phase
  (line budget, schema) for Bash, never domain — by the same line (`:328`) and its own comment:
  "Domain asks WHO may write a path. Shape asks WHAT the file may contain... independent
  questions" (`:820-826`).

**Conclusion**: any of the 16 governed personas — including the validator squad member or build
engineer whose own review is at stake — can, via a plain Bash call with zero domain check, append
a `runs[]` entry claiming `"squad": "validator", "code_grade": "n_a"` about itself. This is real
and reachable. But it is **not new**: the same call could already write `review_sha` to any
non-empty string (no schema constraint on its shape), which alone satisfies INV-6's pre-existing
check (`_sha == "" or _sha in PLACEHOLDER_UNSET`). That gap was reviewed, confirmed, and knowingly
deferred in BUG-1030 as "not introduced by this diff, and strictly safer than the raw-text
hand-edit it replaces." BUG-1080 adds a second key to a door already unlocked by the first.

**What genuinely differs, and why it still isn't `must_fix`** (mirrors BUG-1071 Q2's own
reasoning almost exactly): forging `review_sha` leaves a suspicious artifact — a garbage SHA that
would fail to resolve the moment `validate-digest.py`'s SEC-01 binding (`code_grade_bound_to_
review`) tries to anchor a real reviewer's digest to it, or that a human skimming feature.json
would notice as implausible. Declaring `code_grade: n_a` on a run leaves **no such artifact** —
it is indistinguishable from a legitimate DEC-207 plan-phase record and blends into the exact
shape the fix exists to legalize. That is a real reduction in *visibility/cost*, not in
*reachability* — the same distinction that capped BUG-1071 Q2 at MED rather than low. I apply the
identical treatment: MED, not privilege escalation, recommend rather than block.

## 2. Self-asserted, no corroboration — confirmed, same shape as every other feature.json field

Nothing in this diff (or elsewhere) binds a `runs[].code_grade` entry to the reviewer's own
DIGEST `code_grade` claim, which validate-digest.py **does** rigorously validate (`SEC-01`,
`code_grade_bound_to_review`, `validate-digest.py:568-1257`) — it resolves `review_sha` to a real
commit, checks branch match, and for `n_a` outside plan mode verifies the diff actually touches
no Python file. That hardened check runs once, at the reviewing agent's own `SubagentStop`, on
the DIGEST TEXT. Nothing then carries that verified claim into the `feature.json` `runs[]` entry
— whoever calls `append-run` (found no automated caller; grepped the whole worktree, only
`feature-json-merge.py` itself and its test reference `append-run`) constructs that JSON
independently, by hand, with no code tying it to the validated digest. This is the identical
transcription gap that already exists for `verdict`, `squad`, `id`, and `agent` — not new in
kind, newly consequential because this is the first `runs[]` field whose *value* (not just its
presence) silences a fail-closed gate.

## 3. Schema enum vs. check-state.sh's runtime read — confirmed to disagree, but only by a bypass

Schema: `"code_grade": {"type": "string", "enum": ["n_a"]}` — exact string match.
`check-state.sh`: `str(entry.get("code_grade", "")).strip().lower() != "n_a"` — case/whitespace
tolerant. **Measured live** (ran `check-state.sh` against synthetic fixtures): `"N_A"`,
`" n_a "`, and `"\"N_A\""` (raw text) all suppress the pin-required message exactly like `"n_a"`.

Write paths checked for whether a non-conforming value can land at all:
- `feature-json-merge.py append-run` → `feature_json_write.write_feature_json` →
  `feature_schema.problems_for_text`, called on the **candidate** text before the atomic
  replace. The module's "monotonic non-regression" policy (`feature_json_write.py:92-116`) only
  forgives problems already present in the baseline document — a brand-new `code_grade: "N_A"`
  entry is a NEW problem against any baseline lacking it, so this path **refuses** it.
- `Write`/`Edit` tool → PreToolUse `check-domain.sh` SHAPE phase, same `problems_for_text` call,
  same refusal, before the write lands.
- A raw Bash write that constructs the JSON itself (e.g. `python3 -c "json.dump(...)"`, which
  bash-write-guard's redirect-only scan does not catch) bypasses schema validation entirely and
  lands on disk. PostToolUse `check-domain.sh --post` then detects the schema violation and
  prints it (exit 2) — **detection, not prevention**, by the file's own documented design
  ("Detection, not prevention: an Edit payload carries no whole-file content and arbitrary shell
  cannot be predicted", `check-domain.sh:900-910`). If `check-state.sh`'s own sweep (a separate,
  unrelated invocation) runs before anyone acts on that stderr, the non-conforming value already
  silences INV-6.

Severity: **low**, not medium — it requires deliberately bypassing the sanctioned CLI/tool route,
and the same actor already has a schema-unconstrained, zero-effort route to the identical outcome
(forge `review_sha` to any string; there's no enum on it at all). Recorded as checked-and-clear
for `must_fix` purposes; worth a hardening note (`check-state.sh` could match the schema's exact
string instead of `.strip().lower()`) but not gating.

## 4. Blast radius / GAP-7 reproduction — confirmed reproducible via the mismatch in §2, not via §1/§3 alone

GAP-7 (`check-state.sh:459-460`, `test-check-state.py:3340-3342`) is a reviewer diffing a moving
HEAD because `review_sha` was never pinned before they ran. A **falsely-labelled** `code_grade:
n_a` on a run that in truth graded real code reproduces this exactly: `code_reviewing_runs`
excludes it (`check-state.sh:437-441`), INV-6 stays silent, and nothing else in this diff's own
code re-derives whether the label was true. The only thing that WOULD have caught a genuine
reviewer trying to submit that false claim is `validate-digest.py`'s SEC-01 (§2) — which binds a
digest's `code_grade: n_a` to an actual empty/no-Python diff or a genuine pending plan — but that
check is bypassed entirely the moment the `feature.json` entry is written directly rather than
transcribed from a validated digest (§1's Bash route). So: reachable, but only by chaining §1's
pre-existing unauthenticated write with §2's pre-existing lack of digest-to-record binding —
neither of which BUG-1080 introduces.

## Reachability — no producer exists yet (asked for by the lead, not itself a security gate)

Grepped the full worktree: zero callers of `append-run` other than `feature-json-merge.py`
itself and its own test. No skill doc, agent definition, or orchestrator playbook instructs
writing `code_grade` into a `runs[]` entry (DEC-207 only specifies the **digest's** field, per
`DECISIONS.md:6339-6360`, not the transcription into `feature.json`). Lead's own corpus count
(zero `code_grade` occurrences on disk) is consistent with this. Practically this means: today,
the ONLY way `code_grade: n_a` reaches a real `feature.json` is a hand/Bash write (§1's route),
never a sanctioned one — so in the currently-shipped state, INV-6's exemption is reachable only
by the same deliberate-bypass actor already covered in §1/§3, not by ordinary orchestrator
operation. This narrows real-world exposure further but does not close the write-path gap itself.

## Standard sweep

Secrets/injection: diff touches only `check-state.sh` (embedded Python heredoc, string ops on
parsed YAML values, no shelling out of untrusted content), `feature-schema.json` (data), and
`test-check-state.py` (fixtures). No credential-shaped strings, no new subprocess/shell call
sites. Nothing to report.
