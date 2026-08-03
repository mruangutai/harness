# Grilling — replace hand-rolled YAML regex with a real parser — 2026-08-02

## Destination

Every harness script that reads YAML does so through a real parser, so a legal-YAML variant an
author writes can never again silently void an invariant. Issue #11 closes as a consequence of the
sweep, not as its point.

**The user split this into TWO features.** This artifact seeds both; pm coins the ids (DEC-133).

- **Feature 1 — the `.yaml` file parsers.** PyYAML as an init prerequisite, plus conversion of
  `check-state.sh`, `gh-sync.py`, `cost-report.py`, `upgrade-config.py`, `check-domain.sh`,
  `bash-write-guard.sh`.
- **Feature 2 — the DIGEST parser.** Fence the three-part return, convert `validate-digest.py`.

**Feature 2 is BLOCKED ON Feature 1 and must not be planned in parallel.** `validate-digest.py`
cannot `import yaml` until Feature 1's init gate makes PyYAML a guaranteed prerequisite, and both
features edit `bin/` and `run-unit-tests.sh`. Plan and ship Feature 1 first.

## Settled

- **Dependency posture** → the "no dependencies" clause of DEC-101 is reversed. PyYAML is permitted
  (DEC-171, appended this session). The wider files-only constraint stands: no CLI, no build step,
  no template generator. CLAUDE.md was edited narrowly to say exactly that.
- **No fallback path** → *require* PyYAML and fail loudly when absent. The user explicitly rejected
  the dual yaml/line-scan path on the grounds that it leaves the brittle regex in the tree, which is
  the thing the effort exists to remove. **This reverses the graceful-degradation clause of DEC-171
  as originally written — DEC-171 needs amending before build.**
- **Where the requirement lives** → a seventh entry in `harness-init`'s existing "six prerequisites"
  HARD GATE. Check the import; if missing, STOP and tell the user the exact install command. No
  `requirements.txt` — nothing in the harness would read it, and it would be the first dependency
  manifest in a files-only repo.
- **Hook behaviour when PyYAML is absent** → **fail CLOSED, block the write.** This reverses
  DEC-101's fail-open reasoning for `check-domain.sh`. **Also needs recording as a decision.**
- **Bootstrap escape** → one exception to fail-closed: if PyYAML is missing, the hook prints the
  install command and permits writes **for that session only**, blocking from the next session on.
  Without this, an existing project that pulls the update without re-running init has every agent
  write blocked — including the writes that would fix it.
