# Review — harness-code-reviewer — FEAT-05 PyYAML file parsers
reviewed: 37a8a66..340e18a (18 commits, pinned)

## VERDICT: FAIL

**Headline:** `upgrade-config.py` calls `harness_yaml.load_str` at two live call sites but never
imports `harness_yaml` — every real invocation of `--check`/`--upgrade` crashes with `NameError`,
reproduced live against this repo; the required regression test for this exact script
(`test-upgrade-config.py`, 3 tests, T-04) was never created, so `run-unit-tests.sh` is green with
nothing capable of catching it. Separately, `check-state.sh` converts only 3 of the census's 10
designated CONVERT sites — 7 hand-rolled YAML regex reads (`phase:`, `status:`, `cost:`, `host:`,
the `github:` block) ship unconverted, contradicting REQ-01 and SC-03's own answer key, and one of
them (`status:`/`host:`) is on a **violation-level** invariant a quoted scalar can silently defeat.

## Stage 1 — spec compliance

### Reverse trace: does every change trace to a REQ or D? (~25 files not yet accounted for above)

`git diff --stat 37a8a66..340e18a` touches files beyond the six converted scripts and their tests.
Traced each group by `git log --oneline 37a8a66..340e18a -- <paths>`:

- **`validate-digest.py` + `test-validate-digest.py` + 9 `.claude/agents/harness-*.md` + 5
  `.claude/skills/harness-*/SKILL.md`** all land at a single commit, **`225cc98`**
  ("fix(digest): give 'nothing happened' a spelling... DEC-172/173"), timestamped 06:16:50 — before
  FEAT-05's build spine starts (`60b266c` onward). The BRIEF's own Non-goal line fences
  `validate-digest.py` and the DIGEST fence as **"Feature 2 (DEC-172), blocked on this feature and
  not planned here."** This is real code change to an out-of-scope file, but it predates and is
  disjoint from FEAT-05's task list (T-01..T-17 never touch it) — DEC-171/172/173 were minted in the
  same signing session (`f6c814b`, 06:15:58, "record DEC-171/172/173; sign FEAT-05") as prerequisite
  decisions, then DEC-172/173's own code landed one commit later on the same branch. **Disposition:
  not FEAT-05 scope creep — a distinct, differently-numbered decision's commit riding the same
  branch before the build spine begins.** Flagged so it is not silently absorbed into this feature's
  credit or blame; not a `must_fix`.
- **`CLAUDE.md`, `docs/harness/DECISIONS.md` (+272), `docs/harness/DECISIONS-INDEX.md`,
  `test-gen-decisions-index.py`, `.harness/notes/audit-decisions.py`,
  `.harness/notes/audit-digest-schema.py`** land at `f6c814b` (signing + DEC-171/172/173 record) and
  `60b266c` ("stop self-hosting the enforcement layer (DEC-174); close issue #11") — both are
  FEAT-05's own PLAN-referenced decisions (DEC-174 is the carve-out cited throughout this feature's
  BRIEF/PLAN and `CLAUDE.md`). Traced.
- **`FEAT-03-subissue-mirror/feature.yaml`, `FEAT-04-decisions-index/feature.yaml`** land at
  `60b266c`, matching PLAN Amendment 1's explicit authorization ("the orchestrator's repair of
  FEAT-03's and FEAT-04's feature.yaml... STANDS"). Traced.
- **`.harness/team-config.yaml`** (2 lines) — diffed directly: the only change is quoting the three
  `main_session.writes` glob strings (`.harness/features/*/BRIEF.md ## Approval` etc.), the flow-
  sequence space-`#` repair Amendment 1 describes. **No agent's `domain:` or `read:` entry
  changed** — confirmed by reading the full diff, not just the stat. A domain widening riding in the
  same diff as a write-guard rewrite would have outranked every other finding here; it did not
  happen.

No hand (`[harness:human]`) commits in range: `git log 37a8a66..340e18a --format='%H %s' | grep -in
'harness:human'` → no output.

### SC-03 — NOT MET (check-state.sh); MET (the other five files)

Re-ran `grep -nE 're\.(search|findall|match|finditer|sub|split|compile)'` at `340e18a` over all six
files and diffed row-by-row against `PLAN.md`'s `## Regex census`.

