# Security review — cycle 4 — BUG-1309-mirror-build-entry @ af132780

## BLUF

The bystander-lockout fix (cycle-3's finding) is correctly closed, confirmed by execution.
But the same one-line change that closes it — `feature_for` now `continue`s past any
`feature.json` that parses to a non-`dict` — opens a **new, silent false-allow**: the
feature that OWES the receipt can corrupt its **own** `feature.json` to a JSON array,
string, or `null` and the merge that should be denied is instead let through with **zero**
signal (`rc=0`, empty stdout, empty stderr). Confirmed by differential execution against
the pre-fix code: same fixture denies (generically, but denies) on the cycle-3 code;
allows silently on `af132780`. `feature.json` is agent-and-tool-writable per the dispatch's
own threat model, so this is reachable by ordinary write access, not privilege escalation.

`severity_max: high`, `must_fix` non-empty → **FAIL**.

## Direction 1 — false-allow (executed)

Fixture: feature `FEAT-9001-fixture-non-era`, `entry=None` (owes a receipt — baseline
denies citing `gh-sync.py open`). Corrupted only that feature's own `feature.json` to
`[{"branch": "feature/test"}]` post-fixture-creation, then ran `merge-gate.sh` for
`git merge feature/test`.

- **`af132780` (current diff)**: `rc=0`, stdout empty (no `hookSpecificOutput` printed at
  all), stderr empty. The merge is allowed with no trace anything was evaluated.
- **Pre-fix reconstruction** (isinstance-dict guard removed in-memory, same fixture, run via
  `python3 -c` with `__file__` bound to the real script path — no disk write, no repo
  mutation): `rc=0`, stdout `{"...": {"permissionDecision": "deny", "permissionDecisionReason":
  "merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is
  denied. Repair the feature record and re-run the merge."}}`. Fail-closed (if unattributed
  — the cycle-3 bug), but it blocks.

Same top-level document shapes (`"feature/test"` bare string, `null`) reproduce identically
— all three land on `rc=0`/silent-allow on the current diff (probe script:
`/tmp/sec-probe-merge-gate.py`, scenarios S1a/S1b/S1c).

**Mechanism**: `feature_for` treats "record parses but isn't a dict" identically to "record
doesn't exist" — `continue`s past it, never adds it to the candidate set. If that was the
*only* record for the branch, `feature_for` returns `(None, None)`, and `main()`'s
`document is None` branch takes the same silent-return path used for the legitimate
"no feature owns this branch" case (DEC-138 posture item 2). A feature that IS matched by
branch, but whose own record is malformed, is thereby made indistinguishable from a feature
that was never matched at all — which converts what should be posture item 1 ("internal
error on a matched feature denies, naming it") into item 2's silent allow. This is exactly
the pairwise conflict the dispatch asked to probe for.

**Threat**: any agent, tool, or process with write access to its own
`.harness/*/features/<FEAT>/feature.json` — which the dispatch states is inside the threat
model — can permanently and silently disable the Build-entry merge gate for its own branch:
overwrite the file with `[]`, `null`, or any non-object JSON. No stderr line, no deny
reason, no audit trail (G-04: unauditability is itself an aggravating factor — an operator
scanning hook output afterward cannot distinguish "the gate ran and allowed" from "the gate
never saw this feature"). This defeats DEC-138's actual purpose (a merge may not bypass an
owed Build-entry receipt) for the class of actor DEC-138 exists to constrain.

**Severity: high** — exploitable by an ordinary write-access actor against the system's own
compliance control, silently, with no detection signal. Not critical: no remote/credential
compromise, no cross-tenant data breach.

`must_fix`: `feature_for` (or `main`) must not treat "record exists, parses, mentions this
branch, but isn't a dict" the same as "no record for this branch." A minimal fix: track
whether *any* record for the branch was seen-but-unusable (dict-check fails) separately from
"no record matched," and route the former through the existing matched-feature error/deny
path (attributed if possible, generic-deny if not) rather than the silent-allow path.

## Direction 2 — false-deny / bystander lockout (executed, confirmed fixed)

- **S3**: healthy feature (`entry="opened"`, i.e. allowed) plus an *unrelated* feature
  directory whose `feature.json` is `[]` → `rc=0`, `decision=None`, no reason. The cycle-3
  bug (any malformed record anywhere denies every merge) does not reproduce. Matches the
  lead's independently-verified fixture.
- **S4**: same, but the unrelated malformed directory is named
  `ZZZ-<script>alert(1)</script>-malformed` and the OTHER feature genuinely owes a receipt
  (`entry=None`) → `rc=0`, `decision=deny`, reason correctly names `FEAT-9001-owing` only.
  The malformed record's dirname is never read (the `continue` fires before
  `os.path.basename` is ever called on it), so it cannot leak into a deny reason for a
  different feature — no reflected-content path exists for skipped records.

No exception source survives in `feature_for` for the "record is present, JSON-valid, but
malformed" class — `OSError`/`JSONDecodeError` were already caught pre-diff, and the new
`isinstance` check closes the only remaining `AttributeError` (`document.get(...)` on a
non-dict). The pre-match `try` in `main()` (wrapping `import feature_schema`, `head_branch`,
`feature_for`) can still raise from `head_branch` on an environmental failure (e.g. `git`
binary missing) with the unattributed `"this feature"` default — but that is data-independent
(not driven by any `feature.json` content, attacker or otherwise), unchanged by this diff,
and out of scope per the dispatch's settled-items list.

## Branch-shadowing / glob-order (probed, not attributable to this diff)

Tested whether a same-branch decoy record (a *valid dict*, e.g. `entry="not-applicable"`)
in a directory that sorts alphabetically before the owing feature's directory can win the
first-match-wins race in `feature_for` (S2, plus a standalone `glob.glob` order probe).
Result: `glob.glob` order was **not** reliably alphabetical or creation-order in this
environment — one probe returned alpha order despite reverse creation order, another
returned creation order despite reverse alpha names. In the actual S2 run the real
(`FEAT-9001-owing`) record won and denied correctly; the decoy did not shadow it.

This mechanism is **unchanged by `af132780`** — first-match-wins on `document.get("branch")
== branch` is identical before and after the diff; the new `isinstance` check does not
touch it. Filed as an open question rather than a finding: it is real (no uniqueness
constraint on `branch` across `feature.json` records) but pre-existing, non-deterministic in
this codebase's actual glob usage, and outside "the skip" this cycle's pin is about.

## Data exposure

No new interpolation path. `feat` (directory basename) and `os.path.realpath(feat_dir)` are
only read for a *matched* dict record (confirmed: S4's malformed record's basename is never
touched); that interpolation itself is unchanged from pre-diff code, not introduced by
`af132780`. `gh_head`'s `text.splitlines()[0]` truncation (pre-existing) still bounds the
`failure` string to one line before it reaches stderr/deny reason. All values land inside
`json.dumps(...)`, so no JSON-structural injection into the hook's permission-decision
payload.

## Verdict inputs

- `in_scope`: true — the diff changes what "a record exists but is malformed" means for gate
  outcome, which is squarely this reviewer's surface (Tampering / control-bypass, P-03).
- `severity_max`: high (the false-allow finding).
- `must_fix`: 1 item (see Direction 1).
