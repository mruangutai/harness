# SIMPLIFICATION angle — FEAT-24, run 2026-08-19-8-eng

**HEAD check:** `git rev-parse HEAD` = `3396b5e2bc7b9501c714fce23967adc8de6d74b6`. Matches the
dispatched SHA. No mismatch to report.

**Scope note:** `git diff --stat ada8e99..3396b5e` (whole diff) is 64 files / +7473/-482 — mostly
notes/docs. Restricting to the named code surface (`.claude/skills/harness/bin/`'s six modules +
their test files, `.harness/harness.json`, `.harness/factory/fleet.yaml`) gives 13 files /
+1070/-333, not the dispatch's "19 files, +1394/-437". Widening to every touched file under
`.claude/skills/harness/bin/` plus `harness.json`/`fleet.yaml`/`templates/harness.json` gives 22
files / +1413/-458 — still off by 3 files. I read the named list plus `check-state.sh` (FLAG-ONLY
per dispatch) and could not locate a filter that lands exactly on 19/+1394/-437. Not blocking —
HEAD itself matched — but the count is unverified as stated.

## Finding 1 (the only one worth ranking)

- **File:** `.claude/skills/harness/bin/test-gh-sync.py`
- **Lines:** 22 occurrences of the identical literal
  `json.dump({"github": {"sync": True, "repo": "implentio/fake", "board": None}}, ...)` at 399,
  492, 507, 523, 552, 567, 581, 614, 640, 664, 716, 755, 780, 803, 827, 849, 867, 900, 1303, 1317,
  1334, 1351 — each site got `"board": None` added by this diff to satisfy T-04's new "absent
  board raises" rule.
- **Summary:** **21 of the 22 are dead rewrites**, not just unhelpered duplication; one (line 399)
  is load-bearing and must NOT be touched. `stage()` (`test-gh-sync.py:51-60`) already writes
  `.harness/harness.json` with exactly `{"github": {"sync": sync, "board": None, "repo": repo}}`
  at its own last line. I checked every one of the 22 sites individually:
  - **21 sites** (492 through 1351) are each immediately preceded by a `stage(tmpN, ...)` call
    with no config write in between, and none of the 21 overrides `sync=` or `repo=` away from
    the defaults (`True` / `"implentio/fake"`) — the same two fields the subsequent `json.dump`
    hard-codes. So each of these 21 writes byte-identical JSON to the same path `stage()` just
    wrote, immediately after, with nothing reading the file between the two writes.
  - **Line 399 is different** (checked `test-gh-sync.py:362-400`): its enclosing block calls
    `stage(tmp)` once at the top, then deliberately rewrites `harness.json` twice more before
    line 399 to exercise the skip paths — `{"github": {"sync": False}}` (asserts SKIP) and
    `{"github": {"sync": True}}` with no `repo` (asserts "not pinned") — and line 399 is what
    restores the real config afterward, under the comment `# --- the real open`. That write is
    load-bearing and correctly placed.
- **Concrete cost:** a reader has to reconstruct `stage()`'s internals to know 21 of these 22
  calls are inert, and the block containing line 399 makes it easy to assume ALL 22 are the same
  shape (they read identically) when only that one actually depends on the intervening rewrites.
  The 21 dead ones are not fixture writes any assertion depends on — deleting them changes no
  test outcome, so this is not the "asserts the same fact twice" backlog-only case; it is dead
  code the diff extended (added `"board": None` to it) instead of removing.
- **Alternative:** delete the 21 dead `json.dump(...)` two-line blocks (492, 507, 523, 552, 567,
  581, 614, 640, 664, 716, 755, 780, 803, 827, 849, 867, 900, 1303, 1317, 1334, 1351); `stage()`'s
  own write already covers them. Leave line 399 exactly as-is — it is the one site where the
  rewrite is doing real work. No assertion, behavior, or fixture-shape change.
- Not applied here (read-only dispatch). This is a genuine simplification the diff had the chance
  to make (it touched all 22 lines already) but didn't — and any future apply of this finding
  must exclude line 399 or it reddens the "gh missing"/"sync disabled"/"repo unpinned" cases in
  that block.

## Verified clean (worth recording, not a finding)

The dispatch's named hazard — a fake `gh` that models argv but not HTTP method or response shape,
which let `gh api -f` force a POST and `validate=True` reject line-wrapped base64 ship past a
green suite — is **fixed and now directly tested** in this diff:
- `factory_gh.file_at_ref` (`factory_gh.py:428-465`) builds its `argv` with no `-f` flag, so
  `gh api` defaults to GET; `test-factory-gh.py`'s
  `"file_at_ref: hits the contents path with the ref"` case asserts
  `"-f" not in calls[0]["argv"]` directly.
- The base64 decode (`factory_gh.py:456`) does `base64.b64decode("".join(raw.split()), validate=True)`
  — stripping embedded newlines before validating — and
  `"file_at_ref: decodes GitHub's line-wrapped base64 content"` exercises a 60-char-wrapped fixture
  built to reproduce GitHub's real wrapping, not a synthetic unwrapped string.
I did not find a new instance of the same fake-argv-only blind spot introduced elsewhere in this
diff.

## T-06 `_note` hazard — checked before writing anything

Read T-06's `verify:` in `plan.yaml` (lines 1001-1038) before evaluating `.harness/harness.json`'s
`github.board._note`. Current text contains `loud`, `null`, `PLACEMENT IS TEMPORARY`, `project_id`
and is absent `INV-26 is vacuous`, `station writes are not attempted`, `Three keys` — matches all
seven required substrings. Proposed no change to it.

## `check-state.sh` (FLAG-ONLY, DEC-174 carve-out)

No simplification finding. The new `INV-26 BEGINS`/`ENDS` markers and the `_fc26` import-guard are
exactly the mechanism, not narration, and the dispatch already flags the marker-fragility risk
explicitly — nothing further to add.

## Empty otherwise

`factory_config.py`, `factory_gh.py`, `gh_board.py`, `gh-sync.py`, `board-station.py`,
`fleet.yaml`, `templates/harness.json`, and the remaining test files (`test-board-station.py`,
`test-gh-board.py`, `test-factory-decompose.py`) carry no simplification finding — comments are
anchor-carrying (cite D-01..D-10, FEAT-24 task ids) per the "settled, not flaggable" list, and I
found no redundant conjunct, no dead reference, and no simpler-equivalent pipeline that preserves
the anchoring semantics.

`test-factory-config.py` (+591/-333, the largest code-surface change in scope): read in full, not
just previewed. It relocates every per-repo board case through `board_for`/`product_config`
(remote-stub-driven) instead of `load_fleet`, adds the no-checkout / remote-failure /
no-fallback / memoisation cases (THE FIXTURE TRAP, THE MEMO TRAP), and documents in `check()`'s
own docstring why `clear_product_config_memo()` must be its first statement (memo-sensitive calls
must all happen before `check()` is invoked, since Python evaluates `cond` first). No redundant
conjunct or dead reference found; `board_dict()` gained a `**station_overrides` kwarg replacing
three positional ones (`ready=`/`building=`/`review=`), which is a strict simplification already
made by the diff, not a finding against it.

I ran no suite (read-only angle, not required for this dispatch).