**check-domain.sh, bash-write-guard.sh, gh-sync.py, cost-report.py, upgrade-config.py — all match
the census exactly** (7, 5, 6, 2, 0 STAY calls respectively; every CONVERT call gone). I mapped each
found line to its census bucket by content, not just count, for all five.

**check-state.sh — mismatch.** Found **14** regex calls at final state, not the 7 the census
promises: `check-state.sh:51,52,55,81,83,94` (markdown, correctly stayed) + `:333` (CHECKPOINT_KEYS,
correctly stayed, BRIEF-exempt) = 7 legitimate survivors, **plus** `:268` (`phase:`), `:324`
(`status: complete`), `:328` (`cost:`), `:347` (`host:`), `:425,429,430` (the `github:` block) — the
exact 7 sites the census's own CONVERT column names for this file (old `:237 293 297 316 394 398
399`). `git diff 37a8a66..340e18a -- check-state.sh` shows these blocks are **byte-identical to
baseline** — the whole file's only real change is the `val()`/`runs:` region (issue #11, REQ-02,
correctly fixed) plus the `harness_yaml` import/PYTHONPATH header. INV-11, INV-15, INV-16, INV-17,
INV-21 still hand-parse `state.yaml`/`feature.yaml` with regex. Detail in finding #2.

### SC-04 — MET, re-derived independently

`grep -rn "except ImportError" .claude/skills/harness/bin/*.py *.sh` → exactly one **executable**
hit, `harness_yaml.py:19`, inside the module's own `try: import yaml`. Confirmed via direct `python3`
invocation that it parses nothing (only binds `yaml = None`). Two other files reference the string in
comments/docstrings only (`test-check-domain.py`, `test-harness-yaml.py`).

### SC-11 — MET, re-derived independently, not by citing the author's scan

Wrote my own mechanical scan (not the author's): for every `check("<label>"...)` call in
`test-gh-sync.py`, matched the label's leading subcommand word against the nearest preceding
`run(["<subcommand>", ...])` call. **0 mismatches** across the whole file, including every
`abandon`/`ship`/`open`/`close-task`/`backlog` case. Confirms the author's refutation; issue #12
closes as not-a-defect.

### Other criteria

- **SC-01 MET** — code reads `doc.get("runs")` from a real parse; `test_run_with_trailing_comment_on_id_is_read` present.
- **SC-02 MET** — ran `check-state.sh` myself: exit 0, zero violations, only INV-8 pruned-dir notes (plus one new INV-12 note about an unrecorded FEAT-05 run dir, unrelated to this feature's SCs).
- **SC-05 / SC-06 MET** — ran the suites myself; the paired allow+block assertions exist and pass for both hooks.
- **SC-07 MET** — `ls requirements.txt pyproject.toml package.json` → 3× "No such file"; `grep -ciw six` → 0; "seven prerequisites" and `import yaml` present in `harness-init/SKILL.md`.
- **SC-08 MET (unit level)** — `harness_yaml.py:307-319`, `require_or_bootstrap`'s grant path writes a `json.dumps`-built `systemMessage` to stdout, once, only on the "marker absent" branch (verified: the "present, identity matches" branch returns at line 273, before this code). No competing stdout writer anywhere in `check-domain.sh` or `bash-write-guard.sh` (grepped). UAT (hand-run) originally caught D-14b failing, then confirmed fixed; I independently re-derived the fix's shape from source, not from the disposition note's say-so.
- **SC-09 MET** — UAT (`uat-bootstrap-escape-expiry.md`) ran U-05 against three genuinely distinct transcript UUIDs; block on session mismatch confirmed.
- **SC-10 NOT MET** — see finding #4 below.
- **SC-12 MET, mechanically, but arithmetic exposes the gap** — `run-unit-tests.sh` exits 0, 11 suites, all pass, at-or-above the 9-file baseline. But the plan itself commits to **three** `SCRIPTS` additions across this feature: T-02's `test-harness-yaml.py`, T-04's `test-upgrade-config.py`, and SC-14's `test-harness-yaml-corpus.py` — 9 + 3 = 12 expected, and `run-unit-tests.sh:6`'s `SCRIPTS` array has **11**. The missing entry is `test-upgrade-config.py`, and it names itself: this is the exact test that would have caught finding #1.
- **SC-13 MET, by direct execution, not by re-diffing the receipt file** — `check-state.sh`'s own run against this repo produces the same violation-free result described as baseline; I did not byte-diff `receipt-baseline-run-inventory.md` against a freshly generated post-change listing.
- **SC-14 MET** — `test-harness-yaml-corpus.py` is in the `SCRIPTS` array and passed 8/8, including the four named negative fixtures (team-config.yaml space-`#`, FEAT-04/05 `: ` in prose, FEAT-03 backtick, duplicate key).

## Findings, ranked

### 1. [CRITICAL] `upgrade-config.py` crashes on every real invocation — REQ-06 violated, must_fix

`.claude/skills/harness/bin/upgrade-config.py:99,124` call `harness_yaml.load_str(...)`, but
`harness_yaml` is **never imported anywhere in the file** (only `json, os, re, shutil, sys` at the
top). `yaml_version()`/`yaml_names()` are called unconditionally from `main()` at `:208-209`.
Reproduced live:

```
$ python3 .claude/skills/harness/bin/upgrade-config.py . --check
...
NameError: name 'harness_yaml' is not defined
```

T-04 also required calling `harness_yaml.require_or_die()` once at entry — absent too, so a
PyYAML-less machine gets this same crash instead of the loud, actionable message REQ-03/REQ-04
promise everywhere else. T-04's required `test-upgrade-config.py` (3 named tests) was never
created and never added to `run-unit-tests.sh`'s `SCRIPTS` array — the arithmetic in SC-12 above
names the gap directly. REQ-06 explicitly says the conversion must not "trade a silent fail-open for
a new crash"; this is that crash, and it is not even silent.

### 2. [HIGH] SC-03/REQ-01 violated in `check-state.sh` — must_fix

Seven census-designated CONVERT sites still hand-parse YAML with regex, unchanged from `37a8a66`.
Two concrete failure scenarios, one on a **violation**, one on a **warn**:

- **`check-state.sh:324`** — `re.search(r"^status:\s*complete", txt, re.M)` — and **`:347`** —
  `re.search(r"^host:\s*(\S+)", txt, re.M)`. A legally-quoted scalar, `status: "complete"` or
  `host: "harness-eng-lead"`, is not what these patterns expect: the first fails to match (no
  literal `complete` immediately after the colon-whitespace), and the second captures the literal
  string `"harness-eng-lead"` **with the quote characters included**, which is absent from the
  `LEADS` set it is compared against. Consequence: INV-11 (a complete run with no `cost:` block
  should be a violation) and INV-15 (a complete lead-hosted run's `digest.md` must satisfy the lead
  contract) both **silently stop firing** for that run — exit 0, no message. This is the BRIEF's own
  Problem-statement failure mode, verbatim, on a **violation-level** invariant, in the file whose
  whole job was closing this class everywhere.
- **`check-state.sh:425`** — `re.search(r"^github:\s*$(.*?)(?=^\S|\Z)", txt, re.M | re.S)` requires
  the `github:` key line to hold nothing but trailing whitespace. A `github:  # tracking IDs`
  comment on that line (legal YAML, the exact defect class REQ-01/REQ-02 exist to close) makes the
  match fail, and INV-21 (warn-level) silently never fires for that feature.

`git diff 37a8a66..340e18a -- check-state.sh` confirms these blocks are byte-identical to baseline —
not a partial rewrite that missed an edge case, but the pre-change code, untouched.

### 3. [MED] T-06 Part C never landed; a required comment stayed false

`git diff 37a8a66..340e18a -- test-gh-sync.py` is **empty** — T-06 explicitly required two new
tests (trailing-`#`-comment on `parent:`/`milestone:`; no-`github:`-block returns the all-`None`
default), neither exists. The underlying `load_recorded` logic looks correct on inspection (routed
through `harness_yaml.load_file`, `_opt_int` excludes `bool`), so this is a coverage gap, not a
known-broken path — but it is the exact regression class (#11) this feature exists to guard, in the
one file that got no guard for it. Also: `gh-sync.py:178`'s section comment still reads
`"feature.yaml github block (text ops — no yaml dependency)"` — false since T-06 made
`load_recorded` depend on `harness_yaml`/PyYAML; T-06 explicitly asked for this to be updated.

### 4. [MED] SC-10's receipt is short of its own stated bar, and one of its "swept" claims is wrong

`receipt-harness-backend-dev-typed-value-sweep.md`: `grep -c '^| '` → 10 (5 T-08 rows + header, 3
T-17 rows + header). T-17's own verify text requires **"at least 14 rows."** `gh-sync.py` and
`upgrade-config.py` are covered only by prose ("swept in their own tasks"), not the
one-row-per-consumer table the task calls "the reviewer's checklist." That prose claim is actively
wrong for `upgrade-config.py`: `yaml_names()` (`:99-113`) does
`if isinstance(n, str) and n.strip(): out.append(n.strip())` — a non-`str` `name:` (e.g. an
all-digit or YAML-boolean-shaped agent name) is **silently skipped**, not `str()`-coerced, directly
contradicting D-08's rule and T-04's own instruction ("`str()` every returned name"). Currently
unreachable in production only because finding #1 crashes first.

### 5. [LOW] D-02's "verbatim" claim is not literally true

Old (`check-domain.sh:296` @ `37a8a66`): `"duplicate top-level key(s) {dups} — ..."` (plural, full
list, from a regex scan that also caught **unknown** keys in the same denial when both were
present). New (`:313` @ `340e18a`): `"duplicate key {e.key!r} — ..."` (singular, only the first
duplicate the raising loader hits; the loader raises before the unknown-key check ever runs, so a
file with both problems now reports only one, on this write). Not a security regression — still
fails closed either way — but D-02 explicitly claims the message renders "verbatim," and it does
not; `test-check-domain.py` only asserts the substring `"duplicate key"`, which is why this drifted
unnoticed.

### 6. [LOW, process — see open_questions Q1] T-09's own go/no-go gate was inconclusive

`receipt-harness-backend-dev-hook-identity-probe.md`'s own conclusion: **"RESOLVED VIA:
mechanism-unknown for the real hook"** — two genuine Write/Edit triggers produced zero probe traces.
PLAN.md's Approval note is explicit and binding: *"If nothing resolves, SC-08 and REQ-05 are
unsatisfiable as written and the escape needs redesign — that is a return to the user, not a
member's improvisation."* No ESCALATE was returned; T-12 through T-17 proceeded anyway. A later,
independent probe (`receipt-main-session-hook-resolution-probe.md`) and the user's own hand-run UAT
(`uat-bootstrap-escape-expiry.md`, three genuinely distinct transcript UUIDs) subsequently and
empirically *did* confirm the mechanism works, so the feared outcome did not occur and I am not
raising this above `low` — but the plan's own binding gate was bypassed without the escalation it
mandated, which is worth a durable record.

## Confirmed by independent re-derivation (not just cited)

- D-14b `systemMessage`/T-13 merge interaction: single writer, `json.dumps`-built, correctly gated
  off the silent-allow branch — read the actual code and the whole file for competing stdout writes.
- T-13/T-15 launch-merge equivalence: diffed sorted string-literal sets between pre/post-merge
  commits for both scripts — no message-text drift found, independent of the commit message's own
  claim.
- Fail-closed/deadlock: main session (`agent = ""`) exits 0 in both hooks **before**
  `require_or_bootstrap`/manifest parsing is reached, so a malformed `team-config.yaml` is always
  repairable from the main session. No agent's domain grants that path (grepped, zero hits).
  `harness-dev-ops` is exempt only from `bash-write-guard.sh` (`:56-57`), not from
  `check-domain.sh` — confirmed by reading both files, matches the documented design.
- D-02/D-08 loader semantics: ran `harness_yaml.load_str` directly — duplicate key (top-level and
  nested) raises `DuplicateKeyError`, malformed YAML raises `YamlParseError`, timestamp resolver
  stripped (bare date stays `str`), int/bool resolvers preserved.
- D-13's `read:` tightening and D-08's `str()`-coercion of every `manifest_domains` glob: read at
  source (`harness_yaml.py:129-142`), matches the decision text.
- `run-unit-tests.sh` and `check-state.sh` re-run by me directly (not cited from a prior run):
  11/11 suites PASS, `check-state.sh` exit 0.
- Reverse trace of every file in the diff stat not otherwise covered by the six-script sweep (agents,
  skills, docs, `team-config.yaml`, two other features' `feature.yaml`) — see Stage 1 section above.
  No domain widening, no undisclosed FEAT-05 scope creep; one adjacent-decision commit (`225cc98`,
  DEC-172/173) flagged for the record, not as a defect.

## Severity and gate

`severity_max: critical` (finding #1 — certain, reproduced breakage on a shipped script's primary
path). `must_fix` non-empty. → **FAIL**, independent of the green gates at `340e18a`.
