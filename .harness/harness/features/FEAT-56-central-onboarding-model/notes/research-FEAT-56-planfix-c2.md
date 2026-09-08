# plan-fix cycle 2 — panel findings closed, panel recorded

**BLUF — all four gating panel findings are closed in `plan.yaml` and `BRIEF.md`, the eleven-finding
panel record is transcribed, and every amended `verify:` block was observed RED at `4b5dbb23` before
it was written.** `approval:` is untouched at `status: pending`; no risk acceptance was written. Two
residuals go back up: T-02's `files:` still lists a test file the Q2 ruling deletes (out of scope
here), and `check-state.sh` INV-32 will demand a third reader (`goalcheck`) the moment the plan is
signed.

## What changed

| Where | Change | Route |
|---|---|---|
| `plan.yaml` T-01 `verify` | + marker-ORDER discriminator (A3) | `amend`, CAS on `076d6886…` |
| `plan.yaml` T-02 `verify` | rebuilt: `bash` not `python3`, twelve per-file conjuncts (A1) | `amend`, CAS on `81a54a93…` |
| `plan.yaml` T-02 `intent` | six assertions become a one-time build gate, no unit suite (A5) | `amend`, CAS on `789b8914…` |
| `plan.yaml` T-06 `verify` | + `harness.md`, + `harness-grilling.md` (A2) | `amend`, CAS on `3672252a…` |
| `plan.yaml` T-07 `verify` | + `SPEC.md`, + `BUILD.md` (A2) | `amend`, CAS on `bbd1f09b…` |
| `plan.yaml` `panel` | 2 readers, 11 findings (part B) | `set-panel` |
| `BRIEF.md` SC-01 | `inspection` -> `automated` / `evidence: integration`, restated on ORDER (A4) | direct edit |
| `BRIEF.md` `## Verification gaps` | bullet 2 restated; new bullet on the evidence-kind label | direct edit |

Task count 8, every `execution_mode`/`files`/`traces`/`depends_on`/`lanes`/`decisions`/`approval`
untouched. `check-plan-routes.py` exits 0.

## A1 — what each T-02 conjunct reads, and why that string

Every conjunct opens ONE of the six files and asserts against that file's own content; no conjunct is
file-global. Each PRESENT string was greped at `4b5dbb23` and returns 0 matches; each ABSENT string
returns 1. Counts measured at `4b5dbb23`, working tree clean but for the untracked feature dir.

| file | asserts PRESENT | asserts ABSENT |
|---|---|---|
| `check-instruction-paths.py` | `harness-init` (D-05 preservation guard, green today — NOT a discriminator, kept because deleting the entry is the failure D-05 forbids); `anchor rule` (0) | `"harness-init",  # main session only` (1) — line-specific: the bare comment survives on the other two tuple entries, so a file-global absence check would be wrong |
| `check-state.sh` | `control-plane clone` (0) | `project not onboarded. Run /harness-init.` (1) |
| `check-domain.sh` | `never carries one` (0) | `enforcement OFF (run /harness-init)` (1) |
| `upgrade-config.py` | `default branch` (0), `control-plane clone` (0) | — (intent names no stale string here) |
| `gh-sync.py` | `on its default branch` (0) | `run /harness-init --upgrade to record it` (1) |
| `layout_migration.py` | `only the control plane carries the fleet declaration` (0) | `installs the whole bin/ into product repos` (1) |

**One assertion in the intent was corrected, not merely relocated.** Item 5 said the gh-sync case
asserts `default branch` PRESENT. That string is ALREADY in `gh-sync.py:673` (an unrelated board
comment), so the assertion was green before the task ran. The recorded assertion is now
`on its default branch`, which returns 0 today.

MF-1 itself: `bash` replaces `python3` for `check-domain.sh`, the idiom at
`FEAT-09-plan-time-route-check/PLAN.md:158`.

## A2 — the four unbacked files

Every candidate string was greped at `4b5dbb23` before being committed to: `default branch` was
rejected for SPEC.md (5 matches, already green) and kept for BUILD.md (0 matches), and
`factory/fleet.yaml` is clean in `harness.md` (0 matches), so it is used there.

- `harness.md`: PRESENT `factory/fleet.yaml` (0 today) + ABSENT `except "BRIEF.md missing", which
  routes to` (1 today — `harness.md:12`, the `## 0. Gate` sentence T-06 item 1 replaces).
- `harness-grilling.md`: PRESENT `default branch` (0) + ABSENT
  `the domain description, and the first glossary terms` (1).
- `SPEC.md`: **absence only, deliberately.** Both `fleet.yaml` (4) and `default branch` (5) already
  match at `4b5dbb23`, so no keyword is discriminating; the two conjuncts pin the exact sentences
  T-07 item 3 must replace — `project not onboarded — tell the user to run` (`SPEC.md:144`) and
  `reads them from this repository at onboarding time` (`:451`).
