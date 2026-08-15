# Security review — FEAT-16-factory-per-repo-board

**Verdict: PASS.** Diff `a7c429c..ec195ec` (confirmed ancestor of HEAD). This is a mechanical
migration of one config block (`board:`) from fleet-level to per-repository, plus the callers that
now resolve which repo's board applies. No new input source, no new trust boundary, no credential
handling anywhere in the touched files. Zero findings at low or above; nothing gates.

## The two asks

**1. Query construction in `factory_claim.py`.**

`query = f'{board["station_field"]}:"{board["stations"]["ready"]}" is:open'`
(`factory_claim.py:246`) goes to `gh project item-list ... --query <string>` as ONE argv element
(`factory_gh.py:166-176`, `subprocess.run([gh] + list(args), ...)`, no `shell=True`) — not a shell
command, not SQL, not GraphQL text concatenation. GraphQL calls elsewhere (`_project_field_resolve`,
`factory_gh.py:224-230`) bind `owner`/`number`/`field` as `-f`/`-F` variables, never string-spliced
into the query document — confirmed by reading the call, not inferred.

The interpolated values (`station_field`, `stations.ready`) come only from `fleet.yaml`
— git-tracked, operator-authored — and are validated by **equality membership** against the live
board's own field options before any query is built (`factory_claim.py:229-238`: `if opt not in
options: refuse`). This is **provenance-closed**, not exploitability-proven: the reopening
condition is a Projects field option name that (a) contains filter metacharacters (`"`, `:`) AND
(b) exists on the live board AND (c) is copied into `fleet.yaml` by whoever maintains it. Worst
case if all three align is a widened/misdirected `is:open` read (more or different issues offered
as claimable) — no code execution, no credential path, no cross-repo/cross-board write. This
pattern is **pre-existing, not introduced by this diff** — confirmed at `a7c429c:248`, same
f-string, same lack of character allowlisting, at the fleet level before this feature. The diff
only duplicates it per board. Rating: info.

`--issue` flag-confusion (G-02 in Expertise) is closed by construction: `argparse` declares
`type=int` (`factory_claim.py:197`), so a value starting with `-` cannot reach `gh` as a
re-parseable flag. Assessed and dismissed.

**2. Leakage into logs/refusals/capture artifact.**

No token, credential, or `gh` auth material appears anywhere in the diff — greped the full diff
for `ghp_`/`gho_`/`github_pat_`/PEM headers/`api_key`/`password` patterns: zero hits. `factory_gh.py`
takes no auth material as a parameter and reads no token env var (`gh` handles its own credential
store out of process). Refusal messages (`factory_claim.py:234-237,258-260`;
`factory_decompose.py:237-240`) now name owner, board number, station field, option name and
`boards_searched` — all config-level identifiers, the same class already present pre-diff, just
reworded to be per-repository specific. This is a verbosity change, not an exposure-class change
(P-08).

`notes/board2-capture.md` contains project/field/option **ids** (`PVT_...`, `PVTF_...`) and item
counts — GitHub Projects v2 structural metadata, not secrets, not tokens. No auth material present.

## Other surface checked

- `factory_config.py` `_validate_board`/`load_fleet`: tightened validation (rejects leftover
  top-level `board:`, requires per-repo `board:`) — Tampering-relevant only in that it makes
  misconfiguration LOUDER, not quieter; no fail-open introduced. `repo_entry`/`board_for` raise on
  an unknown `--repo`, so `args.repo` cannot select a board outside the fleet.
- `factory_gh.py` `--repo <value>` call sites are all `["...", "--repo", repo, ...]` — the value is
  always positionally bound to a preceding named flag, so a `-`-leading repo string cannot be
  misread as a flag (distinct from the unflagged-positional shape G-02 warns about).
- `test-check-domain.py` diff is fixture-YAML-only (indenting `board:` under each `repos[]` entry);
  `check-domain.sh` itself is untouched, confirmed by reading the diff directly rather than trusting
  the task framing (DEC-174 carve-out script, correctly absent from this diff).
- `test-no-distribution.py` case5 is a new assertion pinning the live `fleet.yaml` repo-to-board
  pairing via `yaml.safe_load` — no security surface, additive test only.
- No secrets in any of the new receipt/observation files (full-diff grep, clean).

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| `fleet.yaml` (operator config) → `gh` argv | Tampering | yes — list-form argv, equality-membership validation, provenance-closed |
| `gh` output / refusals → stderr, capture artifact | Information disclosure | yes — config-level identifiers only, no credential material anywhere in the touched files |
| `args.repo` (CLI) → board resolution | Elevation of privilege | yes — `repo_entry` raises on unknown repo, no board outside the declared fleet reachable |

```yaml
VERDICT: PASS
DIGEST:
  headline: "Mechanical per-repo board migration; no new input source, no new trust boundary, no credential handling — PASS at info"
  in_scope: true
  scope_reason: "Diff touches a YAML config loader (factory_config.py) and gh CLI invocations (factory_claim/decompose/land.py) that build subprocess argv and refusal-message text from config values — in scope by definition, confirmed clean by inspection."
  severity_max: info
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "fleet.yaml (operator config) -> gh argv", stride: T, mitigated: true }
    - { boundary: "gh output / refusals -> stderr, capture artifact", stride: I, mitigated: true }
    - { boundary: "args.repo (CLI) -> board resolution", stride: E, mitigated: true }
  open_questions: []
  files_touched: [".harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-security-reviewer-c0.md"]
  expertise_update: []
artifact: .harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-security-reviewer-c0.md
```
