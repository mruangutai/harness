# Security review — c7 (fresh) — BUG-1309-mirror-build-entry

Pin `894adc0f08c71c108ef8432f1f7a3cc8a2a763c0`. c6 is ABSENT (rate-limited before its lead verdict);
its member note (`review-harness-security-reviewer-c6.md`) was read as a hypothesis only. Every claim
below is freshly re-derived at this pin with executed fixtures under `/tmp/secprobe7/*.py` (drivers
kept for replay); nothing in the tracked worktree was touched, confirmed by the bash-write-guard
blocking every redirect attempt against it. The whole feature diff was scoped
(`git diff 6ad7233f 894adc0f -- <the 10 named files>`): merge-gate.py/.sh are wholly new within this
feature (did not exist at the feature's merge-base with `origin/main`); gh-sync.py/+359,
feature_schema.py/+99, check-state.sh/+41, post-merge-sweep.sh/+24, settings.json/+4,
settings.snippet.json/+4, harness-hooks.ts/+1, feature-schema.json/+5.

## Item 1 — branch-collision misattribution (glob.glob first-match on two valid dict records)

**(a) Reproduces at the pin: YES, both directions, 5/5 each**, using a content-decoupled fixture:
two literal directory names `aaaaaa`/`zzzzzz` independently established (`item1c_find_pair.py`, a
14-pair sweep) to have `zzzzzz` win `glob.glob` order regardless of creation sequence — proving the
order is a pure function of the directory-name string on this filesystem, unrelated to which record
is "real" and which is "spoof," and unrelated to write order. With that pair held fixed
(`item1d_driver.py`):
  - **DENY-healthy**: `aaaaaa`=the actual, healthy owner of `feature/test` (`build_entry:"opened"`),
    `zzzzzz`=an unrelated feature record that also carries `branch:"feature/test"` and owes a receipt.
    `zzzzzz` wins the match → `deny`, reason names `zzzzzz`, 5/5. A healthy merge is denied and
    misattributed to a feature the operator has no reason to investigate.
  - **ALLOW-owing (mirror)**: `aaaaaa`=the actual owner, itself owing a receipt (`build_entry` absent),
    `zzzzzz`=an unrelated healthy record with the same branch. `zzzzzz` still wins → silent `ALLOW`
    (stdout empty, exit 0), 5/5. The owing merge proceeds with no receipt filed and no audit trail.

**(b) Reproduces identically at the parent (894adc0f^):** YES. Built the parent's `merge-gate.py`
verbatim (`git show 894adc0f^:...`) into `/tmp/secprobe7/bin_parent/`, alongside the tracked, unchanged
`feature_schema.py`/`feature-schema.json` (confirmed byte-identical for this file across
`894adc0f^..894adc0f` via `git diff --stat`), and ran the identical `aaaaaa`/`zzzzzz` fixture through it
(`item1e_parent_driver.py`): same `zzzzzz`-wins order, same `deny`-misattribution 5/5, same silent-ALLOW
5/5. Also confirmed by source: `git diff 894adc0f^ 894adc0f -- merge-gate.py` touches only
`feature_for`'s non-dict/`unusable` handling and `main`'s consumption of it — the match predicate itself
(`document.get("branch") == branch: return path, document`, first-match-wins, unsorted `glob.glob`) is
byte-for-byte untouched.

**(c) Therefore: PRE-EXISTING, not introduced by 894adc0f.** It has existed since merge-gate.py's
creation earlier in this same feature (the file does not exist before this feature's merge-base) and
was never addressed by any of the feature's six commits, nor asserted by `test-merge-gate.py` (grepped;
no test constructs two features on one branch). Glob order observed: **not alphabetical** (`alpha`<
`bravo` orders forward, but `aaaaaa`/`zzzzzz` orders `zzzzzz` first regardless of which was created
first — 2 explicit creation-order swaps, same result both times) and **not creation-order** (same
swap test) — it is a deterministic function of the literal name string on this filesystem (APFS),
opaque to and unguaranteed by the code. 14 name-pairs probed in `item1c`, 1 trial each (deterministic
per pair, confirmed by the follow-up 5-trial reruns on the chosen pair); 5 trials × 2 scenarios at the
pin, 5 × 2 at the parent — 20 gate invocations total for this item.

**Threat model.** T (Tampering)/S (Spoofing) across the feature-directory trust boundary. Per this
repo's own Expertise (`harness-security-reviewer` project tier P-02), the orchestrator role holds
`.harness/*/features/**` write access **not scoped to its own feature id**, and one orchestrator
instance runs per concurrently in-flight feature — so the actor who can plant a colliding `branch`
value in an unrelated feature's `feature.json` is not a hypothetical external attacker, it is a
routine harness role already granted that path. This is not merely theoretical: branch values are
data, not identity-checked for uniqueness anywhere in the write path (`feature-schema.json`/
`feature_schema.py` validate shape, never cross-file uniqueness of `branch`), so a copy-paste feature
scaffold, a reused branch name after an abandoned feature's directory is left behind, or a careless
orchestrator write can trigger either direction without any adversarial intent.

**Severity: high.** Not gating this cycle (pre-existing, not introduced at 894adc0f, and this feature
never closed it in six prior cycles) — recorded as `open_questions`, not `must_fix`, per this
dispatch's explicit rule. Rated honestly per `gates.review: advisory_unless_high` (Contract §3): a real,
freshly-executed high-severity gap in code this feature ships, regardless of which commit is to blame.

## Item 2 — ALLOW when a feature's OWN record is non-dict/unparseable/deleted

Isolated fixture, single feature dir, no collision (`item2_driver.py`, corroborated by
`item2b_stderr_check.py` for exact stdout/stderr):

| own-record state | PIN | PARENT (894adc0f^) |
|---|---|---|
| healthy, owing | `deny` | `deny` (sanity) |
| **non-dict** (valid JSON, e.g. `["branch","feature/test"]`) | **ALLOW, silent** (stdout `''`, stderr `''`, exit 0) | `deny` — "could not evaluate a feature's Build-entry receipt" |
| unparseable JSON | ALLOW | ALLOW (matches at pin — `json.JSONDecodeError` was caught by `except (OSError, json.JSONDecodeError): continue` in the parent too, **before** ever reaching the `unusable`-setting `isinstance` check, so this sub-case never actually flipped) |
| file deleted | ALLOW | ALLOW (same reason — `OSError` on open is caught the same way in both) |

Only the **non-dict-but-parseable** sub-case is a genuine pin-vs-parent behavioral delta, confirmed
executed. **Re-derived against Contract §1: this is the signed trade, not a bypass beyond it.** The
mechanism cannot special-case "this malformed record would have been mine" versus "would have been
someone else's" — both fail at the same `isinstance(document, dict)` check, before `branch` is ever
read, so there is no narrower fix that closes self-corruption while keeping the cross-feature-poisoning
fix Contract §1 signs off on; closing one necessarily reopens the other. I looked for a harm specific
to *self*-corruption beyond that generalization and found none:
  - Write-time defense is unchanged by this diff. `check-domain.sh`'s PreToolUse/PostToolUse hooks
    (`.claude/settings.json:23,68`, `.omp/extensions/harness-hooks.ts:227-270`) run
    `feature_schema.problems_for_text` against `.harness/*/features/*/feature.json` on every
    Write/Edit and, per the tool's own comments (`check-domain.sh:18-21`, `:2102-2106`), on a
    **post-hoc sweep** for Bash too — this is a pre-existing, already-documented, already-accepted
    gap ("truly arbitrary shell remains unwinnable... caught post-hoc, not pre", DEC-151), not a new
    exposure this diff created.
  - Audit-trail silence is symmetric, not specific to corruption: the ordinary "genuinely no record
    exists, branch resolved without failure" ALLOW path is *equally* silent (`if document is None: if
    failure: print(...); return` — no `else` branch prints anything), so corrupted-own-record adds no
    new distinguishability gap beyond what the signed design already accepts everywhere on this path.

**Verdict: assessed and dismissed — within Contract §1's signed trade.** Recorded here so a later
reviewer does not have to re-derive it; not a finding, not in must_fix.

## Item 3 — command-string parsing evasions

`item3_driver.py`, single owing fixture, run at PIN and PARENT for each command form:

| form | PIN | PARENT | note |
|---|---|---|---|
| `git merge feature/test` | deny | deny | baseline |
| `git -C /tmp merge feature/test` | **ALLOW** | **ALLOW** | evasion |
| `git -c foo=bar merge feature/test` | **ALLOW** | **ALLOW** | evasion |
| `git --work-tree /tmp merge feature/test` | **ALLOW** | **ALLOW** | evasion |
| `B=feature/test; git merge $B` | **ALLOW** | **ALLOW** | evasion (see below) |
| `eval "git merge feature/test"` | deny | deny | caught (literal verb inside eval is tokenized fine) |
| `bash -c "git merge feature/test"` (depth 1) | deny | deny | caught |
| `bash -c "bash -c \"git merge feature/test\""` (depth 2) | deny | deny | caught |
| 3 nested `bash -c` (depth 3) | **ALLOW** | **ALLOW** | evasion, by-design cap (`depth >= 3: return None`) |
| 4 nested `bash -c` (depth 4) | **ALLOW** | **ALLOW** | evasion, same cap |

Root cause of the three flag-based evasions: `git_merge`'s `args = [w for w in rest if not
w.startswith("-")]` strips the flag token itself (`-C`, `-c`, `--work-tree`) but **not the flag's
value argument that follows it** (`/tmp`, `foo=bar`), so `merge` shifts to `args[1]` instead of
`args[0]` and the `args[0] != "merge"` check fails. `$B` is never shell-expanded by `shlex` (no shell
semantics at all), so the branch resolved is the literal string `"$B"` — never colliding with any real
feature's `branch` field — while the real merge, on whatever branch `$B` actually expands to in the
live shell, proceeds ungated. All four confirmed **byte-identical at the parent** (`merge_ref`/
`git_merge`/`words`/`nested_merge` are untouched by `894adc0f^..894adc0f` per the earlier `git diff`)
→ **pre-existing, not introduced by this diff.**

**Threat model.** This is a local PreToolUse Bash hook gating the operator's/agent's own shell command
before it runs — not a remote or multi-tenant boundary. The actor who evades it already has full
authority to `git merge` (that is a given for anyone with shell access to the repo at all); evading the
token match grants no privilege they lacked. What it defeats is process/audit integrity (STRIDE
Repudiation), not access control (STRIDE Elevation of Privilege) — per this role's own Expertise P-02,
that reclassifies it down from "privilege escalation" framing. What raises it above pure theory: `-C`,
`-c`, and `--work-tree` are ordinary git idioms (the file's own `local_branch()` helper uses `git -C`),
so this fails open on **routine, non-adversarial usage**, not only deliberate evasion — no test in
`test-merge-gate.py` covers any of the three flag forms or the `$VAR` form (grepped).

**Severity: medium.** Pre-existing, not gating this cycle; recorded as `open_questions`.

## Item 4 — gh-sync.py and hook-install surfaces: secrets, logs, injection

**Read, in full or targeted grep, and confirmed:** `gh-sync.py` (full, 2330 lines — read the header
docstring and every `subprocess.run`/`gh(`/`gh_try(` call site via grep), `feature_schema.py` (full),
`check-state.sh` (grepped), `post-merge-sweep.sh` (grepped), `.claude/settings.json` (grepped),
`.claude/skills/harness/templates/settings.snippet.json` (grepped), `.omp/extensions/harness-hooks.ts`
(grepped). No `shell=True`, no `os.system`, no string-built shell command anywhere in this set — every
`subprocess.run` call is list-argv (`[GH] + args`, `["git", "-C", ...] + args`), which is immune to
shell metacharacter injection by construction. No `TOKEN`/`SECRET`/`Authorization`/`GH_TOKEN` literal
appears in any of these files; `gh-sync.py` never handles an auth token directly — it delegates entirely
to the `gh` CLI's own stored credentials (`gh auth status` is the only auth touchpoint, a status check,
never a credential read). `gh_cost_log.py` (not itself in the feature's file set, so out of scope, but
touched every `gh()`/`gh_try()` call so spot-checked): appends the invocation's argv and returncode to
a JSON-lines cost log — this could, in principle, echo an `-f description=...` field's content into a
local log file, but that content is operator-authored plan/brief text, not credential material, and this
file is unchanged by BUG-1309. **No finding.**

## Severity summary

| item | severity | novelty | gating |
|---|---|---|---|
| 1 — branch-collision misattribution (both directions) | high | pre-existing (confirmed vs 894adc0f^) | no — `open_questions` |
| 2 — self-corruption ALLOW (non-dict own record) | none (assessed & dismissed) | within Contract §1's signed trade | no |
| 3 — command-parsing evasion (git flags, `$VAR`, depth≥3 nesting) | medium | pre-existing (confirmed vs 894adc0f^) | no — `open_questions` |
| 4 — gh-sync.py / hook-install secrets & injection | n/a | no surface found | no |

`severity_max: high` is driven entirely by item 1, which is real and freshly executed but is **not**
attributable to 894adc0f and was never closed across any of this feature's six cycles. Rated honestly
per `gates.review: advisory_unless_high` — the routing/backlog decision for a pre-existing gap is the
lead's and operator's call, not softened here to keep this review green.