- `BUILD.md`: PRESENT `default branch` (0) + ABSENT `| writes every project artifact | yes, once |`
  (`BUILD.md:388`).

## A3 — the T-01 order discriminator, proven to discriminate

Every earlier conjunct is red at `4b5dbb23`, so the order clause would never execute there (O-04).
It was proven on two fixtures that satisfy every presence conjunct and differ only in marker order:

```
/tmp/feat56-order-good.md -> exit 0 (DB=1 FL=2 SG=3)   # default branch, then fleet, then segment
/tmp/feat56-order-bad.md  -> exit 1 (DB=2 FL=1 SG=3)   # fleet first — keyword-compliant, wrong model
```

The marker regex is `grep -niE 'default[ _-]branch'` so either spelling counts, and the comparison is
on FIRST occurrences. **Coupling accepted deliberately:** if the rewrite states the model in a
different order anywhere earlier in the file than Step 2 (a frontmatter description, say), the clause
reddens. That is the intended reading of D-04 — the order is the claim, and stating it inconsistently
is the defect — not a false positive.

## A4 — SC-01

`evidence: integration` per the lead's recommendation. It is the nearest ACTIVE kind
(`--kind integration`, non-null `cmd` in `.harness/harness.json`), and it matches this BRIEF's
existing convention: SC-08 and SC-10 also carry `evidence: integration` while naming an exact command
that the integration runner does not discover. That gap is now stated out loud in a new
`## Verification gaps` bullet rather than left implicit — running the integration suite alone does not
grade SC-01, SC-08 or SC-10.

## Panel identity rule (reproducible)

`PF-` + first 32 hex of `sha256(f"{reader}\n{normalize(summary)}")`, `normalize` = lowercase, collapse
whitespace runs to one space, strip — i.e. `panel_findings.py finding_id`, called rather than retyped
(`/tmp/feat56-build-panel.py`). **The string hashed is the string RECORDED.** Ten of the eleven
summaries are byte-identical to the digest's `findings:` list. One is not: finding 7 carries the
appended closure clause the dispatch required, so its recorded id `PF-38d92d6f…` differs from the id
its unaltered digest summary would produce, `PF-7d76024145e414eeaf8eee356820f780`. Both are recorded
here so a later reader can reconcile the digest against the plan. No `approval.rulings` exist, so no
acceptance is invalidated by that difference.

Findings 9-11 needed no alteration: the panel's dismissal reasons are already carried inside the
digest summaries, so they are transcribed verbatim and a later reader can still tell an
assessed-and-dismissed finding from an unread one.

**Disposition mapping — verified, not adopted.** I agree with all eleven. Finding 2 is one defect
closed by two tasks, so `resolved_by: T-06, T-07`; no tool reads that key (`sign-approval --overrule`
and INV-32 read `id`, `severity`, `disposition` only), and a comma-separated pair is the spelling a
naive reader splits correctly. Finding 6 is the `scope` half of the same defect and is closed by T-06
alone, as the digest scoped it.

## Residuals — not fixed here

1. **T-02's `files:` still lists `tests/unit/test-onboarding-model-strings.py`.** The Q2 ruling means
   that file is never created; the key is `tasks[T-02].files`, entry 7. `files` is out of dispatch
   scope. Raised as an open question.
2. **INV-32 wants three readers.** `check-state.sh:534` sets
   `expected_readers = {"should-not-exist", "scope", "goalcheck"}` and appends a `bad` line for any
   reader absent from `panel.readers`. It grades approved plans only (`:427`), so the plan is clean
   today — but the state check will fail the moment the operator signs unless a `goalcheck` entry
   exists. I did not invent one: the panel ran two readers and recording a third would falsify the
   record.

---

## Evidence

### 1. T-02's ORIGINAL verify, verbatim at `4b5dbb23`

```
$ python3 tests/unit/test-onboarding-model-strings.py &&
  python3 .claude/skills/harness/bin/check-instruction-paths.py &&
  python3 .claude/skills/harness/bin/check-domain.sh --resolve "$PWD/README.md"
can't open file '.../tests/unit/test-onboarding-model-strings.py': [Errno 2] No such file or directory
EXIT=2
```

The chain short-circuits on conjunct 1, so MF-1 was proven on conjunct 3 alone:

```
$ python3 .claude/skills/harness/bin/check-domain.sh --resolve "$PWD/README.md"
  File ".../.claude/skills/harness/bin/check-domain.sh", line 24
    set -uo pipefail
            ^^^^^^^^
SyntaxError: invalid syntax
EXIT=1
$ bash .claude/skills/harness/bin/check-domain.sh --resolve "$PWD/README.md"
harness-documentor
EXIT=0
```