- **DIGEST blocks stay in the return message; they do NOT become files.** They get a ```` ```yaml ````
  fence, and the parser extracts the fence and `safe_load`s it. Rejected: DIGEST as a `.yaml` file
  with the return carrying a path — the hook reads `last_assistant_message`, so the path would still
  have to be found in prose; the DIGEST is the compact routing signal that "pointers not payloads"
  deliberately keeps inline (`artifact:` is already that rule's pointer); and it would change the
  return contract for all 16 agents and DEC-122, which is a larger feature and orthogonal to
  removing regex.
- **Unfenced DIGESTs are BLOCKED, not tolerated** → no deprecation window. **CORRECTED 2026-08-02
  after this artifact was signed:** it said "the 16 agent templates and the parser must land in the
  SAME ship, or every agent breaks." Both halves were wrong. It is **13 files**, not 16, and the
  CURRENT parser already accepts a fenced return (verified: fenced, and fenced-with-prose, both
  `digest ok` exit 0), so **templates may ship FIRST**. Only the parser's REJECTION of unfenced
  returns must wait. The 13 templates were fenced by the main session on 2026-08-02; see
  DECISIONS.md DEC-172's Correction paragraph. Agent files are read at spawn, so a restart caveat applies (the
  `harness-init` step 9 shape).
- **Budget** → default `per_feature_usd` 120 per feature, unraised, because the split is what brings
  each within range. Cost is reported, not gated (DEC-134).

## Not yet specified

- Whether the six converted scripts share one YAML helper module or each import `yaml` directly.
  Recommended a shared `bin/harness_yaml.py` during grilling, but this is architecture — eng-lead
  reviews it, and pm should not have it pre-decided.
- How `bash-write-guard.sh` and `check-domain.sh` detect "same session" for the one-time bypass.
  Sharp enough to state, not yet answered; a marker file under `.harness/` is the obvious shape but
  its lifecycle is unexamined.
- **Who edits the 13 return templates in Feature 2.** RESOLVED 2026-08-02 — the user assigned it to
  the main session, which did it. Retained here because the underlying question is unresolved: `team-config.yaml:35` states
  `.claude/agents/** IS DELIBERATELY UNOWNED — no agent may write it, and that is the point.` So
  `check-domain.sh` blocks every template edit, and DEC-172's "templates and parser ship together"
  is unsatisfiable by any agent as the org stands. This is the FEAT-03 Q13 shape recurring
  (`FEAT-03-subissue-mirror/feature.yaml:96` — "no agent domain covers it"). Either the main session
  makes those edits pre-ship, or the ownership rule needs revisiting. **Feature 2 cannot be planned
  until this is answered.**
- **`check-state.sh` gets no bootstrap escape, but the hooks do.** On a PyYAML-less machine the hooks
  permit writes for one session while the `/harness` door refuses to open — so the recovery path is
  "edit files outside the harness." That may be intended; it is currently unstated.

## Out of scope

- Making DIGEST a real file (feature 2's rejected alternative — recorded, not planned).
- Issue #10 (`validate-digest` `change_type` vocabulary lacks `logic`). Same file, different defect:
  a schema-vocabulary gap, not a parser bug. Not absorbed.
- The other regex in `check-state.sh` that is not YAML parsing (`CHECKPOINT_KEYS` whitelist at :279
  is a key check, and the `T-\d+` scan at :89 reads markdown).

## Facts I verified (so pm does not re-derive them)

All at `37a8a66`.

- **Six production scripts hand-parse YAML.** `check-state.sh` (17 regex calls), `gh-sync.py` (11),
  `validate-digest.py` (11), `check-domain.sh` (9), `bash-write-guard.sh` (6), `upgrade-config.py`
  (2), `cost-report.py` (1). Counted with `grep -cE 're\.(search|findall|match|finditer)'`.
  **Caveat found in FEAT-05 planning:** `cost-report.py` does not PARSE YAML into values — it does a
  targeted line-scan replacement of the `cost:` block (`:189`). Whether it belongs in the sweep is a
  scope judgment, not a given; the BRIEF's REQ-01 named it without that distinction.
- **The three "shell" scripts are bash wrappers around embedded Python heredocs** —
  `check-domain.sh:35,74,97,235`, `bash-write-guard.sh:24,48`, `check-state.sh:17`. There is no
  Python-startup cost to *add*; `check-domain.sh` already launches the interpreter three times per
  hook call. Consolidating would likely make it faster.
- **Measured latency, 100 iterations each:** bare `python3 -c pass` 16.7ms · `python3 -c 'import
  yaml'` 29ms · `check-domain.sh` on a `{}` payload 23.7ms. **The 23.7ms figure is WRONG for the
  governed path** — a `{}` payload has no `agent_type` and returns early, so it never exercised the
  hook. dev-ops measured the real governed path at **80.63ms** during FEAT-05 planning. Use that.
- **PyYAML is NOT importable from `/opt/homebrew/bin/python3`**, and PEP 668 rejects a plain
  `pip install` (`--dry-run` output names `--break-system-packages` as the override).
- **Apple's `/usr/bin/python3` DOES ship PyYAML 6.0.1.** Do not pin it — macOS-only and deprecated
  for scripting; it would break Linux, CI, and the distributable package.
- **The #11 defect, precisely:** `check-state.sh:109`'s block-form regex requires `\s*\n` after the
  `id:` and `squad:` captures, so a trailing `#` comment on either line drops the entire run from
  `runs`, silently failing open on INV-6, INV-7 and INV-8 at exit 0. Reproduced directly. It has not
  fired only because those two lines carry no comments anywhere today (0 of them, vs 18 on
  `verdict:` and 20 on `cost_usd:` in `FEAT-03-subissue-mirror/feature.yaml`, which are harmless
  because `verdict:` is the last capture and `cost_usd:` is outside the regex).
- **An author already hit this and routed around it instead of fixing it** —
  `FEAT-03-subissue-mirror/feature.yaml:63-64` carries a written warning about exactly this bug.
- **The defect class is documented repeatedly in-tree; #11 is not its first appearance.** I did not
  verify an ordinal and am not claiming one. What is checkable: `check-state.sh:105-107` names two
  priors in its own comment (DEC-123 digest parser, DEC-129 INV-4), DEC-101 records an INV-12 false
  positive on block-form YAML, and `validate-digest.py:247-272` documents five hand-patches of the
  same class — one (F4) a trailing-`#`-comment fix identical to #11, found independently.
- **`validate-digest.py` runs as a `SubagentStop` hook** and validates
  `d.get("last_assistant_message")` (`:645`) — the DIGEST is inherently in the return text. Its
  doctrine (`:610-621`) already fails open on its own bugs and returns 0 when `stop_hook_active`, so
  a blocking fence requirement cannot infinite-loop.
- **The three-part return is already a well-formed YAML mapping** (`VERDICT:` scalar, `DIGEST:`
  mapping, `artifact:` scalar) but is unfenced in free prose — `harness-handoff/SKILL.md:14-22`. All
  five patches are boundary-detection bugs, not YAML bugs.
- **`check-state.sh` currently passes** — exit 0, zero violations; all output is INV-8 notes about
  pruned run dirs.
- **No `requirements.txt`, `pyproject.toml` or `package.json` exists at repo root.**
- **Open backlog checked** (`gh issue list`): #11 is the anchor. #12, #13, #14 are test-coverage
  issues in the same scripts — pm should consider whether the sweep's TDD work absorbs any.
- **Issue #5 was closed in this grilling session, outside the user's stated scope.** Appending
  DEC-171/172 reddened `test-gen-decisions-index.py`, which is exactly what #5 predicted ("the next
  appended decision reddens the unit gate"). Rather than bump the frozen constant, the assertion now
  checks the RELATIONSHIP it was actually testing — that the raw regex over-harvests the
  fence-guarded parse by exactly the one DEC-83 duplicate inside a code fence. Verified no other
  frozen totals remain: `grep -nE '(!=|==) *[0-9]{2,}'` over that file returns nothing. Flagged
  because it was not scoped in by the user.
