# Security review — panel2 — FEAT-10 software factory

Diff reviewed: `git show 8bbb246022d660492b14fcb9bafec7729b0ba23d` (53 files). LEAVE list honoured
(DECISIONS.md/-INDEX.md, `.harness/logs/`, `.harness/features/FEAT-10-software-factory/*` other
than this artifact). `harness.json`'s `test_matrix` change treated as signed, not re-litigated.

## Verdict: PASS (severity_max = low)

No `must_fix`. One new, real, low-severity gap found in INV-24 (the block "nobody has ever
reviewed"). Everything else checked in the two flagged anchors (`factory_gh.py` project-id fix,
`factory_decompose.py` feature-key guard) confirms clean against the receipts' own claims — no
counter-finding. The five other factory modules were re-read whole; findings there match or are
subsumed by the prior panel's `review-harness-security-reviewer-panel-validator.md` (cited by id
below), so they are reported as carried, not re-argued in full.

## New finding — INV-24's allowed-repo set can silently admit a null repo (low)

`check-state.sh:~876-882` (pinned commit): the gate builds its own allow-list straight from
`harness_yaml.load_file(fleet_p)` —

```
names = [r.get("name") for r in (fleet.get("repos") or []) if isinstance(r, dict)]
repo = fac.get("repo")
if repo not in names: ...
```

— rather than reusing `factory_config.load_fleet`, which is the only place the nine-shape fleet
schema (name is a non-empty string containing `/`, etc.) is enforced. If one `fleet.yaml` `repos`
entry is a dict missing `name` (a plausible copy/paste or merge artifact, and one that does not
break the *other* declared repos — `factory_config.repo_entry` never looks up that entry, so
publish/claim/land for the well-formed entries keep working), `r.get("name")` yields `None`, so
`names` contains `None`. A `feature.yaml` whose `factory:` block carries `repo: null` — normally
never produced by `factory_decompose.py` itself (it always sets `factory["repo"] = args.repo`,
already fleet-validated, before the first `write_factory`), but reachable via a hand-edited
`feature.yaml` since that file is not gated on write — then satisfies `repo in names` and both the
"repo not declared" check and the duplicate-issue-claim check silently pass it through. Exit 0,
no `bad.append`, no trace.

**Reachability:** requires two local preconditions to both hold — a malformed `fleet.yaml` entry
and a hand-crafted `factory.repo: null` block carrying real issue/parent numbers. Both require
write access to the harness checkout already (same trust tier the rest of this diff's `info`
findings are graded at — see prior panel items 4/6/8). That is why this stays `low` and not
`must_fix`: it is a gap in the control INV-24 exists to be, not a path an external actor can
reach. Recommend (not fixed here, per the no-source-edit constraint): build `names` through
`factory_config.load_fleet`/`repo_entry` instead of a second, unvalidated read of the same file.

**Ruled out, not a finding:** the neighbouring `except harness_yaml.YamlParseError: continue` on
an unparseable `feature.yaml` (comment: "the parse failure is already a violation elsewhere").
Verified — `check-state.sh`'s independent INV-6..8 block (`grep -n 'feature.yaml does not
parse'`) iterates the same `glob.glob(.../features/*/feature.yaml)` earlier in the same script
and unconditionally appends a violation on any parse failure, so INV-24's skip does not fail
open: the same run already reports it.

## The two flagged anchors — confirmed clean

**`factory_gh.py:268-271` (`project_field_set`'s new `gh project view` call).** `owner`/`number`
reaching this call are exclusively `fleet.yaml`'s schema-validated `board.owner`/`board.number`
(via `factory_config.load_fleet`) — never board content, issue text, or any other
externally-influenced value. The parsed response is used for exactly one field, `["id"]`; a
missing or wrong-shaped key raises (`KeyError`/`TypeError`), caught by `factory_cli.run`'s
generic trap and exits 2 — no further remote write happens after that point in any of the three
callers (decompose step 7, claim step 6, land step 5), though note the *board item* and, in
decompose's case, the *GitHub issue*, were already created earlier in the same run — "no further
remote write," not "nothing mutated," is the accurate claim. Nothing from the response (title,
other fields) reaches stdout, stderr, or `feature.yaml`. No shell (`subprocess.run` is list-argv
throughout — reconfirmed, matches prior panel item 1). Matches receipt
`receipt-harness-backend-dev-S1-projectid-c0.md`'s account exactly.

**`factory_decompose.py:287-293` (feature-key guard).** Refuses non-str/blank before
`factory_gh.preflight()` — zero remote calls on refusal, confirmed by reading the call order.
A well-formed-but-hostile `feat_id` (long, contains punctuation, etc.) only ever reaches GitHub as
part of a `--label`/`--title`/`--body` argv token, always after a fixed non-empty prefix
(`"feature:"`) — closing the leading-dash flag-injection channel the prior panel flagged as a
live mechanism elsewhere (item 2b: bare positional labels always take a fixed literal or a
`feature:`-prefixed value in every call site in this diff). Not independently a new risk.
`plan.yaml`/`feature.yaml` are the same trust tier as the operator's own signed plan — not
external input.

## Carried from the prior panel (re-derived, not new)

- Argv is list-form everywhere (`factory_gh.py`, `factory_workspace.py`) — no `shell=True`.
  (panel-validator #1)
- `fleet.yaml`/plan/feature YAML load through `harness_yaml`'s safe-loader-only path — reconfirmed
  `_StrictSafeLoader` subclasses only `CSafeLoader`/`SafeLoader`. (panel-validator #8)
- `FACTORY_GH`/`FACTORY_GIT` env override requires code-exec-equivalent access already.
  (panel-validator #6)
- No token/credential material reaches `GhError.__str__`, stdout, or `feature.yaml` — only
  `what`/`value`/`next_step`, never raw captured stdout/stderr. (panel-validator #9)
- `workspace_path`/`FEATURES_ROOT` path joins are always forced through a fleet-declared,
  schema-validated repo name first. (panel-validator #4)

## New, low-severity observations (info)

- **`factory_claim.py`'s self-ownership shortcut trusts `--as` unverified** (never checked
  against `gh api user`). A peer process invoking `factory_claim.py --issue N --as <other-login>`
  after that issue is already claimed takes the shortcut and re-emits its payload without holding
  the actual mutex (`create_ref`, still the only thing that decides ownership per the module's own
  docstring). No privilege escalation — every invoker already shares the one authenticated `gh`
  session (Expertise P-02) — but it is a **Repudiation** gap: the board's assignee/self-ownership
  attribution is self-asserted by argv, not verified against the authenticated identity. `info`,
  worth a one-line note for whoever next touches identity handling in the factory.
- **`extract_brief` → parent issue body, unredacted, on a possibly-public repo.** `BRIEF.md`'s
  Problem/Goal sections are lifted verbatim into the created parent issue with no content check
  and no repo-visibility gate. Operator-authored, publishing to the operator's own configured
  repo — `info`, not a control gap, but flagged since it is new output reaching a system a human
  will read, and the prior panel already established at least one fleet repo is public.

## Scope note

INV-24 (`check-state.sh:858-908` per dispatch anchors) was read in full, read-only, per the
DEC-174 carve-out permitting review without edit. The other four factory modules
(`factory_claim.py`, `factory_workspace.py`, `factory_land.py`, `factory_config.py`) were read
whole; no findings beyond what is listed above.

files_touched: []