### 2. All four amended blocks, loaded from `plan.yaml` and run at `4b5dbb23`

Run through `/tmp/feat56-run-verify.py`, which `yaml.safe_load`s the plan and executes each `verify`
string verbatim in the worktree root — so this also proves each block round-trips as a literal `|`
scalar (a folded `>` would have collapsed the newlines it printed).

```
===== T-01 ===== exit 1     (first failing conjunct: grep -qF 'factory/fleet.yaml' SKILL.md, 0 matches)
===== T-02 ===== exit 1     (first failing conjunct: grep -qF 'anchor rule' check-instruction-paths.py, 0 matches)
===== T-06 ===== exit 1     (prints "OMP port surface: ok", then grep -qF 'factory/fleet.yaml' harness-plan.md, 0 matches)
===== T-07 ===== exit 1     (first failing conjunct: grep -qF 'central onboarding model' DECISIONS-INDEX.md, 0 matches)
```

### 3. `check-plan-routes.py`

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-04 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-01: declared main-session-direct (.claude/skills/harness-init/SKILL.md ungranted)
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-05: declared main-session-direct (...templates... ungranted)
OK T-06: declared main-session-direct (...commands/agents... ungranted)
OK T-07 granted to harness-documentor
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md ungranted)
0 violation(s) across 1 plan(s)
ROUTES_EXIT=0
```

### 4. Plan shape

```
$ python3 -c "import yaml;d=yaml.safe_load(open('<feature-dir>/plan.yaml'));print(len(d['tasks']),len(d['panel']['findings']),[r['status'] for r in d['panel']['readers']],d['approval'])"
8 11 ['ran', 'ran'] {'status': 'pending'}
```

### 5. BRIEF

```
$ grep -c '^- SC-' BRIEF.md                     -> 10
$ grep -nE '^  verify: (automated|inspection|uat)' BRIEF.md
103:  verify: automated        evidence: integration     <- SC-01, was `inspection`
108:  verify: automated        evidence: integration
115:  verify: inspection
125:  verify: inspection
132:  verify: automated        evidence: unit
134:  verify: automated        evidence: unit
137:  verify: automated        evidence: integration
141:  verify: automated        evidence: integration
146:  verify: uat
155:  verify: automated        evidence: integration
$ grep -nA3 '^## Approval' BRIEF.md
177:## Approval
179-status: pending
```

Ten criteria, ten `verify:` lines, approval untouched.

### 6. Write receipts — every `plan.yaml` write went through a verb

```
AMENDED tasks:T-01.verify   / APPLIED <feature-dir>/plan.yaml
AMENDED tasks:T-02.verify   / APPLIED <feature-dir>/plan.yaml
AMENDED tasks:T-02.intent   / APPLIED <feature-dir>/plan.yaml
AMENDED tasks:T-06.verify   / APPLIED <feature-dir>/plan.yaml
AMENDED tasks:T-07.verify   / APPLIED <feature-dir>/plan.yaml
PANEL cycle 0 -> <feature-dir>/plan.yaml   / APPLIED <feature-dir>/plan.yaml
```

### Finding ids

| # | id | sev | reader | disposition | closed by |
|---|---|---|---|---|---|
| 1 | `PF-1eaa38c5f6a2d3e01711128138170312` | med | should-not-exist | resolved | T-02 |
| 2 | `PF-57bc46a64752a5d08568f2b7d9354e96` | med | should-not-exist | resolved | T-06, T-07 |
| 3 | `PF-557e8589de7e7971b41b77d609f4bf1e` | low | should-not-exist | resolved | T-02 |
| 4 | `PF-58fa27f5fd410345e4cb0545014864d6` | info | should-not-exist | open | — |
| 5 | `PF-4d6298531d64e34b9d0ab91aa399e311` | med | scope | resolved | T-01 |
| 6 | `PF-eb1634cb74a591d50bc047d089c0d778` | med | scope | resolved | T-06 |
| 7 | `PF-38d92d6f318e9295e88ac433fcfe9935` | low | scope | resolved | T-01 |
| 8 | `PF-ff668c9d91bd7353ffb373bcce3da189` | low | scope | open | — |
| 9 | `PF-59491b82216d9fa98824c449a5e5c7a5` | info | scope | open | — |
| 10 | `PF-df9286312ab8275be67f4fa2a508c8ce` | info | scope | open | — |
| 11 | `PF-0dc1b21fc56278ddc20336225317b8dc` | info | scope | open | — |

No severity was changed. `severity_max` remains `med`; no operator risk acceptance is owed.
